# Splits a stream of sample chunks into overlapping fixed-length windows
# Minimal version: one source, mono

from datetime import datetime, timedelta

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


class Windower:
    def __init__(self, window_len: int, hop: int, sample_rate: int, start: datetime) -> None:
        self.window_len = window_len
        self.hop = hop
        self.sample_rate = sample_rate
        self.start = start
        self._buffer = np.empty(0)
        self._consumed = 0  # samples dropped from the front of the buffer so far

    def push(self, samples: np.ndarray) -> list[tuple[datetime, np.ndarray]]:
        """Add a chunk; if window(s) are completed by the chunk, return them"""
        self._buffer = np.concatenate([self._buffer, samples])
        if len(self._buffer) < self.window_len:
            return []
        windows = sliding_window_view(self._buffer, self.window_len)[:: self.hop]
        out = [
            (self.start + timedelta(seconds=(self._consumed + i * self.hop) / self.sample_rate), w)
            for i, w in enumerate(windows.copy())
        ]
        drop = len(windows) * self.hop
        self._buffer = self._buffer[drop:]
        self._consumed += drop
        return out
