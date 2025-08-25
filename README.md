# Rush Royale Bot - macOS Edition

Современное Electron + React приложение для автоматизации игры Rush Royale на macOS.

## 🚀 Быстрый старт

### Требования

- **Node.js** 18+ (рекомендуется 20+)
- **Python** 3.8+ для backend
- **Android Debug Bridge (ADB)** для подключения к Android устройствам
- **macOS** 10.15+ (Catalina или новее)

### Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd Rush-Royale-Bot
   ```

2. **Установите Node.js зависимости:**
   ```bash
   pnpm install
   # или
   npm install
   ```

3. **Установите Python зависимости:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. **Установите ADB (если не установлен):**
   ```bash
   brew install android-platform-tools
   ```

### Запуск в режиме разработки

1. **Запустите все сервисы одновременно:**
   ```bash
   pnpm dev
   ```

   Или запустите каждый сервис отдельно:

2. **Frontend (React + Vite):**
   ```bash
   pnpm dev:frontend
   ```

3. **Backend (Python FastAPI):**
   ```bash
   pnpm dev:backend
   ```

4. **Electron приложение:**
   ```bash
   pnpm dev:electron
   ```

### Сборка для продакшена

1. **Сборка всего проекта:**
   ```bash
   pnpm build
   ```

2. **Создание macOS приложения:**
   ```bash
   pnpm dist
   ```

3. **Создание DMG для распространения:**
   ```bash
   pnpm dist:mac
   ```

## 📁 Структура проекта

```
Rush-Royale-Bot/
├── frontend/                 # React приложение
│   ├── src/
│   │   ├── components/      # React компоненты
│   │   ├── pages/          # Страницы приложения
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Утилиты и библиотеки
│   │   └── assets/         # Статические ресурсы
│   └── index.html
├── electron/                # Electron главный процесс
│   ├── main.ts            # Главный файл Electron
│   └── preload.ts         # Preload скрипт
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/           # API роуты
│   │   ├── core/          # Основная логика бота
│   │   ├── services/      # Сервисы (устройства, и т.д.)
│   │   └── main.py        # FastAPI приложение
│   ├── requirements.txt
│   └── start.py
├── shared/                  # Общие типы и константы
│   ├── types.ts
│   └── constants.ts
├── build/                   # Ресурсы для сборки
│   └── icons/
└── dist/                    # Собранные файлы
```

## 🔧 Конфигурация

### Настройка ADB

1. Включите "Отладку по USB" на Android устройстве
2. Подключите устройство к Mac через USB
3. Разрешите отладку при появлении диалога
4. Проверьте подключение:
   ```bash
   adb devices
   ```

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Backend
HOST=127.0.0.1
PORT=8000
RELOAD=true

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## 🎮 Использование

1. **Запустите приложение**
2. **Подключите Android устройство** через USB
3. **Просканируйте устройства** в разделе "Devices"
4. **Настройте бота** в разделе "Bot Settings"
5. **Запустите сессию бота** для выбранного устройства

## 🛠 Разработка

### Доступные команды

```bash
# Разработка
pnpm dev                    # Запуск всех сервисов
pnpm dev:frontend          # Только frontend
pnpm dev:backend           # Только backend
pnpm dev:electron          # Только Electron

# Сборка
pnpm build                 # Сборка всего проекта
pnpm build:frontend        # Сборка frontend
pnpm build:electron        # Сборка Electron

# Дистрибуция
pnpm dist                  # Создание приложения
pnpm dist:mac              # macOS DMG
pnpm dist:mas              # Mac App Store

# Утилиты
pnpm lint                  # Проверка кода
pnpm type-check            # Проверка типов
pnpm clean                 # Очистка
```

### Архитектура

- **Frontend**: React 18 + TypeScript + Tailwind CSS + Zustand
- **Backend**: Python FastAPI + WebSockets + OpenCV
- **Desktop**: Electron 28 с нативной интеграцией macOS
- **Коммуникация**: REST API + WebSockets для real-time обновлений

### Особенности macOS

- **Нативное меню** в строке меню macOS
- **Жесты трекпада** для управления
- **Уведомления** через Notification Center
- **Интеграция с Dock** и системным треем
- **Автоматические обновления** через electron-updater

## 🐛 Отладка

### Логи

- **Frontend**: Консоль браузера в DevTools
- **Backend**: Терминал с запущенным FastAPI
- **Electron**: Главный процесс в терминале

### Частые проблемы

1. **ADB не найден**: Установите Android Platform Tools
2. **Устройство не подключается**: Проверьте USB отладку
3. **Backend не запускается**: Проверьте Python зависимости
4. **Electron не собирается**: Очистите node_modules и переустановите

## 📝 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

Для вопросов и поддержки создайте Issue в репозитории.