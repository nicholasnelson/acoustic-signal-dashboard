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


async def receive(url: str) -> AsyncIterator[StreamHeader | np.ndarray]:
    async with connect(url) as ws:
        header = json.loads(await ws.recv())
        yield StreamHeader(header["sample_rate"], datetime.fromisoformat(header["start"]))
        async for frame in ws:
            yield np.frombuffer(frame, dtype="<i2").astype(np.float32) / 32768.0
