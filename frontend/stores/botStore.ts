import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface BotConfig {
  auto_start: boolean;
  game_mode: 'coop' | 'pvp' | 'tournament';
  difficulty: 'easy' | 'medium' | 'hard';
  max_games: number;
  pause_between_games: number;
  enable_notifications: boolean;
  auto_restart: boolean;
  stop_on_error: boolean;
  pve: boolean;
  floor: number;
  mana_level: number[];
  dps_unit: string;
  require_shaman: boolean;
  max_loops: number;
}

export interface BotLog {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  details?: any;
}

export interface CurrentGame {
  game_id: string | null;
  start_time: string | null;
  mode: string | null;
  opponent: string | null;
  round: number;
  score: number;
}

export interface BotStats {
  gamesPlayed: number;
  gamesWon: number;
  gamesLost: number;
  totalPlayTime: number;
  averageGameTime: number;
  winRate: number;
  coinsEarned: number;
  cardsEarned: number;
}

export interface BotState {
  // Status
  status: 'stopped' | 'running' | 'paused' | 'error';
  isRunning: boolean;
  isPaused: boolean;
  error: string | null;
  
  // Configuration
  config: BotConfig;
  
  // Statistics
  stats: BotStats;
  
  // Current game info
  currentGame: CurrentGame;
  
  // Logs
  logs: BotLog[];
  
  // WebSocket connection
  ws: WebSocket | null;
  
