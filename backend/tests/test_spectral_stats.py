"""SpectralStats extractor: centroid, bandwidth, rolloff and flatness of one window."""

from datetime import UTC, datetime

import numpy as np
import pytest

from acoustic_dashboard.analysis import SpectralStats
from acoustic_dashboard.analysis.spectral_stats import FEATURES
from acoustic_dashboard.core import FeatureExtractor, FeatureWindow

RATE = 16_000
NYQUIST = RATE / 2
BIN_HZ = RATE / 1024
T0 = datetime(2026, 9, 18, tzinfo=UTC)


def tone(freq_hz: float, seconds: float = 1.0) -> np.ndarray:
    t = np.arange(int(RATE * seconds)) / RATE
    return np.sin(2 * np.pi * freq_hz * t).astype(np.float32)


def noise(seconds: float = 1.0) -> np.ndarray:
    return np.random.default_rng(0).normal(size=int(RATE * seconds))


def features(fw: FeatureWindow) -> dict[str, float]:
    return dict(zip(FEATURES, fw.vector.tolist(), strict=True))


def test_satisfies_extractor_protocol() -> None:
    ex = SpectralStats(RATE)
    assert isinstance(ex, FeatureExtractor)
    fw = ex.extract(tone(1000), T0, "fan-00")
    assert isinstance(fw, FeatureWindow)
    assert fw.dim == ex.dim == 4
    assert fw.source_id == "fan-00" and fw.timestamp == T0


@pytest.mark.parametrize("freq", [500.0, 3000.0])
def test_tone_is_narrow_and_centred_on_its_frequency(freq: float) -> None:
    f = features(SpectralStats(RATE).extract(tone(freq), T0, "s"))
    assert f["centroid"] == pytest.approx(freq, abs=BIN_HZ)
    assert f["rolloff"] == pytest.approx(freq, abs=2 * BIN_HZ)
    assert f["bandwidth"] < 3 * BIN_HZ
    assert f["flatness"] < 0.01


def test_white_noise_is_flat_and_centred_mid_band() -> None:
    f = features(SpectralStats(RATE).extract(noise(), T0, "s"))
    assert f["centroid"] == pytest.approx(NYQUIST / 2, rel=0.05)
    # uniform power over [0, Nyquist]: std = Nyquist / sqrt(12)
    assert f["bandwidth"] == pytest.approx(NYQUIST / np.sqrt(12), rel=0.05)
    assert f["rolloff"] == pytest.approx(0.85 * NYQUIST, rel=0.05)
    assert f["flatness"] > 0.5


def test_rolloff_fraction_moves_rolloff() -> None:
    low = SpectralStats(RATE, ["rolloff"], rolloff_fraction=0.5).extract(noise(), T0, "s")
    high = SpectralStats(RATE, ["rolloff"], rolloff_fraction=0.95).extract(noise(), T0, "s")
    assert low.vector[0] == pytest.approx(0.5 * NYQUIST, rel=0.05)
    assert high.vector[0] > low.vector[0]


def test_silence_is_finite() -> None:
    fw = SpectralStats(RATE).extract(np.zeros(RATE), T0, "s")
    assert np.all(np.isfinite(fw.vector))


@pytest.mark.parametrize("gain", [1e-2, 1e-4, 1e-8])
def test_features_do_not_depend_on_volume(gain: float) -> None:
    ex = SpectralStats(RATE)
    x = tone(1000) + 0.01 * noise()
    loud, quiet = ex.extract(x, T0, "s"), ex.extract(gain * x, T0, "s")
    assert np.allclose(quiet.vector, loud.vector, rtol=1e-3)


def test_feature_subset_sets_order_and_dim() -> None:
    ex = SpectralStats(RATE, features=["flatness", "centroid"])
    fw = ex.extract(tone(2000), T0, "s")
    assert ex.dim == fw.dim == 2
    assert fw.vector[0] < 0.01
    assert fw.vector[1] == pytest.approx(2000, abs=BIN_HZ)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"sample_rate": 0},
        {"n_fft": 1},
        {"rolloff_fraction": 1.0},
        {"features": []},
        {"features": ["loudness"]},
        {"features": ["centroid", "centroid"]},
    ],
)
def test_rejects_bad_configuration(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        SpectralStats(**{"sample_rate": RATE, **kwargs})


@pytest.mark.parametrize("samples", [np.zeros((2, RATE)), np.zeros(512)])
def test_rejects_bad_samples(samples: np.ndarray) -> None:
    with pytest.raises(ValueError):
        SpectralStats(RATE).extract(samples, T0, "s")
