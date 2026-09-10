from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.connection_manager import manager
import json

router = APIRouter()

@router.websocket("/ws/{doc_id}")
async def document_sync(websocket: WebSocket, doc_id: str):
    await manager.connect(websocket, doc_id)
    try:
        while True:
            # Receive the Yjs CRDT delta payload from the client
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # Immediately fan-out to Redis so all other nodes get the update
            await manager.publish_update(doc_id, payload)
            
            # Note: In Phase 3, we will also drop this payload into a queue 
            # (like SQS/RabbitMQ) here for the background worker to save to PostgreSQL/S3.
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, doc_id)