# macOS Migration & Implementation Plan

## 1. Migration Strategy Overview

### 1.1 Phased Migration Approach

**Phase 1: Foundation Setup (Week 1-2)**
- Настройка Electron + React окружения
- Создание базовой архитектуры приложения
- Интеграция с существующим Python backend
- Базовая поддержка Apple Silicon

**Phase 2: Core Functionality (Week 3-4)**
- Миграция основных компонентов с tkinter на React
- Реализация WebSocket коммуникации
- Интеграция ADB и device management
- Базовый UI/UX для macOS

**Phase 3: macOS Integration (Week 5-6)**
- Нативные меню и горячие клавиши
- Поддержка жестов трекпада
- Retina дисплей оптимизация
- Dock и системные уведомления

**Phase 4: Optimization & Polish (Week 7-8)**
- Apple Silicon оптимизация
- Performance tuning
- UI/UX полировка
- Тестирование и отладка

### 1.2 Technology Migration Map

| Текущая технология | Новая технология | Причина замены |
|-------------------|------------------|----------------|
| tkinter | React + Electron | Современный UI, кроссплатформенность |
| Direct ADB calls | FastAPI + WebSocket | Лучшая архитектура, real-time updates |
| Static config files | Dynamic configuration | Гибкость настроек |
| Basic threading | Async/await pattern | Лучшая производительность |
| PIL/OpenCV direct | Core Image Framework | Нативная оптимизация macOS |

## 2. Detailed Implementation Plan

### 2.1 Project Structure

```
rush-royale-bot-macos/
├── electron/                    # Electron main process
│   ├── main.ts                 # Главный процесс Electron
│   ├── preload.ts              # Preload скрипт для безопасности
│   └── native/                 # Нативные модули macOS
│       ├── menu.ts             # Нативное меню
│       ├── gestures.ts         # Жесты трекпада
│       └── system.ts           # Системная интеграция
├── frontend/                   # React приложение
│   ├── src/
│   │   ├── components/         # React компоненты
│   │   │   ├── Dashboard/      # Главная панель
│   │   │   ├── Settings/       # Настройки
│   │   │   ├── Monitoring/     # Мониторинг
│   │   │   ├── Devices/        # Управление устройствами
│   │   │   └── System/         # Системные настройки
│   │   ├── hooks/              # React hooks
│   │   ├── services/           # API сервисы
│   │   ├── store/              # State management (Zustand)
│   │   └── types/              # TypeScript типы
│   ├── public/
│   └── package.json
├── backend/                    # Python backend
│   ├── app/
│   │   ├── api/                # FastAPI endpoints
│   │   ├── core/               # Основная логика бота
│   │   ├── services/           # Сервисы (ADB, CV, etc.)
│   │   └── models/             # Модели данных
│   ├── requirements.txt
│   └── main.py
├── shared/                     # Общие типы и утилиты
│   └── types.ts
└── build/                      # Сборка приложения
    ├── icons/                  # Иконки для macOS
    └── scripts/                # Скрипты сборки
```

### 2.2 Core Components Implementation

#### 2.2.1 Electron Main Process

```typescript
// electron/main.ts
import { app, BrowserWindow, Menu, ipcMain } from 'electron';
import { setupNativeMenu } from './native/menu';
import { setupGestureHandlers } from './native/gestures';
import { startPythonBackend } from './services/backend';

class RushRoyaleBotApp {
  private mainWindow: BrowserWindow | null = null;
  private pythonProcess: any = null;

  async initialize() {
    await app.whenReady();
    
    // Запуск Python backend
    this.pythonProcess = await startPythonBackend();
    
    // Создание главного окна
    this.createMainWindow();
    
    // Настройка нативных функций macOS
    setupNativeMenu(this.mainWindow);
    setupGestureHandlers(this.mainWindow);
  }

  private createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 1000,
      minHeight: 600,
      titleBarStyle: 'hiddenInset', // macOS стиль
      vibrancy: 'under-window',     // Прозрачность macOS
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      }
    });
  }
}
```

#### 2.2.2 React Dashboard Component

