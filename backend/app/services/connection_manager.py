import asyncio
import json
import redis.asyncio as aioredis
from fastapi import WebSocket
from typing import Dict, Set
from app.core.config import settings

class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance.active_connections: Dict[str, Set[WebSocket]] = {}
            cls._instance.redis = aioredis.from_url(settings.REDIS_URL)
            cls._instance.pubsub = cls._instance.redis.pubsub()
            cls._instance._listener_task = None
        return cls._instance

    async def connect(self, websocket: WebSocket, doc_id: str):
        await websocket.accept()
        if doc_id not in self.active_connections:
            self.active_connections[doc_id] = set()
            # Subscribe to the specific document channel in Redis when the first user joins
            await self.pubsub.subscribe(f"doc_{doc_id}")
        self.active_connections[doc_id].add(websocket)

    def disconnect(self, websocket: WebSocket, doc_id: str):
        self.active_connections[doc_id].discard(websocket)
        if not self.active_connections[doc_id]:
            del self.active_connections[doc_id]
            # Unsubscribe if no one on this server node is viewing the document
            asyncio.create_task(self.pubsub.unsubscribe(f"doc_{doc_id}"))

    async def publish_update(self, doc_id: str, message: dict):
        """Pushes a local WebSocket event into the Redis distributed bus."""
        await self.redis.publish(f"doc_{doc_id}", json.dumps(message))

    async def _redis_listener(self):
        """Listens for updates from other server nodes and routes them to local WebSockets."""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"].decode("utf-8")
                data = message["data"].decode("utf-8")
                doc_id = channel.replace("doc_", "")
                
                if doc_id in self.active_connections:
                    for connection in self.active_connections[doc_id]:
                        try:
                            await connection.send_text(data)
                        except Exception:
                            pass # Handle disconnected clients gracefully

    async def start_listener(self):
        if self._listener_task is None:
            self._listener_task = asyncio.create_task(self._redis_listener())

    async def stop_listener(self):
        if self._listener_task:
            self._listener_task.cancel()
            await self.redis.close()

manager = ConnectionManager()