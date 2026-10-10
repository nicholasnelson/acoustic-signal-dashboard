# Network audio minimal demo
# No gap detection; timestamps come from counting samples after the header's start time.

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from websockets.asyncio.client import connect


@dataclass
class StreamHeader:
    sample_rate: int
    start: datetime


# Wire dtype -> (numpy dtype, divisor to get float samples in [-1, 1))
DTYPES = {"int16": ("<i2", 32768.0), "float32": ("<f4", 1.0)}


async def receive(url: str) -> AsyncIterator[StreamHeader | np.ndarray]:
    async with connect(url) as ws:
        header = json.loads(await ws.recv())
        dtype, scale = DTYPES[header.get("dtype", "int16")]
        yield StreamHeader(header["sample_rate"], datetime.fromisoformat(header["start"]))
        async for frame in ws:
            yield np.frombuffer(frame, dtype=dtype).astype(np.float32) / scale
