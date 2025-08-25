import { app, BrowserWindow, Menu, ipcMain, shell, dialog } from 'electron';
import { join } from 'path';
import { spawn, ChildProcess } from 'child_process';
import { setupNativeMenu } from './native/menu';
import { setupGestureHandlers } from './native/gestures';
import { setupSystemIntegration } from './native/system';

class RushRoyaleBotApp {
  private mainWindow: BrowserWindow | null = null;
  private pythonProcess: ChildProcess | null = null;
  private isDev = process.env.NODE_ENV === 'development';

  async initialize() {
    await app.whenReady();
    
    // Настройка macOS специфичных параметров
    if (process.platform === 'darwin') {
      app.dock.setIcon(join(__dirname, '../build/icons/icon.png'));
    }
    
    // Запуск Python backend
    await this.startPythonBackend();
    
    // Создание главного окна
    this.createMainWindow();
    
    // Настройка нативных функций macOS
    if (this.mainWindow) {
      setupNativeMenu(this.mainWindow);
      setupGestureHandlers(this.mainWindow);
      setupSystemIntegration(this.mainWindow);
    }
    
    // Обработка событий приложения
    this.setupAppEvents();
  }

  private createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 1000,
      minHeight: 600,
      titleBarStyle: 'hiddenInset', // macOS стиль
      vibrancy: 'under-window',     // Прозрачность macOS
      trafficLightPosition: { x: 20, y: 20 },
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: join(__dirname, 'preload.js'),
        webSecurity: !this.isDev
      },
      show: false // Показываем после загрузки
    });

    // Загрузка приложения
    if (this.isDev) {
      this.mainWindow.loadURL('http://localhost:5173');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(join(__dirname, '../frontend/dist/index.html'));
    }

    // Показываем окно после загрузки
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
      
      // Фокус на окне для macOS
      if (process.platform === 'darwin') {
        this.mainWindow?.focus();
      }
    });

    // Обработка закрытия окна
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    // Обработка внешних ссылок
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
  }

  private async startPythonBackend(): Promise<void> {
    return new Promise((resolve, reject) => {
      const pythonScript = join(__dirname, '../backend/start.py');
      
      this.pythonProcess = spawn('python3', [pythonScript], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.pythonProcess.stdout?.on('data', (data) => {
        console.log(`Python Backend: ${data}`);
        if (data.toString().includes('started')) {
          resolve();
        }
      });

      this.pythonProcess.stderr?.on('data', (data) => {
        console.error(`Python Backend Error: ${data}`);
      });

      this.pythonProcess.on('error', (error) => {
        console.error('Failed to start Python backend:', error);
        reject(error);
      });

      // Таймаут для запуска
      setTimeout(() => {
        resolve(); // Продолжаем даже если backend не запустился
      }, 5000);
    });
  }

  private setupAppEvents() {
    // macOS: Переоткрытие окна при клике на dock
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createMainWindow();
      }
    });

    // Закрытие всех окон
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    // Завершение приложения
    app.on('before-quit', () => {
      if (this.pythonProcess) {
        this.pythonProcess.kill();
      }
    });

    // IPC обработчики
    this.setupIpcHandlers();
  }

  private setupIpcHandlers() {
    // Управление ботом
    ipcMain.handle('bot:start', async (event, config) => {
      try {
        const response = await fetch('http://localhost:8000/api/bot/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
        });
        return await response.json();
      } catch (error) {
        console.error('Failed to start bot:', error);
        return { success: false, error: error.message };
      }
    });

    ipcMain.handle('bot:stop', async () => {
      try {
        const response = await fetch('http://localhost:8000/api/bot/stop', {
          method: 'POST'
        });
        return await response.json();
      } catch (error) {
        console.error('Failed to stop bot:', error);
        return { success: false, error: error.message };
      }
    });

    // Управление устройствами
    ipcMain.handle('devices:scan', async () => {
      try {
        const response = await fetch('http://localhost:8000/api/devices/scan');
        return await response.json();
      } catch (error) {
        console.error('Failed to scan devices:', error);
        return { devices: [], error: error.message };
      }
    });

    // Системные диалоги
    ipcMain.handle('dialog:showMessageBox', async (event, options) => {
      const result = await dialog.showMessageBox(this.mainWindow!, options);
      return result;
    });

    ipcMain.handle('dialog:showOpenDialog', async (event, options) => {
      const result = await dialog.showOpenDialog(this.mainWindow!, options);
      return result;
    });

    // Системная информация
    ipcMain.handle('system:getInfo', () => {
      return {
        platform: process.platform,
        arch: process.arch,
        version: process.version,
        isAppleSilicon: process.arch === 'arm64' && process.platform === 'darwin'
      };
    });
  }
}

// Инициализация приложения
const rushRoyaleBot = new RushRoyaleBotApp();
rushRoyaleBot.initialize().catch(console.error);

// Обработка необработанных исключений
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});