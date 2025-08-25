// Общие типы для всего приложения

// Типы устройств
export interface AndroidDevice {
  id: string;
  status: 'device' | 'offline' | 'unauthorized';
  model?: string;
  android_version?: string;
  resolution?: string;
  is_connected: boolean;
  last_seen: string;
}

// Типы сессий бота
export interface BotSession {
  id: string;
  device_id: string;
  status: 'idle' | 'running' | 'paused' | 'error';
  created_at: string;
  last_action?: string;
  stats: BotStats;
  config: BotConfig;
}

export interface BotStats {
  games_played: number;
  wins: number;
  losses: number;
  runtime: number;
}

export interface BotConfig {
  auto_start?: boolean;
  auto_upgrade?: boolean;
  target_coop?: number;
  use_joker?: boolean;
  pause_on_defeat?: boolean;
  max_games?: number;
  [key: string]: any;
}

// Типы API ответов
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface DevicesResponse {
  devices: AndroidDevice[];
  total: number;
  connected: number;
}

export interface SessionsResponse {
  sessions: Record<string, BotSession>;
  total: number;
}

// WebSocket типы
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: string;
}

export interface BotStateMessage extends WebSocketMessage {
  type: 'bot_state';
  data: {
    total_sessions: number;
    active_sessions: number;
    sessions: Record<string, BotSession>;
  };
}

// Типы координат и жестов
export interface Coordinates {
  x: number;
  y: number;
}

export interface SwipeGesture {
  start: Coordinates;
  end: Coordinates;
  duration?: number;
}

// Типы для macOS интеграции
export interface MacOSGesture {
  type: 'zoom' | 'swipe' | 'force-touch';
  data: any;
}

export interface NotificationData {
  title: string;
  body: string;
  icon?: string;
}

// Типы меню действий
export type MenuAction = 
  | 'about'
  | 'preferences'
  | 'bot:start'
  | 'bot:stop'
  | 'bot:quit-game'
  | 'devices:scan'
  | 'devices:adb-settings';

// Типы конфигурации приложения
export interface AppConfig {
  theme: 'light' | 'dark' | 'system';
  language: 'en' | 'ru';
  auto_scan_devices: boolean;
  notifications_enabled: boolean;
  sound_enabled: boolean;
  minimize_to_tray: boolean;
  start_minimized: boolean;
}

// Типы для игровой логики
export interface GameUnit {
  id: string;
  name: string;
  class: 'damage' | 'support' | 'merge';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  mana_cost: number;
  icon_path: string;
}

export interface GameBoard {
  width: number;
  height: number;
  cells: GameCell[][];
}

export interface GameCell {
  x: number;
  y: number;
  unit?: GameUnit;
  level?: number;
  is_empty: boolean;
}

// Типы для компьютерного зрения
export interface ImageTemplate {
  name: string;
  path: string;
  threshold: number;
  region?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface MatchResult {
  found: boolean;
  confidence: number;
  location?: Coordinates;
  template: string;
}

// Типы ошибок
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

// Типы логирования
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  source?: string;
  data?: any;
}