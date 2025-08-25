from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
import tempfile
import os
from pathlib import Path

from ..models import (
    DeviceInfo, DeviceActionResult, ScreenshotResult,
    APIResponse, PaginatedResponse
)
from ..services.device_service import DeviceService
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/devices", tags=["devices"])

# Global device service instance
device_service: DeviceService = None

def get_device_service() -> DeviceService:
    """Get the global device service instance."""
    global device_service
    if device_service is None:
        device_service = DeviceService()
    return device_service

@router.get("/", response_model=APIResponse[List[DeviceInfo]])
async def get_devices():
    """Get list of all connected devices."""
    try:
        service = get_device_service()
        devices = await service.get_devices()
        return APIResponse(
            success=True,
            data=devices,
            message=f"Found {len(devices)} devices"
        )
    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}", response_model=APIResponse[DeviceInfo])
async def get_device(device_id: str):
    """Get specific device information."""
    try:
        service = get_device_service()
        device = await service.get_device(device_id)
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return APIResponse(
            success=True,
            data=device,
            message=f"Device {device_id} information retrieved"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh", response_model=APIResponse[List[DeviceInfo]])
async def refresh_devices():
    """Refresh the list of connected devices."""
    try:
        service = get_device_service()
        devices = await service.refresh_devices()
        return APIResponse(
            success=True,
            data=devices,
            message=f"Device list refreshed, found {len(devices)} devices"
        )
    except Exception as e:
        logger.error(f"Failed to refresh devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart-adb", response_model=APIResponse[dict])
async def restart_adb():
    """Restart ADB server."""
    try:
        service = get_device_service()
        success = await service.restart_adb()
        
        if success:
            return APIResponse(
                success=True,
                data={"restarted": True},
                message="ADB server restarted successfully"
            )
        else:
            return APIResponse(
                success=False,
                data={"restarted": False},
                message="Failed to restart ADB server"
            )
    except Exception as e:
        logger.error(f"Failed to restart ADB: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/connect", response_model=APIResponse[DeviceActionResult])
async def connect_device(device_id: str):
    """Connect to a device."""
    try:
        service = get_device_service()
        result = await service.connect_device(device_id)
        return APIResponse(
            success=result.success,
            data=result,
            message=result.message
        )
    except Exception as e:
        logger.error(f"Failed to connect to device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/disconnect", response_model=APIResponse[DeviceActionResult])
async def disconnect_device(device_id: str):
    """Disconnect from a device."""
    try:
        service = get_device_service()
        result = await service.disconnect_device(device_id)
        return APIResponse(
            success=result.success,
            data=result,
            message=result.message
        )
    except Exception as e:
        logger.error(f"Failed to disconnect from device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/screenshot", response_model=APIResponse[ScreenshotResult])
async def take_screenshot(device_id: str):
    """Take a screenshot of the device screen."""
    try:
        service = get_device_service()
        result = await service.take_screenshot(device_id)
        return APIResponse(
            success=result.success,
            data=result,
            message="Screenshot taken successfully" if result.success else result.error
        )
    except Exception as e:
        logger.error(f"Failed to take screenshot for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/tap", response_model=APIResponse[DeviceActionResult])
async def tap_device(device_id: str, x: int, y: int):
    """Tap at specific coordinates on the device screen."""
    try:
        service = get_device_service()
        result = await service.tap(device_id, x, y)
        return APIResponse(
            success=result.success,
            data=result,
            message=result.message
        )
    except Exception as e:
        logger.error(f"Failed to tap on device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/input-text", response_model=APIResponse[DeviceActionResult])
async def send_text_input(device_id: str, text: str):
    """Send text input to the device."""
    try:
        service = get_device_service()
        result = await service.send_text_input(device_id, text)
        return APIResponse(
            success=result.success,
            data=result,
            message=result.message
        )
    except Exception as e:
        logger.error(f"Failed to send text input to device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/install-apk", response_model=APIResponse[DeviceActionResult])
async def install_apk(device_id: str, apk_file: UploadFile = File(...)):
    """Install APK file on the device."""
    try:
        service = get_device_service()
        
        # Validate file type
        if not apk_file.filename.endswith('.apk'):
            raise HTTPException(status_code=400, detail="File must be an APK")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.apk') as temp_file:
            content = await apk_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Install APK
            result = await service.install_apk(device_id, temp_file_path)
            return APIResponse(
                success=result.success,
                data=result,
                message=result.message
            )
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to install APK on device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}/apps", response_model=APIResponse[List[dict]])
async def get_installed_apps(device_id: str):
    """Get list of installed apps on the device."""
    try:
        service = get_device_service()
        
        # Check if device exists and is connected
        device = await service.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get installed packages (simplified implementation)
        # In a real implementation, you would use ADB to get the package list
        apps = [
            {
                "package_name": "com.my.defense",
                "app_name": "Rush Royale",
                "version": device.rush_royale_version or "Unknown",
                "installed": device.rush_royale_installed
            }
        ]
        
        return APIResponse(
            success=True,
            data=apps,
            message=f"Found {len(apps)} installed apps"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get apps for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/launch-app", response_model=APIResponse[DeviceActionResult])
async def launch_app(device_id: str, package_name: str):
    """Launch an app on the device."""
    try:
        service = get_device_service()
        
        # Use ADB to launch the app
        result = await service._run_adb_command(
            ["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"],
            device_id
        )
        
        if result.returncode == 0:
            return APIResponse(
                success=True,
                data=DeviceActionResult(
                    success=True,
                    message=f"App {package_name} launched successfully"
                ),
                message=f"App {package_name} launched successfully"
            )
        else:
            return APIResponse(
                success=False,
                data=DeviceActionResult(
                    success=False,
                    message=f"Failed to launch app: {result.stderr}"
                ),
                message=f"Failed to launch app: {result.stderr}"
            )
    
    except Exception as e:
        logger.error(f"Failed to launch app on device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/key-event", response_model=APIResponse[DeviceActionResult])
async def send_key_event(device_id: str, key_code: int):
    """Send a key event to the device."""
    try:
        service = get_device_service()
        
        # Use ADB to send key event
        result = await service._run_adb_command(
            ["shell", "input", "keyevent", str(key_code)],
            device_id
        )
        
        if result.returncode == 0:
            return APIResponse(
                success=True,
                data=DeviceActionResult(
                    success=True,
                    message=f"Key event {key_code} sent successfully"
                ),
                message=f"Key event {key_code} sent successfully"
            )
        else:
            return APIResponse(
                success=False,
                data=DeviceActionResult(
                    success=False,
                    message=f"Failed to send key event: {result.stderr}"
                ),
                message=f"Failed to send key event: {result.stderr}"
            )
    
    except Exception as e:
        logger.error(f"Failed to send key event to device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}/battery", response_model=APIResponse[dict])
async def get_battery_info(device_id: str):
    """Get battery information for the device."""
    try:
        service = get_device_service()
        
        # Get device info which includes battery data
        device = await service.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        battery_info = {
            "level": device.battery_level,
            "is_charging": device.is_charging,
            "last_updated": device.last_seen.isoformat() if device.last_seen else None
        }
        
        return APIResponse(
            success=True,
            data=battery_info,
            message="Battery information retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get battery info for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}/memory", response_model=APIResponse[dict])
async def get_memory_info(device_id: str):
    """Get memory information for the device."""
    try:
        service = get_device_service()
        
        # Get device info which includes memory data
        device = await service.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        memory_info = {
            "total_memory": device.total_memory,
            "available_memory": device.available_memory,
            "memory_usage_percent": (
                round((1 - (device.available_memory / device.total_memory)) * 100, 1)
                if device.total_memory and device.available_memory
                else None
            ),
            "last_updated": device.last_seen.isoformat() if device.last_seen else None
        }
        
        return APIResponse(
            success=True,
            data=memory_info,
            message="Memory information retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get memory info for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))