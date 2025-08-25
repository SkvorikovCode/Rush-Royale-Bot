# -*- coding: utf-8 -*-
"""
Rush Royale Bot - Data Models
Created: 2025-01-14
Author: SkvorikovCode
"""

from .bot_models import (
    BotStatus,
    BotConfig,
    BotStats,
    GameState,
    DeviceInfo,
    LogEntry,
    VisionAnalysis,
    GridCell,
    UnitInfo,
    ManaInfo,
    BotState,
    GameStateType,
    LogLevel
)

from .api_models import (
    APIResponse,
    BotCommand,
    DeviceCommand,
    VisionCommand,
    WebSocketMessage,
    TapScreenRequest,
    SwipeScreenRequest,
    ScreenshotRequest,
    ConfigRequest,
    LogsRequest,
    DeviceConnectionRequest,
    VisionAnalysisRequest,
    BotConfigUpdate,
    APIStatus,
    BotCommandType,
    DeviceCommandType,
    VisionCommandType,
    WebSocketMessageType
)

__all__ = [
    # Core models
    "BotStatus",
    "BotConfig",
    "BotStats",
    "GameState",
    "DeviceInfo",
    "LogEntry",
    "VisionAnalysis",
    "GridCell",
    "UnitInfo",
    "ManaInfo",
    
    # Enums from bot_models
    "BotState",
    "GameStateType",
    "LogLevel",
    
    # API models
    "APIResponse",
    "BotCommand",
    "DeviceCommand",
    "VisionCommand",
    "WebSocketMessage",
    "TapScreenRequest",
    "SwipeScreenRequest",
    "ScreenshotRequest",
    "ConfigRequest",
    "LogsRequest",
    "DeviceConnectionRequest",
    "VisionAnalysisRequest",
    "BotConfigUpdate",
    
    # Enums from api_models
    "APIStatus",
    "BotCommandType",
    "DeviceCommandType",
    "VisionCommandType",
    "WebSocketMessageType"
]