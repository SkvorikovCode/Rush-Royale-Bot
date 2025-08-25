import asyncio
import uuid
from typing import Dict, Optional, Any
from datetime import datetime

class BotSession:
    """Класс для управления отдельной сессией бота"""
    
    def __init__(self, device_id: str, config: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.device_id = device_id
        self.config = config
        self.status = "idle"  # idle, running, paused, error
        self.created_at = datetime.now()
        self.last_action = None
        self.stats = {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "runtime": 0
        }
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Запуск сессии бота"""
        if self.status == "running":
            return False
        
        self.status = "running"
        self._task = asyncio.create_task(self._run_bot_loop())
        return True
    
    async def stop(self):
        """Остановка сессии бота"""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        self.status = "idle"
    
    async def pause(self):
        """Пауза сессии бота"""
        if self.status == "running":
            self.status = "paused"
    
    async def resume(self):
        """Возобновление сессии бота"""
        if self.status == "paused":
            self.status = "running"
    
    async def _run_bot_loop(self):
        """Основной цикл работы бота"""
        try:
            while self.status == "running":
                # Здесь будет логика бота
                await asyncio.sleep(1)
                
                # Обновление статистики
                self.stats["runtime"] += 1
                
        except Exception as e:
            self.status = "error"
            self.last_action = f"Error: {str(e)}"
    
    def get_state(self) -> Dict[str, Any]:
        """Получение текущего состояния сессии"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_action": self.last_action,
            "stats": self.stats,
            "config": self.config
        }

class BotManager:
    """Менеджер для управления всеми сессиями ботов"""
    
    def __init__(self):
        self.sessions: Dict[str, BotSession] = {}
    
    async def create_session(self, device_id: str, config: Dict[str, Any]) -> str:
        """Создание новой сессии бота"""
        session = BotSession(device_id, config)
        self.sessions[session.id] = session
        return session.id
    
    async def start_session(self, session_id: str) -> bool:
        """Запуск сессии бота"""
        if session_id not in self.sessions:
            return False
        
        return await self.sessions[session_id].start()
    
    async def stop_session(self, session_id: str) -> bool:
        """Остановка сессии бота"""
        if session_id not in self.sessions:
            return False
        
        await self.sessions[session_id].stop()
        return True
    
    async def pause_session(self, session_id: str) -> bool:
        """Пауза сессии бота"""
        if session_id not in self.sessions:
            return False
        
        await self.sessions[session_id].pause()
        return True
    
    async def resume_session(self, session_id: str) -> bool:
        """Возобновление сессии бота"""
        if session_id not in self.sessions:
            return False
        
        await self.sessions[session_id].resume()
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Удаление сессии бота"""
        if session_id not in self.sessions:
            return False
        
        await self.sessions[session_id].stop()
        del self.sessions[session_id]
        return True
    
    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение состояния сессии"""
        if session_id not in self.sessions:
            return None
        
        return self.sessions[session_id].get_state()
    
    async def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Получение всех сессий"""
        return {sid: session.get_state() for sid, session in self.sessions.items()}
    
    async def stop_all_sessions(self):
        """Остановка всех сессий"""
        for session in self.sessions.values():
            await session.stop()
    
    def has_active_session(self) -> bool:
        """Проверка наличия активных сессий"""
        return any(session.status == "running" for session in self.sessions.values())
    
    def get_active_sessions_count(self) -> int:
        """Количество активных сессий"""
        return sum(1 for session in self.sessions.values() if session.status == "running")
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Получение общего состояния всех сессий"""
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": self.get_active_sessions_count(),
            "sessions": await self.get_all_sessions()
        }