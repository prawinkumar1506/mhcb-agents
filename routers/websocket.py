from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_service import websocket_manager
import json

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                await websocket_manager.handle_message(
                    user_id, 
                    message_data.get("message", "")
                )
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)
