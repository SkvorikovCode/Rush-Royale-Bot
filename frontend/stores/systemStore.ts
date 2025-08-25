import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws/system';

export interface SystemPreferences {
  theme: 'light' | 'dark' | 'auto';
  accentColor: string;
  reducedMotion: boolean;
  highContrast: boolean;
  transparency: boolean;
}

export interface PowerInfo {
  batteryLevel: number;
  isCharging: boolean;
  timeRemaining: number; // in minutes
  powerSource: 'battery' | 'ac' | 'ups';
  thermalState: 'nominal' | 'fair' | 'serious' | 'critical';
}

export interface DisplayInfo {
  id: string;
  name: string;
  bounds: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  workArea: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  scaleFactor: number;
  rotation: number;
  isPrimary: boolean;
  isInternal: boolean;
  colorSpace: string;
  colorDepth: number;
}

export interface PerformanceMetrics {
  cpuUsage: number;
  memoryUsage: {
    used: number;
    total: number;
    percentage: number;
  };
  diskUsage: {
    used: number;
    total: number;
    percentage: number;
  };
  networkActivity: {
    bytesReceived: number;
    bytesSent: number;
    packetsReceived: number;
    packetsSent: number;
  };
  temperature: {
    cpu: number;
    gpu: number;
  };
  fanSpeed: number;
}

export interface SystemInfo {
  platform: string;
  arch: string;
  version: string;
  hostname: string;
  uptime: number;
  totalMemory: number;
  cpuModel: string;
  cpuCores: number;
  isAppleSilicon: boolean;
  macOSVersion: string;
  buildNumber: string;
}

export interface NotificationSettings {
  enabled: boolean;
  sound: boolean;
  play_sound: boolean;
  badge: boolean;
  show_badge: boolean;
  banner: boolean;
  show_banner: boolean;
  alert: boolean;
  criticalAlerts: boolean;
}

export interface SystemState {
  // System Information
  systemInfo: SystemInfo | null;
  preferences: SystemPreferences;
  powerInfo: PowerInfo | null;
  displays: DisplayInfo[];
  performance: PerformanceMetrics | null;
  
  // Notifications
  notificationSettings: NotificationSettings;
  notifications: Array<{
    id: string;
    title: string;
    body: string;
    timestamp: Date;
    type: 'info' | 'warning' | 'error' | 'success';
    read: boolean;
  }>;
  
  // Window Management
  windowState: {
    isMaximized: boolean;
    isMinimized: boolean;
    isFullscreen: boolean;
    bounds: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  };
  
  // Connectivity
  networkStatus: {
    isOnline: boolean;
    connectionType: 'wifi' | 'ethernet' | 'cellular' | 'unknown';
    signalStrength: number;
  };
  
  // WebSocket connection
  ws: WebSocket | null;
  
  // Error state
  error: string | null;
  