```typescript
// frontend/src/components/Dashboard/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { useBotStore } from '../../store/botStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import { BotStatus } from './BotStatus';
import { QuickActions } from './QuickActions';
import { DeviceSelector } from './DeviceSelector';

export const Dashboard: React.FC = () => {
  const { botState, startBot, stopBot } = useBotStore();
  const { isConnected, lastMessage } = useWebSocket('ws://localhost:8000/ws');

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Rush Royale Bot
        </h1>
        <BotStatus status={botState.status} isConnected={isConnected} />
      </div>
      
      <div className="dashboard-grid">
        <DeviceSelector />
        <QuickActions onStart={startBot} onStop={stopBot} />
        
        {/* Real-time game state visualization */}
        <div className="game-state-panel">
          <GameFieldVisualization data={lastMessage?.gameState} />
        </div>
      </div>
    </div>
  );
};
```

#### 2.2.3 Python FastAPI Backend

```python
# backend/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import Dict, List

from .core.bot_manager import BotManager
from .services.device_service import DeviceService
from .api.routes import bot_router, device_router

app = FastAPI(title="Rush Royale Bot API", version="2.0.0")

# CORS для Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Менеджеры
bot_manager = BotManager()
device_service = DeviceService()

# WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        while True:
            # Отправка обновлений состояния бота
            if bot_manager.has_active_session():
                state = await bot_manager.get_current_state()
                await websocket.send_text(json.dumps({
                    "type": "bot_state",
                    "data": state
                }))
            
            await asyncio.sleep(0.1)  # 10 FPS updates
            
    except WebSocketDisconnect:
        del active_connections[client_id]

# Подключение роутеров
app.include_router(bot_router, prefix="/api/bot")
app.include_router(device_router, prefix="/api/devices")

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    await device_service.scan_devices()
    print("🚀 Rush Royale Bot API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении"""
    await bot_manager.stop_all_sessions()
    print("🛑 Rush Royale Bot API stopped")
```

### 2.3 macOS Native Integration

#### 2.3.1 Trackpad Gestures

```typescript
// electron/native/gestures.ts
import { BrowserWindow, ipcMain } from 'electron';

export function setupGestureHandlers(window: BrowserWindow) {
  // Pinch to zoom для масштабирования игрового поля
  window.webContents.on('zoom-changed', (event, zoomDirection) => {
    window.webContents.send('gesture:zoom', {
      direction: zoomDirection,
      timestamp: Date.now()
    });
  });

  // Swipe gestures для навигации
  window.webContents.on('swipe', (event, direction) => {
    const actions = {
      'left': 'navigate:back',
      'right': 'navigate:forward',
      'up': 'show:settings',
      'down': 'show:logs'
    };
    
    if (actions[direction]) {
      window.webContents.send('gesture:swipe', {
        action: actions[direction],
        direction
      });
    }
  });

  // Force Touch для контекстных меню
  ipcMain.on('force-touch', (event, data) => {
    if (data.pressure > 0.8) {
      window.webContents.send('gesture:force-touch', {
        x: data.x,
        y: data.y,
        pressure: data.pressure
      });
    }
  });
}
```

#### 2.3.2 Native Menu Integration

```typescript
// electron/native/menu.ts
import { Menu, MenuItem, app, BrowserWindow } from 'electron';

export function setupNativeMenu(window: BrowserWindow) {
  const template = [
    {
      label: 'Rush Royale Bot',
      submenu: [
        {
          label: 'О программе',
          click: () => window.webContents.send('menu:about')
        },
        { type: 'separator' },
        {
          label: 'Настройки...',
          accelerator: 'Cmd+,',
          click: () => window.webContents.send('menu:preferences')
        },
        { type: 'separator' },
        {
          label: 'Скрыть Rush Royale Bot',
          accelerator: 'Cmd+H',
          role: 'hide'
        },
        {
          label: 'Выйти',
          accelerator: 'Cmd+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Бот',
      submenu: [
        {
          label: 'Запустить бота',
          accelerator: 'Cmd+R',
          click: () => window.webContents.send('bot:start')
        },
        {
          label: 'Остановить бота',
          accelerator: 'Cmd+S',
          click: () => window.webContents.send('bot:stop')
        },
        { type: 'separator' },
        {
          label: 'Выйти из игры',
          accelerator: 'Cmd+Shift+Q',
          click: () => window.webContents.send('bot:quit-game')
        }
      ]
    },
    {
      label: 'Устройства',
      submenu: [
        {
          label: 'Сканировать устройства',
          accelerator: 'Cmd+D',
          click: () => window.webContents.send('devices:scan')
        },
        {
          label: 'Настройки ADB',
          click: () => window.webContents.send('devices:adb-settings')
        }
      ]
    },
    {
      label: 'Вид',
      submenu: [
        {
          label: 'Полноэкранный режим',
          accelerator: 'Ctrl+Cmd+F',
          role: 'togglefullscreen'
        },
        { type: 'separator' },
        {
          label: 'Показать инструменты разработчика',
          accelerator: 'Alt+Cmd+I',
          click: () => window.webContents.toggleDevTools()
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}
```

