from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.websockets import router as ws_router
from app.services.connection_manager import manager
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database tables on startup (for development only)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Start the Redis Pub/Sub listener background task
    await manager.start_listener()
    yield
    # Clean up connections on shutdown
    await manager.stop_listener()

app = FastAPI(title="Structura Engine", version="0.1.0", lifespan=lifespan)

# Register the WebSocket routes
app.include_router(ws_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Structura Edge Engine active"}