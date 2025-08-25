import { BrowserWindow } from 'electron';

export function setupGestureHandlers(mainWindow: BrowserWindow) {
  // Обработка жестов трекпада macOS
  mainWindow.webContents.on('before-input-event', (event, input) => {
    // Обработка жестов масштабирования (pinch to zoom)
    if (input.type === 'gestureScrollBegin') {
      mainWindow.webContents.send('gesture:scroll-begin');
    }
    
    if (input.type === 'gestureScrollUpdate') {
      mainWindow.webContents.send('gesture:scroll-update', {
        deltaX: input.deltaX,
        deltaY: input.deltaY
      });
    }
    
    if (input.type === 'gestureScrollEnd') {
      mainWindow.webContents.send('gesture:scroll-end');
    }
    
    // Обработка жестов пинча (масштабирование)
    if (input.type === 'gesturePinchBegin') {
      mainWindow.webContents.send('gesture:pinch-begin');
    }
    
    if (input.type === 'gesturePinchUpdate') {
      mainWindow.webContents.send('gesture:pinch-update', {
        scale: input.scale
      });
    }
    
    if (input.type === 'gesturePinchEnd') {
      mainWindow.webContents.send('gesture:pinch-end');
    }
  });

  // Обработка свайпов (жестов смахивания)
  mainWindow.webContents.on('swipe', (event, direction) => {
    switch (direction) {
      case 'left':
        mainWindow.webContents.send('gesture:swipe-left');
        break;
      case 'right':
        mainWindow.webContents.send('gesture:swipe-right');
        break;
      case 'up':
        mainWindow.webContents.send('gesture:swipe-up');
        break;
      case 'down':
        mainWindow.webContents.send('gesture:swipe-down');
        break;
    }
  });

  // Обработка Force Touch (сильное нажатие)
  mainWindow.webContents.on('new-window-for-tab', () => {
    // Force Touch на ссылке - открываем превью
    mainWindow.webContents.send('gesture:force-touch');
  });

  // Настройка чувствительности жестов
  mainWindow.webContents.executeJavaScript(`
    // Добавляем обработчики жестов на стороне рендерера
    let isGestureActive = false;
    let gestureStartTime = 0;
    let lastScale = 1;
    let lastRotation = 0;
    
    // Обработка жестов масштабирования
    document.addEventListener('gesturestart', (e) => {
      e.preventDefault();
      isGestureActive = true;
      gestureStartTime = Date.now();
      lastScale = e.scale;
      lastRotation = e.rotation;
      
      window.electronAPI?.send('gesture:start', {
        scale: e.scale,
        rotation: e.rotation
      });
    });
    
    document.addEventListener('gesturechange', (e) => {
      e.preventDefault();
      if (!isGestureActive) return;
      
      const scaleDelta = e.scale - lastScale;
      const rotationDelta = e.rotation - lastRotation;
      
      window.electronAPI?.send('gesture:change', {
        scale: e.scale,
        rotation: e.rotation,
        scaleDelta,
        rotationDelta
      });
      
      lastScale = e.scale;
      lastRotation = e.rotation;
    });
    
    document.addEventListener('gestureend', (e) => {
      e.preventDefault();
      if (!isGestureActive) return;
      
      const gestureDuration = Date.now() - gestureStartTime;
      
      window.electronAPI?.send('gesture:end', {
        scale: e.scale,
        rotation: e.rotation,
        duration: gestureDuration
      });
      
      isGestureActive = false;
    });
    
    // Обработка трекпада с высокой точностью
    let wheelTimeout;
    let wheelDelta = { x: 0, y: 0 };
    
    document.addEventListener('wheel', (e) => {
      // Определяем тип устройства ввода
      const isTrackpad = Math.abs(e.deltaY) < 50 && e.deltaMode === 0;
      
      if (isTrackpad) {
        e.preventDefault();
        
        wheelDelta.x += e.deltaX;
        wheelDelta.y += e.deltaY;
        
        clearTimeout(wheelTimeout);
        wheelTimeout = setTimeout(() => {
          window.electronAPI?.send('trackpad:scroll', {
            deltaX: wheelDelta.x,
            deltaY: wheelDelta.y,
            ctrlKey: e.ctrlKey,
            shiftKey: e.shiftKey,
            altKey: e.altKey,
            metaKey: e.metaKey
          });
          
          wheelDelta = { x: 0, y: 0 };
        }, 16); // ~60fps
      }
    }, { passive: false });
    
    // Обработка Force Touch через CSS
    const style = document.createElement('style');
    style.textContent = \`
      .force-touch-enabled {
        -webkit-user-select: none;
        user-select: none;
      }
      
      .force-touch-enabled:active {
        transform: scale(0.98);
        transition: transform 0.1s ease;
      }
    \`;
    document.head.appendChild(style);
  `);

  // Обработка специальных комбинаций жестов
  let gestureSequence: string[] = [];
  const maxSequenceLength = 5;
  const sequenceTimeout = 2000; // 2 секунды
  let sequenceTimer: NodeJS.Timeout;

  const handleGestureSequence = (gesture: string) => {
    gestureSequence.push(gesture);
    
    if (gestureSequence.length > maxSequenceLength) {
      gestureSequence.shift();
    }
    
    clearTimeout(sequenceTimer);
    sequenceTimer = setTimeout(() => {
      gestureSequence = [];
    }, sequenceTimeout);
    
    // Проверяем специальные последовательности
    const sequence = gestureSequence.join('-');
    
    switch (sequence) {
      case 'swipe-left-swipe-right':
        mainWindow.webContents.send('gesture:sequence:back-forward');
        break;
      case 'swipe-up-swipe-down':
        mainWindow.webContents.send('gesture:sequence:refresh');
        break;
      case 'pinch-in-pinch-out':
        mainWindow.webContents.send('gesture:sequence:reset-zoom');
        break;
    }
  };

  // Подписываемся на жесты для создания последовательностей
  mainWindow.webContents.on('swipe', (event, direction) => {
    handleGestureSequence(`swipe-${direction}`);
  });

  // Обработка жестов для навигации
  mainWindow.webContents.on('swipe', (event, direction) => {
    if (direction === 'left') {
      // Свайп влево - назад в истории
      if (mainWindow.webContents.canGoBack()) {
        mainWindow.webContents.goBack();
      } else {
        // Если нет истории, переключаемся на предыдущую вкладку
        mainWindow.webContents.send('navigation:previous-tab');
      }
    } else if (direction === 'right') {
      // Свайп вправо - вперед в истории
      if (mainWindow.webContents.canGoForward()) {
        mainWindow.webContents.goForward();
      } else {
        // Если нет истории, переключаемся на следующую вкладку
        mainWindow.webContents.send('navigation:next-tab');
      }
    }
  });
}