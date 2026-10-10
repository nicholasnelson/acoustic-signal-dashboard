"""Streaming audio preparation for feature extraction.

Capture sources emit :class:`~acoustic_dashboard.capture.AudioChunk` objects at the
sample rate chosen by the file or input device. Feature extractors, however, expect
fixed-length mono windows at a known sample rate. ``AudioPreprocessor`` is the bridge
between those two stages: it optionally resamples incoming chunks, buffers them, and
emits fixed-size (optionally overlapping) analysis windows.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from math import gcd

import numpy as np
from numpy.typing import NDArray
from scipy import signal

from acoustic_dashboard.capture import AudioChunk

AudioSamples = NDArray[np.float32]


@dataclass(frozen=True, slots=True)
class PreparedAudioWindow:
    """One mono audio window ready to be passed to a ``FeatureExtractor``."""

    timestamp: datetime
    source_id: str
    window_index: int
    sample_rate: int
    samples: AudioSamples

    def __post_init__(self) -> None:
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if self.window_index < 0:
            raise ValueError("window_index must be zero or greater")

        samples = np.asarray(self.samples, dtype=np.float32)
        if samples.ndim != 1:
            raise ValueError(f"samples must be 1-D, got shape {samples.shape}")
        if samples.size == 0:
            raise ValueError("samples must not be empty")

        samples = np.array(samples, dtype=np.float32, copy=True)
        samples.setflags(write=False)
        object.__setattr__(self, "samples", samples)

    @property
    def duration(self) -> float:
        return len(self.samples) / self.sample_rate


@dataclass(slots=True)
class _SourceState:
    input_sample_rate: int
    buffer: AudioSamples = field(default_factory=lambda: np.empty(0, dtype=np.float32))
    next_timestamp: datetime | None = None
    next_window_index: int = 0


class AudioPreprocessor:
    """Convert ``AudioChunk`` objects into fixed-rate, fixed-size analysis windows.

    A separate buffer is maintained for each ``source_id`` so multiple capture streams
    can be fed through one preprocessor instance. ``hop_duration`` may equal the window
    duration for non-overlapping windows or be smaller to create overlapping windows.
    """

    def __init__(
        self,
        *,
        target_sample_rate: int = 16_000,
        window_duration: float = 1.0,
        hop_duration: float = 1.0,
    ) -> None:
        if target_sample_rate <= 0:
            raise ValueError("target_sample_rate must be positive")
        if window_duration <= 0:
            raise ValueError("window_duration must be greater than zero")
        if hop_duration <= 0:
            raise ValueError("hop_duration must be greater than zero")
        if hop_duration > window_duration:
            raise ValueError("hop_duration must not be greater than window_duration")

        self.target_sample_rate = int(target_sample_rate)
        self.window_duration = float(window_duration)
        self.hop_duration = float(hop_duration)
        self.window_samples = int(round(self.target_sample_rate * self.window_duration))
        self.hop_samples = int(round(self.target_sample_rate * self.hop_duration))

        if self.window_samples <= 0 or self.hop_samples <= 0:
            raise ValueError("window/hop duration is too small for target_sample_rate")

        self._states: dict[str, _SourceState] = {}

    def push(self, chunk: AudioChunk) -> list[PreparedAudioWindow]:
        """Add one captured chunk and return every complete analysis window now ready."""

        self._validate_chunk(chunk)
        state = self._states.get(chunk.source_id)

        if state is None:
            state = _SourceState(input_sample_rate=chunk.sample_rate)
            state.next_timestamp = self._parse_timestamp(chunk.timestamp)
            self._states[chunk.source_id] = state
        elif state.input_sample_rate != chunk.sample_rate:
            raise ValueError(
                f"source {chunk.source_id!r} changed sample rate from "
                f"{state.input_sample_rate} to {chunk.sample_rate}; use a new source_id "
                "for a different stream configuration"
            )

        prepared = self._resample(chunk.samples, chunk.sample_rate)
        state.buffer = np.concatenate((state.buffer, prepared))

        windows: list[PreparedAudioWindow] = []
        while len(state.buffer) >= self.window_samples:
            assert state.next_timestamp is not None
            samples = state.buffer[: self.window_samples]
            windows.append(
                PreparedAudioWindow(
                    timestamp=state.next_timestamp,
                    source_id=chunk.source_id,
                    window_index=state.next_window_index,
                    sample_rate=self.target_sample_rate,
                    samples=samples,
                )
            )

            state.buffer = state.buffer[self.hop_samples :]
            state.next_timestamp += timedelta(seconds=self.hop_duration)
            state.next_window_index += 1

        return windows

    def reset(self, source_id: str | None = None) -> None:
        """Clear buffered samples for one source, or for every source when omitted."""

        if source_id is None:
            self._states.clear()
        else:
            self._states.pop(source_id, None)

    def buffered_samples(self, source_id: str) -> int:
        """Number of target-rate samples currently waiting for ``source_id``."""

        state = self._states.get(source_id)
        return 0 if state is None else len(state.buffer)

    def _resample(self, samples: np.ndarray, input_sample_rate: int) -> AudioSamples:
        x = np.asarray(samples, dtype=np.float32)
        if input_sample_rate == self.target_sample_rate:
            return np.array(x, dtype=np.float32, copy=True)

        divisor = gcd(input_sample_rate, self.target_sample_rate)
        up = self.target_sample_rate // divisor
        down = input_sample_rate // divisor
        resampled = signal.resample_poly(x, up, down)
        return np.asarray(resampled, dtype=np.float32)

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        try:
            return datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"AudioChunk timestamp must be ISO-8601, got {value!r}") from error

    @staticmethod
    def _validate_chunk(chunk: AudioChunk) -> None:
        if chunk.sample_rate <= 0:
            raise ValueError("AudioChunk sample_rate must be positive")
        samples = np.asarray(chunk.samples)
        if samples.ndim != 1:
            raise ValueError(f"AudioChunk samples must be 1-D, got shape {samples.shape}")
        if samples.size == 0:
            raise ValueError("AudioChunk samples must not be empty")
