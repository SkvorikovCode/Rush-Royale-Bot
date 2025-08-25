# -*- coding: utf-8 -*-
"""
Bot Service для Rush Royale Bot
Основной сервис для управления ботом и координации всех компонентов

Автор: SkvorikovCode
Дата: 2025
"""

import asyncio
import json
import os
import time
import subprocess
import shutil
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from subprocess import Popen, DEVNULL, PIPE

# Android ADB - Интеграция с оригинальным bot_core.py
try:
    from ppadb.client import Client as AdbClient
    from ppadb.device import Device as AdbDevice
    ADB_AVAILABLE = True
    
    # Попытка импорта scrcpy для улучшенных скриншотов
    try:
        import scrcpy
        SCRCPY_AVAILABLE = True
    except ImportError:
        SCRCPY_AVAILABLE = False
    
    # Константы для touch действий
    class TouchConstants:
        ACTION_DOWN = 0
        ACTION_UP = 1
        KEYCODE_BACK = 4
    
    const = TouchConstants()
except ImportError:
    # Fallback для отсутствующих зависимостей
    class AdbClient:
        def __init__(self, host='127.0.0.1', port=5037):
            self.host = host
            self.port = port
        def devices(self):
            return []
    
    class AdbDevice:
        def __init__(self):
            self.serial = None
        def shell(self, command):
            pass
        def input_tap(self, x, y):
            pass
        def input_swipe(self, x1, y1, x2, y2, duration=1000):
            pass
    
    class TouchConstants:
        ACTION_DOWN = 0
        ACTION_UP = 1
        KEYCODE_BACK = 4
    
    ADB_AVAILABLE = False
    SCRCPY_AVAILABLE = False
    const = TouchConstants()

# Обработка изображений
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Импорты сервисов
from .logger_service import logger_service, LogLevel
from .device_service import device_service
from .vision_service import vision_service

