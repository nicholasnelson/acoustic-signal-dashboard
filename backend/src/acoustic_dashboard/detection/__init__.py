"""Stage 3: Detection

Score each window against what normal sounds like for this env and raises
an explainable alert when it departs.
"""

from acoustic_dashboard.detection.mahalanobis import MahalanobisDetector

__all__ = ["MahalanobisDetector"]
