"""Windower: turns streamed input of chunks into windows"""

from datetime import UTC, datetime, timedelta

import numpy as np

from acoustic_dashboard.analysis.windowing import Windower

T0 = datetime(2026, 9, 18, tzinfo=UTC)


def test_chunk_boundaries_do_not_matter() -> None:
    rate, window_len, hop = 100, 50, 20
    x = np.arange(1000, dtype=float)
    w = Windower(window_len, hop, rate, T0)

    out = []
    for chunk in np.array_split(x, [7, 60, 61, 300, 777]):  # uneven chunk sizes
        out += w.push(chunk)

    starts = range(0, len(x) - window_len + 1, hop)
    assert [t for t, _ in out] == [T0 + timedelta(seconds=s / rate) for s in starts]
    for (_, window), s in zip(out, starts, strict=True):
        assert np.array_equal(window, x[s : s + window_len])
