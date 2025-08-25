# -*- coding: utf-8 -*-
"""
Logger Service для Rush Royale Bot
Обеспечивает централизованное логирование с поддержкой уровней и категорий

Автор: SkvorikovCode
Дата: 2025
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
import json
from pathlib import Path

class LogLevel(str, Enum):
    """Уровни логирования"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class LogEntry:
    """Запись лога"""
    timestamp: str
    level: LogLevel
    message: str
    category: str = "general"
    source: str = "bot"
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return asdict(self)

@dataclass
class LogStats:
    """Статистика логирования"""
    total_logs: int = 0
    debug_count: int = 0
    info_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    critical_count: int = 0
    categories: Dict[str, int] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return asdict(self)

@dataclass
class LogConfig:
    """Конфигурация логирования"""
    max_logs: int = 1000
    log_to_file: bool = True
    log_file_path: str = "logs/bot.log"
    console_level: LogLevel = LogLevel.INFO
    file_level: LogLevel = LogLevel.DEBUG
    enabled_categories: List[str] = None
    
    def __post_init__(self):
        if self.enabled_categories is None:
            self.enabled_categories = ["general", "bot", "vision", "device", "error"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return asdict(self)

class LoggerService:
    """Сервис логирования"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.stats = LogStats()
        self.config = LogConfig()
        self.logger = logging.getLogger("rush_royale_bot")
        self._setup_logging()
        
    def _setup_logging(self):
        """Настройка системы логирования"""
        # Очистка существующих обработчиков
        self.logger.handlers.clear()
        
        # Установка уровня логгера
        self.logger.setLevel(logging.DEBUG)
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.console_level.upper()))
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Файловый обработчик
        if self.config.log_to_file:
            log_path = Path(self.config.log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(getattr(logging, self.config.file_level.upper()))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    async def log(self, level: LogLevel, message: str, category: str = "general", 
                  source: str = "bot", details: Optional[Dict[str, Any]] = None):
        """Добавление записи в лог"""
        # Проверка категории
        if category not in self.config.enabled_categories:
            return
        
        # Создание записи
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            category=category,
            source=source,
            details=details
        )
        
        # Добавление в память
        self.logs.append(entry)
        
        # Ограничение количества логов
        if len(self.logs) > self.config.max_logs:
            self.logs = self.logs[-self.config.max_logs:]
        
        # Обновление статистики
        self._update_stats(entry)
        
        # Логирование через стандартный logger
        log_level = getattr(logging, level.upper())
        log_message = f"[{category}] {message}"
        if details:
            log_message += f" | Details: {json.dumps(details, ensure_ascii=False)}"
        
        self.logger.log(log_level, log_message)
    
    def _update_stats(self, entry: LogEntry):
        """Обновление статистики"""
        self.stats.total_logs += 1
        
        # Счетчики по уровням
        if entry.level == LogLevel.DEBUG:
            self.stats.debug_count += 1
        elif entry.level == LogLevel.INFO:
            self.stats.info_count += 1
        elif entry.level == LogLevel.WARNING:
            self.stats.warning_count += 1
        elif entry.level == LogLevel.ERROR:
            self.stats.error_count += 1
        elif entry.level == LogLevel.CRITICAL:
            self.stats.critical_count += 1
        
        # Счетчики по категориям
        if entry.category in self.stats.categories:
            self.stats.categories[entry.category] += 1
        else:
            self.stats.categories[entry.category] = 1
    
    async def get_logs(self, level: Optional[LogLevel] = None, 
                      category: Optional[str] = None, 
                      limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Получение логов с фильтрацией"""
        filtered_logs = self.logs
        
        # Фильтрация по уровню
        if level:
            level_priority = {
                LogLevel.DEBUG: 0,
                LogLevel.INFO: 1,
                LogLevel.WARNING: 2,
                LogLevel.ERROR: 3,
                LogLevel.CRITICAL: 4
            }
            min_priority = level_priority[level]
            filtered_logs = [
                log for log in filtered_logs 
                if level_priority[log.level] >= min_priority
            ]
        
        # Фильтрация по категории
        if category:
            filtered_logs = [
                log for log in filtered_logs 
                if log.category == category
            ]
        
        # Ограничение количества
        if limit:
            filtered_logs = filtered_logs[-limit:]
        
        return [log.to_dict() for log in filtered_logs]
    
    async def clear_logs(self):
        """Очистка логов"""
        self.logs.clear()
        self.stats = LogStats()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        return self.stats.to_dict()
    
    async def update_config(self, config_data: Dict[str, Any]):
        """Обновление конфигурации"""
        # Обновление конфигурации
        for key, value in config_data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Пересоздание системы логирования
        self._setup_logging()
    
    async def get_config(self) -> Dict[str, Any]:
        """Получение текущей конфигурации"""
        return self.config.to_dict()
    
    # Удобные методы для разных уровней
    async def debug(self, message: str, category: str = "general", **kwargs):
        """Логирование уровня DEBUG"""
        await self.log(LogLevel.DEBUG, message, category, **kwargs)
    
    async def info(self, message: str, category: str = "general", **kwargs):
        """Логирование уровня INFO"""
        await self.log(LogLevel.INFO, message, category, **kwargs)
    
    async def warning(self, message: str, category: str = "general", **kwargs):
        """Логирование уровня WARNING"""
        await self.log(LogLevel.WARNING, message, category, **kwargs)
    
    async def error(self, message: str, category: str = "general", **kwargs):
        """Логирование уровня ERROR"""
        await self.log(LogLevel.ERROR, message, category, **kwargs)
    
    async def critical(self, message: str, category: str = "general", **kwargs):
        """Логирование уровня CRITICAL"""
        await self.log(LogLevel.CRITICAL, message, category, **kwargs)

# Глобальный экземпляр сервиса
logger_service = LoggerService()