### 2.4 Apple Silicon Optimization

#### 2.4.1 Metal Performance Shaders Integration

```python
# backend/app/services/vision_service_macos.py
import cv2
import numpy as np
from typing import Optional, Tuple

try:
    # Попытка использовать Core Image для ускорения на Apple Silicon
    import objc
    from Foundation import NSBundle
    
    # Загрузка Core Image framework
    CoreImage = NSBundle.bundleWithPath_('/System/Library/Frameworks/CoreImage.framework')
    if CoreImage and CoreImage.load():
        CORE_IMAGE_AVAILABLE = True
    else:
        CORE_IMAGE_AVAILABLE = False
except ImportError:
    CORE_IMAGE_AVAILABLE = False

class AppleSiliconVisionService:
    """Оптимизированный сервис компьютерного зрения для Apple Silicon"""
    
    def __init__(self):
        self.use_metal = CORE_IMAGE_AVAILABLE
        self.setup_optimization()
    
    def setup_optimization(self):
        """Настройка оптимизаций для Apple Silicon"""
        if self.use_metal:
            # Настройка Metal Performance Shaders
            cv2.setUseOptimized(True)
            cv2.setNumThreads(0)  # Автоматическое определение количества ядер
    
    def process_screenshot_optimized(self, image_path: str) -> np.ndarray:
        """Оптимизированная обработка скриншота"""
        if self.use_metal:
            return self._process_with_core_image(image_path)
        else:
            return self._process_with_opencv(image_path)
    
    def _process_with_core_image(self, image_path: str) -> np.ndarray:
        """Обработка с использованием Core Image (Metal acceleration)"""
        # Реализация через Core Image для максимальной производительности
        image = cv2.imread(image_path)
        # Дополнительные оптимизации для Apple Silicon
        return image
    
    def _process_with_opencv(self, image_path: str) -> np.ndarray:
        """Fallback обработка через OpenCV"""
        return cv2.imread(image_path)
```

#### 2.4.2 Memory Optimization for Unified Memory

```python
# backend/app/core/memory_manager.py
import psutil
import gc
from typing import Dict, Any

class UnifiedMemoryManager:
    """Менеджер памяти для оптимизации под Unified Memory Architecture"""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% использования памяти
        self.is_apple_silicon = self._detect_apple_silicon()
    
    def _detect_apple_silicon(self) -> bool:
        """Определение Apple Silicon"""
        try:
            import platform
            return platform.processor() == 'arm' and platform.system() == 'Darwin'
        except:
            return False
    
    def optimize_memory_usage(self):
        """Оптимизация использования памяти"""
        if self.is_apple_silicon:
            # Специальные оптимизации для Unified Memory
            self._optimize_for_unified_memory()
        
        # Общие оптимизации
        self._cleanup_memory()
    
    def _optimize_for_unified_memory(self):
        """Оптимизации для Unified Memory Architecture"""
        # Настройка буферов для эффективного использования
        # общей памяти CPU/GPU
        pass
    
    def _cleanup_memory(self):
        """Очистка памяти"""
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > self.memory_threshold * 100:
            gc.collect()
```

## 3. Testing & Quality Assurance

### 3.1 Testing Strategy

```typescript
// frontend/src/__tests__/Dashboard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Dashboard } from '../components/Dashboard/Dashboard';
import { BotStoreProvider } from '../store/botStore';

describe('Dashboard Component', () => {
  test('renders bot status correctly', () => {
    render(
      <BotStoreProvider>
        <Dashboard />
      </BotStoreProvider>
    );
    
    expect(screen.getByText('Rush Royale Bot')).toBeInTheDocument();
  });
  
  test('handles bot start/stop actions', () => {
    const { getByTestId } = render(
      <BotStoreProvider>
        <Dashboard />
      </BotStoreProvider>
    );
    
    const startButton = getByTestId('start-bot-button');
    fireEvent.click(startButton);
    
    // Проверка изменения состояния
    expect(getByTestId('bot-status')).toHaveTextContent('Starting...');
  });
});
```

