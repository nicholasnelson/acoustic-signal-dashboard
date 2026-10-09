# Mahalanobis distance detector
# as in the EDA notebook

from collections.abc import Sequence

import numpy as np
from scipy.spatial.distance import mahalanobis

from acoustic_dashboard.core import FeatureWindow


class MahalanobisDetector:
    def __init__(self) -> None:
        self.source_id: str | None = None
        self.mean: np.ndarray | None = None
        self.inv_cov: np.ndarray | None = None

    def fit(self, windows: Sequence[FeatureWindow]) -> None:
        if len(windows) < 2:
            raise ValueError("need at least 2 baseline windows")
        sources = {w.source_id for w in windows}
        if len(sources) != 1:
            raise ValueError(f"baseline windows must share one source_id, got {sorted(sources)}")
        dims = {w.dim for w in windows}
        if len(dims) != 1:
            raise ValueError(f"baseline windows must share one dim, got {sorted(dims)}")

        x = np.stack([w.vector for w in windows]).astype(np.float64)
        self.source_id = sources.pop()
        self.mean = x.mean(axis=0)
        self.inv_cov = np.linalg.pinv(np.atleast_2d(np.cov(x, rowvar=False)))

    def score(self, window: FeatureWindow) -> float:
        if self.mean is None:
            raise RuntimeError("detector is not fitted")
        if window.source_id != self.source_id:
            raise ValueError(f"fitted on {self.source_id!r}, got window from {window.source_id!r}")
        if window.dim != self.mean.shape[0]:
            raise ValueError(f"fitted on dim {self.mean.shape[0]}, got dim {window.dim}")
        return float(mahalanobis(window.vector, self.mean, self.inv_cov))

    def threshold_from_baseline(
        self, windows: Sequence[FeatureWindow], percentile: float = 99.0
    ) -> float:
        """Score that ``percentile`` % of the given normal windows fall at or under."""
        if not 0 < percentile <= 100:
            raise ValueError("percentile must be in (0, 100]")
        if not windows:
            raise ValueError("need at least 1 window")
        return float(np.percentile([self.score(w) for w in windows], percentile))
