from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from typing import Dict, Any, Optional, List
import base64
import numpy as np
import cv2
from ..websocket_manager import websocket_manager
from ..models import (
    APIResponse, BotStatus, BotConfig, BotStats, DeviceInfo, LogEntry,
    BotCommand, DeviceCommand, VisionCommand, TapScreenRequest, SwipeScreenRequest,
    ConfigRequest, LogsRequest, DeviceConnectionRequest, VisionAnalysisRequest,
    BotConfigUpdate, BotCommandType, DeviceCommandType, VisionCommandType, APIStatus
)

# Модели данных теперь импортируются из models/

# Bot router
bot_router = APIRouter()

@bot_router.get("/status")
async def get_bot_status():
    """Get current bot status"""
    from ..services.bot_service import bot_service
    return await bot_service.get_status()

@bot_router.post("/start")
async def start_bot(config: Optional[BotConfigUpdate] = None):
    """Start the bot"""
    from ..services.bot_service import bot_service
    
    custom_config = None
    if config:
        custom_config = {k: v for k, v in config.dict().items() if v is not None}
    
    result = await bot_service.start_bot(custom_config)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@bot_router.post("/stop")
async def stop_bot():
    """Stop the bot"""
    from ..services.bot_service import bot_service
    
    result = await bot_service.stop_bot()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@bot_router.post("/toggle-pause")
async def toggle_pause():
    """Toggle bot pause state"""
    from ..services.bot_service import bot_service
    
    result = await bot_service.toggle_pause()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@bot_router.post("/quick-start")
async def quick_start():
    """Quick start with default settings"""
    from ..services.bot_service import bot_service
    
    result = await bot_service.quick_start()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@bot_router.post("/quit-game")
async def quit_game():
    """Quit current game"""
    from ..services.bot_service import bot_service
    
    result = await bot_service.quit_game()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@bot_router.put("/config")
async def update_bot_config(config: ConfigRequest):
    """Обновление конфигурации бота"""
    from ..services.bot_service import bot_service
    
    # Обновляем только переданные поля
    config_dict = config.dict(exclude_unset=True)
    
    try:
        await bot_service.update_config(config_dict)
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Configuration updated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update config: {str(e)}")

@bot_router.get("/logs")
async def get_logs(limit: int = 50, level: Optional[str] = None):
    """Get bot logs with optional filtering by level"""
    from ..services.bot_service import bot_service
    from ..services.logger_service import logger_service
    
    # Get logs from logger service
    logs = logger_service.get_log_stats()
    
    # Filter by level if specified
    if level:
        try:
            log_level = LogLevel(level.upper())
            # This would need to be implemented in logger_service
            # For now, return all logs
            pass
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid log level: {level}")
    
    # Get recent logs from bot service for compatibility
    status = await bot_service.get_status()
    recent_logs = status["logs"][-limit:] if len(status["logs"]) > limit else status["logs"]
    
    return {
        "logs": recent_logs, 
        "total": len(status["logs"]),
        "stats": logs
    }

@bot_router.delete("/logs")
async def clear_logs():
    """Clear bot logs"""
    from ..services.bot_service import bot_service
    from ..services.logger_service import logger_service
    
    # Clear logs in both services
    bot_service.logs.clear()
    logger_service.clear_logs()
    
    bot_service.add_log("info", "Logs cleared")
    
    return {"message": "Logs cleared successfully"}

@bot_router.websocket("/ws")
async def bot_websocket(websocket: WebSocket):
    """WebSocket соединение для real-time обновлений бота"""
    await websocket_manager.handle_bot_websocket(websocket)

# Роутер для устройств
device_router = APIRouter(tags=["devices"])

# WebSocket для устройств
@device_router.websocket("/ws")
async def device_websocket(websocket: WebSocket):
    """WebSocket соединение для обновлений устройств"""
    await websocket_manager.handle_device_websocket(websocket)

@device_router.get("/scan")
async def scan_devices():
    """Сканирование подключенных устройств"""
    from ..services.device_service import device_service
    
    devices = await device_service.scan_devices()
    
    return {
        "devices": devices,
        "total": len(devices),
        "connected": len([d for d in devices if d["is_connected"]])
    }

@device_router.get("/")
async def get_devices():
    """Получение всех устройств"""
    from ..services.device_service import device_service
    
    devices = device_service.get_device_list()
    
    return {
        "devices": devices,
        "total": len(devices)
    }

