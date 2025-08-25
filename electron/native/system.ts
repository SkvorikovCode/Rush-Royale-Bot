import { BrowserWindow, app, systemPreferences, powerMonitor, screen } from 'electron';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export function setupSystemIntegration(mainWindow: BrowserWindow) {
  // Настройка системных предпочтений macOS
  setupSystemPreferences(mainWindow);
  
  // Мониторинг питания
  setupPowerMonitoring(mainWindow);
  
  // Мониторинг дисплеев
  setupDisplayMonitoring(mainWindow);
  
  // Интеграция с Notification Center
  setupNotifications(mainWindow);
  
  // Мониторинг системных событий
  setupSystemEventMonitoring(mainWindow);
  
  // Оптимизация для Apple Silicon
  setupAppleSiliconOptimizations(mainWindow);
}

function setupSystemPreferences(mainWindow: BrowserWindow) {
  // Проверка разрешений на доступность
  const hasAccessibilityAccess = systemPreferences.isTrustedAccessibilityClient(false);
  
  if (!hasAccessibilityAccess) {
    mainWindow.webContents.send('system:accessibility-permission-required');
  }
  
  // Запрос разрешений на доступность
  mainWindow.webContents.on('dom-ready', () => {
    mainWindow.webContents.send('system:permissions-status', {
      accessibility: systemPreferences.isTrustedAccessibilityClient(false),
      screenCapture: systemPreferences.getMediaAccessStatus('screen') === 'granted',
      camera: systemPreferences.getMediaAccessStatus('camera') === 'granted'
    });
  });
  
  // Мониторинг изменений системных настроек
  systemPreferences.subscribeNotification('AppleInterfaceThemeChangedNotification', () => {
    const isDarkMode = systemPreferences.isDarkMode();
    mainWindow.webContents.send('system:theme-changed', { isDarkMode });
  });
  
  systemPreferences.subscribeNotification('AppleColorPreferencesChangedNotification', () => {
    const accentColor = systemPreferences.getAccentColor();
    mainWindow.webContents.send('system:accent-color-changed', { accentColor });
  });
}

function setupPowerMonitoring(mainWindow: BrowserWindow) {
  // Мониторинг состояния питания
  powerMonitor.on('suspend', () => {
    mainWindow.webContents.send('system:power:suspend');
  });
  
  powerMonitor.on('resume', () => {
    mainWindow.webContents.send('system:power:resume');
  });
  
  powerMonitor.on('on-ac', () => {
    mainWindow.webContents.send('system:power:ac-connected');
  });
  
  powerMonitor.on('on-battery', () => {
    mainWindow.webContents.send('system:power:battery');
  });
  
  // Мониторинг уровня заряда батареи
  setInterval(async () => {
    try {
      const { stdout } = await execAsync('pmset -g batt | grep -o "[0-9]*%"');
      const batteryLevel = parseInt(stdout.replace('%', ''));
      
      mainWindow.webContents.send('system:battery-level', { level: batteryLevel });
      
      // Предупреждение о низком заряде
      if (batteryLevel < 20) {
        mainWindow.webContents.send('system:low-battery-warning', { level: batteryLevel });
      }
    } catch (error) {
      console.error('Failed to get battery level:', error);
    }
  }, 60000); // Каждую минуту
}

function setupDisplayMonitoring(mainWindow: BrowserWindow) {
  // Мониторинг изменений дисплеев
  screen.on('display-added', (event, newDisplay) => {
    mainWindow.webContents.send('system:display-added', {
      display: {
        id: newDisplay.id,
        bounds: newDisplay.bounds,
        workArea: newDisplay.workArea,
        scaleFactor: newDisplay.scaleFactor,
        rotation: newDisplay.rotation
      }
    });
  });
  
  screen.on('display-removed', (event, oldDisplay) => {
    mainWindow.webContents.send('system:display-removed', {
      displayId: oldDisplay.id
    });
  });
  
  screen.on('display-metrics-changed', (event, display, changedMetrics) => {
    mainWindow.webContents.send('system:display-metrics-changed', {
      display: {
        id: display.id,
        bounds: display.bounds,
        workArea: display.workArea,
        scaleFactor: display.scaleFactor,
        rotation: display.rotation
      },
      changedMetrics
    });
  });
  
  // Оптимизация для Retina дисплеев
  const primaryDisplay = screen.getPrimaryDisplay();
  if (primaryDisplay.scaleFactor > 1) {
    mainWindow.webContents.send('system:retina-display-detected', {
      scaleFactor: primaryDisplay.scaleFactor
    });
  }
}

function setupNotifications(mainWindow: BrowserWindow) {
  // Интеграция с Notification Center macOS
  mainWindow.webContents.on('dom-ready', () => {
    mainWindow.webContents.executeJavaScript(`
      // Настройка нативных уведомлений
      if ('Notification' in window) {
        if (Notification.permission === 'default') {
          Notification.requestPermission().then(permission => {
            window.electronAPI?.send('system:notification-permission', { permission });
          });
        }
      }
      
      // Кастомная функция для отправки уведомлений
      window.showNativeNotification = (title, options = {}) => {
        if (Notification.permission === 'granted') {
          const notification = new Notification(title, {
            icon: '/icons/icon.png',
            badge: '/icons/badge.png',
            ...options
          });
          
          notification.onclick = () => {
            window.electronAPI?.send('notification:clicked', { title, options });
          };
          
          return notification;
        }
      };
    `);
  });
}