  // Actions
  initializeSystem: () => Promise<void>;
  updatePreferences: (preferences: Partial<SystemPreferences>) => Promise<void>;
  refreshSystemInfo: () => Promise<void>;
  refreshPerformanceMetrics: () => Promise<void>;
  showNotification: (title: string, body: string, type?: string) => Promise<void>;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  updateNotificationSettings: (settings: Partial<NotificationSettings>) => Promise<void>;
  minimizeWindow: () => Promise<void>;
  maximizeWindow: () => Promise<void>;
  closeWindow: () => Promise<void>;
  setWindowBounds: (bounds: Partial<SystemState['windowState']['bounds']>) => Promise<void>;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const defaultPreferences: SystemPreferences = {
  theme: 'auto',
  accentColor: '#007AFF',
  reducedMotion: false,
  highContrast: false,
  transparency: true
};

const defaultNotificationSettings: NotificationSettings = {
  enabled: true,
  sound: true,
  play_sound: true,
  badge: true,
  show_badge: true,
  banner: true,
  show_banner: true,
  alert: false,
  criticalAlerts: true
};

export const useSystemStore = create<SystemState>()(devtools(
  (set, get) => ({
    // Initial state
    systemInfo: null,
    preferences: defaultPreferences,
    powerInfo: null,
    displays: [],
    performance: null,
    notificationSettings: defaultNotificationSettings,
    notifications: [],
    windowState: {
      isMaximized: false,
      isMinimized: false,
      isFullscreen: false,
      bounds: { x: 0, y: 0, width: 1200, height: 800 }
    },
    networkStatus: {
      isOnline: true,
      connectionType: 'unknown',
      signalStrength: 0
    },
    ws: null,
    error: null,

    // Actions
    initializeSystem: async () => {
      try {
        // Get initial system information from API
        const [systemInfoRes, preferencesRes, powerInfoRes, displaysRes, performanceRes] = await Promise.all([
          fetch(`${API_BASE_URL}/system/info`),
          fetch(`${API_BASE_URL}/system/preferences`),
          fetch(`${API_BASE_URL}/system/power`),
          fetch(`${API_BASE_URL}/system/displays`),
          fetch(`${API_BASE_URL}/system/performance`)
        ]);

        const [systemInfo, preferences, powerInfo, displays, performance] = await Promise.all([
          systemInfoRes.ok ? systemInfoRes.json() : null,
          preferencesRes.ok ? preferencesRes.json() : {},
          powerInfoRes.ok ? powerInfoRes.json() : null,
          displaysRes.ok ? displaysRes.json() : [],
          performanceRes.ok ? performanceRes.json() : null
        ]);

        set({
          systemInfo,
          preferences: { ...defaultPreferences, ...preferences },
          powerInfo,
          displays,
          performance,
          error: null
        });

        // Connect WebSocket for real-time updates
        get().connectWebSocket();

        // Start performance monitoring
        setInterval(() => {
          get().refreshPerformanceMetrics();
        }, 5000); // Update every 5 seconds
      } catch (error) {
        console.error('Failed to initialize system:', error);
        set({ error: 'Failed to initialize system' });
      }
    },

    updatePreferences: async (newPreferences) => {
      try {
        const updatedPreferences = { ...get().preferences, ...newPreferences };
        
        const response = await fetch(`${API_BASE_URL}/system/preferences`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updatedPreferences)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({ preferences: updatedPreferences, error: null });
      } catch (error) {
        console.error('Failed to update preferences:', error);
        set({ error: 'Failed to update preferences' });
      }
    },

    refreshSystemInfo: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/system/info`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const systemInfo = await response.json();
        set({ systemInfo, error: null });
      } catch (error) {
        console.error('Failed to refresh system info:', error);
        set({ error: 'Failed to refresh system info' });
      }
    },

    refreshPerformanceMetrics: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/system/performance`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const performance = await response.json();
        set({ performance, error: null });
      } catch (error) {
        console.error('Failed to refresh performance metrics:', error);
        // Don't set error for performance metrics as they update frequently
      }
    },

    showNotification: async (title, body, type = 'info') => {
      try {
        if (get().notificationSettings.enabled) {
          const response = await fetch(`${API_BASE_URL}/system/notifications`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              title,
              body,
              type,
              sound: get().notificationSettings.sound
            })
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          // Add to local notifications list
          const newNotification = {
            id: Date.now().toString(),
            title,
            body,
            timestamp: new Date(),
            type: type as 'info' | 'warning' | 'error' | 'success',
            read: false
          };
          
          set({
            notifications: [newNotification, ...get().notifications].slice(0, 100)
          });
        }
      } catch (error) {
        console.error('Failed to show notification:', error);
      }
    },

    markNotificationRead: (id) => {
      set({
        notifications: get().notifications.map(n => 
          n.id === id ? { ...n, read: true } : n
        )
      });
    },

    clearNotifications: () => {
      set({ notifications: [] });
    },

    updateNotificationSettings: async (newSettings) => {
      try {
        const updatedSettings = { ...get().notificationSettings, ...newSettings };
        
        const response = await fetch(`${API_BASE_URL}/system/notification-settings`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updatedSettings)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({ notificationSettings: updatedSettings, error: null });
      } catch (error) {
        console.error('Failed to update notification settings:', error);
        set({ error: 'Failed to update notification settings' });
      }
    },

    minimizeWindow: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/system/window/minimize`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } catch (error) {
        console.error('Failed to minimize window:', error);
      }
    },

    maximizeWindow: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/system/window/maximize`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } catch (error) {
        console.error('Failed to maximize window:', error);
      }
    },

    closeWindow: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/system/window/close`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } catch (error) {
        console.error('Failed to close window:', error);
      }
    },

    setWindowBounds: async (bounds) => {
      try {
        const newBounds = { ...get().windowState.bounds, ...bounds };
        
        const response = await fetch(`${API_BASE_URL}/system/window/bounds`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newBounds)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({
          windowState: { ...get().windowState, bounds: newBounds }
        });
      } catch (error) {
        console.error('Failed to set window bounds:', error);
      }
    },

    connectWebSocket: () => {
      try {
        const ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
          console.log('System WebSocket connected');
          set({ ws });
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
              case 'theme_changed':
                set({
                  preferences: { ...get().preferences, theme: data.theme }
                });
                break;
                
              case 'power_changed':
                set({ powerInfo: data.power_info });
                break;
                
              case 'display_changed':
                set({ displays: data.displays });
                break;
                
              case 'performance_update':
                set({ performance: data.performance });
                break;
                
              case 'notification':
                const newNotification = {
                  id: Date.now().toString(),
                  title: data.title,
                  body: data.body,
                  timestamp: new Date(),
                  type: data.type || 'info',
                  read: false
                };
                
                set({
                  notifications: [newNotification, ...get().notifications].slice(0, 100)
                });
                break;
                
              case 'window_state_changed':
                set({ windowState: { ...get().windowState, ...data.window_state } });
                break;
                
              case 'network_changed':
                set({ networkStatus: data.network_status });
                break;
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        ws.onerror = (error) => {
          console.error('System WebSocket error:', error);
        };
        
        ws.onclose = () => {
          console.log('System WebSocket disconnected');
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
    name: 'system-store'
  }
));