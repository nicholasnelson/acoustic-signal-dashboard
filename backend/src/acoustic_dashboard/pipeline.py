# Pipeline runner
# network audio -> windows -> features -> score
# Minimal demo, assumes the first N windows are normal
#     uv run python -m acoustic_dashboard.pipeline sources.example.json

import asyncio
import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path

from websockets.exceptions import ConnectionClosed

from acoustic_dashboard.analysis.binned_fft import BinnedFFT
from acoustic_dashboard.analysis.spectral_stats import SpectralStats
from acoustic_dashboard.analysis.time_domain import TimeDomainStats
from acoustic_dashboard.analysis.windowing import Windower
from acoustic_dashboard.capture.websocket_source import StreamHeader, receive
from acoustic_dashboard.core import FeatureWindow
from acoustic_dashboard.detection import MahalanobisDetector

log = logging.getLogger(__name__)

EXTRACTORS: dict[str, Callable] = {
    "binned_fft": BinnedFFT,
    "spectral_stats": SpectralStats,
    "time_domain": lambda sample_rate, **params: TimeDomainStats(**params),
}


class Runner:
    def __init__(self, source: dict, publish: Callable[[dict], None]) -> None:
        self.source = source
        self.publish = publish
        self.detector = MahalanobisDetector()
        self.baseline: list[FeatureWindow] = []
        self.threshold: float | None = None

    async def run(self) -> None:
        while True:
            try:
                await self._consume()
            except (OSError, ConnectionClosed) as e:
                log.warning("%s: stream lost (%s), reconnecting", self.source["source_id"], e)
            await asyncio.sleep(2)

    async def _consume(self) -> None:
        s = self.source
        async for item in receive(s["url"]):
            if isinstance(item, StreamHeader):
                rate = item.sample_rate
                windower = Windower(
                    int(s["window_seconds"] * rate), int(s["hop_seconds"] * rate), rate, item.start
                )
                extractor = EXTRACTORS[s["extractor"]](rate, **s.get("extractor_params", {}))
                continue
            for timestamp, window in windower.push(item):
                self._handle(extractor.extract(window, timestamp, s["source_id"]))

    def _handle(self, fw: FeatureWindow) -> None:
        event = {"source_id": fw.source_id, "timestamp": fw.timestamp.isoformat()}
        if self.threshold is None:
            self.baseline.append(fw)
            n = self.source["calibration_windows"]
            if len(self.baseline) >= n:
                self.detector.fit(self.baseline)
                self.threshold = self.detector.threshold_from_baseline(self.baseline)
                log.info("%s: calibrated, threshold %.3f", fw.source_id, self.threshold)
            self.publish(event | {"state": "calibrating", "progress": len(self.baseline) / n})
            return
        score = self.detector.score(fw)
        self.publish(
            event
            | {
                "state": "armed",
                "score": score,
                "threshold": self.threshold,
                "is_anomaly": score > self.threshold,
            }
        )


async def main(config_path: str) -> None:
    sources = json.loads(Path(config_path).read_text())["sources"]
    async with asyncio.TaskGroup() as tg:
        for source in sources:
            tg.create_task(Runner(source, lambda e: print(json.dumps(e), flush=True)).run())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(sys.argv[1]))
