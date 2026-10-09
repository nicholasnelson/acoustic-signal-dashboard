from datetime import datetime, timezone

import numpy as np
import pytest

from acoustic_dashboard.analysis import AudioPreprocessor, BinnedFFT
from acoustic_dashboard.capture import AudioChunk


def _chunk(
    samples,
    *,
    source_id: str = "mic_1",
    sample_rate: int = 100,
    chunk_index: int = 0,
    timestamp: str = "2026-10-09T12:00:00+09:30",
) -> AudioChunk:
    samples = np.asarray(samples, dtype=np.float32)
    return AudioChunk(
        source_id=source_id,
        machine_type="fan",
        machine_id="fan_01",
        machine_profile="test",
        chunk_index=chunk_index,
        stream_start_time=chunk_index * len(samples) / sample_rate,
        duration=len(samples) / sample_rate,
        timestamp=timestamp,
        sample_rate=sample_rate,
        samples=samples,
    )


def test_preprocessor_buffers_chunks_and_emits_overlapping_windows():
    preprocessor = AudioPreprocessor(
        target_sample_rate=100,
        window_duration=0.04,
        hop_duration=0.02,
    )

    assert preprocessor.push(_chunk([0, 1], chunk_index=0)) == []
    first = preprocessor.push(_chunk([2, 3], chunk_index=1))
    second = preprocessor.push(_chunk([4, 5], chunk_index=2))

    assert len(first) == 1
    assert len(second) == 1
    np.testing.assert_array_equal(first[0].samples, [0, 1, 2, 3])
    np.testing.assert_array_equal(second[0].samples, [2, 3, 4, 5])
    assert first[0].window_index == 0
    assert second[0].window_index == 1
    assert (second[0].timestamp - first[0].timestamp).total_seconds() == pytest.approx(0.02)


def test_preprocessor_resamples_to_target_rate():
    preprocessor = AudioPreprocessor(
        target_sample_rate=50,
        window_duration=1.0,
        hop_duration=1.0,
    )
    t = np.arange(100, dtype=np.float32) / 100
    samples = np.sin(2 * np.pi * 5 * t).astype(np.float32)

    windows = preprocessor.push(_chunk(samples, sample_rate=100))

    assert len(windows) == 1
    assert windows[0].sample_rate == 50
    assert len(windows[0].samples) == 50
    assert windows[0].samples.dtype == np.float32
    assert not windows[0].samples.flags.writeable


def test_preprocessor_keeps_source_buffers_separate():
    preprocessor = AudioPreprocessor(
        target_sample_rate=100,
        window_duration=0.04,
        hop_duration=0.04,
    )

    assert preprocessor.push(_chunk([1, 2], source_id="a")) == []
    assert preprocessor.push(_chunk([9, 8], source_id="b")) == []

    a_windows = preprocessor.push(_chunk([3, 4], source_id="a", chunk_index=1))
    b_windows = preprocessor.push(_chunk([7, 6], source_id="b", chunk_index=1))

    np.testing.assert_array_equal(a_windows[0].samples, [1, 2, 3, 4])
    np.testing.assert_array_equal(b_windows[0].samples, [9, 8, 7, 6])


def test_preprocessor_rejects_sample_rate_change_for_same_source():
    preprocessor = AudioPreprocessor(target_sample_rate=100, window_duration=0.04, hop_duration=0.04)
    preprocessor.push(_chunk([1, 2], sample_rate=100))

    with pytest.raises(ValueError, match="changed sample rate"):
        preprocessor.push(_chunk([1, 2], sample_rate=200, chunk_index=1))


def test_preprocessed_live_style_audio_can_feed_binned_fft():
    input_rate = 48_000
    duration = 1.0
    t = np.arange(int(input_rate * duration), dtype=np.float32) / input_rate
    samples = (0.25 * np.sin(2 * np.pi * 1_000 * t)).astype(np.float32)

    preprocessor = AudioPreprocessor(
        target_sample_rate=16_000,
        window_duration=1.0,
        hop_duration=1.0,
    )
    windows = preprocessor.push(
        _chunk(
            samples,
            sample_rate=input_rate,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    )

    extractor = BinnedFFT(
        sample_rate=16_000,
        n_bins=6,
        edges=[0, 250, 500, 1_000, 2_000, 4_000, 8_000],
    )
    features = extractor.extract(
        windows[0].samples,
        timestamp=windows[0].timestamp,
        source_id=windows[0].source_id,
    )

    assert len(windows) == 1
    assert features.dim == 6
    assert np.all(np.isfinite(features.vector))
