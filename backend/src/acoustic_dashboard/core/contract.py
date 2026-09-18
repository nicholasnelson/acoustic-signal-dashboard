"""The feature vector contract.

A :class:`FeatureWindow` is the state of one input source over one window of time,
compressed into a fixed-length float vector. It is intentionally minimal: this is the
entire structure the detector sees. Any two windows with the same ``source_id`` are
comparable, because a source id names one immutable configuration of an input stream
(device, sample rate, window/hop, extractor and its parameters).
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import ArrayLike, NDArray

Vector = NDArray[np.float32]


@dataclass(frozen=True, slots=True)
class FeatureWindow:
    """One source, one window of time, one fixed-length feature vector."""

    #: Start of the window
    timestamp: datetime
    #: Immutable input-stream configuration this window came from
    source_id: str
    #: 1-D float32, same length for every window of a given source. Read-only.
    vector: Vector

    def __post_init__(self) -> None:
        vector = np.asarray(self.vector, dtype=np.float32)
        if vector.ndim != 1:
            raise ValueError(f"vector must be 1-D, got shape {vector.shape}")
        if vector.size == 0:
            raise ValueError("vector must not be empty")
        # Copy so a caller mutating their array can't change us, then freeze
        vector = np.array(vector, copy=True)
        vector.setflags(write=False)
        object.__setattr__(self, "vector", vector)

    @property
    def dim(self) -> int:
        return self.vector.shape[0]


@runtime_checkable
class FeatureExtractor(Protocol):
    """Turns one window of raw samples into a :class:`FeatureWindow`.

    Extractors are the only modality-specific code in the pipeline. An extractor for
    audio, vibration or a slow scalar sensor all satisfy this same protocol.
    """

    @property
    def dim(self) -> int:
        """Length of the vectors this extractor produces."""
        ...

    def extract(self, samples: ArrayLike, timestamp: datetime, source_id: str) -> FeatureWindow:
        """Compute the feature vector for one window of ``samples``."""
        ...


@runtime_checkable
class Detector(Protocol):
    """Answers: how unusual is this window compared to normal for its source?

    Trained on normal data only. ``fit`` learns what normal looks like from baseline
    windows, ``score`` returns a distance from that baseline where higher means more
    anomalous. Detectors never see raw samples, only :class:`FeatureWindow`.
    """

    def fit(self, windows: Sequence[FeatureWindow]) -> None:
        """Learn a baseline from windows known to be normal."""
        ...

    def score(self, window: FeatureWindow) -> float:
        """Anomaly score for one window. Higher is more anomalous."""
        ...
