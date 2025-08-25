// Общие константы для всего приложения

// API endpoints
export const API_ENDPOINTS = {
  BASE_URL: 'http://localhost:8000',
  WEBSOCKET_URL: 'ws://localhost:8000/ws',
  
  // Bot endpoints
  BOT: {
    SESSIONS: '/api/bot/sessions',
    SESSION: (id: string) => `/api/bot/sessions/${id}`,
    START: (id: string) => `/api/bot/sessions/${id}/start`,
    STOP: (id: string) => `/api/bot/sessions/${id}/stop`,
    PAUSE: (id: string) => `/api/bot/sessions/${id}/pause`,
    RESUME: (id: string) => `/api/bot/sessions/${id}/resume`,
  },
  
  // Device endpoints
  DEVICES: {
    SCAN: '/api/devices/scan',
    LIST: '/api/devices',
    DEVICE: (id: string) => `/api/devices/${id}`,
    REFRESH: (id: string) => `/api/devices/${id}/refresh`,
    SCREENSHOT: (id: string) => `/api/devices/${id}/screenshot`,
    TAP: (id: string) => `/api/devices/${id}/tap`,
    SWIPE: (id: string) => `/api/devices/${id}/swipe`,
    ADB_STATUS: '/api/devices/adb/status',
  },
  
  // Health check
  HEALTH: '/health',
} as const;

// Electron IPC channels
export const IPC_CHANNELS = {
  // App events
  APP_VERSION: 'get-app-version',
  APP_PLATFORM: 'get-platform',
  
  // Menu events
  MENU_ABOUT: 'menu:about',
  MENU_PREFERENCES: 'menu:preferences',
  MENU_BOT_START: 'bot:start',
  MENU_BOT_STOP: 'bot:stop',
  MENU_BOT_QUIT: 'bot:quit-game',
  MENU_DEVICES_SCAN: 'devices:scan',
  MENU_DEVICES_ADB: 'devices:adb-settings',
  
  // Gesture events
  GESTURE_ZOOM: 'gesture:zoom',
  GESTURE_SWIPE: 'gesture:swipe',
  GESTURE_FORCE_TOUCH: 'gesture:force-touch',
  
  // Notifications
  SHOW_NOTIFICATION: 'show-notification',
  
  // File operations
  SELECT_FILE: 'select-file',
  SAVE_FILE: 'save-file',
} as const;

// Game constants
export const GAME_CONSTANTS = {
  // Размеры игрового поля
  BOARD_SIZE: {
    WIDTH: 4,
    HEIGHT: 3,
  },
  
  // Классы юнитов
  UNIT_CLASSES: {
    DAMAGE: 'damage',
    SUPPORT: 'support',
    MERGE: 'merge',
  } as const,
  
  // Редкость юнитов
  UNIT_RARITY: {
    COMMON: 'common',
    RARE: 'rare',
    EPIC: 'epic',
    LEGENDARY: 'legendary',
  } as const,
  
  // Максимальные уровни
  MAX_LEVELS: {
    UNIT: 15,
    COOP: 20,
  },
  
  // Время ожидания (мс)
  TIMEOUTS: {
    GAME_START: 5000,
    UNIT_SPAWN: 1000,
    MERGE_DELAY: 500,
    SCREENSHOT_INTERVAL: 100,
  },
} as const;

// UI константы
export const UI_CONSTANTS = {
  // Размеры окна
  WINDOW_SIZE: {
    MIN_WIDTH: 1200,
    MIN_HEIGHT: 800,
    DEFAULT_WIDTH: 1400,
    DEFAULT_HEIGHT: 900,
  },
  
  // Анимации
  ANIMATIONS: {
    DURATION_FAST: 150,
    DURATION_NORMAL: 300,
    DURATION_SLOW: 500,
  },
  
  // Z-index слои
  Z_INDEX: {
    MODAL: 1000,
    TOOLTIP: 1100,
    NOTIFICATION: 1200,
    LOADING: 1300,
  },
  
  // Breakpoints
  BREAKPOINTS: {
    SM: 640,
    MD: 768,
    LG: 1024,
    XL: 1280,
  },
} as const;

// Цвета статусов
export const STATUS_COLORS = {
  SUCCESS: '#10B981',
  WARNING: '#F59E0B',
  ERROR: '#EF4444',
  INFO: '#3B82F6',
  IDLE: '#6B7280',
  RUNNING: '#10B981',
  PAUSED: '#F59E0B',
  OFFLINE: '#6B7280',
} as const;

// Настройки по умолчанию
export const DEFAULT_CONFIG = {
  BOT: {
    auto_start: false,
    auto_upgrade: true,
    target_coop: 10,
    use_joker: true,
    pause_on_defeat: true,
    max_games: 0, // 0 = unlimited
  },
  
  APP: {
    theme: 'system' as const,
    language: 'en' as const,
    auto_scan_devices: true,
    notifications_enabled: true,
    sound_enabled: true,
    minimize_to_tray: true,
    start_minimized: false,
  },
  
  DEVICE: {
    screenshot_quality: 80,
    tap_delay: 50,
    swipe_duration: 300,
  },
} as const;

// Пути к ресурсам
export const RESOURCE_PATHS = {
  ICONS: {
    APP: '/icons/app-icon.png',
    TRAY: '/icons/tray-icon.png',
    UNITS: '/icons/units',
    BUTTONS: '/icons/buttons',
  },
  
  TEMPLATES: {
    GAME_UI: '/templates/game_ui',
    UNITS: '/templates/units',
    BUTTONS: '/templates/buttons',
  },
  
  SOUNDS: {
    NOTIFICATION: '/sounds/notification.mp3',
    SUCCESS: '/sounds/success.mp3',
    ERROR: '/sounds/error.mp3',
  },
} as const;

// Регулярные выражения
export const REGEX_PATTERNS = {
  DEVICE_ID: /^[a-zA-Z0-9]+$/,
  IP_ADDRESS: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  VERSION: /^\d+\.\d+\.\d+$/,
} as const;

// Сообщения об ошибках
export const ERROR_MESSAGES = {
  DEVICE_NOT_FOUND: 'Device not found',
  DEVICE_NOT_CONNECTED: 'Device not connected',
  SESSION_NOT_FOUND: 'Bot session not found',
  ADB_NOT_AVAILABLE: 'ADB is not available',
  SCREENSHOT_FAILED: 'Failed to take screenshot',
  NETWORK_ERROR: 'Network connection error',
  INVALID_CONFIG: 'Invalid configuration',
  PERMISSION_DENIED: 'Permission denied',
} as const;

// Успешные сообщения
export const SUCCESS_MESSAGES = {
  SESSION_CREATED: 'Bot session created successfully',
  SESSION_STARTED: 'Bot session started',
  SESSION_STOPPED: 'Bot session stopped',
  SESSION_PAUSED: 'Bot session paused',
  SESSION_RESUMED: 'Bot session resumed',
  DEVICE_CONNECTED: 'Device connected successfully',
  CONFIG_SAVED: 'Configuration saved',
} as const;