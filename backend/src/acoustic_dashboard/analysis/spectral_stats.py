# Spectral summary statistics feature extractor

from collections.abc import Sequence
from datetime import datetime
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike
from scipy import signal, stats

from acoustic_dashboard.core import FeatureWindow

Feature = Literal["centroid", "bandwidth", "rolloff", "flatness"]

FEATURES: tuple[Feature, ...] = ("centroid", "bandwidth", "rolloff", "flatness")

_EPS = 1e-12


class SpectralStats:
    """Shape of the window average power spectrum.

    - centroid - power weighted mean frequency
    - bandwidth - power weighted spread around centroid
    - rolloff - frequency under which rolloff_fraction of power is
    - flatness - evenness of power distribution over the freq spectrum
    """

    def __init__(
        self,
        sample_rate: int,
        features: Sequence[Feature] = FEATURES,
        *,
        n_fft: int = 1024,
        rolloff_fraction: float = 0.85,
    ) -> None:
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if n_fft < 2:
            raise ValueError("n_fft must be at least 2")
        if not 0 < rolloff_fraction < 1:
            raise ValueError("rolloff_fraction must be between 0 and 1")
        features = tuple(features)
        if not features:
            raise ValueError("features must not be empty")
        unknown = [f for f in features if f not in FEATURES]
        if unknown:
            raise ValueError(f"unknown features {unknown}; choose from {list(FEATURES)}")
        if len(set(features)) != len(features):
            raise ValueError("features must not repeat")

        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.rolloff_fraction = rolloff_fraction
        self.features = features

    @property
    def dim(self) -> int:
        return len(self.features)

    def power_spectrum(self, samples: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
        x = np.asarray(samples, dtype=np.float64)
        if x.ndim != 1:
            raise ValueError(f"samples must be 1-D, got shape {x.shape}")
        if x.size < self.n_fft:
            raise ValueError(f"need at least n_fft={self.n_fft} samples, got {x.size}")
        return signal.welch(
            x, fs=self.sample_rate, window="hann", nperseg=self.n_fft, noverlap=self.n_fft // 2
        )

    def extract(self, samples: ArrayLike, timestamp: datetime, source_id: str) -> FeatureWindow:
        freqs, power = self.power_spectrum(samples)
        # epsilon prevents divide by zero-ish issues. Scaled to the peak so the
        # features don't change with signal level; silence becomes a flat spectrum
        power = power + _EPS * (power.max() or 1.0)
        weights = power / power.sum()

        centroid = np.sum(freqs * weights)
        cumulative = np.cumsum(weights)
        rolloff_idx = min(int(np.searchsorted(cumulative, self.rolloff_fraction)), len(freqs) - 1)
        values = {
            "centroid": centroid,
            "bandwidth": np.sqrt(np.sum((freqs - centroid) ** 2 * weights)),
            "rolloff": freqs[rolloff_idx],
            "flatness": stats.gmean(power) / np.mean(power),
        }
        vector = np.array([values[f] for f in self.features])
        return FeatureWindow(timestamp=timestamp, source_id=source_id, vector=vector)
