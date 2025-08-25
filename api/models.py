from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class BotState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"

class DeviceStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    UNAUTHORIZED = "unauthorized"
    ERROR = "error"

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ConnectionType(str, Enum):
    USB = "usb"
    WIFI = "wifi"
    EMULATOR = "emulator"

# Bot Models
class BotConfig(BaseModel):
    """Bot configuration settings."""
    auto_start: bool = False
    auto_reconnect: bool = True
    battle_timeout: int = Field(default=300, ge=30, le=600)
    card_upgrade_enabled: bool = True
    auto_merge_enabled: bool = True
    screenshot_interval: float = Field(default=1.0, ge=0.1, le=5.0)
    debug_mode: bool = False
    preferred_device: Optional[str] = None
    rush_royale_package: str = "com.my.defense"
    
    # Game strategy settings
    merge_strategy: str = Field(default="conservative", regex="^(aggressive|conservative|balanced)$")
    upgrade_priority: List[str] = Field(default_factory=lambda: ["damage", "support", "utility"])
    max_merge_level: int = Field(default=7, ge=1, le=15)
    
    # Performance settings
    cpu_limit: float = Field(default=80.0, ge=10.0, le=100.0)
    memory_limit: float = Field(default=512.0, ge=128.0, le=2048.0)
    
class BotStatus(BaseModel):
    """Current bot status."""
    state: BotState
    uptime: Optional[float] = None
    battles_played: int = 0
    battles_won: int = 0
    current_wave: Optional[int] = None
    current_coop: Optional[int] = None
    last_action: Optional[str] = None
    last_action_time: Optional[datetime] = None
    error_message: Optional[str] = None
    connected_device: Optional[str] = None
    config: BotConfig
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BotStats(BaseModel):
    """Bot performance statistics."""
    total_runtime: float
    total_battles: int
    win_rate: float
    average_wave: float
    cards_upgraded: int
    merges_performed: int
    screenshots_taken: int
    errors_encountered: int
    last_reset: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Device Models
class DeviceInfo(BaseModel):
    """Android device information."""
    id: str
    name: str
    model: str
    android_version: str
    api_level: int
    architecture: str
    status: DeviceStatus
    connection_type: ConnectionType
    battery_level: Optional[int] = None
    is_charging: Optional[bool] = None
    screen_resolution: Optional[str] = None
    screen_density: Optional[int] = None
    total_memory: Optional[int] = None
    available_memory: Optional[int] = None
    cpu_info: Optional[str] = None
    last_seen: Optional[datetime] = None
    rush_royale_installed: bool = False
    rush_royale_version: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DeviceAction(BaseModel):
    """Device action request."""
    action: str
    device_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class DeviceActionResult(BaseModel):
    """Device action result."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# System Models
class SystemInfo(BaseModel):
    """System information."""
    platform: str
    platform_version: str
    architecture: str
    hostname: str
    cpu_count: int
    cpu_model: str
    total_memory: int
    python_version: str
    uptime: float
    boot_time: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PerformanceMetrics(BaseModel):
    """System performance metrics."""
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu_usage: float
    memory_usage: float
    memory_available: int
    disk_usage: float
    disk_free: int
    network_sent: int
    network_received: int
    temperature: Optional[float] = None
    fan_speed: Optional[int] = None
    gpu_usage: Optional[float] = None
    gpu_memory: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DisplayInfo(BaseModel):
    """Display information."""
    id: int
    name: str
    resolution: str
    scale_factor: float
    color_space: str
    refresh_rate: float
    is_primary: bool

class PowerInfo(BaseModel):
    """Power/battery information."""
    battery_level: Optional[int] = None
    is_charging: Optional[bool] = None
    power_source: Optional[str] = None
    time_remaining: Optional[int] = None
    cycle_count: Optional[int] = None
    health: Optional[str] = None

class SystemPreferences(BaseModel):
    """System preferences and settings."""
    theme: str = "auto"  # light, dark, auto
    accent_color: str = "blue"
    reduce_motion: bool = False
    high_contrast: bool = False
    transparency: bool = True
    language: str = "en"
    timezone: str = "UTC"

# Monitoring Models
class LogEntry(BaseModel):
    """Log entry."""
    id: str
    timestamp: datetime
    level: LogLevel
    source: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LogFilter(BaseModel):
    """Log filtering options."""
    level: Optional[LogLevel] = None
    source: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    search_query: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NetworkMetrics(BaseModel):
    """Network monitoring metrics."""
    timestamp: datetime = Field(default_factory=datetime.now)
    interface: str
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    errors_in: int
    errors_out: int
    drops_in: int
    drops_out: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    type: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SubscriptionRequest(BaseModel):
    """WebSocket subscription request."""
    streams: List[str]

class CommandRequest(BaseModel):
    """Command request via WebSocket."""
    command: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

# API Response Models
class APIResponse(BaseModel):
    """Standard API response."""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginatedResponse(BaseModel):
    """Paginated API response."""
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    connections: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# File Upload Models
class FileUpload(BaseModel):
    """File upload information."""
    filename: str
    size: int
    content_type: str
    upload_time: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScreenshotResult(BaseModel):
    """Screenshot capture result."""
    success: bool
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }