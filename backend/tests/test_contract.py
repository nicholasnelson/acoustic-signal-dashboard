"""The feature vector contract: FeatureWindow plus the extractor/detector protocols."""

from collections.abc import Sequence
from datetime import UTC, datetime

import numpy as np
import pytest

from acoustic_dashboard.core import Detector, FeatureExtractor, FeatureWindow

T0 = datetime(2026, 9, 5, tzinfo=UTC)


def test_feature_window_normalises_vector() -> None:
    fw = FeatureWindow(timestamp=T0, source_id="fan-01", vector=[1, 2, 3])

    assert fw.vector.dtype == np.float32
    assert fw.vector.shape == (3,)
    assert fw.dim == 3
    assert fw.source_id == "fan-01"
    assert fw.timestamp == T0


def test_feature_window_is_immutable() -> None:
    src = np.array([1.0, 2.0], dtype=np.float32)
    fw = FeatureWindow(timestamp=T0, source_id="s", vector=src)

    src[0] = 99.0  # caller's array, must not leak in
    assert fw.vector[0] == 1.0

    with pytest.raises(ValueError):
        fw.vector[0] = 5.0
    with pytest.raises(AttributeError):
        fw.source_id = "other"  # type: ignore[misc]


@pytest.mark.parametrize("bad", [np.zeros((2, 3)), np.float32(1.0), []])
def test_feature_window_rejects_bad_shapes(bad) -> None:
    with pytest.raises(ValueError):
        FeatureWindow(timestamp=T0, source_id="s", vector=bad)


class MeanExtractor:
    """Trivial extractor: the window mean, as a 1-element vector."""

    @property
    def dim(self) -> int:
        return 1

    def extract(self, samples, timestamp: datetime, source_id: str) -> FeatureWindow:
        return FeatureWindow(timestamp, source_id, np.array([np.mean(samples)]))


class OffsetDetector:
    """Trivial detector: distance from the baseline mean."""

    def __init__(self) -> None:
        self.mean: np.ndarray | None = None

    def fit(self, windows: Sequence[FeatureWindow]) -> None:
        self.mean = np.mean([w.vector for w in windows], axis=0)

    def score(self, window: FeatureWindow) -> float:
        assert self.mean is not None
        return float(np.linalg.norm(window.vector - self.mean))


def test_trivial_implementations_satisfy_protocols() -> None:
    extractor = MeanExtractor()
    detector = OffsetDetector()
    assert isinstance(extractor, FeatureExtractor)
    assert isinstance(detector, Detector)

    baseline = [extractor.extract([1.0, 1.0], T0, "s") for _ in range(5)]
    assert all(w.dim == extractor.dim for w in baseline)

    detector.fit(baseline)
    assert detector.score(extractor.extract([1.0, 1.0], T0, "s")) == pytest.approx(0.0)
    assert detector.score(extractor.extract([4.0, 4.0], T0, "s")) == pytest.approx(3.0)


def test_incomplete_class_is_not_a_detector() -> None:
    class OnlyFit:
        def fit(self, windows) -> None: ...

    assert not isinstance(OnlyFit(), Detector)