class BotStatus(str, Enum):
    """Статусы бота"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"

class GameMode(str, Enum):
    """Режимы игры"""
    PVP = "pvp"
    COOP = "coop"
    ARENA = "arena"
    TOURNAMENT = "tournament"
    PRACTICE = "practice"

@dataclass
class BotConfig:
    """Конфигурация бота"""
    # Основные настройки
    auto_start: bool = False
    game_mode: GameMode = GameMode.PVP
    max_games: int = 0  # 0 = бесконечно
    delay_between_actions: float = 1.0
    delay_between_games: float = 5.0
    
    # Настройки стратегии
    auto_merge: bool = True
    auto_upgrade: bool = True
    preferred_cards: List[str] = None
    avoid_cards: List[str] = None
    
    # Настройки безопасности
    max_errors: int = 5
    restart_on_error: bool = True
    screenshot_on_error: bool = True
    
    # Настройки устройства
    device_id: Optional[str] = None
    screen_resolution: tuple = (1080, 1920)
    
    def __post_init__(self):
        if self.preferred_cards is None:
            self.preferred_cards = []
        if self.avoid_cards is None:
            self.avoid_cards = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BotStats:
    """Статистика бота"""
    # Общая статистика
    total_games: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    
    # Статистика времени
    total_runtime: float = 0.0
    average_game_time: float = 0.0
    start_time: Optional[str] = None
    
    # Статистика действий
    total_actions: int = 0
    merges_performed: int = 0
    upgrades_performed: int = 0
    cards_played: int = 0
    
    # Статистика ошибок
    total_errors: int = 0
    connection_errors: int = 0
    vision_errors: int = 0
    game_errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GameState:
    """Состояние игры"""
    in_game: bool = False
    game_mode: Optional[GameMode] = None
    current_mana: int = 0
    max_mana: int = 10
    grid_state: Optional[Dict[str, Any]] = None
    enemy_health: int = 100
    player_health: int = 100
    wave_number: int = 0
    game_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class Bot:
    """Класс для управления Android устройством через ADB - интеграция из bot_core.py"""
    
    def __init__(self):
        self.adb_client = None
        self.device = None
        self.scrcpy_process = None
        self.device_serial = None
        self.app_package = "com.my.defense"  # Rush Royale package
        self.connected = False
        
        # Инициализация ADB клиента
        if ADB_AVAILABLE:
            try:
                self.adb_client = AdbClient(host="127.0.0.1", port=5037)
                logger_service.log("ADB клиент инициализирован", LogLevel.INFO)
            except Exception as e:
                logger_service.log(f"Ошибка инициализации ADB: {e}", LogLevel.ERROR)
        else:
            logger_service.log("ADB недоступен - установите ppadb", LogLevel.WARNING)
    
    def connect_device(self, device_serial: Optional[str] = None) -> bool:
        """Подключение к Android устройству"""
        if not ADB_AVAILABLE:
            logger_service.log("ADB недоступен", LogLevel.ERROR)
            return False
        
        try:
            devices = self.adb_client.devices()
            if not devices:
                logger_service.log("Устройства не найдены", LogLevel.ERROR)
                return False
            
            # Выбор устройства
            if device_serial:
                self.device = next((d for d in devices if d.serial == device_serial), None)
            else:
                self.device = devices[0]  # Первое доступное устройство
            
            if self.device:
                self.device_serial = self.device.serial
                self.connected = True
                logger_service.log(f"Подключено к устройству: {self.device_serial}", LogLevel.INFO)
                return True
            else:
                logger_service.log("Не удалось подключиться к устройству", LogLevel.ERROR)
                return False
                
        except Exception as e:
            logger_service.log(f"Ошибка подключения к устройству: {e}", LogLevel.ERROR)
            return False
    
    def start_app(self) -> bool:
        """Запуск приложения Rush Royale"""
        if not self.connected or not self.device:
            logger_service.log("Устройство не подключено", LogLevel.ERROR)
            return False
        
        try:
            # Запуск приложения
            self.device.shell(f"monkey -p {self.app_package} -c android.intent.category.LAUNCHER 1")
            logger_service.log(f"Запущено приложение: {self.app_package}", LogLevel.INFO)
            time.sleep(3)  # Ожидание загрузки
            return True
        except Exception as e:
            logger_service.log(f"Ошибка запуска приложения: {e}", LogLevel.ERROR)
            return False
    
    def get_screenshot(self) -> Optional[bytes]:
        """Получение скриншота экрана"""
        if not self.connected or not self.device:
            return None
        
        try:
            # Попытка использовать scrcpy если доступен
            if SCRCPY_AVAILABLE and self.scrcpy_process:
                return self._get_scrcpy_screenshot()
            else:
                # Fallback на ADB screencap
                return self._get_adb_screenshot()
        except Exception as e:
            logger_service.log(f"Ошибка получения скриншота: {e}", LogLevel.ERROR)
            return None
    
    def _get_adb_screenshot(self) -> Optional[bytes]:
        """Получение скриншота через ADB screencap"""
        try:
            result = self.device.shell("screencap -p", encode=False)
            if result:
                return result
        except Exception as e:
            logger_service.log(f"Ошибка ADB screencap: {e}", LogLevel.ERROR)
        return None
    
    def _get_scrcpy_screenshot(self) -> Optional[bytes]:
        """Получение скриншота через scrcpy"""
        # Реализация для scrcpy будет добавлена позже
        return self._get_adb_screenshot()
    
    def tap(self, x: int, y: int) -> bool:
        """Тап по координатам"""
        if not self.connected or not self.device:
            return False
        
        try:
            self.device.input_tap(x, y)
            logger_service.log(f"Тап по координатам: ({x}, {y})", LogLevel.DEBUG)
            return True
        except Exception as e:
            logger_service.log(f"Ошибка тапа: {e}", LogLevel.ERROR)
            return False
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 1000) -> bool:
        """Свайп между координатами"""
        if not self.connected or not self.device:
            return False
        
        try:
            self.device.input_swipe(x1, y1, x2, y2, duration)
            logger_service.log(f"Свайп: ({x1}, {y1}) -> ({x2}, {y2})", LogLevel.DEBUG)
            return True
        except Exception as e:
            logger_service.log(f"Ошибка свайпа: {e}", LogLevel.ERROR)
            return False
    
    def back_button(self) -> bool:
        """Нажатие кнопки назад"""
        if not self.connected or not self.device:
            return False
        
        try:
            self.device.shell(f"input keyevent {const.KEYCODE_BACK}")
            logger_service.log("Нажата кнопка назад", LogLevel.DEBUG)
            return True
        except Exception as e:
            logger_service.log(f"Ошибка кнопки назад: {e}", LogLevel.ERROR)
            return False
    
    def disconnect(self):
        """Отключение от устройства"""
        if self.scrcpy_process:
            try:
                self.scrcpy_process.terminate()
                self.scrcpy_process = None
            except:
                pass
        
        self.device = None
        self.connected = False
        self.device_serial = None
        logger_service.log("Отключено от устройства", LogLevel.INFO)


class BotService:
    """Основной сервис бота"""
    
    def __init__(self):
        self.status = BotStatus.STOPPED
        self.config = BotConfig()
        self.stats = BotStats()
        self.game_state = GameState()
        
        # Управление циклом
        self._running = False
        self._paused = False
        self._main_task: Optional[asyncio.Task] = None
        self._error_count = 0
        
        # Логи и события
        self.logs: List[Dict[str, Any]] = []
        self.event_callbacks: List[Callable] = []
        
        # Временные метки
        self._start_time: Optional[datetime] = None
        self._game_start_time: Optional[datetime] = None
        
        # Интеграция Bot класса
        self.bot = Bot()
    
    async def initialize(self) -> Dict[str, Any]:
        """Инициализация сервиса бота"""
        try:
            await logger_service.info("Инициализация BotService", "bot")
            
            # Инициализация Bot класса
            if hasattr(self.bot, 'initialize'):
                await self.bot.initialize()
            
            return {"success": True, "message": "BotService инициализирован"}
            
        except Exception as e:
            await logger_service.error(f"Ошибка инициализации BotService: {str(e)}", "bot")
            return {"success": False, "message": f"Ошибка инициализации: {str(e)}"}
    
    async def start(self) -> Dict[str, Any]:
        """Запуск бота"""
        if self.status in [BotStatus.RUNNING, BotStatus.STARTING]:
            return {"success": False, "message": "Бот уже запущен или запускается"}
        
        try:
            self.status = BotStatus.STARTING
            await logger_service.info("Запуск бота", "bot")
            
            # Подключение к устройству через Bot класс
            if not self.bot.connected:
                if not self.bot.connect_device():
                    return {"success": False, "message": "Не удалось подключиться к устройству"}
            
            # Запуск приложения Rush Royale
            if not self.bot.start_app():
                return {"success": False, "message": "Не удалось запустить приложение"}
            
            # Инициализация статистики
            self._start_time = datetime.now()
            self.stats.start_time = self._start_time.isoformat()
            self._error_count = 0
            
            # Запуск основного цикла
            self._running = True
            self._paused = False
            self.status = BotStatus.RUNNING
            
            self._main_task = asyncio.create_task(self._main_loop())
            
            await logger_service.info(f"Бот запущен на устройстве {self.bot.device_serial}", "bot")
            await self._emit_event("bot_started", {"device_id": self.bot.device_serial})
            
            return {"success": True, "message": "Бот успешно запущен"}
            
        except Exception as e:
            self.status = BotStatus.ERROR
            await logger_service.error(f"Ошибка запуска бота: {str(e)}", "bot")
            return {"success": False, "message": f"Ошибка запуска: {str(e)}"}
    
    async def stop(self) -> Dict[str, Any]:
        """Остановка бота"""
        if self.status == BotStatus.STOPPED:
            return {"success": False, "message": "Бот уже остановлен"}
        
        try:
            self.status = BotStatus.STOPPING
            await logger_service.info("Остановка бота", "bot")
            
            self._running = False
            self._paused = False
            
            # Ожидание завершения основного цикла
            if self._main_task and not self._main_task.done():
                self._main_task.cancel()
                try:
                    await self._main_task
                except asyncio.CancelledError:
                    pass
            
            # Отключение от устройства
            self.bot.disconnect()
            
            # Обновление статистики
            if self._start_time:
                runtime = (datetime.now() - self._start_time).total_seconds()
                self.stats.total_runtime += runtime
            
            self.status = BotStatus.STOPPED
            self.game_state = GameState()  # Сброс состояния игры
            
            await logger_service.info("Бот остановлен", "bot")
            await self._emit_event("bot_stopped", {})
            
            return {"success": True, "message": "Бот успешно остановлен"}
            
        except Exception as e:
            self.status = BotStatus.ERROR
            await logger_service.error(f"Ошибка остановки бота: {str(e)}", "bot")
            return {"success": False, "message": f"Ошибка остановки: {str(e)}"}
    
    async def toggle_pause(self) -> Dict[str, Any]:
        """Переключение паузы"""
        if self.status != BotStatus.RUNNING and not self._paused:
            return {"success": False, "message": "Бот не запущен"}
        
        self._paused = not self._paused
        new_status = BotStatus.PAUSED if self._paused else BotStatus.RUNNING
        self.status = new_status
        
        action = "приостановлен" if self._paused else "возобновлен"
        await logger_service.info(f"Бот {action}", "bot")
        await self._emit_event("bot_paused" if self._paused else "bot_resumed", {})
        
        return {"success": True, "message": f"Бот {action}"}
    
    async def quick_start(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Быстрый запуск с минимальными настройками"""
        if device_id:
            self.config.device_id = device_id
        
        # Установка базовых настроек для быстрого старта
        self.config.auto_start = True
        self.config.game_mode = GameMode.PVP
        
        return await self.start()
    
    async def quit_game(self) -> Dict[str, Any]:
        """Выход из текущей игры"""
        if not self.game_state.in_game:
            return {"success": False, "message": "Не в игре"}
        
        try:
            # Попытка выйти из игры через интерфейс
            device = await device_service.get_device(self.config.device_id)
            if device:
                # Нажатие кнопки выхода (координаты могут отличаться)
                await device.tap(50, 50)  # Примерные координаты кнопки меню
                await asyncio.sleep(1)
                await device.tap(200, 300)  # Примерные координаты кнопки выхода
            
            self.game_state.in_game = False
            await logger_service.info("Выход из игры", "bot")
            await self._emit_event("game_quit", {})
            
            return {"success": True, "message": "Выход из игры выполнен"}
            
        except Exception as e:
            await logger_service.error(f"Ошибка выхода из игры: {str(e)}", "bot")
            return {"success": False, "message": f"Ошибка выхода: {str(e)}"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        return {
            "status": self.status.value,
            "running": self._running,
            "paused": self._paused,
            "config": self.config.to_dict(),
            "stats": self.stats.to_dict(),
            "game_state": self.game_state.to_dict(),
            "error_count": self._error_count,
            "device_connected": self.bot.connected,
            "device_serial": self.bot.device_serial,
            "start_time": self._start_time.isoformat() if self._start_time else None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики бота"""
        return self.stats.to_dict()
    
    async def update_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление конфигурации"""
        try:
            for key, value in config_data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            await logger_service.info("Конфигурация обновлена", "bot")
            return {"success": True, "message": "Конфигурация обновлена"}
            
        except Exception as e:
            await logger_service.error(f"Ошибка обновления конфигурации: {str(e)}", "bot")
            return {"success": False, "message": f"Ошибка обновления: {str(e)}"}
    
    async def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение логов бота"""
        return self.logs[-limit:] if limit > 0 else self.logs
    
    async def clear_logs(self):
        """Очистка логов"""
        self.logs.clear()
        await logger_service.info("Логи очищены", "bot")
    
    # Методы для управления устройством через Bot класс
    
    async def connect_device(self, device_serial: Optional[str] = None) -> Dict[str, Any]:
        """Подключение к устройству"""
        try:
            if self.bot.connect_device(device_serial):
                await self._emit_event('device_connected', {
                    "device_serial": self.bot.device_serial
                })
                return {"success": True, "message": f"Подключено к устройству {self.bot.device_serial}"}
            else:
                return {"success": False, "message": "Не удалось подключиться к устройству"}
        except Exception as e:
            error_msg = f"Ошибка подключения: {str(e)}"
            logger_service.log(error_msg, LogLevel.ERROR)
            return {"success": False, "message": error_msg}
    
    async def disconnect_device(self) -> Dict[str, Any]:
        """Отключение от устройства"""
        try:
            self.bot.disconnect()
            await self._emit_event('device_disconnected', {})
            return {"success": True, "message": "Устройство отключено"}
        except Exception as e:
            error_msg = f"Ошибка отключения: {str(e)}"
            logger_service.log(error_msg, LogLevel.ERROR)
            return {"success": False, "message": error_msg}
    
    async def get_screenshot(self) -> Optional[str]:
        """Получение скриншота в формате base64"""
        try:
            screenshot_bytes = self.bot.get_screenshot()
            if screenshot_bytes:
                # Конвертация в base64 для передачи через WebSocket
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                return screenshot_b64
            return None
        except Exception as e:
            logger_service.log(f"Ошибка получения скриншота: {e}", LogLevel.ERROR)
            return None
    
    async def tap_screen(self, x: int, y: int) -> Dict[str, Any]:
        """Тап по экрану"""
        try:
            if self.bot.tap(x, y):
                return {"success": True, "message": f"Тап по координатам ({x}, {y})"}
            else:
                return {"success": False, "message": "Не удалось выполнить тап"}
        except Exception as e:
            error_msg = f"Ошибка тапа: {str(e)}"
            logger_service.log(error_msg, LogLevel.ERROR)
            return {"success": False, "message": error_msg}
    
    async def swipe_screen(self, x1: int, y1: int, x2: int, y2: int, duration: int = 1000) -> Dict[str, Any]:
        """Свайп по экрану"""
        try:
            if self.bot.swipe(x1, y1, x2, y2, duration):
                return {"success": True, "message": f"Свайп ({x1}, {y1}) -> ({x2}, {y2})"}
            else:
                return {"success": False, "message": "Не удалось выполнить свайп"}
        except Exception as e:
            error_msg = f"Ошибка свайпа: {str(e)}"
            logger_service.log(error_msg, LogLevel.ERROR)
            return {"success": False, "message": error_msg}
    
    def add_event_callback(self, callback: Callable):
        """Добавление callback для событий"""
        self.event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable):
        """Удаление callback для событий"""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Отправка события всем подписчикам"""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Добавление в логи
        self.logs.append(event)
        
        # Ограничение количества логов
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
        
        # Отправка callback'ам
        for callback in self.event_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                await logger_service.error(f"Ошибка в callback: {str(e)}", "bot")
    
    async def _main_loop(self):
        """Основной цикл работы бота"""
        try:
            self.status = BotStatus.RUNNING
            await self._emit_event('status_changed', self.get_status())
            
            while self._running:
                if self._paused:
                    await asyncio.sleep(1)
                    continue
                
                try:
                    # Проверка подключения к устройству
                    if not self.bot.connected:
                        logger_service.log("Устройство отключено, попытка переподключения", LogLevel.WARNING)
                        if not self.bot.connect_device():
                            await asyncio.sleep(5)
                            continue
                    
                    # Получение скриншота для анализа
                    screenshot_bytes = self.bot.get_screenshot()
                    if not screenshot_bytes:
                        logger_service.log("Не удалось получить скриншот", LogLevel.WARNING)
                        await asyncio.sleep(2)
                        continue
                    
                    # Анализ состояния игры с использованием компьютерного зрения
                    await self._analyze_game_state(screenshot_bytes)
                    
                    # Выполнение действий в зависимости от состояния
                    await self._execute_game_actions()
                    
                    # Обновление статистики
                    await self._update_stats()
                    
                    # Пауза между итерациями
                    await asyncio.sleep(self.config.delay_between_actions)
                    
                except Exception as e:
                    logger_service.log(f"Ошибка в основном цикле: {str(e)}", LogLevel.ERROR)
                    await self._emit_event('error_occurred', {"error": str(e)})
                    await asyncio.sleep(5)  # Пауза при ошибке
                    
        except asyncio.CancelledError:
            logger_service.log("Основной цикл бота отменен", LogLevel.INFO)
        except Exception as e:
            self.status = BotStatus.ERROR
            error_msg = f"Критическая ошибка в основном цикле: {str(e)}"
            logger_service.log(error_msg, LogLevel.ERROR)
            await self._emit_event('error_occurred', {"error": error_msg})
        finally:
            self.status = BotStatus.STOPPED
            await self._emit_event('status_changed', self.get_status())
    
    async def _game_cycle(self):
        """Один цикл игрового процесса"""
        # Получение скриншота
        device = await device_service.get_device(self.config.device_id)
        if not device:
            raise Exception("Устройство недоступно")
        
        screenshot = await device.get_screenshot()
        if not screenshot:
            raise Exception("Не удалось получить скриншот")
        
        # Анализ состояния игры
        await self._analyze_game_state(screenshot)
        
        # Выполнение действий в зависимости от состояния
        if self.game_state.in_game:
            await self._perform_game_actions(device)
        else:
            await self._handle_menu_state(device)
    
    async def _analyze_game_state(self, screenshot_bytes):
        """Анализ состояния игры по скриншоту"""
        try:
            # Конвертация скриншота в формат для анализа
            import numpy as np
            nparr = np.frombuffer(screenshot_bytes, np.uint8)
            
            try:
                import cv2
                screenshot = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except ImportError:
                logger_service.log("OpenCV не установлен, используется базовый анализ", LogLevel.WARNING)
                screenshot = None
            
            # Анализ состояния через компьютерное зрение
            game_state = await self._vision_analysis(screenshot)
            
            # Обновление состояния
            self.current_state = game_state
            await self._emit_event('game_state_changed', game_state)
            
        except Exception as e:
            logger_service.log(f"Ошибка анализа состояния игры: {str(e)}", LogLevel.ERROR)
    
    async def _vision_analysis(self, screenshot):
        """Анализ скриншота с помощью компьютерного зрения"""
        try:
            if screenshot is None:
                return {
                    'in_game': False,
                    'current_mana': 0,
                    'max_mana': 0,
                    'grid_state': {},
                    'menu_detected': True
                }
            
            # Анализ сетки игрового поля
            grid_analysis = await vision_service.analyze_grid(screenshot)
            
            # Анализ маны
            mana_analysis = await vision_service.analyze_mana(screenshot)
            
            # Определение состояния игры
            game_state = {
                'in_game': grid_analysis.get('occupied_cells', 0) > 0 or mana_analysis.get('current_mana', 0) > 0,
                'current_mana': mana_analysis.get('current_mana', 0),
                'max_mana': mana_analysis.get('max_mana', 0),
                'grid_state': grid_analysis,
                'menu_detected': False
            }
            
            return game_state
            
        except Exception as e:
            logger_service.log(f"Ошибка анализа компьютерного зрения: {str(e)}", LogLevel.ERROR)
            return {
                'in_game': False,
                'current_mana': 0,
                'max_mana': 0,
                'grid_state': {},
                'menu_detected': True
            }
    
    async def _execute_game_actions(self):
        """Выполнение игровых действий на основе текущего состояния"""
        try:
            if not self.current_state:
                return
            
            if self.current_state.get('in_game', False):
                await self._perform_game_actions()
            elif self.current_state.get('menu_detected', False):
                await self._handle_menu_actions()
                
        except Exception as e:
            logger_service.log(f"Ошибка выполнения игровых действий: {str(e)}", LogLevel.ERROR)
    
    async def _perform_game_actions(self):
        """Выполнение действий в игре"""
        try:
            current_mana = self.current_state.get('current_mana', 0)
            grid_state = self.current_state.get('grid_state', {})
            
            # Логика размещения юнитов если есть мана
            if current_mana >= 3:  # Минимальная стоимость юнита
                await self._place_units()
            
            # Логика объединения юнитов
            await self._merge_units()
            
            # Логика использования заклинаний
            await self._use_spells()
            
        except Exception as e:
            logger_service.log(f"Ошибка выполнения игровых действий: {str(e)}", LogLevel.ERROR)
            self.stats.game_errors += 1
    
    async def _place_units(self):
        """Размещение юнитов на игровом поле"""
        try:
            # Поиск свободных ячеек на поле
            grid_state = self.current_state.get('grid_state', {})
            empty_cells = grid_state.get('empty_cells', [])
            
            if empty_cells and self.config.auto_upgrade:
                # Выбираем случайную свободную ячейку
                import random
                target_cell = random.choice(empty_cells)
                
                # Клик по ячейке для размещения юнита
                await self.bot.tap(target_cell['x'], target_cell['y'])
                logger_service.log(f"Размещен юнит в ячейке ({target_cell['x']}, {target_cell['y']})", LogLevel.INFO)
                
                self.stats.total_actions += 1
                
        except Exception as e:
            logger_service.log(f"Ошибка размещения юнитов: {str(e)}", LogLevel.ERROR)
    
    async def _merge_units(self):
        """Объединение одинаковых юнитов"""
        try:
            if not self.config.auto_merge:
                return
                
            grid_state = self.current_state.get('grid_state', {})
            mergeable_pairs = grid_state.get('mergeable_pairs', [])
            
            for pair in mergeable_pairs:
                # Перетаскивание одного юнита на другой для объединения
                await self.bot.swipe(
                    pair['from']['x'], pair['from']['y'],
                    pair['to']['x'], pair['to']['y']
                )
                logger_service.log(f"Объединены юниты: ({pair['from']['x']}, {pair['from']['y']}) -> ({pair['to']['x']}, {pair['to']['y']})", LogLevel.INFO)
                
                self.stats.total_actions += 1
                await asyncio.sleep(0.5)  # Пауза между объединениями
                
        except Exception as e:
            logger_service.log(f"Ошибка объединения юнитов: {str(e)}", LogLevel.ERROR)
    
    async def _use_spells(self):
        """Использование заклинаний"""
        try:
            # Логика использования заклинаний будет добавлена позже
            # В зависимости от конкретных потребностей игры
            pass
            
        except Exception as e:
            logger_service.log(f"Ошибка использования заклинаний: {str(e)}", LogLevel.ERROR)
    
    async def _handle_menu_actions(self):
        """Обработка действий в меню"""
        try:
            # Попытка найти и нажать кнопку "Play" или "Start"
            # Координаты могут быть определены через компьютерное зрение
            
            # Временная логика - клик по центру экрана
            screen_center_x = 540  # Примерное значение для разрешения 1080x1920
            screen_center_y = 960
            
            await self.bot.tap(screen_center_x, screen_center_y)
            logger_service.log("Выполнен клик в меню", LogLevel.INFO)
            
            await asyncio.sleep(2)  # Ожидание загрузки
            
        except Exception as e:
             logger_service.log(f"Ошибка обработки меню: {str(e)}", LogLevel.ERROR)
     
    async def _update_stats(self):
        """Обновление статистики бота"""
        try:
            # Обновляем время работы
            if self.stats.start_time:
                self.stats.uptime = time.time() - self.stats.start_time
            
            # Обновляем статистику игры
            if self.current_state and self.current_state.get('in_game', False):
                self.stats.games_played += 1
            
            # Отправляем обновленную статистику через WebSocket
            await self._emit_event('stats_updated', await self.get_stats())
            
        except Exception as e:
            logger_service.log(f"Ошибка обновления статистики: {str(e)}", LogLevel.ERROR)
    
    async def _try_merge_cards(self, device):
        """Попытка объединения карт"""
        # Заглушка для логики объединения
        # В реальной реализации здесь будет анализ сетки и поиск возможных объединений
        pass
    
    async def _try_place_card(self, device):
        """Попытка размещения карты"""
        # Заглушка для логики размещения карт
        # В реальной реализации здесь будет поиск пустых ячеек и размещение карт
        pass
    
    async def _handle_menu_state(self, device):
        """Обработка состояния меню"""
        # Логика для навигации по меню и запуска игр
        if self.config.auto_start:
            # Попытка запустить игру
            # Координаты кнопок будут зависеть от конкретного интерфейса
            await device.tap(540, 1200)  # Примерные координаты кнопки "Играть"
            await asyncio.sleep(2)
    
    async def _handle_error(self, error: Exception):
        """Обработка ошибок"""
        self._error_count += 1
        self.stats.total_errors += 1
        
        await logger_service.error(f"Ошибка в боте: {str(error)}", "bot")
        
        # Скриншот при ошибке
        if self.config.screenshot_on_error:
            try:
                device = await device_service.get_device(self.config.device_id)
                if device:
                    screenshot = await device.get_screenshot()
                    if screenshot:
                        # Сохранение скриншота ошибки
                        error_dir = Path("logs/error_screenshots")
                        error_dir.mkdir(parents=True, exist_ok=True)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = error_dir / f"error_{timestamp}.png"
                        
                        # Здесь должно быть сохранение base64 в файл
                        await logger_service.info(f"Скриншот ошибки сохранен: {screenshot_path}", "bot")
            except Exception:
                pass  # Игнорируем ошибки при сохранении скриншота
        
        # Перезапуск при критических ошибках
        if self.config.restart_on_error and self._error_count >= 3:
            await logger_service.warning("Попытка перезапуска из-за множественных ошибок", "bot")
            await self.stop()
            await asyncio.sleep(5)
            await self.start()

# Глобальный экземпляр сервиса
bot_service = BotService()