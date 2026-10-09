# In-memory fanout from runners to however many WebSocket clients are connected
# Minimal demo version

import asyncio


class Broadcast:
    def __init__(self, maxsize: int = 100) -> None:
        self.maxsize = maxsize
        self.queues: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=self.maxsize)
        self.queues.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self.queues.discard(q)

    def publish(self, event: dict) -> None:
        for q in self.queues:
            if q.full():
                q.get_nowait()
            q.put_nowait(event)
