// Electron API types for renderer process
// Updated: 2025-08-25

interface ElectronAPI {
  // Системная информация и диалоги
  getSystemInfo: () => Promise<any>;
  showMessageBox: (options: any) => Promise<any>;
  showOpenDialog: (options: any) => Promise<any>;

  // Управление окном (используется в System.tsx)
  minimizeWindow: () => Promise<void | boolean>;
  maximizeWindow: () => Promise<void | boolean>; // toggle maximize
  closeWindow: () => Promise<void | boolean>;

  // Управление ботом
  bot: {
    start: (config: any) => Promise<any>;
    stop: () => Promise<any>;
    togglePause: () => Promise<any>;
    quickStart: () => Promise<any>;
    quitGame: () => Promise<any>;
    getStatus: () => Promise<any>;
  };

  // Управление устройствами
  devices: {
    scan: () => Promise<any>;
    connect: (deviceId: string) => Promise<any>;
    disconnect: (deviceId: string) => Promise<any>;
    restartAdb: () => Promise<any>;
    getList: () => Promise<any>;
  };

  // События/IPC
  on: (channel: string, callback: (...args: any[]) => void) => void;
  off: (channel: string, callback: (...args: any[]) => void) => void;
  send: (channel: string, ...args: any[]) => void;

  // Жесты
  gestures: {
    onSwipe: (callback: (direction: string) => void) => void;
    onPinch: (callback: (data: any) => void) => void;
    onForceTouch: (callback: () => void) => void;
  };

  // Уведомления (используется в Settings.tsx)
  notifications: {
    show: (title: string, options?: any) => void;
    requestPermission: () => Promise<string>;
  };
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

export {};