### 3.2 Performance Benchmarks

```python
# backend/tests/performance/test_apple_silicon.py
import pytest
import time
import cv2
from app.services.vision_service_macos import AppleSiliconVisionService

class TestAppleSiliconPerformance:
    
    @pytest.fixture
    def vision_service(self):
        return AppleSiliconVisionService()
    
    def test_screenshot_processing_speed(self, vision_service):
        """Тест скорости обработки скриншотов"""
        test_image = 'test_assets/sample_screenshot.png'
        
        start_time = time.time()
        result = vision_service.process_screenshot_optimized(test_image)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # На Apple Silicon должно быть быстрее 50ms
        assert processing_time < 0.05, f"Processing took {processing_time}s, expected < 0.05s"
        assert result is not None
    
    def test_memory_usage_optimization(self, vision_service):
        """Тест оптимизации использования памяти"""
        import psutil
        
        initial_memory = psutil.virtual_memory().percent
        
        # Обработка множественных изображений
        for i in range(100):
            vision_service.process_screenshot_optimized('test_assets/sample_screenshot.png')
        
        final_memory = psutil.virtual_memory().percent
        memory_increase = final_memory - initial_memory
        
        # Увеличение памяти не должно превышать 10%
        assert memory_increase < 10, f"Memory increased by {memory_increase}%, expected < 10%"
```

## 4. Deployment & Distribution

### 4.1 Build Configuration

```json
// package.json
{
  "name": "rush-royale-bot-macos",
  "version": "2.0.0",
  "description": "Rush Royale Bot для macOS с React интерфейсом",
  "main": "dist/electron/main.js",
  "scripts": {
    "dev": "concurrently \"npm run dev:frontend\" \"npm run dev:backend\" \"npm run dev:electron\"",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && python -m uvicorn app.main:app --reload --port 8000",
    "dev:electron": "electron .",
    "build": "npm run build:frontend && npm run build:backend && npm run build:electron",
    "build:frontend": "cd frontend && npm run build",
    "build:backend": "cd backend && pyinstaller --onefile main.py",
    "build:electron": "electron-builder",
    "dist": "npm run build && electron-builder --publish=never",
    "dist:mas": "npm run build && electron-builder --mac --publish=never"
  },
  "build": {
    "appId": "com.skvorikovcode.rush-royale-bot",
    "productName": "Rush Royale Bot",
    "directories": {
      "output": "dist"
    },
    "mac": {
      "category": "public.app-category.games",
      "target": [
        {
          "target": "dmg",
          "arch": ["arm64", "x64"]
        },
        {
          "target": "mas",
          "arch": ["arm64", "x64"]
        }
      ],
      "icon": "build/icons/icon.icns",
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist",
      "hardenedRuntime": true,
      "notarize": {
        "teamId": "YOUR_TEAM_ID"
      }
    },
    "dmg": {
      "title": "Rush Royale Bot ${version}",
      "icon": "build/icons/icon.icns",
      "background": "build/background.png",
      "contents": [
        {
          "x": 130,
          "y": 220
        },
        {
          "x": 410,
          "y": 220,
          "type": "link",
          "path": "/Applications"
        }
      ]
    }
  }
}
```

### 4.2 Code Signing & Notarization

```bash
#!/bin/bash
# build/scripts/sign_and_notarize.sh

set -e

echo "🔐 Подписание приложения для macOS..."

# Подписание приложения
codesign --force --deep --sign "Developer ID Application: Your Name (TEAM_ID)" \
  --options runtime \
  --entitlements build/entitlements.mac.plist \
  "dist/mac/Rush Royale Bot.app"

echo "✅ Приложение подписано"

# Создание DMG
electron-builder --mac dmg

echo "📦 DMG создан"

# Нотаризация
echo "🔍 Отправка на нотаризацию..."
xcrun notarytool submit "dist/Rush Royale Bot-2.0.0.dmg" \
  --apple-id "your-apple-id@example.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

echo "✅ Нотаризация завершена"

# Прикрепление билета нотаризации
xcrun stapler staple "dist/Rush Royale Bot-2.0.0.dmg"

echo "🎉 Приложение готово к распространению!"
```

Этот план обеспечивает полную миграцию Rush Royale Bot на современную архитектуру с React интерфейсом и глубокой интеграцией с macOS, включая все требуемые нативные функции и оптимизации для Apple Silicon.