  // Actions
  initializeBot: () => Promise<void>;
  startBot: (customConfig?: Partial<BotConfig>) => Promise<void>;
  stopBot: () => Promise<void>;
  togglePause: () => Promise<void>;
  quickStart: () => Promise<void>;
  quitGame: () => Promise<void>;
  updateConfig: (config: Partial<BotConfig>) => Promise<void>;
  addLog: (level: string, message: string, details?: any) => void;
  clearLogs: () => Promise<void>;
  resetStats: () => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const defaultConfig: BotConfig = {
  auto_start: false,
  game_mode: 'coop',
  difficulty: 'medium',
  max_games: 10,
  pause_between_games: 5,
  enable_notifications: true,
  auto_restart: false,
  stop_on_error: true,
  pve: true,
  floor: 1,
  mana_level: [1, 1, 1, 1, 1],
  dps_unit: 'demon_hunter',
  require_shaman: false,
  max_loops: 100
};

const API_BASE_URL = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/api/bot/ws';

const defaultStats: BotStats = {
  gamesPlayed: 0,
  gamesWon: 0,
  gamesLost: 0,
  totalPlayTime: 0,
  averageGameTime: 0,
  winRate: 0,
  coinsEarned: 0,
  cardsEarned: 0
};

export const useBotStore = create<BotState>()(devtools(
  (set, get) => ({
    // Initial state
    status: 'stopped',
    isRunning: false,
    isPaused: false,
    error: null,
    config: defaultConfig,
    stats: defaultStats,
    currentGame: {
      game_id: null,
      start_time: null,
      mode: null,
      opponent: null,
      round: 0,
      score: 0
    },
    logs: [],
    ws: null,

    // Actions
    // Initialize bot and set up WebSocket connection
    initializeBot: async () => {
      try {
        // Get initial bot status
        const response = await fetch(`${API_BASE_URL}/bot/status`);
        const status = await response.json();
        
        set({ 
          status: status.is_running ? (status.is_paused ? 'paused' : 'running') : 'stopped',
          isRunning: status.is_running,
          isPaused: status.is_paused,
          error: status.error
        });

        // Connect WebSocket for real-time updates
        get().connectWebSocket();

      } catch (error) {
        console.error('Failed to initialize bot:', error);
        set({ error: 'Failed to initialize bot connection' });
      }
    },

    startBot: async (customConfig) => {
      try {
        const config = { ...get().config, ...customConfig };
        
        const response = await fetch(`${API_BASE_URL}/bot/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(config),
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({
          status: 'running',
          isRunning: true,
          isPaused: false,
          error: null,
          config
        });
        
        get().addLog('info', 'Bot started successfully', { config });
      } catch (error) {
        console.error('Failed to start bot:', error);
        set({ error: 'Failed to start bot' });
        get().addLog('error', 'Failed to start bot', { error });
      }
    },

    stopBot: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/bot/stop`, {
          method: 'POST',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({ 
          status: 'stopped',
          isRunning: false,
          isPaused: false,
          error: null
        });
        
        get().addLog('info', 'Bot stopped successfully');
      } catch (error) {
        console.error('Failed to stop bot:', error);
        set({ error: 'Failed to stop bot' });
        get().addLog('error', 'Failed to stop bot', { error });
      }
    },

    togglePause: async () => {
      try {
        const { isPaused } = get();
        
        const endpoint = isPaused ? 'resume' : 'pause';
        const response = await fetch(`${API_BASE_URL}/bot/${endpoint}`, {
          method: 'POST',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        if (isPaused) {
          set({ status: 'running', isPaused: false });
          get().addLog('info', 'Bot resumed');
        } else {
          set({ status: 'paused', isPaused: true });
          get().addLog('info', 'Bot paused');
        }
      } catch (error) {
        console.error('Failed to toggle pause:', error);
        set({ error: 'Failed to toggle pause' });
        get().addLog('error', 'Failed to toggle pause', { error });
      }
    },

    quickStart: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/bot/quick-start`, {
          method: 'POST',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({ 
          status: 'running',
          isRunning: true,
          isPaused: false,
          error: null
        });
        
        get().addLog('info', 'Bot quick started');
      } catch (error) {
        console.error('Failed to quick start bot:', error);
        set({ error: 'Failed to quick start bot' });
        get().addLog('error', 'Failed to quick start bot', { error });
      }
    },

    quitGame: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/bot/quit-game`, {
          method: 'POST',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({
          currentGame: {
            game_id: null,
            start_time: null,
            mode: null,
            opponent: null,
            round: 0,
            score: 0
          }
        });
        
        get().addLog('info', 'Game quit successfully');
      } catch (error) {
        console.error('Failed to quit game:', error);
        set({ error: 'Failed to quit game' });
        get().addLog('error', 'Failed to quit game', { error });
      }
    },

    updateConfig: async (newConfig) => {
      try {
        const response = await fetch(`${API_BASE_URL}/bot/config`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newConfig),
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({
          config: { ...get().config, ...newConfig }
        });
        get().addLog('info', 'Bot configuration updated', { config: newConfig });
      } catch (error) {
        console.error('Failed to update config:', error);
        get().addLog('error', 'Failed to update configuration', { error });
      }
    },

    addLog: (level, message, details) => {
      const newLog: BotLog = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        level: level as 'info' | 'warning' | 'error' | 'debug',
        message,
        details
      };
      
      set({
        logs: [newLog, ...get().logs].slice(0, 1000) // Keep only last 1000 logs
      });
    },

    clearLogs: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/bot/logs`, {
          method: 'DELETE',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({ logs: [] });
      } catch (error) {
        console.error('Failed to clear logs:', error);
        set({ logs: [] }); // Clear locally anyway
      }
    },

    resetStats: () => {
      set({ stats: defaultStats });
      get().addLog('info', 'Statistics reset');
    },

    // WebSocket connection management
    connectWebSocket: () => {
      try {
        const ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          set({ ws });
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
              case 'status_update':
                set({
                  status: data.payload.is_running ? (data.payload.is_paused ? 'paused' : 'running') : 'stopped',
                  isRunning: data.payload.is_running,
                  isPaused: data.payload.is_paused,
                  error: data.payload.error
                });
                break;
                
              case 'stats_update':
                set({ stats: data.payload });
                break;
                
              case 'game_update':
                set({ currentGame: data.payload });
                break;
                
              case 'log':
                get().addLog(data.payload.level, data.payload.message, data.payload.details);
                break;
                
              default:
                console.log('Unknown WebSocket message type:', data.type);
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          get().addLog('error', 'WebSocket connection error');
        };
        
        ws.onclose = () => {
          console.log('WebSocket disconnected');
          set({ ws: null });
          
          // Attempt to reconnect after 5 seconds
          setTimeout(() => {
            if (!get().ws) {
              get().connectWebSocket();
            }
          }, 5000);
        };
        
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        get().addLog('error', 'Failed to establish WebSocket connection');
      }
    },

    disconnectWebSocket: () => {
      const { ws } = get();
      if (ws) {
        ws.close();
        set({ ws: null });
      }
    }
  }),
  {
    name: 'bot-store'
  }
));