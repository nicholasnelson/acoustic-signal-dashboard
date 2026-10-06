"""BinnedFFT extractor: band energies in dB from one window of samples."""

from datetime import UTC, datetime

import numpy as np
import pytest
from scipy import signal

from acoustic_dashboard.analysis import BinnedFFT
from acoustic_dashboard.core import FeatureExtractor, FeatureWindow

RATE = 16_000
T0 = datetime(2026, 9, 18, tzinfo=UTC)
NOTEBOOK_EDGES = [0, 250, 500, 1000, 2000, 4000, 8000]


def tone(freq_hz: float, seconds: float = 1.0) -> np.ndarray:
    t = np.arange(int(RATE * seconds)) / RATE
    return np.sin(2 * np.pi * freq_hz * t).astype(np.float32)


def test_satisfies_extractor_protocol() -> None:
    ex = BinnedFFT(RATE, n_bins=6)
    assert isinstance(ex, FeatureExtractor)
    fw = ex.extract(tone(1000), T0, "fan-00")
    assert isinstance(fw, FeatureWindow)
    assert fw.dim == ex.dim == 6
    assert fw.source_id == "fan-00" and fw.timestamp == T0


@pytest.mark.parametrize("spacing", ["linear", "log"])
def test_tone_lands_in_its_band(spacing: str) -> None:
    ex = BinnedFFT(RATE, n_bins=8, spacing=spacing)
    freq = 3000.0
    fw = ex.extract(tone(freq), T0, "s")
    expected = int(np.digitize(freq, ex.edges[1:-1]))
    assert int(np.argmax(fw.vector)) == expected


def test_log_edges_are_geometric() -> None:
    ex = BinnedFFT(RATE, n_bins=4, spacing="log")
    ratios = ex.edges[1:] / ex.edges[:-1]
    assert np.allclose(ratios, ratios[0])
    assert ex.edges[-1] == RATE / 2


def test_explicit_edges_match_notebook_band_energies() -> None:
    """Same numbers as ``band_energies`` in notebooks/eda_mimii_fan.ipynb."""
    rng = np.random.default_rng(0)
    x = rng.normal(size=RATE).astype(np.float32) + tone(440)

    f, _, sxx = signal.spectrogram(x, fs=RATE, nperseg=1024, noverlap=512)
    idx = np.digitize(f, NOTEBOOK_EDGES[1:-1])
    notebook = [10 * np.log10(sxx[idx == b].mean() + 1e-12) for b in range(6)]

    fw = BinnedFFT(RATE, n_bins=6, edges=NOTEBOOK_EDGES).extract(x, T0, "s")
    assert np.allclose(fw.vector, notebook, atol=1e-4)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_bins": 0},
        {"spacing": "mel"},
        {"n_bins": 2, "edges": [0, 100]},  # wrong count
        {"n_bins": 2, "edges": [0, 9000, 8000]},  # not ascending
        {"n_bins": 2, "edges": [0, 4000, 9000]},  # above Nyquist
        {"n_bins": 2, "edges": [10, 11, 8000]},  # band with no FFT bin
    ],
)
def test_rejects_bad_configuration(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        BinnedFFT(RATE, **kwargs)


def test_rejects_non_1d_samples() -> None:
    with pytest.raises(ValueError):
        BinnedFFT(RATE).extract(np.zeros((2, RATE)), T0, "s")
