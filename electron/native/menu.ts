import { Menu, BrowserWindow, app } from 'electron';

export function setupNativeMenu(mainWindow: BrowserWindow) {
  const template = [
    {
      label: 'Rush Royale Bot',
      submenu: [
        {
          label: 'О программе Rush Royale Bot',
          click: () => mainWindow.webContents.send('menu:about')
        },
        { type: 'separator' },
        {
          label: 'Настройки...',
          accelerator: 'Cmd+,',
          click: () => mainWindow.webContents.send('menu:preferences')
        },
        { type: 'separator' },
        {
          label: 'Скрыть Rush Royale Bot',
          accelerator: 'Cmd+H',
          role: 'hide'
        },
        {
          label: 'Скрыть остальные',
          accelerator: 'Cmd+Alt+H',
          role: 'hideothers'
        },
        {
          label: 'Показать все',
          role: 'unhide'
        },
        { type: 'separator' },
        {
          label: 'Выйти из Rush Royale Bot',
          accelerator: 'Cmd+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Бот',
      submenu: [
        {
          label: 'Запустить бота',
          accelerator: 'Cmd+R',
          click: () => mainWindow.webContents.send('bot:start')
        },
        {
          label: 'Остановить бота',
          accelerator: 'Cmd+S',
          click: () => mainWindow.webContents.send('bot:stop')
        },
        {
          label: 'Пауза/Возобновить',
          accelerator: 'Cmd+P',
          click: () => mainWindow.webContents.send('bot:toggle-pause')
        },
        { type: 'separator' },
        {
          label: 'Быстрый старт',
          accelerator: 'Cmd+Shift+R',
          click: () => mainWindow.webContents.send('bot:quick-start')
        },
        {
          label: 'Выйти из игры',
          accelerator: 'Cmd+Shift+Q',
          click: () => mainWindow.webContents.send('bot:quit-game')
        }
      ]
    },
    {
      label: 'Устройства',
      submenu: [
        {
          label: 'Сканировать устройства',
          accelerator: 'Cmd+D',
          click: () => mainWindow.webContents.send('devices:scan')
        },
        {
          label: 'Подключить устройство',
          accelerator: 'Cmd+Shift+D',
          click: () => mainWindow.webContents.send('devices:connect')
        },
        { type: 'separator' },
        {
          label: 'Настройки ADB',
          click: () => mainWindow.webContents.send('devices:adb-settings')
        },
        {
          label: 'Перезапустить ADB',
          click: () => mainWindow.webContents.send('devices:restart-adb')
        }
      ]
    },
    {
      label: 'Правка',
      submenu: [
        {
          label: 'Отменить',
          accelerator: 'Cmd+Z',
          role: 'undo'
        },
        {
          label: 'Повторить',
          accelerator: 'Shift+Cmd+Z',
          role: 'redo'
        },
        { type: 'separator' },
        {
          label: 'Вырезать',
          accelerator: 'Cmd+X',
          role: 'cut'
        },
        {
          label: 'Копировать',
          accelerator: 'Cmd+C',
          role: 'copy'
        },
        {
          label: 'Вставить',
          accelerator: 'Cmd+V',
          role: 'paste'
        },
        {
          label: 'Выделить все',
          accelerator: 'Cmd+A',
          role: 'selectall'
        }
      ]
    },
    {
      label: 'Вид',
      submenu: [
        {
          label: 'Перезагрузить',
          accelerator: 'Cmd+R',
          click: () => mainWindow.reload()
        },
        {
          label: 'Принудительная перезагрузка',
          accelerator: 'Cmd+Shift+R',
          click: () => mainWindow.webContents.reloadIgnoringCache()
        },
        { type: 'separator' },
        {
          label: 'Увеличить',
          accelerator: 'Cmd+Plus',
          click: () => {
            const currentZoom = mainWindow.webContents.getZoomLevel();
            mainWindow.webContents.setZoomLevel(currentZoom + 0.5);
          }
        },
        {
          label: 'Уменьшить',
          accelerator: 'Cmd+-',
          click: () => {
            const currentZoom = mainWindow.webContents.getZoomLevel();
            mainWindow.webContents.setZoomLevel(currentZoom - 0.5);
          }
        },
        {
          label: 'Фактический размер',
          accelerator: 'Cmd+0',
          click: () => mainWindow.webContents.setZoomLevel(0)
        },
        { type: 'separator' },
        {
          label: 'Полноэкранный режим',
          accelerator: 'Ctrl+Cmd+F',
          role: 'togglefullscreen'
        },
        { type: 'separator' },
        {
          label: 'Показать инструменты разработчика',
          accelerator: 'Alt+Cmd+I',
          click: () => mainWindow.webContents.toggleDevTools()
        }
      ]
    },
    {
      label: 'Окно',
      submenu: [
        {
          label: 'Свернуть',
          accelerator: 'Cmd+M',
          role: 'minimize'
        },
        {
          label: 'Закрыть',
          accelerator: 'Cmd+W',
          role: 'close'
        },
        { type: 'separator' },
        {
          label: 'Переместить на передний план',
          role: 'front'
        }
      ]
    },
    {
      label: 'Справка',
      submenu: [
        {
          label: 'Руководство пользователя',
          click: () => mainWindow.webContents.send('help:user-guide')
        },
        {
          label: 'Горячие клавиши',
          accelerator: 'Cmd+/',
          click: () => mainWindow.webContents.send('help:shortcuts')
        },
        { type: 'separator' },
        {
          label: 'Сообщить об ошибке',
          click: () => mainWindow.webContents.send('help:report-bug')
        },
        {
          label: 'Проверить обновления',
          click: () => mainWindow.webContents.send('help:check-updates')
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template as any);
  Menu.setApplicationMenu(menu);

  // Контекстное меню для правого клика
  mainWindow.webContents.on('context-menu', (event, params) => {
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Назад',
        enabled: mainWindow.webContents.canGoBack(),
        click: () => mainWindow.webContents.goBack()
      },
      {
        label: 'Вперед',
        enabled: mainWindow.webContents.canGoForward(),
        click: () => mainWindow.webContents.goForward()
      },
      {
        label: 'Перезагрузить',
        click: () => mainWindow.webContents.reload()
      },
      { type: 'separator' },
      {
        label: 'Копировать',
        enabled: params.selectionText.length > 0,
        click: () => mainWindow.webContents.copy()
      },
      {
        label: 'Вставить',
        enabled: params.isEditable,
        click: () => mainWindow.webContents.paste()
      },
      { type: 'separator' },
      {
        label: 'Инспектировать элемент',
        click: () => {
          mainWindow.webContents.inspectElement(params.x, params.y);
          mainWindow.webContents.openDevTools();
        }
      }
    ]);

    contextMenu.popup({ window: mainWindow });
  });
}