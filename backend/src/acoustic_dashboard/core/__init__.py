"""Shared contract between pipeline stages.

Everything after feature extraction (detectors, storage, alerting, the API) handles
:class:`FeatureWindow` and nothing else. Adding a new input modality means writing a
:class:`FeatureExtractor`; nothing downstream changes.
"""

from acoustic_dashboard.core.contract import Detector, FeatureExtractor, FeatureWindow

__all__ = ["Detector", "FeatureExtractor", "FeatureWindow"]
