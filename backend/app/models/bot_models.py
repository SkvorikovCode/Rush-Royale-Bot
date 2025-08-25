# -*- coding: utf-8 -*-
"""
Rush Royale Bot - Bot Data Models
Created: 2025-01-14
Author: SkvorikovCode
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from enum import Enum


class BotState(str, Enum):
    """Состояния бота"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    CONNECTING = "connecting"


class GameStateType(str, Enum):
    """Типы состояний игры"""
    IN_GAME = "in_game"
    IN_MENU = "in_menu"
    LOADING = "loading"
    UNKNOWN = "unknown"


class LogLevel(str, Enum):
    """Уровни логирования"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BotStatus(BaseModel):
    """Модель статуса бота"""
    state: BotState = BotState.STOPPED
    is_running: bool = False
    is_paused: bool = False
    device_connected: bool = False
    device_id: Optional[str] = None
    current_game_state: GameStateType = GameStateType.UNKNOWN
    error_message: Optional[str] = None
    last_update: datetime = Field(default_factory=datetime.now)
    uptime_seconds: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BotConfig(BaseModel):
    """Модель конфигурации бота"""
    # Основные настройки
    auto_start: bool = False
    auto_restart_on_error: bool = True
    max_error_count: int = 5
    screenshot_interval: float = 1.0
    action_delay: float = 0.5
    
    # Настройки игры
    auto_merge_units: bool = True
    auto_place_units: bool = True
    auto_use_spells: bool = False
    preferred_units: List[str] = Field(default_factory=list)
    
    # Настройки устройства
    device_resolution: Optional[str] = None
    scrcpy_quality: int = 8
    scrcpy_bitrate: str = "8M"
    
    # Настройки компьютерного зрения
    vision_confidence_threshold: float = 0.8
    grid_detection_enabled: bool = True
    mana_detection_enabled: bool = True
    unit_recognition_enabled: bool = True
    
    # Настройки логирования
    log_level: LogLevel = LogLevel.INFO
    max_log_entries: int = 1000
    save_screenshots_on_error: bool = True


class BotStats(BaseModel):
    """Модель статистики бота"""
    total_runtime_seconds: int = 0
    games_played: int = 0
    units_placed: int = 0
    units_merged: int = 0
    spells_used: int = 0
    errors_count: int = 0
    screenshots_taken: int = 0
    last_game_duration: Optional[int] = None
    average_game_duration: Optional[float] = None
    success_rate: float = 0.0
    last_reset: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeviceInfo(BaseModel):
    """Модель информации об устройстве"""
    device_id: str
    name: Optional[str] = None
    model: Optional[str] = None
    android_version: Optional[str] = None
    resolution: Optional[str] = None
    is_connected: bool = False
    adb_port: Optional[int] = None
    scrcpy_port: Optional[int] = None
    last_seen: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LogEntry(BaseModel):
    """Модель записи лога"""
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    level: LogLevel
    message: str
    source: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GridCell(BaseModel):
    """Модель ячейки игровой сетки"""
    x: int
    y: int
    is_occupied: bool = False
    unit_type: Optional[str] = None
    unit_rank: Optional[int] = None
    confidence: float = 0.0
    can_merge: bool = False
    merge_target: Optional[tuple] = None


class UnitInfo(BaseModel):
    """Модель информации о юните"""
    type: str
    rank: int
    position: tuple  # (x, y)
    confidence: float
    can_merge: bool = False
    merge_candidates: List[tuple] = Field(default_factory=list)


class ManaInfo(BaseModel):
    """Модель информации о мане"""
    current: int = 0
    maximum: int = 100
    percentage: float = 0.0
    is_full: bool = False
    confidence: float = 0.0


class VisionAnalysis(BaseModel):
    """Модель результата анализа компьютерного зрения"""
    timestamp: datetime = Field(default_factory=datetime.now)
    game_state: GameStateType
    confidence: float
    
    # Анализ сетки
    grid_detected: bool = False
    grid_cells: List[GridCell] = Field(default_factory=list)
    free_cells: List[tuple] = Field(default_factory=list)
    occupied_cells: List[tuple] = Field(default_factory=list)
    
    # Анализ юнитов
    units_detected: List[UnitInfo] = Field(default_factory=list)
    mergeable_units: List[tuple] = Field(default_factory=list)
    
    # Анализ маны
    mana_info: Optional[ManaInfo] = None
    
    # Дополнительная информация
    screenshot_size: Optional[tuple] = None
    processing_time_ms: float = 0.0
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GameState(BaseModel):
    """Модель состояния игры"""
    type: GameStateType
    in_game: bool = False
    in_menu: bool = False
    is_loading: bool = False
    
    # Игровая информация
    current_wave: Optional[int] = None
    game_time: Optional[int] = None
    
    # Анализ экрана
    vision_analysis: Optional[VisionAnalysis] = None
    last_screenshot: Optional[str] = None  # base64 encoded
    
    # Метаданные
    last_update: datetime = Field(default_factory=datetime.now)
    confidence: float = 0.0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }