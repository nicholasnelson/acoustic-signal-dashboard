"""Stage 2: Analysis

Turns one window of samples into the features the dashboard plots and the
detectors read: waveform, spectrogram, band energy, etc
"""

from acoustic_dashboard.analysis.spectral_stats import SpectralStats

__all__ = ["SpectralStats"]
