#!/usr/bin/env python3
"""Скрипт запуска Rush Royale Bot Backend"""

import uvicorn
import os
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Главная функция запуска сервера"""
    
    # Настройки сервера
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting Rush Royale Bot Backend...")
    print(f"📡 Server: http://{host}:{port}")
    print(f"🔄 Reload: {reload}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Запуск сервера
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["app"] if reload else None,
        log_level="info"
    )

if __name__ == "__main__":
    main()