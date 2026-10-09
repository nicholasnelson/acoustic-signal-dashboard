import asyncio
import wave

import numpy as np

from acoustic_dashboard.capture import AudioChunk, WavPlaybackSource, read_wav


def _write_test_wav(path, sample_rate: int = 100, seconds: float = 0.03) -> None:
    frame_count = int(sample_rate * seconds)
    samples = np.arange(frame_count, dtype=np.int16)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())


def test_read_wav_returns_float32_mono_samples(tmp_path):
    wav_path = tmp_path / "test.wav"
    _write_test_wav(wav_path)

    samples, sample_rate, channels = read_wav(wav_path)

    assert samples.dtype == np.float32
    assert sample_rate == 100
    assert channels == 1
    assert len(samples) == 3


def test_wav_playback_source_emits_sequential_chunks(tmp_path):
    wav_path = tmp_path / "test.wav"
    _write_test_wav(wav_path, sample_rate=100, seconds=0.03)

    source = WavPlaybackSource(
        wav_path,
        {
            "source_id": "mic_1",
            "machine_type": "fan",
            "machine_id": "fan_01",
            "machine_profile": "fan_type_a",
            "channel": 0,
        },
        chunk_duration=0.01,
    )

    emitted: list[AudioChunk] = []

    async def collect_chunks() -> None:
        await source.stream(emitted.append)

    asyncio.run(collect_chunks())

    assert source.total_chunks == 3
    assert [chunk.chunk_index for chunk in emitted] == [0, 1, 2]
    assert [len(chunk.samples) for chunk in emitted] == [1, 1, 1]
    assert all(chunk.sample_rate == 100 for chunk in emitted)

def test_live_microphone_source_emits_audio_chunks(monkeypatch):
    from acoustic_dashboard.capture import microphone_source

    class FakeInputStream:
        def __init__(self, **kwargs):
            self.callback = kwargs["callback"]
            assert kwargs["samplerate"] == 100
            assert kwargs["channels"] == 2
            assert kwargs["blocksize"] == 2
            assert kwargs["dtype"] == "float32"

        def __enter__(self):
            first = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
            second = np.array([[0.5, 0.6], [0.7, 0.8]], dtype=np.float32)
            self.callback(first, 2, None, None)
            self.callback(second, 2, None, None)
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    class FakeSoundDevice:
        InputStream = FakeInputStream

        @staticmethod
        def query_devices(device=None, kind=None):
            assert kind == "input"
            return {
                "name": "Fake two-channel input",
                "max_input_channels": 2,
                "default_samplerate": 100.0,
            }

    monkeypatch.setattr(
        microphone_source,
        "_load_sounddevice",
        lambda: FakeSoundDevice,
    )

    source = microphone_source.LiveMicrophoneSource(
        {
            "source_id": "live_1",
            "machine_type": "fan",
            "machine_id": "fan_live",
            "machine_profile": "live_test",
            "channel": 1,
        },
        chunk_duration=0.02,
    )

    emitted: list[AudioChunk] = []
    asyncio.run(source.stream(emitted.append, max_chunks=2))

    assert source.device_name == "Fake two-channel input"
    assert source.sample_rate == 100
    assert [chunk.chunk_index for chunk in emitted] == [0, 1]
    assert [chunk.stream_start_time for chunk in emitted] == [0.0, 0.02]
    assert all(chunk.sample_rate == 100 for chunk in emitted)
    assert all(chunk.samples.dtype == np.float32 for chunk in emitted)
    np.testing.assert_allclose(emitted[0].samples, [0.2, 0.4])
    np.testing.assert_allclose(emitted[1].samples, [0.6, 0.8])


def test_live_microphone_source_rejects_missing_channel(monkeypatch):
    from acoustic_dashboard.capture import microphone_source

    class FakeSoundDevice:
        @staticmethod
        def query_devices(device=None, kind=None):
            return {
                "name": "Mono input",
                "max_input_channels": 1,
                "default_samplerate": 48000.0,
            }

    monkeypatch.setattr(
        microphone_source,
        "_load_sounddevice",
        lambda: FakeSoundDevice,
    )

    import pytest

    with pytest.raises(ValueError, match="channel 1 was requested"):
        microphone_source.LiveMicrophoneSource(
            {
                "source_id": "live_1",
                "machine_type": "fan",
                "machine_id": "fan_live",
                "machine_profile": "live_test",
                "channel": 1,
            }
        )