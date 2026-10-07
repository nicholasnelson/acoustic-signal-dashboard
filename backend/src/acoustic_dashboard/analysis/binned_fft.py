# Binned FFT feature extractor

from collections.abc import Sequence
from datetime import datetime
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike
from scipy import signal

from acoustic_dashboard.core import FeatureWindow

Spacing = Literal["linear", "log"]

_EPS = 1e-12


class BinnedFFT:
    def __init__(
        self,
        sample_rate: int,
        n_bins: int = 6,
        spacing: Spacing = "linear",
        *,
        n_fft: int = 1024,
        edges: Sequence[float] | None = None,
    ) -> None:
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if n_bins <= 0:
            raise ValueError("n_bins must be positive")
        if n_fft <= 0:
            raise ValueError("n_fft must be positive")

        nyquist = sample_rate / 2
        if edges is None:
            if spacing == "linear":
                edges = np.linspace(0.0, nyquist, n_bins + 1)
            elif spacing == "log":
                edges = np.geomspace(sample_rate / n_fft, nyquist, n_bins + 1)
            else:
                raise ValueError(f"spacing must be 'linear' or 'log', got {spacing!r}")
        edges = np.asarray(edges, dtype=np.float64)
        if edges.shape != (n_bins + 1,) or np.any(np.diff(edges) <= 0):
            raise ValueError(f"edges must be {n_bins + 1} ascending values")
        if edges[-1] > nyquist:
            raise ValueError(f"top edge {edges[-1]} Hz exceeds Nyquist {nyquist} Hz")

        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.edges = edges

        # Which band each FFT bin belongs to
        freqs = np.fft.rfftfreq(n_fft, d=1 / sample_rate)
        band_of_bin = np.digitize(freqs, edges[1:-1])
        band_of_bin[(freqs < edges[0]) | (freqs > edges[-1])] = -1
        self._band_of_bin = band_of_bin
        empty = [b for b in range(n_bins) if not np.any(band_of_bin == b)]
        if empty:
            raise ValueError(f"bands {empty} contain no FFT bins; use fewer bins or a larger n_fft")

    @property
    def dim(self) -> int:
        return len(self.edges) - 1

    def extract(self, samples: ArrayLike, timestamp: datetime, source_id: str) -> FeatureWindow:
        x = np.asarray(samples, dtype=np.float64)
        if x.ndim != 1:
            raise ValueError(f"samples must be 1-D, got shape {x.shape}")
        _, _, sxx = signal.spectrogram(
            x, fs=self.sample_rate, nperseg=self.n_fft, noverlap=self.n_fft // 2
        )
        energies = [
            10 * np.log10(sxx[self._band_of_bin == b].mean() + _EPS) for b in range(self.dim)
        ]
        return FeatureWindow(timestamp=timestamp, source_id=source_id, vector=np.array(energies))
