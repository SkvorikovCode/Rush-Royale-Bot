import asyncio
import psutil
import platform
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import deque
import json
import re

from ..models import (
    SystemInfo, PerformanceMetrics, DisplayInfo, PowerInfo,
    LogEntry, LogLevel, LogFilter, NetworkMetrics
)
from ..utils.logger import get_logger, LogCapture
from ..utils.config import get_settings

logger = get_logger(__name__)

class MonitoringService:
    """Service for monitoring system metrics, logs, and performance."""
    
    def __init__(self):
        self.settings = get_settings()
        self.log_capture = LogCapture(max_entries=self.settings.max_log_entries)
        self.metrics_history: deque = deque(maxlen=self.settings.metrics_history_size)
        self.network_history: deque = deque(maxlen=100)
        self._monitoring_task: Optional[asyncio.Task] = None
        self._stop_monitoring = asyncio.Event()
        
        # Cache for expensive operations
        self._system_info_cache: Optional[SystemInfo] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
    
    async def initialize(self):
        """Initialize the monitoring service."""
        logger.info("Initializing monitoring service...")
        
        # Get initial system info
        await self.get_system_info()
        
        # Start background monitoring
        self._monitoring_task = asyncio.create_task(self._monitor_metrics())
        
        logger.info("Monitoring service initialized")
    
    async def cleanup(self):
        """Cleanup monitoring service."""
        logger.info("Cleaning up monitoring service...")
        
        # Stop monitoring
        self._stop_monitoring.set()
        if self._monitoring_task:
            await self._monitoring_task
        
        logger.info("Monitoring service cleanup complete")
    
    async def get_system_info(self, force_refresh: bool = False) -> SystemInfo:
        """Get comprehensive system information."""
        now = datetime.now()
        
        # Use cache if available and not expired
        if (not force_refresh and 
            self._system_info_cache and 
            self._cache_timestamp and 
            now - self._cache_timestamp < self._cache_ttl):
            return self._system_info_cache
        
        try:
            # Basic system info
            uname = platform.uname()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            # CPU info
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            
            # Memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk info
            disk_usage = psutil.disk_usage('/')
            
            # macOS specific info
            macos_version = await self._get_macos_version()
            hardware_info = await self._get_hardware_info()
            
            system_info = SystemInfo(
                hostname=uname.node,
                platform=uname.system,
                platform_version=uname.release,
                architecture=uname.machine,
                processor=uname.processor or hardware_info.get('processor', 'Unknown'),
                cpu_count=cpu_count,
                cpu_count_logical=cpu_count_logical,
                cpu_frequency_mhz=int(cpu_freq.current) if cpu_freq else 0,
                total_memory_gb=round(memory.total / (1024**3), 2),
                total_disk_gb=round(disk_usage.total / (1024**3), 2),
                boot_time=boot_time,
                uptime_seconds=int((now - boot_time).total_seconds()),
                macos_version=macos_version,
                is_apple_silicon=hardware_info.get('is_apple_silicon', False),
                model_identifier=hardware_info.get('model_identifier'),
                chip_name=hardware_info.get('chip_name'),
                memory_type=hardware_info.get('memory_type'),
                gpu_info=hardware_info.get('gpu_info', [])
            )
            
            # Cache the result
            self._system_info_cache = system_info
            self._cache_timestamp = now
            
            return system_info
            
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            # Return minimal info on error
            return SystemInfo(
                hostname="Unknown",
                platform=platform.system(),
                platform_version=platform.release(),
                architecture=platform.machine(),
                processor="Unknown",
                cpu_count=1,
                cpu_count_logical=1,
                cpu_frequency_mhz=0,
                total_memory_gb=0,
                total_disk_gb=0,
                boot_time=datetime.now(),
                uptime_seconds=0
            )
    
    async def _get_macos_version(self) -> Optional[str]:
        """Get macOS version information."""
        try:
            result = await asyncio.create_subprocess_exec(
                "sw_vers", "-productVersion",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            if result.returncode == 0:
                return stdout.decode().strip()
        except Exception:
            pass
        return None
    
    async def _get_hardware_info(self) -> Dict[str, Any]:
        """Get detailed hardware information for macOS."""
        info = {}
        
        try:
            # Get system profiler info
            result = await asyncio.create_subprocess_exec(
                "system_profiler", "SPHardwareDataType", "-json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                data = json.loads(stdout.decode())
                hardware_data = data.get("SPHardwareDataType", [{}])[0]
                
                info['model_identifier'] = hardware_data.get('machine_model')
                info['processor'] = hardware_data.get('cpu_type')
                info['chip_name'] = hardware_data.get('chip_type')
                info['memory_type'] = hardware_data.get('memory_type')
                
                # Check if Apple Silicon
                chip_type = hardware_data.get('chip_type', '')
                info['is_apple_silicon'] = 'Apple' in chip_type
            
            # Get GPU info
            result = await asyncio.create_subprocess_exec(
                "system_profiler", "SPDisplaysDataType", "-json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                data = json.loads(stdout.decode())
                displays_data = data.get("SPDisplaysDataType", [])
                gpu_info = []
                
                for display in displays_data:
                    gpu_info.append({
                        'name': display.get('sppci_model', 'Unknown GPU'),
                        'vendor': display.get('sppci_vendor', 'Unknown'),
                        'vram': display.get('spdisplays_vram', 'Unknown')
                    })
                
                info['gpu_info'] = gpu_info
        
        except Exception as e:
            logger.warning(f"Failed to get hardware info: {e}")
        
        return info
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Temperature (macOS specific)
            temperature = await self._get_cpu_temperature()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage_percent=cpu_percent,
                cpu_usage_per_core=cpu_per_core,
                cpu_frequency_mhz=int(cpu_freq.current) if cpu_freq else 0,
                load_average_1m=load_avg[0],
                load_average_5m=load_avg[1],
                load_average_15m=load_avg[2],
                memory_usage_percent=memory.percent,
                memory_used_gb=round(memory.used / (1024**3), 2),
                memory_available_gb=round(memory.available / (1024**3), 2),
                swap_usage_percent=swap.percent,
                swap_used_gb=round(swap.used / (1024**3), 2),
                disk_usage_percent=round((disk_usage.used / disk_usage.total) * 100, 1),
                disk_used_gb=round(disk_usage.used / (1024**3), 2),
                disk_free_gb=round(disk_usage.free / (1024**3), 2),
                disk_read_mb_per_sec=round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
                disk_write_mb_per_sec=round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0,
                network_sent_mb_per_sec=round(network_io.bytes_sent / (1024**2), 2),
                network_recv_mb_per_sec=round(network_io.bytes_recv / (1024**2), 2),
                process_count=process_count,
                cpu_temperature_celsius=temperature
            )
            
            # Add to history
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            # Return minimal metrics on error
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage_percent=0,
                cpu_usage_per_core=[],
                cpu_frequency_mhz=0,
                load_average_1m=0,
                load_average_5m=0,
                load_average_15m=0,
                memory_usage_percent=0,
                memory_used_gb=0,
                memory_available_gb=0,
                swap_usage_percent=0,
                swap_used_gb=0,
                disk_usage_percent=0,
                disk_used_gb=0,
                disk_free_gb=0,
                disk_read_mb_per_sec=0,
                disk_write_mb_per_sec=0,
                network_sent_mb_per_sec=0,
                network_recv_mb_per_sec=0,
                process_count=0
            )
    
    async def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature on macOS."""
        try:
            # Try using powermetrics (requires sudo, might not work)
            result = await asyncio.create_subprocess_exec(
                "sudo", "powermetrics", "--samplers", "smc", "-n", "1", "-i", "1",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(result.communicate(), timeout=5)
            
            if result.returncode == 0:
                # Parse temperature from output
                for line in stdout.decode().split('\n'):
                    if 'CPU die temperature' in line:
                        match = re.search(r'(\d+\.\d+)', line)
                        if match:
                            return float(match.group(1))
        except Exception:
            pass
        
        return None
    
    async def get_display_info(self) -> List[DisplayInfo]:
        """Get display information."""
        displays = []
        
        try:
            result = await asyncio.create_subprocess_exec(
                "system_profiler", "SPDisplaysDataType", "-json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                data = json.loads(stdout.decode())
                displays_data = data.get("SPDisplaysDataType", [])
                
                for i, display_data in enumerate(displays_data):
                    # Get display info from system profiler
                    displays_info = display_data.get('spdisplays_ndrvs', [])
                    
                    for j, display_info in enumerate(displays_info):
                        resolution = display_info.get('_spdisplays_resolution', 'Unknown')
                        
                        display = DisplayInfo(
                            id=f"display_{i}_{j}",
                            name=display_info.get('_name', f"Display {i+1}"),
                            resolution=resolution,
                            refresh_rate=display_info.get('_spdisplays_refresh_rate'),
                            color_depth=display_info.get('_spdisplays_depth'),
                            is_main=display_info.get('_spdisplays_main', False),
                            is_retina=self._is_retina_display(resolution),
                            brightness=await self._get_display_brightness(i)
                        )
                        displays.append(display)
        
        except Exception as e:
            logger.warning(f"Failed to get display info: {e}")
            # Return basic display info
            displays.append(DisplayInfo(
                id="display_0",
                name="Main Display",
                resolution="Unknown",
                is_main=True
            ))
        
        return displays
    
    def _is_retina_display(self, resolution: str) -> bool:
        """Determine if display is Retina based on resolution."""
        if not resolution or resolution == "Unknown":
            return False
        
        try:
            # Extract width from resolution string
            match = re.search(r'(\d+)\s*x\s*(\d+)', resolution)
            if match:
                width = int(match.group(1))
                # Consider displays with width >= 2560 as Retina
                return width >= 2560
        except Exception:
            pass
        
        return False
    
    async def _get_display_brightness(self, display_index: int) -> Optional[int]:
        """Get display brightness."""
        try:
            result = await asyncio.create_subprocess_exec(
                "brightness", "-l",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                if display_index < len(lines):
                    brightness_str = lines[display_index].split(':')[-1].strip()
                    return int(float(brightness_str) * 100)
        except Exception:
            pass
        
        return None
    
    async def get_power_info(self) -> PowerInfo:
        """Get power and battery information."""
        try:
            result = await asyncio.create_subprocess_exec(
                "pmset", "-g", "batt",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                output = stdout.decode()
                
                # Parse battery info
                battery_level = None
                is_charging = False
                time_remaining = None
                power_source = "Unknown"
                
                for line in output.split('\n'):
                    if 'InternalBattery' in line:
                        # Extract battery percentage
                        match = re.search(r'(\d+)%', line)
                        if match:
                            battery_level = int(match.group(1))
                        
                        # Check charging status
                        is_charging = 'charging' in line.lower()
                        
                        # Extract time remaining
                        time_match = re.search(r'(\d+:\d+)', line)
                        if time_match:
                            time_remaining = time_match.group(1)
                    
                    elif 'AC Power' in line or 'Battery Power' in line:
                        power_source = "AC Power" if "AC Power" in line else "Battery"
                
                return PowerInfo(
                    battery_level=battery_level,
                    is_charging=is_charging,
                    time_remaining=time_remaining,
                    power_source=power_source,
                    thermal_state=await self._get_thermal_state()
                )
        
        except Exception as e:
            logger.warning(f"Failed to get power info: {e}")
        
        # Return default power info
        return PowerInfo(
            power_source="Unknown",
            thermal_state="Normal"
        )
    
    async def _get_thermal_state(self) -> str:
        """Get thermal state of the system."""
        try:
            result = await asyncio.create_subprocess_exec(
                "pmset", "-g", "therm",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                output = stdout.decode().lower()
                if "cpu_speed_limit" in output:
                    return "Throttled"
                elif "thermal_pressure" in output:
                    return "Pressure"
                else:
                    return "Normal"
        except Exception:
            pass
        
        return "Normal"
    
    async def get_network_metrics(self) -> NetworkMetrics:
        """Get network metrics."""
        try:
            net_io = psutil.net_io_counters()
            connections = len(psutil.net_connections())
            
            # Get network interface info
            interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                if interface.startswith('lo'):  # Skip loopback
                    continue
                
                for addr in addrs:
                    if addr.family == 2:  # IPv4
                        interfaces.append({
                            'name': interface,
                            'ip': addr.address,
                            'netmask': addr.netmask
                        })
                        break
            
            metrics = NetworkMetrics(
                timestamp=datetime.now(),
                bytes_sent=net_io.bytes_sent,
                bytes_received=net_io.bytes_recv,
                packets_sent=net_io.packets_sent,
                packets_received=net_io.packets_recv,
                errors_in=net_io.errin,
                errors_out=net_io.errout,
                drops_in=net_io.dropin,
                drops_out=net_io.dropout,
                active_connections=connections,
                interfaces=interfaces
            )
            
            # Add to history
            self.network_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get network metrics: {e}")
            return NetworkMetrics(
                timestamp=datetime.now(),
                bytes_sent=0,
                bytes_received=0,
                packets_sent=0,
                packets_received=0,
                errors_in=0,
                errors_out=0,
                drops_in=0,
                drops_out=0,
                active_connections=0,
                interfaces=[]
            )
    
    def get_logs(self, filter_params: Optional[LogFilter] = None) -> List[LogEntry]:
        """Get filtered logs."""
        logs = self.log_capture.get_logs()
        
        if not filter_params:
            return logs
        
        filtered_logs = []
        for log in logs:
            # Filter by level
            if filter_params.level and log.level != filter_params.level:
                continue
            
            # Filter by source
            if filter_params.source and filter_params.source not in log.source:
                continue
            
            # Filter by message content
            if filter_params.message and filter_params.message.lower() not in log.message.lower():
                continue
            
            # Filter by time range
            if filter_params.start_time and log.timestamp < filter_params.start_time:
                continue
            
            if filter_params.end_time and log.timestamp > filter_params.end_time:
                continue
            
            filtered_logs.append(log)
        
        # Apply limit
        if filter_params.limit:
            filtered_logs = filtered_logs[-filter_params.limit:]
        
        return filtered_logs
    
    def get_metrics_history(self, hours: int = 1) -> List[PerformanceMetrics]:
        """Get performance metrics history."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metric for metric in self.metrics_history 
            if metric.timestamp >= cutoff_time
        ]
    
    def get_network_history(self, hours: int = 1) -> List[NetworkMetrics]:
        """Get network metrics history."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metric for metric in self.network_history 
            if metric.timestamp >= cutoff_time
        ]
    
    async def _monitor_metrics(self):
        """Background task to collect metrics periodically."""
        logger.info("Starting metrics monitoring...")
        
        while not self._stop_monitoring.is_set():
            try:
                # Collect performance metrics
                await self.get_performance_metrics()
                
                # Collect network metrics
                await self.get_network_metrics()
                
                # Wait for next collection
                await asyncio.sleep(self.settings.metrics_collection_interval)
                
            except Exception as e:
                logger.error(f"Metrics monitoring error: {e}")
                await asyncio.sleep(30)  # Wait longer on error
        
        logger.info("Metrics monitoring stopped")