function setupSystemEventMonitoring(mainWindow: BrowserWindow) {
  // Мониторинг системных событий
  app.on('browser-window-focus', () => {
    mainWindow.webContents.send('system:window-focus');
  });
  
  app.on('browser-window-blur', () => {
    mainWindow.webContents.send('system:window-blur');
  });
  
  // Мониторинг изменений в системе
  setInterval(async () => {
    try {
      // Проверка использования CPU
      const { stdout: cpuUsage } = await execAsync('top -l 1 | grep "CPU usage" | awk \'{print $3}\' | sed \'s/%//\'');
      
      // Проверка использования памяти
      const { stdout: memUsage } = await execAsync('vm_stat | grep "Pages free" | awk \'{print $3}\' | sed \'s/\\.//'\');
      
      mainWindow.webContents.send('system:performance-stats', {
        cpu: parseFloat(cpuUsage.trim()) || 0,
        memory: parseInt(memUsage.trim()) || 0,
        timestamp: Date.now()
      });
    } catch (error) {
      console.error('Failed to get system stats:', error);
    }
  }, 5000); // Каждые 5 секунд
  
  // Мониторинг температуры (для Apple Silicon)
  if (process.arch === 'arm64') {
    setInterval(async () => {
      try {
        const { stdout } = await execAsync('sudo powermetrics -n 1 -s thermal | grep "CPU die temperature"');
        const temperature = parseFloat(stdout.match(/([0-9.]+)/)?.[1] || '0');
        
        mainWindow.webContents.send('system:temperature', {
          cpu: temperature,
          timestamp: Date.now()
        });
        
        // Предупреждение о перегреве
        if (temperature > 80) {
          mainWindow.webContents.send('system:thermal-warning', { temperature });
        }
      } catch (error) {
        // Игнорируем ошибки, так как требуются права sudo
      }
    }, 30000); // Каждые 30 секунд
  }
}

function setupAppleSiliconOptimizations(mainWindow: BrowserWindow) {
  if (process.arch === 'arm64' && process.platform === 'darwin') {
    // Оптимизации для Apple Silicon
    mainWindow.webContents.on('dom-ready', () => {
      mainWindow.webContents.executeJavaScript(`
        // Включаем аппаратное ускорение для Apple Silicon
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
        
        if (gl) {
          const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
          if (debugInfo) {
            const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            
            window.electronAPI?.send('system:gpu-info', {
              renderer,
              isAppleGPU: renderer.includes('Apple'),
              webglVersion: gl.constructor.name
            });
          }
        }
        
        // Оптимизация для высокого DPI
        const devicePixelRatio = window.devicePixelRatio;
        if (devicePixelRatio > 1) {
          document.documentElement.style.setProperty('--device-pixel-ratio', devicePixelRatio.toString());
        }
        
        // Включаем Metal Performance Shaders через CSS
        const style = document.createElement('style');
        style.textContent = \`
          * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
          
          canvas, video {
            image-rendering: -webkit-optimize-contrast;
            image-rendering: crisp-edges;
          }
          
          .gpu-accelerated {
            transform: translateZ(0);
            will-change: transform;
          }
        \`;
        document.head.appendChild(style);
      `);
    });
    
    // Настройка для оптимального использования памяти
    app.commandLine.appendSwitch('enable-features', 'VaapiVideoDecoder');
    app.commandLine.appendSwitch('enable-gpu-rasterization');
    app.commandLine.appendSwitch('enable-zero-copy');
  }
}

// Экспорт утилитарных функций
export async function getSystemInfo() {
  try {
    const { stdout: systemVersion } = await execAsync('sw_vers -productVersion');
    const { stdout: buildVersion } = await execAsync('sw_vers -buildVersion');
    const { stdout: hardwareModel } = await execAsync('sysctl -n hw.model');
    const { stdout: cpuBrand } = await execAsync('sysctl -n machdep.cpu.brand_string');
    
    return {
      systemVersion: systemVersion.trim(),
      buildVersion: buildVersion.trim(),
      hardwareModel: hardwareModel.trim(),
      cpuBrand: cpuBrand.trim(),
      isAppleSilicon: process.arch === 'arm64',
      platform: process.platform,
      arch: process.arch
    };
  } catch (error) {
    console.error('Failed to get system info:', error);
    return {
      systemVersion: 'Unknown',
      buildVersion: 'Unknown',
      hardwareModel: 'Unknown',
      cpuBrand: 'Unknown',
      isAppleSilicon: process.arch === 'arm64',
      platform: process.platform,
      arch: process.arch
    };
  }
}

export async function requestSystemPermissions() {
  // Запрос разрешений на доступность
  const hasAccessibility = systemPreferences.isTrustedAccessibilityClient(true);
  
  // Запрос разрешений на захват экрана
  const screenAccess = await systemPreferences.askForMediaAccess('screen');
  
  return {
    accessibility: hasAccessibility,
    screenCapture: screenAccess
  };
}