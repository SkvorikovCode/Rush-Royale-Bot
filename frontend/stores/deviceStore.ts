import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws/devices';

export interface Device {
  id: string;
  name: string;
  model: string;
  androidVersion: string;
  resolution: {
    width: number;
    height: number;
  };
  dpi: number;
  status: 'connected' | 'disconnected' | 'unauthorized' | 'offline' | 'error';
  isEmulator: boolean;
  batteryLevel?: number;
  temperature?: number;
  cpuUsage?: number;
  memoryUsage?: number;
  cpuAbi?: string;
  totalMemory?: number;
  availableMemory?: number;
  connectionType?: string;
  lastSeen: Date;
  capabilities: {
    canScreenshot: boolean;
    canInput: boolean;
    canInstallApps: boolean;
    hasRushRoyale: boolean;
  };
}

export interface AdbStatus {
  isInstalled: boolean;
  version: string | null;
  isRunning: boolean;
  port: number;
}

export interface DeviceState {
  // Devices
  devices: Device[];
  selectedDevice: Device | null;
  
  // ADB Status
  adbStatus: AdbStatus;
  
  // Connection state
  isScanning: boolean;
  isConnecting: boolean;
  lastScanTime: Date | null;
  
  // WebSocket
  ws: WebSocket | null;
  
  // Errors
  error: string | null;
  
  // Logs
  logs: Array<{
    id: string;
    timestamp: Date;
    level: 'info' | 'warning' | 'error' | 'debug';
    message: string;
    deviceId?: string;
    details?: any;
  }>;
  
