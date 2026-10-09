"""Stage 1: Capture

Provides prerecorded WAV replay and live microphone capture behind the same AudioChunk
contract so downstream stages do not need to know where the audio originated.

"""

from .microphone_source import LiveMicrophoneSource, list_input_devices
from .models import AudioChunk
from .wav_source import WavPlaybackSource, read_wav

__all__ = [
    "AudioChunk",
    "LiveMicrophoneSource",
    "WavPlaybackSource",
    "list_input_devices",
    "read_wav",
]