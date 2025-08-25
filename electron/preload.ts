import { contextBridge, ipcRenderer } from 'electron';

// Типы для API
interface ElectronAPI {
  // Системные функции
  getSystemInfo: () => Promise<any>;
  showMessageBox: (options: any) => Promise<any>;
  showOpenDialog: (options: any) => Promise<any>;
  
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
  
  // Системные события
  on: (channel: string, callback: (...args: any[]) => void) => void;
  off: (channel: string, callback: (...args: any[]) => void) => void;
  send: (channel: string, ...args: any[]) => void;
  
  // Жесты и навигация
  gestures: {
    onSwipe: (callback: (direction: string) => void) => void;
    onPinch: (callback: (data: any) => void) => void;
    onForceTouch: (callback: () => void) => void;
  };
  
  // Системные уведомления
  notifications: {
    show: (title: string, options?: any) => void;
    requestPermission: () => Promise<string>;
  };
}

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Системная информация
  getSystemInfo: () => ipcRenderer.invoke('system:getInfo'),
  showMessageBox: (options: any) => ipcRenderer.invoke('dialog:showMessageBox', options),
  showOpenDialog: (options: any) => ipcRenderer.invoke('dialog:showOpenDialog', options),
  
  // Управление ботом
  bot: {
    start: (config: any) => ipcRenderer.invoke('bot:start', config),
    stop: () => ipcRenderer.invoke('bot:stop'),
    togglePause: () => ipcRenderer.invoke('bot:toggle-pause'),
    quickStart: () => ipcRenderer.invoke('bot:quick-start'),
    quitGame: () => ipcRenderer.invoke('bot:quit-game'),
    getStatus: () => ipcRenderer.invoke('bot:get-status')
  },
  
  // Управление устройствами
  devices: {
    scan: () => ipcRenderer.invoke('devices:scan'),
    connect: (deviceId: string) => ipcRenderer.invoke('devices:connect', deviceId),
    disconnect: (deviceId: string) => ipcRenderer.invoke('devices:disconnect', deviceId),
    restartAdb: () => ipcRenderer.invoke('devices:restart-adb'),
    getList: () => ipcRenderer.invoke('devices:get-list')
  },
  
  // Системные события
  on: (channel: string, callback: (...args: any[]) => void) => {
    const validChannels = [
      // Меню события
      'menu:about', 'menu:preferences', 'menu:shortcuts',
      // Бот события
      'bot:status-changed', 'bot:error', 'bot:log',
      // Устройства события
      'devices:status-changed', 'devices:connected', 'devices:disconnected',
      // Системные события
      'system:theme-changed', 'system:power:suspend', 'system:power:resume',
      'system:battery-level', 'system:low-battery-warning',
      'system:display-added', 'system:display-removed',
      'system:window-focus', 'system:window-blur',
      'system:performance-stats', 'system:temperature',
      // Жесты
      'gesture:swipe-left', 'gesture:swipe-right', 'gesture:swipe-up', 'gesture:swipe-down',
      'gesture:pinch-begin', 'gesture:pinch-update', 'gesture:pinch-end',
      'gesture:force-touch', 'gesture:scroll-begin', 'gesture:scroll-update', 'gesture:scroll-end',
      'gesture:sequence:back-forward', 'gesture:sequence:refresh', 'gesture:sequence:reset-zoom',
      // Навигация
      'navigation:previous-tab', 'navigation:next-tab',
      // Помощь
      'help:user-guide', 'help:shortcuts', 'help:report-bug', 'help:check-updates'
    ];
    
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, callback);
    }
  },
  
  off: (channel: string, callback: (...args: any[]) => void) => {
    ipcRenderer.off(channel, callback);
  },
  
  send: (channel: string, ...args: any[]) => {
    const validChannels = [
      'gesture:start', 'gesture:change', 'gesture:end',
      'trackpad:scroll', 'notification:clicked',
      'system:notification-permission', 'system:gpu-info'
    ];
    
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, ...args);
    }
  },
  
  // Удобные методы для жестов
  gestures: {
    onSwipe: (callback: (direction: string) => void) => {
      ipcRenderer.on('gesture:swipe-left', () => callback('left'));
      ipcRenderer.on('gesture:swipe-right', () => callback('right'));
      ipcRenderer.on('gesture:swipe-up', () => callback('up'));
      ipcRenderer.on('gesture:swipe-down', () => callback('down'));
    },
    
    onPinch: (callback: (data: any) => void) => {
      ipcRenderer.on('gesture:pinch-update', (event, data) => callback(data));
    },
    
    onForceTouch: (callback: () => void) => {
      ipcRenderer.on('gesture:force-touch', callback);
    }
  },
  
  // Системные уведомления
  notifications: {
    show: (title: string, options: any = {}) => {
      if ('Notification' in window && Notification.permission === 'granted') {
        return new Notification(title, {
          icon: '/icons/icon.png',
          badge: '/icons/badge.png',
          ...options
        });
      }
    },
    
    requestPermission: () => {
      if ('Notification' in window) {
        return Notification.requestPermission();
      }
      return Promise.resolve('denied');
    }
  }
} as ElectronAPI);

// Глобальные типы для TypeScript
declare global {
  interface Window {
    electronAPI: ElectronAPI;
    showNativeNotification: (title: string, options?: any) => Notification | undefined;
  }
}

// Добавляем поддержку для разработки
if (process.env.NODE_ENV === 'development') {
  contextBridge.exposeInMainWorld('electronDev', {
    reload: () => ipcRenderer.send('dev:reload'),
    toggleDevTools: () => ipcRenderer.send('dev:toggle-devtools'),
    getVersion: () => process.versions
  });
}