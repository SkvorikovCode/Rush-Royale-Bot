import asyncio
import subprocess
import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
import uuid

from ..models import DeviceInfo, DeviceStatus, ConnectionType, DeviceActionResult, ScreenshotResult
from ..utils.logger import get_logger, log_performance
from ..utils.config import get_settings

logger = get_logger(__name__)

class DeviceService:
    """Service for managing Android devices via ADB."""
    
    def __init__(self):
        self.settings = get_settings()
        self.adb_path = self._find_adb_path()
        self.devices: Dict[str, DeviceInfo] = {}
        self._device_monitor_task: Optional[asyncio.Task] = None
        self._stop_monitoring = asyncio.Event()
    
    async def initialize(self):
        """Initialize the device service."""
        logger.info("Initializing device service...")
        
        if not self.adb_path:
            logger.warning("ADB not found. Device functionality will be limited.")
            return
        
        # Start ADB server
        await self._start_adb_server()
        
        # Initial device scan
        await self.refresh_devices()
        
        # Start device monitoring
        self._device_monitor_task = asyncio.create_task(self._monitor_devices())
        
        logger.info("Device service initialized")
    
    async def cleanup(self):
        """Cleanup device service."""
        logger.info("Cleaning up device service...")
        
        # Stop monitoring
        self._stop_monitoring.set()
        if self._device_monitor_task:
            await self._device_monitor_task
        
        logger.info("Device service cleanup complete")
    
    def _find_adb_path(self) -> Optional[str]:
        """Find ADB executable path."""
        if self.settings.adb_path:
            return self.settings.adb_path
        
        # Common ADB locations on macOS
        common_paths = [
            "/usr/local/bin/adb",
            "/opt/homebrew/bin/adb",
            "~/Library/Android/sdk/platform-tools/adb",
            "~/Android/sdk/platform-tools/adb",
            "/Applications/Android Studio.app/Contents/plugins/android/lib/android.jar/../../../bin/adb"
        ]
        
        for path in common_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                return str(expanded_path)
        
        # Try to find in PATH
        try:
            result = subprocess.run(["which", "adb"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return None
    
    async def _run_adb_command(self, args: List[str], device_id: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run an ADB command."""
        if not self.adb_path:
            raise RuntimeError("ADB not available")
        
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(args)
        
        logger.debug(f"Running ADB command: {' '.join(cmd)}")
        
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                result.communicate(),
                timeout=self.settings.adb_timeout
            )
            
            return subprocess.CompletedProcess(
                cmd, result.returncode, stdout.decode(), stderr.decode()
            )
        except asyncio.TimeoutError:
            logger.error(f"ADB command timed out: {' '.join(cmd)}")
            raise RuntimeError("ADB command timed out")
        except Exception as e:
            logger.error(f"ADB command failed: {e}")
            raise
    
    async def _start_adb_server(self):
        """Start ADB server."""
        try:
            await self._run_adb_command(["start-server"])
            logger.info("ADB server started")
        except Exception as e:
            logger.error(f"Failed to start ADB server: {e}")
            raise
    
    async def restart_adb(self) -> bool:
        """Restart ADB server."""
        try:
            logger.info("Restarting ADB server...")
            await self._run_adb_command(["kill-server"])
            await asyncio.sleep(1)
            await self._run_adb_command(["start-server"])
            await self.refresh_devices()
            logger.info("ADB server restarted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to restart ADB server: {e}")
            return False
    
    @log_performance
    async def refresh_devices(self) -> List[DeviceInfo]:
        """Refresh the list of connected devices."""
        if not self.adb_path:
            return []
        
        try:
            result = await self._run_adb_command(["devices", "-l"])
            if result.returncode != 0:
                logger.error(f"Failed to list devices: {result.stderr}")
                return []
            
            devices = []
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                if not line.strip():
                    continue
                
                device_info = await self._parse_device_line(line)
                if device_info:
                    devices.append(device_info)
                    self.devices[device_info.id] = device_info
            
            # Remove devices that are no longer connected
            current_device_ids = {d.id for d in devices}
            for device_id in list(self.devices.keys()):
                if device_id not in current_device_ids:
                    del self.devices[device_id]
            
            logger.debug(f"Found {len(devices)} devices")
            return devices
            
        except Exception as e:
            logger.error(f"Failed to refresh devices: {e}")
            return []
    
    async def _parse_device_line(self, line: str) -> Optional[DeviceInfo]:
        """Parse a device line from adb devices output."""
        parts = line.split()
        if len(parts) < 2:
            return None
        
        device_id = parts[0]
        status_str = parts[1]
        
        # Map ADB status to our enum
        status_map = {
            "device": DeviceStatus.CONNECTED,
            "offline": DeviceStatus.DISCONNECTED,
            "unauthorized": DeviceStatus.UNAUTHORIZED,
            "no permissions": DeviceStatus.ERROR
        }
        status = status_map.get(status_str, DeviceStatus.ERROR)
        
        # Determine connection type
        connection_type = ConnectionType.USB
        if ":" in device_id and device_id.count(".") == 3:
            connection_type = ConnectionType.WIFI
        elif "emulator" in device_id:
            connection_type = ConnectionType.EMULATOR
        
        # Get detailed device info if connected
        device_info = DeviceInfo(
            id=device_id,
            name=device_id,  # Will be updated with actual name
            model="Unknown",
            android_version="Unknown",
            api_level=0,
            architecture="Unknown",
            status=status,
            connection_type=connection_type,
            last_seen=datetime.now()
        )
        
        if status == DeviceStatus.CONNECTED:
            await self._update_device_details(device_info)
        
        return device_info
    
    async def _update_device_details(self, device: DeviceInfo):
        """Update detailed device information."""
        try:
            # Get device properties
            props = await self._get_device_properties(device.id)
            
            device.name = props.get("ro.product.model", device.id)
            device.model = props.get("ro.product.model", "Unknown")
            device.android_version = props.get("ro.build.version.release", "Unknown")
            device.api_level = int(props.get("ro.build.version.sdk", "0"))
            device.architecture = props.get("ro.product.cpu.abi", "Unknown")
            
            # Get battery info
            battery_info = await self._get_battery_info(device.id)
            device.battery_level = battery_info.get("level")
            device.is_charging = battery_info.get("charging")
            
            # Get memory info
            memory_info = await self._get_memory_info(device.id)
            device.total_memory = memory_info.get("total")
            device.available_memory = memory_info.get("available")
            
            # Get screen info
            screen_info = await self._get_screen_info(device.id)
            device.screen_resolution = screen_info.get("resolution")
            device.screen_density = screen_info.get("density")
            
            # Check if Rush Royale is installed
            device.rush_royale_installed = await self._is_app_installed(
                device.id, self.settings.rush_royale_package or "com.my.defense"
            )
            
            if device.rush_royale_installed:
                device.rush_royale_version = await self._get_app_version(
                    device.id, self.settings.rush_royale_package or "com.my.defense"
                )
            
        except Exception as e:
            logger.warning(f"Failed to update device details for {device.id}: {e}")
    
    async def _get_device_properties(self, device_id: str) -> Dict[str, str]:
        """Get device properties."""
        try:
            result = await self._run_adb_command(["shell", "getprop"], device_id)
            if result.returncode != 0:
                return {}
            
            props = {}
            for line in result.stdout.split('\n'):
                match = re.match(r'\[([^\]]+)\]:\s*\[([^\]]*)\]', line)
                if match:
                    props[match.group(1)] = match.group(2)
            
            return props
        except Exception:
            return {}
    
    async def _get_battery_info(self, device_id: str) -> Dict[str, Any]:
        """Get battery information."""
        try:
            result = await self._run_adb_command(
                ["shell", "dumpsys", "battery"], device_id
            )
            if result.returncode != 0:
                return {}
            
            info = {}
            for line in result.stdout.split('\n'):
                if "level:" in line:
                    info["level"] = int(line.split(":")[1].strip())
                elif "AC powered:" in line or "USB powered:" in line:
                    info["charging"] = "true" in line.lower()
            
            return info
        except Exception:
            return {}
    
    async def _get_memory_info(self, device_id: str) -> Dict[str, int]:
        """Get memory information."""
        try:
            result = await self._run_adb_command(
                ["shell", "cat", "/proc/meminfo"], device_id
            )
            if result.returncode != 0:
                return {}
            
            info = {}
            for line in result.stdout.split('\n'):
                if "MemTotal:" in line:
                    info["total"] = int(line.split()[1]) * 1024  # Convert KB to bytes
                elif "MemAvailable:" in line:
                    info["available"] = int(line.split()[1]) * 1024
            
            return info
        except Exception:
            return {}
    
    async def _get_screen_info(self, device_id: str) -> Dict[str, Any]:
        """Get screen information."""
        try:
            result = await self._run_adb_command(
                ["shell", "wm", "size"], device_id
            )
            if result.returncode == 0:
                match = re.search(r'(\d+)x(\d+)', result.stdout)
                if match:
                    resolution = f"{match.group(1)}x{match.group(2)}"
                else:
                    resolution = "Unknown"
            else:
                resolution = "Unknown"
            
            # Get density
            result = await self._run_adb_command(
                ["shell", "wm", "density"], device_id
            )
            if result.returncode == 0:
                match = re.search(r'(\d+)', result.stdout)
                density = int(match.group(1)) if match else None
            else:
                density = None
            
            return {
                "resolution": resolution,
                "density": density
            }
        except Exception:
            return {"resolution": "Unknown", "density": None}
    
    async def _is_app_installed(self, device_id: str, package_name: str) -> bool:
        """Check if an app is installed."""
        try:
            result = await self._run_adb_command(
                ["shell", "pm", "list", "packages", package_name], device_id
            )
            return package_name in result.stdout
        except Exception:
            return False
    
    async def _get_app_version(self, device_id: str, package_name: str) -> Optional[str]:
        """Get app version."""
        try:
            result = await self._run_adb_command(
                ["shell", "dumpsys", "package", package_name], device_id
            )
            if result.returncode != 0:
                return None
            
            for line in result.stdout.split('\n'):
                if "versionName=" in line:
                    return line.split("versionName=")[1].strip()
            
            return None
        except Exception:
            return None
    
    async def get_devices(self) -> List[DeviceInfo]:
        """Get list of all devices."""
        return list(self.devices.values())
    
    async def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        """Get specific device by ID."""
        return self.devices.get(device_id)
    
    async def connect_device(self, device_id: str) -> DeviceActionResult:
        """Connect to a device."""
        try:
            if ":" in device_id:  # WiFi device
                result = await self._run_adb_command(["connect", device_id])
                if result.returncode != 0:
                    return DeviceActionResult(
                        success=False,
                        message=f"Failed to connect: {result.stderr}"
                    )
            
            # Refresh device info
            await self.refresh_devices()
            
            return DeviceActionResult(
                success=True,
                message=f"Connected to device {device_id}"
            )
        except Exception as e:
            return DeviceActionResult(
                success=False,
                message=f"Connection failed: {str(e)}"
            )
    
    async def disconnect_device(self, device_id: str) -> DeviceActionResult:
        """Disconnect from a device."""
        try:
            if ":" in device_id:  # WiFi device
                result = await self._run_adb_command(["disconnect", device_id])
                if result.returncode != 0:
                    return DeviceActionResult(
                        success=False,
                        message=f"Failed to disconnect: {result.stderr}"
                    )
            
            # Remove from devices list
            if device_id in self.devices:
                del self.devices[device_id]
            
            return DeviceActionResult(
                success=True,
                message=f"Disconnected from device {device_id}"
            )
        except Exception as e:
            return DeviceActionResult(
                success=False,
                message=f"Disconnection failed: {str(e)}"
            )
    
    async def take_screenshot(self, device_id: str) -> ScreenshotResult:
        """Take a screenshot of the device."""
        try:
            device = self.devices.get(device_id)
            if not device or device.status != DeviceStatus.CONNECTED:
                return ScreenshotResult(
                    success=False,
                    error="Device not connected"
                )
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{device_id}_{timestamp}_{uuid.uuid4().hex[:8]}.png"
            file_path = Path(self.settings.screenshots_dir) / filename
            
            # Take screenshot
            result = await self._run_adb_command(
                ["exec-out", "screencap", "-p"], device_id
            )
            
            if result.returncode != 0:
                return ScreenshotResult(
                    success=False,
                    error=f"Screenshot failed: {result.stderr}"
                )
            
            # Save screenshot
            with open(file_path, "wb") as f:
                f.write(result.stdout.encode('latin1'))
            
            file_size = file_path.stat().st_size
            
            return ScreenshotResult(
                success=True,
                filename=filename,
                file_path=str(file_path),
                file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Screenshot failed for device {device_id}: {e}")
            return ScreenshotResult(
                success=False,
                error=str(e)
            )
    
    async def install_apk(self, device_id: str, apk_path: str) -> DeviceActionResult:
        """Install APK on device."""
        try:
            if not Path(apk_path).exists():
                return DeviceActionResult(
                    success=False,
                    message="APK file not found"
                )
            
            result = await self._run_adb_command(
                ["install", "-r", apk_path], device_id
            )
            
            if result.returncode != 0:
                return DeviceActionResult(
                    success=False,
                    message=f"Installation failed: {result.stderr}"
                )
            
            return DeviceActionResult(
                success=True,
                message="APK installed successfully"
            )
            
        except Exception as e:
            return DeviceActionResult(
                success=False,
                message=f"Installation error: {str(e)}"
            )
    
    async def send_text_input(self, device_id: str, text: str) -> DeviceActionResult:
        """Send text input to device."""
        try:
            # Escape special characters
            escaped_text = text.replace(" ", "%s").replace("&", "\\&")
            
            result = await self._run_adb_command(
                ["shell", "input", "text", escaped_text], device_id
            )
            
            if result.returncode != 0:
                return DeviceActionResult(
                    success=False,
                    message=f"Text input failed: {result.stderr}"
                )
            
            return DeviceActionResult(
                success=True,
                message="Text sent successfully"
            )
            
        except Exception as e:
            return DeviceActionResult(
                success=False,
                message=f"Text input error: {str(e)}"
            )
    
    async def tap(self, device_id: str, x: int, y: int) -> DeviceActionResult:
        """Tap at coordinates on device."""
        try:
            result = await self._run_adb_command(
                ["shell", "input", "tap", str(x), str(y)], device_id
            )
            
            if result.returncode != 0:
                return DeviceActionResult(
                    success=False,
                    message=f"Tap failed: {result.stderr}"
                )
            
            return DeviceActionResult(
                success=True,
                message=f"Tapped at ({x}, {y})"
            )
            
        except Exception as e:
            return DeviceActionResult(
                success=False,
                message=f"Tap error: {str(e)}"
            )
    
    async def _monitor_devices(self):
        """Monitor device connections in background."""
        logger.info("Starting device monitoring...")
        
        while not self._stop_monitoring.is_set():
            try:
                await self.refresh_devices()
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Device monitoring error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
        
        logger.info("Device monitoring stopped")