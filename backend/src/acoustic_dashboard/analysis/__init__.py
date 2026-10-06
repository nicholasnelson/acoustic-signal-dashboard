"""Stage 2: Analysis

Turns one window of samples into the features the dashboard plots and the
detectors read: waveform, spectrogram, band energy, etc
"""

from acoustic_dashboard.analysis.binned_fft import BinnedFFT

__all__ = ["BinnedFFT"]
