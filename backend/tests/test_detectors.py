"""Behaviour every Detector must have"""

from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from acoustic_dashboard.core import Detector, FeatureWindow
from acoustic_dashboard.detection import MahalanobisDetector

DETECTORS = [MahalanobisDetector]

T0 = datetime(2026, 9, 18, tzinfo=UTC)
SOURCE = "fan-00"
# features on different scales: Hz, dB, ratio
MEANS = np.array([2000.0, -40.0, 1.4])
STDS = np.array([100.0, 2.0, 0.05])


def normal_windows(n: int, seed: int) -> list[FeatureWindow]:
    vectors = np.random.default_rng(seed).normal(MEANS, STDS, size=(n, len(MEANS)))
    return [
        FeatureWindow(timestamp=T0 + timedelta(seconds=i), source_id=SOURCE, vector=v)
        for i, v in enumerate(vectors)
    ]


@pytest.fixture(params=DETECTORS, ids=lambda cls: cls.__name__)
def fitted(request: pytest.FixtureRequest) -> Detector:
    detector = request.param()
    detector.fit(normal_windows(2000, seed=0))
    return detector


def test_satisfies_detector_protocol(fitted: Detector) -> None:
    assert isinstance(fitted, Detector)
    assert isinstance(fitted.score(normal_windows(1, seed=1)[0]), float)


@pytest.mark.parametrize("feature", range(len(MEANS)))
def test_anomaly_scores_above_normal(fitted: Detector, feature: int) -> None:
    # A 6-std shift in any one feature, whatever its units, outscores held-out normal
    normal_scores = [fitted.score(w) for w in normal_windows(500, seed=1)]
    shifted = MEANS + 6 * STDS * np.eye(len(MEANS))[feature]
    anomaly = FeatureWindow(timestamp=T0, source_id=SOURCE, vector=shifted)
    assert fitted.score(anomaly) > np.percentile(normal_scores, 99)
