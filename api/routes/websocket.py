from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Any
import json
import asyncio
from datetime import datetime

from ..models import (
    WebSocketMessage, SubscriptionRequest, CommandRequest,
    BotStatus, PerformanceMetrics, DeviceInfo
)
from ..websocket_manager import WebSocketManager
from ..services.bot_service import BotService
from ..services.device_service import DeviceService
from ..services.monitoring_service import MonitoringService
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])

# Global instances
ws_manager = WebSocketManager()
bot_service: BotService = None
device_service: DeviceService = None
monitoring_service: MonitoringService = None

def get_services():
    """Get or initialize service instances."""
    global bot_service, device_service, monitoring_service
    
    if bot_service is None:
        bot_service = BotService()
    if device_service is None:
        device_service = DeviceService()
    if monitoring_service is None:
        monitoring_service = MonitoringService()
    
    return bot_service, device_service, monitoring_service

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication."""
    await ws_manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await ws_manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="connection",
                data={"status": "connected", "timestamp": datetime.now().isoformat()}
            )
        )
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                await handle_websocket_message(websocket, message_data)
            except json.JSONDecodeError:
                await ws_manager.send_personal_message(
                    websocket,
                    WebSocketMessage(
                        type="error",
                        data={"message": "Invalid JSON format"}
                    )
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await ws_manager.send_personal_message(
                    websocket,
                    WebSocketMessage(
                        type="error",
                        data={"message": str(e)}
                    )
                )
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, message_data: Dict[str, Any]):
    """Handle incoming WebSocket messages."""
    message_type = message_data.get("type")
    data = message_data.get("data", {})
    
    if message_type == "subscribe":
        await handle_subscription(websocket, data)
    elif message_type == "unsubscribe":
        await handle_unsubscription(websocket, data)
    elif message_type == "command":
        await handle_command(websocket, data)
    elif message_type == "ping":
        await handle_ping(websocket)
    else:
        await ws_manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="error",
                data={"message": f"Unknown message type: {message_type}"}
            )
        )

async def handle_subscription(websocket: WebSocket, data: Dict[str, Any]):
    """Handle subscription requests."""
    try:
        subscription = SubscriptionRequest(**data)
        
        # Subscribe to the stream
        ws_manager.subscribe(websocket, subscription.stream)
        
        # Send confirmation
        await ws_manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="subscription_confirmed",
                data={
                    "stream": subscription.stream,
                    "timestamp": datetime.now().isoformat()
                }
            )
        )
        
        # Send initial data for the subscribed stream
        await send_initial_stream_data(websocket, subscription.stream)
        
        logger.info(f"Client subscribed to stream: {subscription.stream}")
    
    except Exception as e:
        await ws_manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="subscription_error",
                data={"message": str(e)}
            )
        )

async def handle_unsubscription(websocket: WebSocket, data: Dict[str, Any]):
    """Handle unsubscription requests."""
    try:
        stream = data.get("stream")
        if not stream:
            raise ValueError("Stream name is required for unsubscription")
        
        # Unsubscribe from the stream
        ws_manager.unsubscribe(websocket, stream)
        
        # Send confirmation
        await ws_manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="unsubscription_confirmed",
                data={
                    "stream": stream,
                    "timestamp": datetime.now().isoformat()
                }
            )
        )
        
        logger.info(f"Client unsubscribed from stream: {stream}")
    
    except Exception as e:
        await ws_manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="unsubscription_error",
                data={"message": str(e)}
            )
        )

async def handle_command(websocket: WebSocket, data: Dict[str, Any]):
    """Handle command requests."""
    try:
        command = CommandRequest(**data)
        bot_svc, device_svc, monitoring_svc = get_services()
        
        result = None
        
        # Execute command based on type
        if command.command == "bot_start":
            result = await bot_svc.start()
        elif command.command == "bot_stop":
            result = await bot_svc.stop()
        elif command.command == "bot_pause":
            result = await bot_svc.pause()
        elif command.command == "bot_resume":
            result = await bot_svc.resume()
        elif command.command == "bot_emergency_stop":
            result = await bot_svc.emergency_stop()
        elif command.command == "refresh_devices":
            result = await device_svc.refresh_devices()
        elif command.command == "take_screenshot":
            device_id = command.params.get("device_id")
            if device_id:
                result = await device_svc.take_screenshot(device_id)
            else:
                raise ValueError("device_id is required for screenshot command")
        else:
            raise ValueError(f"Unknown command: {command.command}")
        
        # Send command result
        await ws_manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="command_result",
                data={
                    "command": command.command,
                    "result": result.dict() if hasattr(result, 'dict') else result,
                    "timestamp": datetime.now().isoformat()
                }
            )
        )
        
        logger.info(f"Executed command: {command.command}")
    
    except Exception as e:
        await ws_manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="command_error",
                data={
                    "command": data.get("command", "unknown"),
                    "message": str(e)
                }
            )
        )

async def handle_ping(websocket: WebSocket):
    """Handle ping requests."""
    await ws_manager.send_personal_message(
        websocket,
        WebSocketMessage(
            type="pong",
            data={"timestamp": datetime.now().isoformat()}
        )
    )

async def send_initial_stream_data(websocket: WebSocket, stream: str):
    """Send initial data for a newly subscribed stream."""
    try:
        bot_svc, device_svc, monitoring_svc = get_services()
        
        if stream == "bot_status":
            status = await bot_svc.get_status()
            await ws_manager.send_personal_message(
                websocket,
                WebSocketMessage(
                    type="bot_status",
                    data=status.dict()
                )
            )
        
        elif stream == "bot_stats":
            stats = await bot_svc.get_stats()
            await ws_manager.send_personal_message(
                websocket,
                WebSocketMessage(
                    type="bot_stats",
                    data=stats.dict()
                )
            )
        
        elif stream == "devices":
            devices = await device_svc.get_devices()
            await ws_manager.send_personal_message(
                websocket,
                WebSocketMessage(
                    type="devices",
                    data=[device.dict() for device in devices]
                )
            )
        
        elif stream == "system_metrics":
            metrics = await monitoring_svc.get_performance_metrics()
            await ws_manager.send_personal_message(
                websocket,
                WebSocketMessage(
                    type="system_metrics",
                    data=metrics.dict()
                )
            )
        
        elif stream == "system_info":
            info = await monitoring_svc.get_system_info()
            await ws_manager.send_personal_message(
                websocket,
                WebSocketMessage(
                    type="system_info",
                    data=info.dict()
                )
            )
    
    except Exception as e:
        logger.error(f"Failed to send initial data for stream {stream}: {e}")

# Background task to broadcast periodic updates
async def broadcast_periodic_updates():
    """Background task to broadcast periodic updates to subscribed clients."""
    while True:
        try:
            bot_svc, device_svc, monitoring_svc = get_services()
            
            # Broadcast bot status updates
            if ws_manager.has_subscribers("bot_status"):
                status = await bot_svc.get_status()
                await ws_manager.broadcast_to_stream(
                    "bot_status",
                    WebSocketMessage(
                        type="bot_status",
                        data=status.dict()
                    )
                )
            
            # Broadcast bot stats updates
            if ws_manager.has_subscribers("bot_stats"):
                stats = await bot_svc.get_stats()
                await ws_manager.broadcast_to_stream(
                    "bot_stats",
                    WebSocketMessage(
                        type="bot_stats",
                        data=stats.dict()
                    )
                )
            
            # Broadcast device updates
            if ws_manager.has_subscribers("devices"):
                devices = await device_svc.get_devices()
                await ws_manager.broadcast_to_stream(
                    "devices",
                    WebSocketMessage(
                        type="devices",
                        data=[device.dict() for device in devices]
                    )
                )
            
            # Broadcast system metrics updates
            if ws_manager.has_subscribers("system_metrics"):
                metrics = await monitoring_svc.get_performance_metrics()
                await ws_manager.broadcast_to_stream(
                    "system_metrics",
                    WebSocketMessage(
                        type="system_metrics",
                        data=metrics.dict()
                    )
                )
            
            # Wait before next update cycle
            await asyncio.sleep(5)  # Update every 5 seconds
        
        except Exception as e:
            logger.error(f"Error in periodic update broadcast: {e}")
            await asyncio.sleep(10)  # Wait longer on error

# Function to get WebSocket manager instance (for use in other modules)
def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    return ws_manager

# Function to start background tasks
async def start_websocket_background_tasks():
    """Start WebSocket background tasks."""
    # Start the periodic update task
    asyncio.create_task(broadcast_periodic_updates())
    logger.info("WebSocket background tasks started")