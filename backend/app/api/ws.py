from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.realtime import subscribe_events

router = APIRouter(tags=["realtime"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        async for event in subscribe_events():
            await websocket.send_json(event)
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close(code=1011, reason="Realtime event stream unavailable")
