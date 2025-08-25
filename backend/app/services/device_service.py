# -*- coding: utf-8 -*-
"""
Device Service для Rush Royale Bot
Отвечает за управление Android устройствами через ADB

Автор: SkvorikovCode
Дата: 2025
"""

import asyncio
import subprocess
import json
import time
import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Условные импорты для обработки отсутствующих зависимостей
try:
    from ppadb.client import Client as AdbClient
    from ppadb.device import Device as AdbDevice
except ImportError:
    AdbClient = None
    AdbDevice = None
    print("Warning: ppadb не установлен. Функциональность ADB недоступна.")

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

class DeviceStatus(Enum):
    """Статусы устройства"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    UNAUTHORIZED = "unauthorized"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

class ConnectionType(Enum):
    """Типы подключения"""
    USB = "usb"
    WIFI = "wifi"
    UNKNOWN = "unknown"

@dataclass
class DeviceInfo:
    """Информация об устройстве"""
    device_id: str
    name: str
    model: str
    android_version: str
    resolution: Tuple[int, int]
    status: DeviceStatus
    connection_type: ConnectionType
    is_connected: bool
    last_seen: float
    adb_port: Optional[int] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['status'] = self.status.value
        data['connection_type'] = self.connection_type.value
        return data

class Device:
    """Класс для работы с отдельным устройством"""
    
    def __init__(self, device_info: DeviceInfo, adb_device: Optional[Any] = None):
        self.info = device_info
        self.adb_device = adb_device
        self._last_screenshot_time = 0
        self._screenshot_cache = None
        
    @property
    def device_id(self) -> str:
        return self.info.device_id
    
    @property
    def is_connected(self) -> bool:
        return self.info.is_connected and self.adb_device is not None
    
    async def take_screenshot(self) -> Optional[bytes]:
        """Получение скриншота устройства"""
        if not self.is_connected or not self.adb_device:
            return None
            
        try:
            # Кэширование скриншотов (не чаще раза в секунду)
            current_time = time.time()
            if current_time - self._last_screenshot_time < 1.0 and self._screenshot_cache:
                return self._screenshot_cache
            
            # Получение скриншота через ADB
            screenshot_data = self.adb_device.screencap()
            if screenshot_data:
                self._screenshot_cache = screenshot_data
                self._last_screenshot_time = current_time
                return screenshot_data
                
        except Exception as e:
            print(f"Ошибка получения скриншота: {e}")
            
        return None
    
    async def tap(self, x: int, y: int) -> bool:
        """Тап по координатам"""
        if not self.is_connected or not self.adb_device:
            return False
            
        try:
            self.adb_device.shell(f"input tap {x} {y}")
            return True
        except Exception as e:
            print(f"Ошибка тапа: {e}")
            return False
    
    async def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """Свайп между координатами"""
        if not self.is_connected or not self.adb_device:
            return False
            
        try:
            self.adb_device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
            return True
        except Exception as e:
            print(f"Ошибка свайпа: {e}")
            return False
    
    async def get_device_info(self) -> DeviceInfo:
        """Получение актуальной информации об устройстве"""
        if not self.is_connected or not self.adb_device:
            self.info.is_connected = False
            self.info.status = DeviceStatus.DISCONNECTED
            return self.info
            
        try:
            # Обновление информации об устройстве
            self.info.last_seen = time.time()
            self.info.is_connected = True
            self.info.status = DeviceStatus.CONNECTED
            
            # Получение разрешения экрана
            wm_size = self.adb_device.shell("wm size")
            if wm_size and "Physical size:" in wm_size:
                size_str = wm_size.split("Physical size:")[1].strip()
                if "x" in size_str:
                    width, height = map(int, size_str.split("x"))
                    self.info.resolution = (width, height)
                    
        except Exception as e:
            print(f"Ошибка получения информации об устройстве: {e}")
            self.info.is_connected = False
            self.info.status = DeviceStatus.UNKNOWN
            
        return self.info
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return self.info.to_dict()

class DeviceService:
    """Сервис для управления устройствами"""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.adb_client: Optional[Any] = None
        self._last_scan_time = 0
        self._scan_interval = 2.0  # Минимальный интервал между сканированиями
        self.adb_path: Optional[str] = None
        self._port_scan_lock = threading.Lock()
        
    async def initialize(self):
        """Инициализация сервиса устройств"""
        self.adb_path = self.find_adb()
        await self.check_adb_connection()
    
    def find_adb(self) -> Optional[str]:
        """Поиск исполняемого файла ADB"""
        # Проверка в PATH
        adb_path = shutil.which('adb')
        if adb_path:
            return adb_path
        
        # Проверка стандартных путей для macOS
        possible_paths = [
            '/usr/local/bin/adb',
            '/opt/homebrew/bin/adb',
            '/Users/{}/Library/Android/sdk/platform-tools/adb'.format(os.getenv('USER', '')),
            '/Applications/Android Studio.app/Contents/bin/adb',
            '~/Android/Sdk/platform-tools/adb',
            '~/Library/Android/sdk/platform-tools/adb'
        ]
        
        for path in possible_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.isfile(expanded_path) and os.access(expanded_path, os.X_OK):
                return expanded_path
        
        print("ADB не найден в системе")
        return None
    
    async def connect_port(self, port: int) -> bool:
        """Подключение к порту"""
        if not self.adb_path:
            return False
            
        try:
            result = subprocess.run(
                [self.adb_path, 'connect', f'127.0.0.1:{port}'],
                capture_output=True, text=True, timeout=5
            )
            
            return 'connected' in result.stdout.lower() or 'already connected' in result.stdout.lower()
            
        except Exception as e:
            print(f"Ошибка подключения к порту {port}: {e}")
            return False
    
    async def scan_ports(self, start_port: int = 5555, end_port: int = 5585, max_workers: int = 10) -> List[int]:
        """Сканирование портов в заданном диапазоне"""
        with self._port_scan_lock:
            connected_ports = []
            
            def scan_single_port(port: int) -> Optional[int]:
                try:
                    result = subprocess.run(
                        [self.adb_path, 'connect', f'127.0.0.1:{port}'],
                        capture_output=True, text=True, timeout=3
                    )
                    
                    if 'connected' in result.stdout.lower() or 'already connected' in result.stdout.lower():
                        return port
                except Exception:
                    pass
                return None
            
            if not self.adb_path:
                return connected_ports
            
            # Многопоточное сканирование портов
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_port = {executor.submit(scan_single_port, port): port 
                                for port in range(start_port, end_port + 1)}
                
                for future in as_completed(future_to_port):
                    result = future.result()
                    if result is not None:
                        connected_ports.append(result)
            
            print(f"Найдено {len(connected_ports)} активных портов: {connected_ports}")
            return sorted(connected_ports)
    
    async def get_adb_devices(self) -> List[str]:
        """Получение списка подключенных ADB устройств"""
        if not self.adb_path:
            return []
            
        try:
            result = subprocess.run(
                [self.adb_path, 'devices'],
                capture_output=True, text=True, timeout=10
            )
            
            devices = []
            lines = result.stdout.strip().split('\n')[1:]  # Пропускаем заголовок
            
            for line in lines:
                if line.strip() and '\t' in line:
                    device_id = line.split('\t')[0].strip()
                    if device_id:
                        devices.append(device_id)
            
            return devices
            
        except Exception as e:
             print(f"Ошибка получения списка ADB устройств: {e}")
             return []
    
    async def get_device_by_adb(self) -> Optional[str]:
        """Получение первого доступного ADB устройства (совместимость с port_scan.py)"""
        devices = await self.get_adb_devices()
        return devices[0] if devices else None
    
    async def auto_discover_devices(self) -> List[str]:
        """Автоматическое обнаружение устройств через сканирование портов"""
        # Сначала проверяем уже подключенные устройства
        existing_devices = await self.get_adb_devices()
        
        # Затем сканируем порты для поиска новых устройств
        active_ports = await self.scan_ports()
        
        # Подключаемся к найденным портам
        for port in active_ports:
            await self.connect_port(port)
        
        # Получаем обновленный список устройств
        all_devices = await self.get_adb_devices()
        
        print(f"Обнаружено устройств: {len(all_devices)}")
        return all_devices
    
    async def check_adb_connection(self) -> bool:
        """Проверка доступности ADB"""
        if not AdbClient:
            print("ADB клиент недоступен (ppadb не установлен)")
            return False
            
        try:
            # Проверка запуска ADB сервера
            result = subprocess.run(["adb", "start-server"], 
                                  capture_output=True, text=True, timeout=10)
            
            # Создание клиента
            self.adb_client = AdbClient(host="127.0.0.1", port=5037)
            
            # Проверка подключения
            devices = self.adb_client.devices()
            print(f"ADB подключен, найдено устройств: {len(devices)}")
            return True
            
        except Exception as e:
            print(f"Ошибка подключения к ADB: {e}")
            self.adb_client = None
            return False
    
    async def scan_devices(self, auto_discover: bool = True) -> List[Dict[str, Any]]:
        """Сканирование подключенных устройств"""
        current_time = time.time()
        
        # Ограничение частоты сканирования
        if current_time - self._last_scan_time < self._scan_interval:
            return [device.to_dict() for device in self.devices.values()]
        
        self._last_scan_time = current_time
        
        # Автоматическое обнаружение устройств через сканирование портов
        if auto_discover and self.adb_path:
            try:
                await self.auto_discover_devices()
            except Exception as e:
                print(f"Ошибка автоматического обнаружения устройств: {e}")
        
        if not self.adb_client:
            await self.check_adb_connection()
            
        if not self.adb_client:
            return []
        
        try:
            adb_devices = self.adb_client.devices()
            current_device_ids = set()
            
            for adb_device in adb_devices:
                device_id = adb_device.serial
                current_device_ids.add(device_id)
                
                # Получение информации об устройстве
                device_info = await self._get_device_info(adb_device)
                
                if device_id in self.devices:
                    # Обновление существующего устройства
                    self.devices[device_id].info = device_info
                    self.devices[device_id].adb_device = adb_device
                else:
                    # Добавление нового устройства
                    self.devices[device_id] = Device(device_info, adb_device)
            
            # Удаление отключенных устройств
            disconnected_devices = set(self.devices.keys()) - current_device_ids
            for device_id in disconnected_devices:
                self.devices[device_id].info.is_connected = False
                self.devices[device_id].info.status = DeviceStatus.DISCONNECTED
                self.devices[device_id].adb_device = None
            
            print(f"Сканирование завершено: {len(current_device_ids)} активных устройств")
            
        except Exception as e:
            print(f"Ошибка сканирования устройств: {e}")
        
        return [device.to_dict() for device in self.devices.values()]
    
    async def _get_device_info(self, adb_device: Any) -> DeviceInfo:
        """Получение информации об устройстве"""
        device_id = adb_device.serial
        
        try:
            # Базовая информация
            model = adb_device.shell("getprop ro.product.model").strip()
            android_version = adb_device.shell("getprop ro.build.version.release").strip()
            
            # Разрешение экрана
            wm_size = adb_device.shell("wm size")
            resolution = (1080, 1920)  # По умолчанию
            if wm_size and "Physical size:" in wm_size:
                size_str = wm_size.split("Physical size:")[1].strip()
                if "x" in size_str:
                    width, height = map(int, size_str.split("x"))
                    resolution = (width, height)
            
            # Тип подключения
            connection_type = ConnectionType.USB
            if ":" in device_id and device_id.count(".") == 3:
                connection_type = ConnectionType.WIFI
            
            return DeviceInfo(
                device_id=device_id,
                name=model or f"Device {device_id[:8]}",
                model=model or "Unknown",
                android_version=android_version or "Unknown",
                resolution=resolution,
                status=DeviceStatus.CONNECTED,
                connection_type=connection_type,
                is_connected=True,
                last_seen=time.time()
            )
            
        except Exception as e:
            print(f"Ошибка получения информации об устройстве {device_id}: {e}")
            return DeviceInfo(
                device_id=device_id,
                name=f"Device {device_id[:8]}",
                model="Unknown",
                android_version="Unknown",
                resolution=(1080, 1920),
                status=DeviceStatus.UNKNOWN,
                connection_type=ConnectionType.UNKNOWN,
                is_connected=False,
                last_seen=time.time()
            )
    
    async def get_device(self, device_id: str) -> Optional[Device]:
        """Получение устройства по ID"""
        return self.devices.get(device_id)
    
    async def refresh_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Обновление информации об устройстве"""
        device = self.devices.get(device_id)
        if not device:
            return None
            
        updated_info = await device.get_device_info()
        return updated_info.to_dict()
    
    async def get_connected_devices_count(self) -> int:
        """Получение количества подключенных устройств"""
        return len([d for d in self.devices.values() if d.is_connected])
    
    def get_device_list(self) -> List[Dict[str, Any]]:
        """Получение списка всех устройств"""
        return [device.to_dict() for device in self.devices.values()]
    
    async def connect_wifi_device(self, ip_address: str, port: int = 5555) -> bool:
        """Подключение устройства по WiFi"""
        if not self.adb_client:
            return False
            
        try:
            result = subprocess.run(
                ["adb", "connect", f"{ip_address}:{port}"],
                capture_output=True, text=True, timeout=10
            )
            
            if "connected" in result.stdout.lower():
                # Обновление списка устройств
                await asyncio.sleep(1)  # Небольшая задержка
                await self.scan_devices()
                return True
                
        except Exception as e:
            print(f"Ошибка подключения WiFi устройства: {e}")
            
        return False
    
    async def disconnect_device(self, device_id: str) -> bool:
        """Отключение устройства"""
        try:
            result = subprocess.run(
                ["adb", "disconnect", device_id],
                capture_output=True, text=True, timeout=10
            )
            
            # Обновление статуса устройства
            if device_id in self.devices:
                self.devices[device_id].info.is_connected = False
                self.devices[device_id].info.status = DeviceStatus.DISCONNECTED
                self.devices[device_id].adb_device = None
            
            return True
            
        except Exception as e:
            print(f"Ошибка отключения устройства: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики сервиса"""
        connected_count = len([d for d in self.devices.values() if d.is_connected])
        
        return {
            "total_devices": len(self.devices),
            "connected_devices": connected_count,
            "disconnected_devices": len(self.devices) - connected_count,
            "adb_available": self.adb_client is not None,
            "adb_path": self.adb_path,
            "adb_path_found": self.adb_path is not None,
            "last_scan_time": self._last_scan_time,
            "scan_interval": self._scan_interval,
            "port_scanning_enabled": True
        }

# Глобальный экземпляр сервиса
device_service = DeviceService()