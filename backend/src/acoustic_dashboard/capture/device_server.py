# Device server: serves capture sources as network audio streams
# Stands in for networked microphones, run as its own process. Each machine in the config
# is served at ws://host:port/<machine>: one JSON header, then float32 mono PCM frames.
# A machine with a "playlist" replays WAV files on a loop (playback per connection);
# a machine with "mic" captures a live input once and shares it with every client.
#
#     uv run python -m acoustic_dashboard.capture.device_server machine_config.example.json

import argparse
import asyncio
import glob
import json
from datetime import UTC, datetime
from pathlib import Path

from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosed

from acoustic_dashboard.broadcast import Broadcast
from acoustic_dashboard.capture.microphone_source import LiveMicrophoneSource
from acoustic_dashboard.capture.models import AudioChunk
from acoustic_dashboard.capture.wav_source import WavPlaybackSource


def expand(playlist: list[dict], base: Path) -> list[Path]:
    """[{"glob": "...", "count": n}, ...] -> WAV paths, in order."""
    files = []
    for entry in playlist:
        matches = sorted(glob.glob(str(base / entry["glob"])))
        if not matches:
            raise ValueError(f"no files match {entry['glob']}")
        files += [Path(m) for m in matches[: entry.get("count", len(matches))]]
    return files


async def send_header(ws: ServerConnection, sample_rate: int) -> None:
    header = {
        "sample_rate": sample_rate,
        "dtype": "float32",
        "start": datetime.now(UTC).isoformat(),
    }
    await ws.send(json.dumps(header))


async def replay(ws: ServerConnection, machine: dict, files: list[Path]) -> None:
    sources = [WavPlaybackSource(f, machine) for f in files]
    await send_header(ws, sources[0].sample_rate)

    async def send(chunk: AudioChunk) -> None:
        await ws.send(chunk.samples.astype("<f4").tobytes())

    while True:
        for source in sources:
            await source.stream(send)


class SharedMic:
    """Live capture fanned to clients"""

    def __init__(self, machine: dict) -> None:
        self.machine = machine
        self.broadcast = Broadcast()
        self.source: LiveMicrophoneSource | None = None

    def start(self) -> None:
        if self.source is None:  # singleton open on first connection
            self.source = LiveMicrophoneSource(self.machine, device=self.machine["mic"])
            asyncio.create_task(self.source.stream(lambda c: self.broadcast.publish(c.samples)))

    async def serve(self, ws: ServerConnection) -> None:
        self.start()
        queue = self.broadcast.subscribe()
        try:
            await send_header(ws, self.source.sample_rate)
            while True:
                await ws.send((await queue.get()).astype("<f4").tobytes())
        finally:
            self.broadcast.unsubscribe(queue)


async def main(config_path: Path, host: str, port: int) -> None:
    machines = json.loads(config_path.read_text())
    playlists = {
        name: expand(m["playlist"], config_path.parent)
        for name, m in machines.items()
        if "playlist" in m
    }
    mics = {name: SharedMic(m) for name, m in machines.items() if "mic" in m}

    async def handler(ws: ServerConnection) -> None:
        name = ws.request.path.strip("/")
        try:
            if name in playlists:
                await replay(ws, machines[name], playlists[name])
            elif name in mics:
                await mics[name].serve(ws)
            else:
                await ws.close(code=4004, reason=f"unknown stream {name!r}")
        except ConnectionClosed:
            pass

    async with serve(handler, host, port):
        for name in [*playlists, *mics]:
            print(f"ws://{host}:{port}/{name}", flush=True)
        await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve capture sources as network audio streams")
    parser.add_argument("config", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9001)
    args = parser.parse_args()
    asyncio.run(main(args.config, args.host, args.port))
