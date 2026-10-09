import asyncio
import inspect
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any, TypeAlias

import numpy as np

from .models import AudioChunk


ChunkHandler: TypeAlias = Callable[[AudioChunk], None | Awaitable[None]]


def _load_sounddevice() -> Any:
    """Import sounddevice only when live capture is actually requested."""

    try:
        import sounddevice as sd
    except (ImportError, OSError) as error:
        raise RuntimeError(
            "Live microphone capture requires the 'sounddevice' package and a working "
            "PortAudio input backend. Install/sync the backend dependencies and check "
            "that an input device is available."
        ) from error

    return sd


def list_input_devices() -> list[dict[str, Any]]:
    """Return the PortAudio devices that expose at least one input channel."""

    sd = _load_sounddevice()
    devices = sd.query_devices()

    return [
        {
            "index": index,
            "name": device["name"],
            "max_input_channels": int(device["max_input_channels"]),
            "default_samplerate": float(device["default_samplerate"]),
            "hostapi": int(device["hostapi"]),
        }
        for index, device in enumerate(devices)
        if int(device["max_input_channels"]) > 0
    ]


class LiveMicrophoneSource:
    """Capture a physical microphone/input and emit the existing AudioChunk contract.

    The live source deliberately stops at the capture boundary: it preserves the input
    device's sample rate in ``AudioChunk.sample_rate`` rather than resampling to the MIMII
    16 kHz rate. Resampling belongs in a downstream analysis/pre-processing stage.
    """

    def __init__(
        self,
        machine_config: dict,
        *,
        device: int | str | None = None,
        sample_rate: int | None = None,
        chunk_duration: float = 1.0,
        queue_size: int = 4,
    ) -> None:
        if chunk_duration <= 0:
            raise ValueError("chunk_duration must be greater than zero.")
        if sample_rate is not None and sample_rate <= 0:
            raise ValueError("sample_rate must be greater than zero.")
        if queue_size <= 0:
            raise ValueError("queue_size must be greater than zero.")

        required = ("source_id", "machine_type", "machine_id", "machine_profile")
        missing = [key for key in required if key not in machine_config]
        if missing:
            raise ValueError(f"machine_config is missing required field(s): {', '.join(missing)}")

        self.machine_config = machine_config
        self.device = device
        self.channel_index = int(machine_config.get("channel", 0))
        self.chunk_duration = chunk_duration
        self.queue_size = queue_size

        if self.channel_index < 0:
            raise ValueError("channel must be zero or greater.")

        sd = _load_sounddevice()
        device_info = sd.query_devices(self.device, "input")
        max_input_channels = int(device_info["max_input_channels"])

        if self.channel_index >= max_input_channels:
            raise ValueError(
                f"Input device exposes {max_input_channels} channel(s), but channel "
                f"{self.channel_index} was requested."
            )

        self.device_name = str(device_info["name"])
        self.max_input_channels = max_input_channels
        self.sample_rate = (
            int(sample_rate)
            if sample_rate is not None
            else int(round(float(device_info["default_samplerate"])))
        )
        self.samples_per_chunk = int(round(self.sample_rate * self.chunk_duration))

        if self.samples_per_chunk <= 0:
            raise ValueError("chunk_duration is too small for the selected sample rate.")

        # To select channel N through PortAudio, the stream must expose channels 0..N.
        self.input_channels = self.channel_index + 1
        self.dropped_blocks = 0
        self.last_status: str | None = None
        self._sd = sd

    async def stream(
        self,
        emit_chunk: ChunkHandler,
        *,
        max_chunks: int | None = None,
    ) -> None:
        """Capture live audio until cancelled, or until ``max_chunks`` is reached.

        PortAudio invokes its callback on a separate thread. The callback only copies the
        selected channel and schedules a queue write onto the asyncio event loop; chunk
        construction and downstream processing happen outside the audio callback.
        """

        if max_chunks is not None and max_chunks <= 0:
            raise ValueError("max_chunks must be greater than zero when supplied.")

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[tuple[np.ndarray, str | None]] = asyncio.Queue(
            maxsize=self.queue_size
        )

        def enqueue_block(samples: np.ndarray, status_text: str | None) -> None:
            if queue.full():
                self.dropped_blocks += 1
                return
            queue.put_nowait((samples, status_text))

        def callback(indata, frames, time_info, status) -> None:  # noqa: ARG001
            # This callback runs on PortAudio's thread. Keep it short and never execute
            # detector/feature code here, otherwise the audio stream can underrun.
            selected = np.asarray(indata[:, self.channel_index], dtype=np.float32).copy()
            status_text = str(status) if status else None
            loop.call_soon_threadsafe(enqueue_block, selected, status_text)

        chunk_index = 0
        emitted_frames = 0

        with self._sd.InputStream(
            device=self.device,
            samplerate=self.sample_rate,
            channels=self.input_channels,
            dtype="float32",
            blocksize=self.samples_per_chunk,
            callback=callback,
        ):
            while max_chunks is None or chunk_index < max_chunks:
                samples, status_text = await queue.get()
                self.last_status = status_text

                actual_duration = len(samples) / self.sample_rate
                stream_start_time = emitted_frames / self.sample_rate

                chunk = AudioChunk(
                    source_id=self.machine_config["source_id"],
                    machine_type=self.machine_config["machine_type"],
                    machine_id=self.machine_config["machine_id"],
                    machine_profile=self.machine_config["machine_profile"],
                    chunk_index=chunk_index,
                    stream_start_time=stream_start_time,
                    duration=actual_duration,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    sample_rate=self.sample_rate,
                    samples=samples,
                )

                result = emit_chunk(chunk)
                if inspect.isawaitable(result):
                    await result

                emitted_frames += len(samples)
                chunk_index += 1
