"""Live score stream."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["stream"])


@router.websocket("/stream")
async def stream(websocket: WebSocket) -> None:
    await websocket.accept()
    broadcast = websocket.app.state.broadcast
    queue = broadcast.subscribe()
    try:
        while True:
            await websocket.send_json(await queue.get())
    except WebSocketDisconnect:
        pass
    finally:
        broadcast.unsubscribe(queue)
