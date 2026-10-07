"""TimeDomainStats extractor over one window"""

from datetime import UTC, datetime

import numpy as np
import pytest

from acoustic_dashboard.analysis import TimeDomainStats
from acoustic_dashboard.analysis.time_domain import FEATURES
from acoustic_dashboard.core import FeatureExtractor, FeatureWindow

RATE = 16_000
T0 = datetime(2026, 9, 15, tzinfo=UTC)


def tone(freq_hz: float, seconds: float = 1.0, amplitude: float = 1.0) -> np.ndarray:
    t = np.arange(int(RATE * seconds)) / RATE
    return (amplitude * np.sin(2 * np.pi * freq_hz * t)).astype(np.float32)


def features(fw: FeatureWindow) -> dict[str, float]:
    return dict(zip(FEATURES, fw.vector.tolist(), strict=True))


def test_satisfies_extractor_protocol() -> None:
    ex = TimeDomainStats()
    assert isinstance(ex, FeatureExtractor)
    fw = ex.extract(tone(1000), T0, "fan-00")
    assert isinstance(fw, FeatureWindow)
    assert fw.dim == ex.dim == 5
    assert fw.source_id == "fan-00" and fw.timestamp == T0


def test_sine_has_known_statistics() -> None:
    freq, amp = 250.0, 0.5
    f = features(TimeDomainStats().extract(tone(freq, amplitude=amp), T0, "s"))
    assert f["rms"] == pytest.approx(amp / np.sqrt(2), rel=1e-3)
    assert f["peak"] == pytest.approx(amp, rel=1e-3)
    assert f["crest_factor"] == pytest.approx(np.sqrt(2), rel=1e-3)
    assert f["zero_crossing_rate"] == pytest.approx(2 * freq / RATE, rel=0.01)
    assert f["kurtosis"] == pytest.approx(-1.5, abs=0.01)


def test_gaussian_noise_has_zero_excess_kurtosis() -> None:
    x = np.random.default_rng(0).normal(size=10 * RATE)
    f = features(TimeDomainStats().extract(x, T0, "s"))
    assert f["kurtosis"] == pytest.approx(0.0, abs=0.1)
    assert f["zero_crossing_rate"] == pytest.approx(0.5, abs=0.01)


def test_impulses_raise_crest_factor_and_kurtosis() -> None:
    x = np.random.default_rng(0).normal(scale=0.1, size=RATE)
    clicks = x.copy()
    clicks[::1600] += 5.0
    ex = TimeDomainStats()
    smooth, spiky = features(ex.extract(x, T0, "s")), features(ex.extract(clicks, T0, "s"))
    assert spiky["crest_factor"] > 2 * smooth["crest_factor"]
    assert spiky["kurtosis"] > 10 * max(smooth["kurtosis"], 1.0)


def test_silence_is_finite() -> None:
    fw = TimeDomainStats().extract(np.zeros(RATE), T0, "s")
    assert np.all(np.isfinite(fw.vector))
    assert np.allclose(fw.vector, 0.0)


def test_feature_subset_sets_order_and_dim() -> None:
    ex = TimeDomainStats(features=["kurtosis", "rms"])
    fw = ex.extract(tone(250), T0, "s")
    assert ex.dim == fw.dim == 2
    assert fw.vector[0] == pytest.approx(-1.5, abs=0.01)
    assert fw.vector[1] == pytest.approx(1 / np.sqrt(2), rel=1e-3)


@pytest.mark.parametrize("feats", [[], ["loudness"], ["rms", "rms"]])
def test_rejects_bad_configuration(feats: list[str]) -> None:
    with pytest.raises(ValueError):
        TimeDomainStats(features=feats)


@pytest.mark.parametrize("samples", [np.zeros((2, RATE)), np.zeros(1)])
def test_rejects_bad_samples(samples: np.ndarray) -> None:
    with pytest.raises(ValueError):
        TimeDomainStats().extract(samples, T0, "s")
