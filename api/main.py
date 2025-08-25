from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import uvicorn
from datetime import datetime

from .routes import bot, devices, system, websocket
from .models import HealthCheck, APIResponse
from .utils.config import get_settings
from .utils.logger import setup_logger, get_logger
from .services.bot_service import BotService
from .services.device_service import DeviceService
from .services.monitoring_service import MonitoringService
from .routes.websocket import start_websocket_background_tasks

# Initialize settings and logger
settings = get_settings()
setup_logger()
logger = get_logger(__name__)

# Global service instances
bot_service: BotService = None
device_service: DeviceService = None
monitoring_service: MonitoringService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Rush Royale Bot API server...")
    
    try:
        # Initialize services
        global bot_service, device_service, monitoring_service
        
        logger.info("Initializing services...")
        bot_service = BotService()
        device_service = DeviceService()
        monitoring_service = MonitoringService()
        
        # Start background tasks
        logger.info("Starting background tasks...")
        await start_websocket_background_tasks()
        
        # Start device monitoring
        await device_service.start_monitoring()
        
        # Start system monitoring
        await monitoring_service.start_background_collection()
        
        logger.info(f"API server started successfully on {settings.host}:{settings.port}")
        
        yield
    
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Rush Royale Bot API server...")
        
        try:
            # Stop services
            if bot_service:
                await bot_service.stop()
            
            if device_service:
                await device_service.stop_monitoring()
            
            if monitoring_service:
                await monitoring_service.stop_background_collection()
            
            logger.info("API server shutdown complete")
        
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title="Rush Royale Bot API",
    description="FastAPI backend for Rush Royale Bot macOS application",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )

# Health check endpoint
@app.get("/health", response_model=APIResponse[HealthCheck])
async def health_check():
    """Health check endpoint."""
    try:
        # Check service health
        services_status = {
            "bot_service": "healthy" if bot_service else "not_initialized",
            "device_service": "healthy" if device_service else "not_initialized",
            "monitoring_service": "healthy" if monitoring_service else "not_initialized"
        }
        
        # Get basic system info
        if monitoring_service:
            try:
                system_info = await monitoring_service.get_system_info()
                performance = await monitoring_service.get_performance_metrics()
                
                health_data = HealthCheck(
                    status="healthy",
                    timestamp=datetime.now(),
                    version="1.0.0",
                    uptime_seconds=int((datetime.now() - performance.timestamp).total_seconds()) if performance.timestamp else 0,
                    services=services_status,
                    system_info={
                        "platform": system_info.platform,
                        "cpu_count": system_info.cpu_count,
                        "memory_total": system_info.memory_total,
                        "cpu_usage": performance.cpu_percent,
                        "memory_usage": performance.memory.percent
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to get detailed health info: {e}")
                health_data = HealthCheck(
                    status="degraded",
                    timestamp=datetime.now(),
                    version="1.0.0",
                    uptime_seconds=0,
                    services=services_status
                )
        else:
            health_data = HealthCheck(
                status="starting",
                timestamp=datetime.now(),
                version="1.0.0",
                uptime_seconds=0,
                services=services_status
            )
        
        return APIResponse(
            success=True,
            data=health_data,
            message="Service is healthy"
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return APIResponse(
            success=False,
            data=HealthCheck(
                status="unhealthy",
                timestamp=datetime.now(),
                version="1.0.0",
                uptime_seconds=0,
                services={"error": str(e)}
            ),
            message="Health check failed"
        )

# Root endpoint
@app.get("/", response_model=APIResponse[dict])
async def root():
    """Root endpoint with API information."""
    return APIResponse(
        success=True,
        data={
            "name": "Rush Royale Bot API",
            "version": "1.0.0",
            "description": "FastAPI backend for Rush Royale Bot macOS application",
            "docs_url": "/docs" if settings.debug else None,
            "health_url": "/health",
            "websocket_url": "/ws"
        },
        message="Welcome to Rush Royale Bot API"
    )

# Include routers
app.include_router(bot.router)
app.include_router(devices.router)
app.include_router(system.router)
app.include_router(websocket.router)

# Function to get service instances (for use in other modules)
def get_bot_service() -> BotService:
    """Get the global bot service instance."""
    return bot_service

def get_device_service() -> DeviceService:
    """Get the global device service instance."""
    return device_service

def get_monitoring_service() -> MonitoringService:
    """Get the global monitoring service instance."""
    return monitoring_service

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=settings.debug
    )