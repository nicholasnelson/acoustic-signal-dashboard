import asyncio
import inspect
import wave
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeAlias

import numpy as np

from .models import AudioChunk


ChunkHandler: TypeAlias = Callable[[AudioChunk], None | Awaitable[None]]


def read_wav(
    file_path: str | Path,
    channel_index: int = 0,
) -> tuple[np.ndarray, int, int]:
    """Load a 16-bit PCM WAV file and return one channel as float32 samples."""

    file_path = Path(file_path)

    with wave.open(str(file_path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_count = wav_file.getnframes()

        if sample_width != 2:
            raise ValueError(f"{file_path}: expected a 16-bit PCM WAV file.")

        if channel_index < 0 or channel_index >= channels:
            raise ValueError(
                f"{file_path}: requested channel {channel_index}, "
                f"but WAV contains {channels} channel(s)."
            )

        raw_audio = wav_file.readframes(frame_count)

    samples = np.frombuffer(raw_audio, dtype=np.int16)

    if channels > 1:
        samples = samples.reshape(-1, channels)
        samples = samples[:, channel_index]

    samples = samples.astype(np.float32) / 32768.0

    return samples, sample_rate, channels


class WavPlaybackSource:
    """Replay a prerecorded WAV file as a simulated live capture source."""

    def __init__(
        self,
        file_path: str | Path,
        machine_config: dict,
        *,
        chunk_duration: float = 1.0,
    ) -> None:
        if chunk_duration <= 0:
            raise ValueError("chunk_duration must be greater than zero.")

        self.file_path = Path(file_path)
        self.machine_config = machine_config
        self.chunk_duration = chunk_duration
        self.channel_index = machine_config.get("channel", 0)

        self.samples, self.sample_rate, self.original_channels = read_wav(
            self.file_path,
            channel_index=self.channel_index,
        )

        self.samples_per_chunk = int(self.sample_rate * self.chunk_duration)

        if self.samples_per_chunk <= 0:
            raise ValueError("chunk_duration is too small for the WAV sample rate.")

    @property
    def total_chunks(self) -> int:
        return int(np.ceil(len(self.samples) / self.samples_per_chunk))

    async def stream(self, emit_chunk: ChunkHandler) -> None:
        """Emit WAV audio chunks at approximately real-time intervals."""

        for chunk_index, start_sample in enumerate(
            range(0, len(self.samples), self.samples_per_chunk)
        ):
            end_sample = start_sample + self.samples_per_chunk
            chunk_samples = self.samples[start_sample:end_sample]

            actual_duration = len(chunk_samples) / self.sample_rate
            stream_start_time = start_sample / self.sample_rate

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
                samples=chunk_samples,
            )

            result = emit_chunk(chunk)
            if inspect.isawaitable(result):
                await result

            # WAV replay is intentionally paced to simulate live capture.
            await asyncio.sleep(actual_duration)