  // Actions
  initializeDevices: () => Promise<void>;
  scanDevices: () => Promise<void>;
  connectDevice: (deviceId: string) => Promise<void>;
  disconnectDevice: (deviceId: string) => Promise<void>;
  selectDevice: (device: Device | null) => void;
  restartAdb: () => Promise<void>;
  installApp: (deviceId: string, apkPath: string) => Promise<void>;
  takeScreenshot: (deviceId: string) => Promise<string>;
  sendInput: (deviceId: string, x: number, y: number, action: 'tap' | 'swipe') => Promise<void>;
  checkRushRoyale: (deviceId: string) => Promise<boolean>;
  getDeviceInfo: (deviceId: string) => Promise<Partial<Device>>;
  addLog: (level: string, message: string, deviceId?: string, details?: any) => void;
  clearLogs: () => Promise<void>;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const defaultAdbStatus: AdbStatus = {
  isInstalled: false,
  version: null,
  isRunning: false,
  port: 5037
};

export const useDeviceStore = create<DeviceState>()(devtools(
  (set, get) => ({
    // Initial state
    devices: [],
    selectedDevice: null,
    adbStatus: defaultAdbStatus,
    isScanning: false,
    isConnecting: false,
    lastScanTime: null,
    ws: null,
    error: null,
    logs: [],

    // Actions
    initializeDevices: async () => {
      try {
        // Check ADB status
        const adbResponse = await fetch(`${API_BASE_URL}/devices/adb/status`);
        const adbStatus = await adbResponse.json();
        set({ adbStatus });

        // Get initial device list
        const devicesResponse = await fetch(`${API_BASE_URL}/devices`);
        const devices = await devicesResponse.json();
        set({ devices });

        // Connect WebSocket for real-time updates
        get().connectWebSocket();

        get().addLog('info', 'Device manager initialized');
      } catch (error) {
        console.error('Failed to initialize devices:', error);
        set({ error: 'Failed to initialize device manager' });
        get().addLog('error', 'Failed to initialize device manager', undefined, { error });
      }
    },

    scanDevices: async () => {
      if (get().isScanning) return;
      
      try {
        set({ isScanning: true, error: null });
        
        const response = await fetch(`${API_BASE_URL}/devices/scan`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const devices = await response.json();
        
        set({
          devices,
          lastScanTime: new Date(),
          isScanning: false
        });
        
        get().addLog('info', `Device scan completed. Found ${devices.length} devices`);
      } catch (error) {
        console.error('Failed to scan devices:', error);
        set({ 
          error: 'Failed to scan devices',
          isScanning: false
        });
        get().addLog('error', 'Failed to scan devices', undefined, { error });
      }
    },

    connectDevice: async (deviceId) => {
      if (get().isConnecting) return;
      
      try {
        set({ isConnecting: true, error: null });
        
        const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/connect`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Update device status
        set({
          devices: get().devices.map(d => 
            d.id === deviceId ? { ...d, status: 'connected' } : d
          ),
          isConnecting: false
        });
        
        get().addLog('info', 'Device connected successfully', deviceId);
      } catch (error) {
        console.error('Failed to connect device:', error);
        set({ 
          error: 'Failed to connect device',
          isConnecting: false
        });
        get().addLog('error', 'Failed to connect device', deviceId, { error });
      }
    },

    disconnectDevice: async (deviceId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/disconnect`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({
          devices: get().devices.map(d => 
            d.id === deviceId ? { ...d, status: 'disconnected' } : d
          ),
          selectedDevice: get().selectedDevice?.id === deviceId ? null : get().selectedDevice
        });
        
        get().addLog('info', 'Device disconnected', deviceId);
      } catch (error) {
        console.error('Failed to disconnect device:', error);
        set({ error: 'Failed to disconnect device' });
        get().addLog('error', 'Failed to disconnect device', deviceId, { error });
      }
    },

    selectDevice: (device) => {
      set({ selectedDevice: device });
      if (device) {
        get().addLog('info', `Selected device: ${device.name}`, device.id);
      }
    },

    restartAdb: async () => {
      try {
        set({ error: null });
        
        const response = await fetch(`${API_BASE_URL}/devices/adb/restart`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Update ADB status
        const adbResponse = await fetch(`${API_BASE_URL}/devices/adb/status`);
        const adbStatus = await adbResponse.json();
        set({ adbStatus });
        
        // Rescan devices
        await get().scanDevices();
        
        get().addLog('info', 'ADB restarted successfully');
      } catch (error) {
        console.error('Failed to restart ADB:', error);
        set({ error: 'Failed to restart ADB' });
        get().addLog('error', 'Failed to restart ADB', undefined, { error });
      }
    },

    installApp: async (deviceId, apkPath) => {
      try {
        const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/install`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ apk_path: apkPath })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        get().addLog('info', 'App installed successfully', deviceId, { apkPath });
      } catch (error) {
        console.error('Failed to install app:', error);
        get().addLog('error', 'Failed to install app', deviceId, { error, apkPath });
        throw error;
      }
    },

    takeScreenshot: async (deviceId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/screenshot`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        const screenshotPath = result.screenshot_path;
        
        get().addLog('debug', 'Screenshot taken', deviceId, { path: screenshotPath });
        return screenshotPath;
      } catch (error) {
        console.error('Failed to take screenshot:', error);
        get().addLog('error', 'Failed to take screenshot', deviceId, { error });
        throw error;
      }
    },

    sendInput: async (deviceId, x, y, action) => {
      try {
        const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/input`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ x, y, action })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        get().addLog('debug', `Input sent: ${action} at (${x}, ${y})`, deviceId);
      } catch (error) {
        console.error('Failed to send input:', error);
        get().addLog('error', 'Failed to send input', deviceId, { error, x, y, action });
        throw error;
      }
    },

    checkRushRoyale: async (deviceId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/check-rush-royale`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        const hasRushRoyale = result.has_rush_royale;
        
        // Update device capabilities
        set({
          devices: get().devices.map(d => 
            d.id === deviceId 
              ? { ...d, capabilities: { ...d.capabilities, hasRushRoyale } }
              : d
          )
        });
        
        get().addLog('info', `Rush Royale ${hasRushRoyale ? 'found' : 'not found'}`, deviceId);
        return hasRushRoyale;
      } catch (error) {
        console.error('Failed to check Rush Royale:', error);
        get().addLog('error', 'Failed to check Rush Royale', deviceId, { error });
        return false;
      }
    },

    getDeviceInfo: async (deviceId) => {
      try {
        const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/info`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const deviceInfo = await response.json();
        
        // Update device with new info
        set({
          devices: get().devices.map(d => 
            d.id === deviceId ? { ...d, ...deviceInfo } : d
          )
        });
        
        return deviceInfo;
      } catch (error) {
        console.error('Failed to get device info:', error);
        get().addLog('error', 'Failed to get device info', deviceId, { error });
        return {};
      }
    },

    addLog: (level, message, deviceId, details) => {
      const newLog = {
        id: Date.now().toString(),
        timestamp: new Date(),
        level: level as 'info' | 'warning' | 'error' | 'debug',
        message,
        deviceId,
        details
      };
      
      set({
        logs: [newLog, ...get().logs].slice(0, 1000) // Keep only last 1000 logs
      });
    },

    clearLogs: async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/devices/logs`, {
          method: 'DELETE'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        set({ logs: [] });
      } catch (error) {
        console.error('Failed to clear logs:', error);
        get().addLog('error', 'Failed to clear logs', undefined, { error });
      }
    },

    connectWebSocket: () => {
      try {
        const ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
          console.log('Device WebSocket connected');
          set({ ws });
          get().addLog('info', 'WebSocket connected');
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
              case 'device_connected':
                set({
                  devices: [...get().devices.filter(d => d.id !== data.device.id), data.device]
                });
                get().addLog('info', `Device connected: ${data.device.name}`, data.device.id);
                break;
                
              case 'device_disconnected':
                set({
                  devices: get().devices.filter(d => d.id !== data.device_id),
                  selectedDevice: get().selectedDevice?.id === data.device_id ? null : get().selectedDevice
                });
                get().addLog('warning', 'Device disconnected', data.device_id);
                break;
                
              case 'device_status_changed':
                set({
                  devices: get().devices.map(d => 
                    d.id === data.device_id ? { ...d, status: data.status } : d
                  )
                });
                get().addLog('info', `Device status changed: ${data.status}`, data.device_id);
                break;
                
              case 'adb_status_changed':
                set({ adbStatus: data.adb_status });
                get().addLog('info', 'ADB status updated');
                break;
                
              case 'device_log':
                get().addLog(data.level, data.message, data.device_id, data.details);
                break;
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        ws.onerror = (error) => {
          console.error('Device WebSocket error:', error);
          get().addLog('error', 'WebSocket error occurred');
        };
        
        ws.onclose = () => {
          console.log('Device WebSocket disconnected');
          set({ ws: null });
          get().addLog('warning', 'WebSocket disconnected');
          
          // Attempt to reconnect after 5 seconds
          setTimeout(() => {
            if (!get().ws) {
              get().connectWebSocket();
            }
          }, 5000);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        get().addLog('error', 'Failed to connect WebSocket', undefined, { error });
      }
    },

    disconnectWebSocket: () => {
      const { ws } = get();
      if (ws) {
        ws.close();
        set({ ws: null });
        get().addLog('info', 'WebSocket disconnected');
      }
    }
  }),
  {
    name: 'device-store'
  }
));