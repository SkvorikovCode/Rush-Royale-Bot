# -*- coding: utf-8 -*-
"""
WebSocket Manager для Rush Royale Bot
Управление WebSocket соединениями и real-time обновлениями

Автор: SkvorikovCode
Дата: 2025
"""

import asyncio
import json
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        # Активные соединения по типам
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "bot": set(),
            "devices": set(),
            "logs": set(),
            "vision": set()
        }
        
        # Метаданные соединений
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, connection_type: str, metadata: Optional[Dict[str, Any]] = None):
        """Подключение нового WebSocket"""
        await websocket.accept()
        
        if connection_type not in self.active_connections:
            self.active_connections[connection_type] = set()
        
        self.active_connections[connection_type].add(websocket)
        
        # Сохранение метаданных
        self.connection_metadata[websocket] = {
            "type": connection_type,
            "connected_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        print(f"WebSocket подключен: {connection_type}, всего соединений: {len(self.active_connections[connection_type])}")
    
    def disconnect(self, websocket: WebSocket):
        """Отключение WebSocket"""
        # Поиск и удаление из всех типов соединений
        for connection_type, connections in self.active_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                print(f"WebSocket отключен: {connection_type}, осталось соединений: {len(connections)}")
                break
        
        # Удаление метаданных
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Отправка сообщения конкретному соединению"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Ошибка отправки личного сообщения: {e}")
            self.disconnect(websocket)
    
    async def broadcast_to_type(self, message: Dict[str, Any], connection_type: str):
        """Отправка сообщения всем соединениям определенного типа"""
        if connection_type not in self.active_connections:
            return
        
        disconnected = set()
        
        for websocket in self.active_connections[connection_type].copy():
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Ошибка отправки сообщения {connection_type}: {e}")
                disconnected.add(websocket)
        
        # Удаление отключенных соединений
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Отправка сообщения всем активным соединениям"""
        for connection_type in self.active_connections:
            await self.broadcast_to_type(message, connection_type)
    
    def get_connection_count(self, connection_type: Optional[str] = None) -> int:
        """Получение количества активных соединений"""
        if connection_type:
            return len(self.active_connections.get(connection_type, set()))
        
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Получение статистики соединений"""
        stats = {
            "total_connections": self.get_connection_count(),
            "connections_by_type": {},
            "active_types": list(self.active_connections.keys())
        }
        
        for connection_type, connections in self.active_connections.items():
            stats["connections_by_type"][connection_type] = len(connections)
        
        return stats
    
    async def handle_bot_websocket(self, websocket: WebSocket):
        """Обработка WebSocket соединения для бота"""
        await self.connect(websocket, "bot")
        
        try:
            # Импорт здесь для избежания циклических импортов
            from .services.bot_service import bot_service
            
            # Callback для отправки событий бота
            async def send_bot_event(event):
                try:
                    await self.send_personal_message(event, websocket)
                except Exception as e:
                    print(f"Ошибка отправки события бота: {e}")
            
            # Добавление callback к сервису бота
            bot_service.add_event_callback(send_bot_event)
            
            # Отправка текущего статуса при подключении
            status = await bot_service.get_status()
            await self.send_personal_message({
                "type": "initial_status",
                "timestamp": datetime.now().isoformat(),
                "data": status
            }, websocket)
            
            # Отправка текущих логов
            logs = await bot_service.get_logs(limit=20)
            await self.send_personal_message({
                "type": "initial_logs",
                "timestamp": datetime.now().isoformat(),
                "data": logs
            }, websocket)
            
            # Отправка статистики
            stats = bot_service.get_stats()
            await self.send_personal_message({
                "type": "initial_stats",
                "timestamp": datetime.now().isoformat(),
                "data": stats
            }, websocket)
            
            # Обработка команд от клиента
            while True:
                data = await websocket.receive_json()
                await self._handle_bot_command(data, websocket, bot_service)
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Ошибка в bot WebSocket: {e}")
        finally:
            # Удаление callback при отключении
            try:
                from .services.bot_service import bot_service
                bot_service.remove_event_callback(send_bot_event)
            except:
                pass
            self.disconnect(websocket)
    
    async def _handle_bot_command(self, data: Dict[str, Any], websocket: WebSocket, bot_service):
        """Обработка команд бота от клиента"""
        action = data.get("action")
        result = None
        
        try:
            if action == "start":
                device_id = data.get("device_id")
                result = await bot_service.start() if not device_id else await bot_service.quick_start(device_id)
            elif action == "stop":
                result = await bot_service.stop()
            elif action == "pause":
                result = await bot_service.toggle_pause()
            elif action == "quit_game":
                result = await bot_service.quit_game()
            elif action == "get_status":
                result = await bot_service.get_status()
            elif action == "get_stats":
                result = bot_service.get_stats()
            elif action == "get_logs":
                limit = data.get("limit", 50)
                result = await bot_service.get_logs(limit=limit)
            elif action == "clear_logs":
                result = await bot_service.clear_logs()
            elif action == "update_config":
                config = data.get("config", {})
                result = await bot_service.update_config(config)
            elif action == "connect_device":
                device_id = data.get("device_id")
                result = await bot_service.connect_device(device_id)
            elif action == "disconnect_device":
                result = await bot_service.disconnect_device()
            elif action == "get_screenshot":
                result = await bot_service.get_screenshot()
            elif action == "tap_screen":
                x = data.get("x")
                y = data.get("y")
                if x is not None and y is not None:
                    result = await bot_service.tap_screen(x, y)
                else:
                    result = {"success": False, "message": "Координаты x и y обязательны"}
            elif action == "swipe_screen":
                x1 = data.get("x1")
                y1 = data.get("y1")
                x2 = data.get("x2")
                y2 = data.get("y2")
                if all(coord is not None for coord in [x1, y1, x2, y2]):
                    result = await bot_service.swipe_screen(x1, y1, x2, y2)
                else:
                    result = {"success": False, "message": "Все координаты обязательны"}
            else:
                result = {"success": False, "message": f"Неизвестная команда: {action}"}
            
            # Отправка результата команды
            await self.send_personal_message({
                "type": "command_result",
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }, websocket)
            
        except Exception as e:
            await self.send_personal_message({
                "type": "command_error",
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }, websocket)
    
    async def handle_device_websocket(self, websocket: WebSocket):
        """Обработка WebSocket соединения для устройств"""
        await self.connect(websocket, "devices")
        
        try:
            from .services.device_service import device_service
            
            # Отправка списка устройств при подключении
            devices = device_service.get_device_list()
            await self.send_personal_message({
                "type": "device_list",
                "timestamp": datetime.now().isoformat(),
                "data": devices
            }, websocket)
            
            # Периодическое обновление статуса устройств
            while True:
                await asyncio.sleep(5)  # Обновление каждые 5 секунд
                
                devices = device_service.get_device_list()
                await self.send_personal_message({
                    "type": "device_update",
                    "timestamp": datetime.now().isoformat(),
                    "data": devices
                }, websocket)
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Ошибка в device WebSocket: {e}")
        finally:
            self.disconnect(websocket)
    
    async def handle_logs_websocket(self, websocket: WebSocket):
        """Обработка WebSocket соединения для логов"""
        await self.connect(websocket, "logs")
        
        try:
            from .services.logger_service import logger_service
            from .services.bot_service import bot_service
            
            # Отправка последних логов при подключении
            logs = await logger_service.get_logs(limit=50)
            await self.send_personal_message({
                "type": "logs_history",
                "timestamp": datetime.now().isoformat(),
                "data": logs
            }, websocket)
            
            # Callback для отправки новых логов
            async def send_log_event(event):
                try:
                    if event.get("type") in ["log_added", "error_occurred"]:
                        await self.send_personal_message(event, websocket)
                except Exception as e:
                    print(f"Ошибка отправки лога: {e}")
            
            # Добавление callback к сервису бота для получения логов
            bot_service.add_event_callback(send_log_event)
            
            # Ожидание отключения
            while True:
                await asyncio.sleep(1)
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Ошибка в logs WebSocket: {e}")
        finally:
            # Удаление callback при отключении
            try:
                from .services.bot_service import bot_service
                bot_service.remove_event_callback(send_log_event)
            except:
                pass
            self.disconnect(websocket)
    
    async def handle_vision_websocket(self, websocket: WebSocket):
        """Обработка WebSocket соединения для компьютерного зрения"""
        await self.connect(websocket, "vision")
        
        try:
            from .services.bot_service import bot_service
            from .services.vision_service import vision_service
            
            # Callback для отправки данных компьютерного зрения
            async def send_vision_event(event):
                try:
                    if event.get("type") in ["game_state_changed", "vision_analysis", "screenshot_taken"]:
                        await self.send_personal_message(event, websocket)
                except Exception as e:
                    print(f"Ошибка отправки данных зрения: {e}")
            
            # Добавление callback к сервису бота
            bot_service.add_event_callback(send_vision_event)
            
            # Отправка текущего состояния игры при подключении
            if hasattr(bot_service, 'current_state') and bot_service.current_state:
                await self.send_personal_message({
                    "type": "initial_game_state",
                    "timestamp": datetime.now().isoformat(),
                    "data": bot_service.current_state
                }, websocket)
            
            # Обработка команд vision от клиента
            while True:
                try:
                    data = await asyncio.wait_for(websocket.receive_json(), timeout=1.0)
                    await self._handle_vision_command(data, websocket)
                except asyncio.TimeoutError:
                    continue
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Ошибка в vision WebSocket: {e}")
        finally:
            # Удаление callback при отключении
            try:
                from .services.bot_service import bot_service
                bot_service.remove_event_callback(send_vision_event)
            except:
                pass
            self.disconnect(websocket)
    
    async def _handle_vision_command(self, data: Dict[str, Any], websocket: WebSocket):
        """Обработка команд компьютерного зрения от клиента"""
        action = data.get("action")
        result = None
        
        try:
            from .services.vision_service import vision_service
            from .services.bot_service import bot_service
            
            if action == "analyze_screenshot":
                screenshot_data = data.get("screenshot")
                if screenshot_data:
                    result = await vision_service.analyze_screenshot(screenshot_data)
                else:
                    result = {"success": False, "message": "Скриншот не предоставлен"}
            elif action == "get_game_state":
                result = getattr(bot_service, 'current_state', None) or {"in_game": False}
            elif action == "analyze_grid":
                screenshot_data = data.get("screenshot")
                if screenshot_data:
                    result = await vision_service.analyze_grid(screenshot_data)
                else:
                    result = {"success": False, "message": "Скриншот не предоставлен"}
            elif action == "analyze_mana":
                screenshot_data = data.get("screenshot")
                if screenshot_data:
                    result = await vision_service.analyze_mana(screenshot_data)
                else:
                    result = {"success": False, "message": "Скриншот не предоставлен"}
            else:
                result = {"success": False, "message": f"Неизвестная команда vision: {action}"}
            
            # Отправка результата команды
            await self.send_personal_message({
                "type": "vision_command_result",
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }, websocket)
            
        except Exception as e:
            await self.send_personal_message({
                "type": "vision_command_error",
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }, websocket)

# Глобальный экземпляр менеджера
connection_manager = ConnectionManager()
websocket_manager = connection_manager  # Алиас для совместимости