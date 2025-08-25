// Electron API types for renderer process
// Created: 2025-01-15

interface ElectronAPI {
  // Window management
  minimizeWindow?: () => Promise<void>;
  maximizeWindow?: () => Promise<void>;
  closeWindow?: () => Promise<void>;
  
  // System events
  onSystemPerformanceStats?: (callback: (stats: any) => void) => void;
  onSystemBatteryLevel?: (callback: (level: number) => void) => void;
  
  // Device management
  onDeviceConnected?: (callback: (device: any) => void) => void;
  onDeviceDisconnected?: (callback: (deviceId: string) => void) => void;
  
  // Bot events
  onBotStatusChanged?: (callback: (status: string) => void) => void;
  onBotStatsUpdated?: (callback: (stats: any) => void) => void;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};