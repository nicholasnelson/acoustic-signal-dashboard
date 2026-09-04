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
