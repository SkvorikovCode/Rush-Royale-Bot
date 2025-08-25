from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .services.device_service import device_service
from .services.bot_service import bot_service
from .api.routes import device_router, vision_router, logging_router, bot_router
from .websocket_manager import websocket_manager

app = FastAPI(title="Rush Royale Bot API", version="2.0.0")

# CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "app://localhost",       # Electron app
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services уже импортированы как глобальные экземпляры

# Регистрация роутеров
app.include_router(device_router, prefix="/api/devices", tags=["devices"])
app.include_router(vision_router, prefix="/api/vision", tags=["vision"])
app.include_router(logging_router, prefix="/api/logging", tags=["logging"])
app.include_router(bot_router, prefix="/api/bot", tags=["bot"])

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await device_service.scan_devices()
    await bot_service.initialize()
    print("🚀 Rush Royale Bot API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await bot_service.cleanup()
    print("🛑 Rush Royale Bot API stopped")

@app.get("/")
async def root():
    return {"message": "Rush Royale Bot API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    bot_status = await bot_service.get_status()
    return {
        "status": "healthy",
        "bot_status": bot_status["status"],
        "connected_devices": await device_service.get_connected_devices_count(),
        "websocket_connections": websocket_manager.get_connection_count()
    }

@app.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """WebSocket endpoint для логов"""
    await websocket_manager.handle_logs_websocket(websocket)

@app.websocket("/ws/vision")
async def websocket_vision_endpoint(websocket: WebSocket):
    """WebSocket endpoint для компьютерного зрения"""
    await websocket_manager.handle_vision_websocket(websocket)