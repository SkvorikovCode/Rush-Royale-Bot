# -*- coding: utf-8 -*-
"""
Rush Royale Bot - API Data Models
Created: 2025-01-14
Author: SkvorikovCode
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from enum import Enum

from .bot_models import BotConfig, LogLevel


class APIStatus(str, Enum):
    """Статусы API ответов"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BotCommandType(str, Enum):
    """Типы команд для бота"""
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    RESTART = "restart"
    QUICK_START = "quick_start"
    QUIT_GAME = "quit_game"
    GET_STATUS = "get_status"
    GET_STATS = "get_stats"
    GET_LOGS = "get_logs"
    CLEAR_LOGS = "clear_logs"
    UPDATE_CONFIG = "update_config"


class DeviceCommandType(str, Enum):
    """Типы команд для устройства"""
    CONNECT = "connect_device"
    DISCONNECT = "disconnect_device"
    GET_SCREENSHOT = "get_screenshot"
    TAP_SCREEN = "tap_screen"
    SWIPE_SCREEN = "swipe_screen"
    SCAN_DEVICES = "scan_devices"
    GET_DEVICE_INFO = "get_device_info"


class VisionCommandType(str, Enum):
    """Типы команд для компьютерного зрения"""
    ANALYZE_SCREENSHOT = "analyze_screenshot"
    GET_GAME_STATE = "get_game_state"
    ANALYZE_GRID = "analyze_grid"
    ANALYZE_MANA = "analyze_mana"
    DETECT_UNITS = "detect_units"
    FIND_MERGEABLE = "find_mergeable"


class WebSocketMessageType(str, Enum):
    """Типы WebSocket сообщений"""
    # Статус бота
    BOT_STATUS_UPDATE = "bot_status_update"
    BOT_STATS_UPDATE = "bot_stats_update"
    BOT_CONFIG_UPDATE = "bot_config_update"
    
    # События бота
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    BOT_PAUSED = "bot_paused"
    BOT_RESUMED = "bot_resumed"
    BOT_ERROR = "bot_error"
    
    # Игровые события
    GAME_STATE_CHANGED = "game_state_changed"
    UNIT_PLACED = "unit_placed"
    UNIT_MERGED = "unit_merged"
    SPELL_USED = "spell_used"
    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"
    
    # События устройства
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"
    SCREENSHOT_TAKEN = "screenshot_taken"
    
    # События компьютерного зрения
    VISION_ANALYSIS = "vision_analysis"
    GRID_DETECTED = "grid_detected"
    UNITS_DETECTED = "units_detected"
    MANA_DETECTED = "mana_detected"
    
    # Логи
    LOG_ADDED = "log_added"
    LOGS_CLEARED = "logs_cleared"
    ERROR_OCCURRED = "error_occurred"
    
    # Команды и ответы
    COMMAND_RESULT = "command_result"
    COMMAND_ERROR = "command_error"
    INITIAL_DATA = "initial_data"


class APIResponse(BaseModel):
    """Базовая модель ответа API"""
    status: APIStatus
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BotCommand(BaseModel):
    """Модель команды для бота"""
    action: BotCommandType
    parameters: Optional[Dict[str, Any]] = None
    
    # Специфичные параметры для разных команд
    device_id: Optional[str] = None  # для start, connect_device
    config: Optional[BotConfig] = None  # для update_config
    limit: Optional[int] = None  # для get_logs
    level: Optional[LogLevel] = None  # для get_logs


class DeviceCommand(BaseModel):
    """Модель команды для устройства"""
    action: DeviceCommandType
    device_id: Optional[str] = None
    
    # Параметры для tap_screen
    x: Optional[int] = None
    y: Optional[int] = None
    
    # Параметры для swipe_screen
    start_x: Optional[int] = None
    start_y: Optional[int] = None
    end_x: Optional[int] = None
    end_y: Optional[int] = None
    duration: Optional[int] = None
    
    # Параметры для get_screenshot
    quality: Optional[int] = None
    format: Optional[str] = "png"


class VisionCommand(BaseModel):
    """Модель команды для компьютерного зрения"""
    action: VisionCommandType
    screenshot: Optional[str] = None  # base64 encoded
    parameters: Optional[Dict[str, Any]] = None
    
    # Параметры анализа
    confidence_threshold: Optional[float] = None
    detect_grid: Optional[bool] = None
    detect_units: Optional[bool] = None
    detect_mana: Optional[bool] = None


class WebSocketMessage(BaseModel):
    """Модель WebSocket сообщения"""
    type: WebSocketMessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[Any] = None
    
    # Метаданные
    source: Optional[str] = None  # bot, device, vision, api
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TapScreenRequest(BaseModel):
    """Модель запроса для тапа по экрану"""
    x: int = Field(..., ge=0, description="X координата")
    y: int = Field(..., ge=0, description="Y координата")
    device_id: Optional[str] = None


class SwipeScreenRequest(BaseModel):
    """Модель запроса для свайпа по экрану"""
    start_x: int = Field(..., ge=0, description="Начальная X координата")
    start_y: int = Field(..., ge=0, description="Начальная Y координата")
    end_x: int = Field(..., ge=0, description="Конечная X координата")
    end_y: int = Field(..., ge=0, description="Конечная Y координата")
    duration: int = Field(default=500, ge=100, le=5000, description="Длительность в мс")
    device_id: Optional[str] = None


class ScreenshotRequest(BaseModel):
    """Модель запроса для получения скриншота"""
    device_id: Optional[str] = None
    quality: int = Field(default=8, ge=1, le=10, description="Качество скриншота")
    format: str = Field(default="png", description="Формат изображения")


class ConfigRequest(BaseModel):
    """Модель запроса для обновления конфигурации"""
    config: BotConfig
    restart_bot: bool = Field(default=False, description="Перезапустить бота после обновления")


class LogsRequest(BaseModel):
    """Модель запроса для получения логов"""
    limit: int = Field(default=100, ge=1, le=1000, description="Количество записей")
    level: Optional[LogLevel] = Field(default=None, description="Фильтр по уровню")
    source: Optional[str] = Field(default=None, description="Фильтр по источнику")
    since: Optional[datetime] = Field(default=None, description="Логи с определенного времени")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeviceConnectionRequest(BaseModel):
    """Модель запроса для подключения устройства"""
    device_id: str = Field(..., description="ID устройства")
    force_reconnect: bool = Field(default=False, description="Принудительное переподключение")
    scrcpy_quality: int = Field(default=8, ge=1, le=10, description="Качество scrcpy")
    scrcpy_bitrate: str = Field(default="8M", description="Битрейт scrcpy")


class VisionAnalysisRequest(BaseModel):
    """Модель запроса для анализа изображения"""
    image_data: str = Field(description="Base64 encoded image data")
    analysis_type: str = Field(default="full", description="Тип анализа: full, quick, specific")
    target_elements: Optional[List[str]] = Field(default=None, description="Конкретные элементы для поиска")


class BotConfigUpdate(BaseModel):
    """Модель для частичного обновления конфигурации бота"""
    auto_start: Optional[bool] = None
    auto_upgrade: Optional[bool] = None
    auto_merge: Optional[bool] = None
    auto_speed_up: Optional[bool] = None
    auto_collect_rewards: Optional[bool] = None
    auto_open_chests: Optional[bool] = None
    max_games_per_session: Optional[int] = None
    delay_between_actions: Optional[float] = None
    screenshot_interval: Optional[float] = None
    vision_confidence_threshold: Optional[float] = None