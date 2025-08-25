from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from ..models import (
    BotConfig, BotStatus, BotStats, APIResponse,
    BotState
)
from ..services.bot_service import BotService
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/bot", tags=["bot"])

# Global bot service instance
bot_service: BotService = None

def get_bot_service() -> BotService:
    """Get the global bot service instance."""
    global bot_service
    if bot_service is None:
        bot_service = BotService()
    return bot_service

@router.get("/status", response_model=APIResponse[BotStatus])
async def get_bot_status():
    """Get current bot status."""
    try:
        service = get_bot_service()
        status = await service.get_status()
        return APIResponse(
            success=True,
            data=status,
            message="Bot status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get bot status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=APIResponse[BotStats])
async def get_bot_stats():
    """Get bot statistics."""
    try:
        service = get_bot_service()
        stats = await service.get_stats()
        return APIResponse(
            success=True,
            data=stats,
            message="Bot statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get bot stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config", response_model=APIResponse[BotConfig])
async def get_bot_config():
    """Get current bot configuration."""
    try:
        service = get_bot_service()
        config = await service.get_config()
        return APIResponse(
            success=True,
            data=config,
            message="Bot configuration retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get bot config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config", response_model=APIResponse[BotConfig])
async def update_bot_config(config: BotConfig):
    """Update bot configuration."""
    try:
        service = get_bot_service()
        updated_config = await service.update_config(config)
        return APIResponse(
            success=True,
            data=updated_config,
            message="Bot configuration updated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to update bot config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start", response_model=APIResponse[Dict[str, Any]])
async def start_bot(background_tasks: BackgroundTasks):
    """Start the bot."""
    try:
        service = get_bot_service()
        
        # Check if bot is already running
        status = await service.get_status()
        if status.state in [BotState.RUNNING, BotState.PAUSED]:
            return APIResponse(
                success=False,
                data={"state": status.state.value},
                message=f"Bot is already {status.state.value.lower()}"
            )
        
        # Start bot in background
        background_tasks.add_task(service.start)
        
        return APIResponse(
            success=True,
            data={"state": "starting"},
            message="Bot start initiated"
        )
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop", response_model=APIResponse[Dict[str, Any]])
async def stop_bot():
    """Stop the bot."""
    try:
        service = get_bot_service()
        
        # Check if bot is running
        status = await service.get_status()
        if status.state == BotState.STOPPED:
            return APIResponse(
                success=False,
                data={"state": status.state.value},
                message="Bot is already stopped"
            )
        
        await service.stop()
        
        return APIResponse(
            success=True,
            data={"state": "stopped"},
            message="Bot stopped successfully"
        )
    except Exception as e:
        logger.error(f"Failed to stop bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pause", response_model=APIResponse[Dict[str, Any]])
async def pause_bot():
    """Pause the bot."""
    try:
        service = get_bot_service()
        
        # Check if bot is running
        status = await service.get_status()
        if status.state != BotState.RUNNING:
            return APIResponse(
                success=False,
                data={"state": status.state.value},
                message=f"Cannot pause bot in {status.state.value} state"
            )
        
        await service.pause()
        
        return APIResponse(
            success=True,
            data={"state": "paused"},
            message="Bot paused successfully"
        )
    except Exception as e:
        logger.error(f"Failed to pause bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume", response_model=APIResponse[Dict[str, Any]])
async def resume_bot():
    """Resume the bot."""
    try:
        service = get_bot_service()
        
        # Check if bot is paused
        status = await service.get_status()
        if status.state != BotState.PAUSED:
            return APIResponse(
                success=False,
                data={"state": status.state.value},
                message=f"Cannot resume bot in {status.state.value} state"
            )
        
        await service.resume()
        
        return APIResponse(
            success=True,
            data={"state": "running"},
            message="Bot resumed successfully"
        )
    except Exception as e:
        logger.error(f"Failed to resume bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-stats", response_model=APIResponse[BotStats])
async def reset_bot_stats():
    """Reset bot statistics."""
    try:
        service = get_bot_service()
        stats = await service.reset_stats()
        return APIResponse(
            success=True,
            data=stats,
            message="Bot statistics reset successfully"
        )
    except Exception as e:
        logger.error(f"Failed to reset bot stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-stop", response_model=APIResponse[Dict[str, Any]])
async def emergency_stop_bot():
    """Emergency stop the bot (force stop)."""
    try:
        service = get_bot_service()
        await service.emergency_stop()
        
        return APIResponse(
            success=True,
            data={"state": "stopped"},
            message="Bot emergency stopped successfully"
        )
    except Exception as e:
        logger.error(f"Failed to emergency stop bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=APIResponse[list])
async def get_bot_logs(limit: int = 100):
    """Get recent bot logs."""
    try:
        service = get_bot_service()
        logs = await service.get_recent_logs(limit)
        return APIResponse(
            success=True,
            data=logs,
            message=f"Retrieved {len(logs)} log entries"
        )
    except Exception as e:
        logger.error(f"Failed to get bot logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=APIResponse[Dict[str, Any]])
async def get_bot_health():
    """Get bot health status."""
    try:
        service = get_bot_service()
        health = await service.get_health_status()
        return APIResponse(
            success=True,
            data=health,
            message="Bot health status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get bot health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-config", response_model=APIResponse[Dict[str, Any]])
async def validate_bot_config(config: BotConfig):
    """Validate bot configuration without applying it."""
    try:
        service = get_bot_service()
        validation_result = await service.validate_config(config)
        return APIResponse(
            success=validation_result["valid"],
            data=validation_result,
            message="Configuration validation completed"
        )
    except Exception as e:
        logger.error(f"Failed to validate bot config: {e}")
        raise HTTPException(status_code=500, detail=str(e))