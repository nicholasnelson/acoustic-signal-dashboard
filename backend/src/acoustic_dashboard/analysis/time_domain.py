# Time domain feature extractor

from collections.abc import Sequence
from datetime import datetime
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike
from scipy import stats

from acoustic_dashboard.core import FeatureWindow

Feature = Literal["rms", "peak", "crest_factor", "zero_crossing_rate", "kurtosis"]

FEATURES: tuple[Feature, ...] = ("rms", "peak", "crest_factor", "zero_crossing_rate", "kurtosis")

_EPS = 1e-12


class TimeDomainStats:
    """Loudness and shape of one window, straight from the samples.

    Includes:
    - rms - root mean square amplitude
    - peak - largest sample amplitude
    - crest_factor - peak over rms
    - zero_crossing_rate - proportion of adjacent sample pairs which change sign
    - kurtosis - excess kurtosis, how frequently we see extreme values, "spikiness"
    """

    def __init__(self, features: Sequence[Feature] = FEATURES) -> None:
        features = tuple(features)
        if not features:
            raise ValueError("features must not be empty")
        unknown = [f for f in features if f not in FEATURES]
        if unknown:
            raise ValueError(f"unknown features {unknown}; choose from {list(FEATURES)}")
        if len(set(features)) != len(features):
            raise ValueError("features must not repeat")
        self.features = features

    @property
    def dim(self) -> int:
        return len(self.features)

    def extract(self, samples: ArrayLike, timestamp: datetime, source_id: str) -> FeatureWindow:
        x = np.asarray(samples, dtype=np.float64)
        if x.ndim != 1:
            raise ValueError(f"samples must be 1-D, got shape {x.shape}")
        if x.size < 2:
            raise ValueError("samples must contain at least 2 values")

        rms = np.sqrt(np.mean(x**2))
        peak = np.max(np.abs(x))
        values = {
            "rms": rms,
            "peak": peak,
            "crest_factor": peak / (rms + _EPS),
            "zero_crossing_rate": np.mean(np.signbit(x[1:]) != np.signbit(x[:-1])),
            # scipy gives nan for a constant window, so call it 0
            "kurtosis": stats.kurtosis(x) if np.var(x) > _EPS else 0.0,
        }
        vector = np.array([values[f] for f in self.features])
        return FeatureWindow(timestamp=timestamp, source_id=source_id, vector=vector)
