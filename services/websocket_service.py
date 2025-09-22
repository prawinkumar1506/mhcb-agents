from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from services.conversation_flow import ConversationFlowService

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversation_service = ConversationFlowService()
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))
    
    async def handle_message(self, user_id: str, message: str):
        try:
            # Process message through conversation flow
            response = await self.conversation_service.process_message(
                user_id=user_id,
                message=message
            )
            
            # Send response back
            await self.send_message(user_id, {
                "type": "message",
                "response": response["response"],
                "agent": response.get("agent_type"),
                "crisis_detected": response.get("crisis_detected", False),
                "escalation_triggered": response.get("escalation_triggered", False)
            })
            
        except Exception as e:
            await self.send_message(user_id, {
                "type": "error",
                "message": "Sorry, I encountered an error processing your message."
            })

websocket_manager = WebSocketManager()