@device_router.get("/{device_id}")
async def get_device(device_id: str):
    """Получение информации об устройстве"""
    from ..services.device_service import device_service
    
    device = await device_service.get_device(device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return device.to_dict()

@device_router.post("/{device_id}/refresh")
async def refresh_device(device_id: str):
    """Обновление информации об устройстве"""
    from ..services.device_service import device_service
    
    device_info = await device_service.refresh_device_info(device_id)
    
    if not device_info:
        raise HTTPException(status_code=404, detail="Device not found or not connected")
    
    return device_info

@device_router.get("/{device_id}/screenshot")
async def get_screenshot(device_id: str):
    """Получение скриншота устройства"""
    from ..services.device_service import device_service
    from fastapi.responses import Response
    
    device = await device_service.get_device(device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if not device.is_connected:
        raise HTTPException(status_code=400, detail="Device not connected")
    
    screenshot_data = await device.take_screenshot()
    
    if not screenshot_data:
        raise HTTPException(status_code=500, detail="Failed to take screenshot")
    
    return Response(content=screenshot_data, media_type="image/png")

# TapRequest заменен на TapScreenRequest из models

@device_router.post("/{device_id}/tap")
async def tap_device(device_id: str, tap_data: TapScreenRequest):
    """Тап по устройству"""
    from ..services.device_service import device_service
    
    device = await device_service.get_device(device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if not device.is_connected:
        raise HTTPException(status_code=400, detail="Device not connected")
    
    success = await device.tap(tap_data.x, tap_data.y)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to tap")
    
    return {"message": f"Tapped at ({tap_data.x}, {tap_data.y})"}

# SwipeRequest заменен на SwipeScreenRequest из models

@device_router.post("/{device_id}/swipe")
async def swipe_device(device_id: str, swipe_data: SwipeScreenRequest):
    """Свайп по устройству"""
    from ..services.device_service import device_service
    
    device = await device_service.get_device(device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if not device.is_connected:
        raise HTTPException(status_code=400, detail="Device not connected")
    
    success = await device.swipe(
        swipe_data.x1, swipe_data.y1, 
        swipe_data.x2, swipe_data.y2, 
        swipe_data.duration
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to swipe")
    
    return {
        "message": f"Swiped from ({swipe_data.x1}, {swipe_data.y1}) to ({swipe_data.x2}, {swipe_data.y2})"
    }

@device_router.get("/adb/status")
async def check_adb_status():
    """Проверка статуса ADB"""
    from ..services.device_service import device_service
    
    is_available = await device_service.check_adb_connection()
    
    return {
        "adb_available": is_available,
        "message": "ADB is available" if is_available else "ADB is not available"
    }

# Роутер для компьютерного зрения
vision_router = APIRouter(tags=["vision"])

@vision_router.get("/templates")
async def get_templates():
    """Получение списка загруженных шаблонов"""
    from ..services.vision_service import vision_service
    
    templates = vision_service.get_loaded_templates()
    
    return {
        "templates": templates,
        "total": len(templates)
    }

@vision_router.post("/analyze/grid")
async def analyze_grid(request: VisionAnalysisRequest):
    """Анализ состояния игровой сетки"""
    from ..services.vision_service import vision_service
    
    try:
        # Декодирование base64 изображения
        image_bytes = base64.b64decode(request.image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Анализ сетки
        grid_state = vision_service.analyze_grid_state(image)
        
        return {
            "grid_state": grid_state,
            "analyzed_at": vision_service.get_stats()["last_analysis_time"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@vision_router.post("/analyze/mana")
async def analyze_mana(request: VisionAnalysisRequest):
    """Определение значения маны"""
    from ..services.vision_service import vision_service
    
    try:
        # Декодирование base64 изображения
        image_bytes = base64.b64decode(request.image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Анализ маны
        mana_value = vision_service.detect_mana_value(image)
        
        return {
            "mana_value": mana_value,
            "detected_at": vision_service.get_stats()["last_analysis_time"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mana analysis failed: {str(e)}")

@vision_router.get("/stats")
async def get_vision_stats():
    """Получение статистики сервиса зрения"""
    from ..services.vision_service import vision_service
    
    stats = vision_service.get_stats()
    
    return stats

@vision_router.delete("/cache")
async def clear_vision_cache():
    """Очистка кэша шаблонов"""
    from ..services.vision_service import vision_service
    
    vision_service.clear_template_cache()
    
    return APIResponse(
        status=APIStatus.SUCCESS,
        message="Vision cache cleared successfully"
    )

# Роутер для логирования
logging_router = APIRouter(tags=["logging"])

# WebSocket для логов
@logging_router.websocket("/ws")
async def logs_websocket(websocket: WebSocket):
    """WebSocket соединение для real-time логов"""
    await websocket_manager.handle_logs_websocket(websocket)

@logging_router.get("/stats")
async def get_logging_stats():
    """Получение статистики логирования"""
    from ..services.logger_service import logger_service
    
    stats = logger_service.get_log_stats()
    
    return stats

@logging_router.post("/config")
async def update_logging_config(config: Dict[str, Any]):
    """Обновление конфигурации логирования"""
    from ..services.logger_service import logger_service
    
    try:
        logger_service.update_config(config)
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Logging configuration updated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update config: {str(e)}")

# LogRequest заменен на LogsRequest из models

@logging_router.post("/log")
async def add_log_entry(log_data: LogsRequest):
    """Добавление записи в лог"""
    from ..services.logger_service import logger_service, LogLevel
    
    try:
        log_level = LogLevel(log_data.level.upper())
        logger_service.log(log_level, log_data.message, category=log_data.category or "api")
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Log entry added successfully"
        )
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid log level: {log_data.level}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add log entry: {str(e)}")