# -*- coding: utf-8 -*-
"""
Vision Service для Rush Royale Bot
Обеспечивает компьютерное зрение для анализа игровых элементов

Автор: SkvorikovCode
Дата: 2025
"""

import base64
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import json
from datetime import datetime

try:
    import cv2
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    import pickle
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None
    pd = None
    LogisticRegression = None
    pickle = None

@dataclass
class GridCell:
    """Ячейка игровой сетки"""
    x: int
    y: int
    width: int
    height: int
    occupied: bool = False
    card_type: Optional[str] = None
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GridAnalysis:
    """Результат анализа игровой сетки"""
    cells: List[GridCell]
    grid_width: int
    grid_height: int
    total_cells: int
    occupied_cells: int
    empty_cells: int
    detected_cards: Dict[str, int]
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cells": [cell.to_dict() for cell in self.cells],
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "total_cells": self.total_cells,
            "occupied_cells": self.occupied_cells,
            "empty_cells": self.empty_cells,
            "detected_cards": self.detected_cards,
            "confidence": self.confidence
        }

@dataclass
class ManaAnalysis:
    """Результат анализа маны"""
    current_mana: int
    max_mana: int
    mana_percentage: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Template:
    """Шаблон для распознавания"""
    name: str
    image: Any  # np.ndarray when available
    threshold: float = 0.8
    category: str = "card"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "threshold": self.threshold,
            "category": self.category,
            "shape": self.image.shape if self.image is not None else None
        }

@dataclass
class UnitRecognition:
    """Результат распознавания юнита"""
    unit_type: str
    confidence: float
    rank: int = 0
    rank_confidence: float = 0.0
    position: Tuple[int, int] = (0, 0)
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'unit_type': self.unit_type,
            'confidence': self.confidence,
            'rank': self.rank,
            'rank_confidence': self.rank_confidence,
            'position': self.position,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'error': self.error
        }

@dataclass
class VisionStats:
    """Статистика сервиса зрения"""
    total_analyses: int = 0
    grid_analyses: int = 0
    mana_analyses: int = 0
    template_matches: int = 0
    unit_recognitions: int = 0
    rank_predictions: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_processing_time: float = 0.0
    templates_loaded: int = 0
    model_loaded: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class VisionService:
    """Сервис компьютерного зрения"""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self.stats = VisionStats()
        self.cache: Dict[str, Any] = {}
        self.processing_times: List[float] = []
        
        # Модель для распознавания рангов
        self.rank_model: Optional[LogisticRegression] = None
        self.ref_units: List[str] = []
        self.ref_colors: List[Any] = []
        
        # Параметры игровой сетки Rush Royale (примерные)
        self.grid_config = {
            "rows": 4,
            "cols": 4,
            "cell_width": 80,
            "cell_height": 80,
            "grid_start_x": 100,
            "grid_start_y": 200,
            "cell_spacing": 10
        }
        
        # Параметры маны
        self.mana_config = {
            "mana_bar_x": 50,
            "mana_bar_y": 50,
            "mana_bar_width": 200,
            "mana_bar_height": 30,
            "mana_color_range": [(100, 150, 200), (120, 255, 255)]  # HSV
        }
    
    def _check_cv2_availability(self):
        """Проверка доступности OpenCV"""
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV не установлен. Установите: pip install opencv-python")
    
    def _base64_to_image(self, base64_str: str) -> Any:
        """Преобразование base64 в изображение"""
        self._check_cv2_availability()
        
        # Удаление префикса data:image если есть
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        # Декодирование
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Не удалось декодировать изображение")
        
        return image
    
    def _image_to_base64(self, image: Any) -> str:
        """Преобразование изображения в base64"""
        self._check_cv2_availability()
        
        _, buffer = cv2.imencode('.png', image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    
    async def load_template(self, name: str, image_path: str, 
                           threshold: float = 0.8, category: str = "card") -> bool:
        """Загрузка шаблона для распознавания"""
        try:
            self._check_cv2_availability()
            
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if image is None:
                return False
            
            template = Template(
                name=name,
                image=image,
                threshold=threshold,
                category=category
            )
            
            self.templates[name] = template
            self.stats.templates_loaded = len(self.templates)
            
            return True
        except Exception:
            return False
    
    async def load_rank_model(self, model_path: str) -> bool:
        """Загрузка модели для распознавания рангов"""
        try:
            if not CV2_AVAILABLE or pickle is None:
                return False
            
            model_file = Path(model_path)
            if not model_file.exists():
                return False
            
            with open(model_path, 'rb') as f:
                self.rank_model = pickle.load(f)
            
            self.stats.model_loaded = True
            return True
            
        except Exception:
            return False
    
    async def load_unit_references(self, units_dir: str) -> bool:
        """Загрузка референсных данных юнитов"""
        try:
            self._check_cv2_availability()
            
            units_path = Path(units_dir)
            if not units_path.exists():
                return False
            
            self.ref_units = []
            self.ref_colors = []
            
            # Загрузка всех изображений юнитов
            for unit_file in units_path.glob('*.png'):
                unit_image = cv2.imread(str(unit_file))
                if unit_image is not None:
                    # Получение основного цвета юнита
                    colors = self._get_color(unit_image)
                    if len(colors) > 0:
                        self.ref_units.append(unit_file.name)
                        self.ref_colors.append(colors[0])  # Берем самый распространенный цвет
            
            return len(self.ref_units) > 0
            
        except Exception:
            return False
    
    async def train_rank_model(self, training_data_dir: str) -> bool:
        """Обучение модели распознавания рангов"""
        try:
            if not CV2_AVAILABLE or LogisticRegression is None:
                return False
            
            X_train, Y_train = await self._load_training_dataset(training_data_dir)
            if len(X_train) == 0:
                return False
            
            # Обучение логистической регрессии
            self.rank_model = LogisticRegression(max_iter=1000)
            self.rank_model.fit(X_train, Y_train)
            
            self.stats.model_loaded = True
            return True
            
        except Exception:
            return False
    
    async def _load_training_dataset(self, folder: str) -> Tuple[Any, Any]:
        """Загрузка обучающего датасета"""
        X_train = []
        Y_train = []
        
        folder_path = Path(folder)
        if not folder_path.exists():
            return np.array([]), np.array([])
        
        for file_path in folder_path.glob('*.png'):
            try:
                # Загрузка изображения в градациях серого
                img = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    # Детекция краев
                    edges = cv2.Canny(img, 50, 100)
                    X_train.append(edges)
                    
                    # Извлечение метки из имени файла
                    rank_label = file_path.name.split('_')[0]
                    Y_train.append(int(rank_label))
            except (ValueError, IndexError):
                continue
        
        if len(X_train) == 0:
            return np.array([]), np.array([])
        
        X_train = np.array(X_train)
        data_shape = X_train.shape
        X_train = X_train.reshape(data_shape[0], data_shape[1] * data_shape[2])
        Y_train = np.array(Y_train, dtype=int)
        
        return X_train, Y_train
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        """Получение списка загруженных шаблонов"""
        return [template.to_dict() for template in self.templates.values()]
    
    def _get_color(self, image: Any, crop: bool = False) -> Any:
        """Получение наиболее распространенных цветов в изображении"""
        self._check_cv2_availability()
        
        unit_img = image.copy()
        if crop and len(unit_img.shape) == 3:
            # Обрезка центральной части
            h, w = unit_img.shape[:2]
            crop_size = min(90, h-30, w-34)
            start_y = max(0, 15)
            start_x = max(0, 17)
            unit_img = unit_img[start_y:start_y + crop_size, start_x:start_x + crop_size]
        
        # Преобразование BGR в RGB
        if len(unit_img.shape) == 3:
            unit_img = cv2.cvtColor(unit_img, cv2.COLOR_BGR2RGB)
        
        # Сглаживание пикселей
        flat_img = unit_img.reshape(-1, unit_img.shape[2] if len(unit_img.shape) == 3 else 1)
        flat_img_round = flat_img // 20 * 20
        unique, counts = np.unique(flat_img_round, axis=0, return_counts=True)
        
        colors = np.zeros((5, 3), dtype=int)
        if len(unique) < 10:
            return colors
        
        # Сортировка по частоте
        sorted_count = np.sort(counts)[::-1]
        
        # Получение 5 наиболее распространенных цветов
        for i in range(min(5, len(sorted_count))):
            index = np.where(counts == sorted_count[i])[0][0]
            colors[i] = unique[index]
        
        return colors
    
    def _match_unit(self, image: Any) -> Tuple[str, float]:
        """Сопоставление юнита по цвету"""
        if not self.ref_colors or not self.ref_units:
            return 'empty.png', 2001.0
        
        unit_colors = self._get_color(image, crop=True)
        
        # Поиск ближайшего совпадения (среднеквадратичная ошибка)
        for color in unit_colors:
            if len(color) == 3:  # RGB цвет
                mse = np.sum((np.array(self.ref_colors) - color)**2, axis=1)
                min_mse = mse.min()
                # Порог для определения совпадения
                if min_mse <= 2000:
                    best_match_idx = mse.argmin()
                    return self.ref_units[best_match_idx], float(min_mse)
        
        return 'empty.png', 2001.0
    
    def _match_rank(self, image: Any) -> Tuple[int, float]:
        """Определение ранга юнита с помощью машинного обучения"""
        if self.rank_model is None:
            return 0, 0.0
        
        try:
            # Преобразование в градации серого
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Детекция краев
            edges = cv2.Canny(gray, 50, 100)
            
            # Предсказание ранга
            prob = self.rank_model.predict_proba(edges.reshape(1, -1))
            rank = prob.argmax()
            confidence = float(prob.max())
            
            self.stats.rank_predictions += 1
            return rank, round(confidence, 3)
            
        except Exception:
            return 0, 0.0
    
    async def analyze_grid(self, image_base64: str) -> GridAnalysis:
        """Анализ игровой сетки"""
        start_time = datetime.now()
        
        try:
            self._check_cv2_availability()
            
            # Преобразование изображения
            image = self._base64_to_image(image_base64)
            
            # Создание ячеек сетки
            cells = []
            detected_cards = {}
            occupied_count = 0
            
            for row in range(self.grid_config["rows"]):
                for col in range(self.grid_config["cols"]):
                    # Вычисление координат ячейки
                    x = (self.grid_config["grid_start_x"] + 
                         col * (self.grid_config["cell_width"] + self.grid_config["cell_spacing"]))
                    y = (self.grid_config["grid_start_y"] + 
                         row * (self.grid_config["cell_height"] + self.grid_config["cell_spacing"]))
                    
                    # Извлечение области ячейки
                    cell_image = image[y:y+self.grid_config["cell_height"], 
                                     x:x+self.grid_config["cell_width"]]
                    
                    # Анализ ячейки
                    occupied, card_type, confidence = await self._analyze_cell(cell_image)
                    
                    cell = GridCell(
                        x=x, y=y,
                        width=self.grid_config["cell_width"],
                        height=self.grid_config["cell_height"],
                        occupied=occupied,
                        card_type=card_type,
                        confidence=confidence
                    )
                    
                    cells.append(cell)
                    
                    if occupied:
                        occupied_count += 1
                        if card_type:
                            detected_cards[card_type] = detected_cards.get(card_type, 0) + 1
            
            total_cells = len(cells)
            empty_cells = total_cells - occupied_count
            overall_confidence = sum(cell.confidence for cell in cells) / total_cells if cells else 0
            
            analysis = GridAnalysis(
                cells=cells,
                grid_width=self.grid_config["cols"],
                grid_height=self.grid_config["rows"],
                total_cells=total_cells,
                occupied_cells=occupied_count,
                empty_cells=empty_cells,
                detected_cards=detected_cards,
                confidence=overall_confidence
            )
            
            # Обновление статистики
            self.stats.grid_analyses += 1
            self.stats.total_analyses += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_processing_time(processing_time)
            
            return analysis
            
        except Exception as e:
            # В случае ошибки возвращаем пустой анализ
            return GridAnalysis(
                cells=[],
                grid_width=0,
                grid_height=0,
                total_cells=0,
                occupied_cells=0,
                empty_cells=0,
                detected_cards={},
                confidence=0.0
            )
    
    async def _analyze_cell(self, cell_image: Any) -> Tuple[bool, Optional[str], float]:
        """Анализ отдельной ячейки с использованием распознавания юнитов"""
        if cell_image is None or cell_image.size == 0:
            return False, None, 0.0
        
        # Простая проверка на пустоту (по яркости)
        gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Если ячейка слишком темная или слишком светлая - считаем пустой
        if mean_brightness < 30 or mean_brightness > 220:
            return False, None, 0.1
        
        # Сначала пробуем распознавание по цвету (более точное)
        if self.ref_colors and self.ref_units:
            unit_type, color_confidence = self._match_unit(cell_image)
            if unit_type != 'empty.png' and color_confidence <= 2000:
                # Определяем ранг юнита
                rank, rank_confidence = self._match_rank(cell_image)
                
                # Формируем имя с рангом если ранг определен
                if rank > 0 and rank_confidence > 0.5:
                    unit_name = f"{unit_type.replace('.png', '')}_rank_{rank}"
                else:
                    unit_name = unit_type.replace('.png', '')
                
                self.stats.unit_recognitions += 1
                # Инвертируем confidence для цвета (меньше = лучше)
                final_confidence = max(0.1, 1.0 - (color_confidence / 2000.0))
                return True, unit_name, final_confidence
        
        # Fallback: поиск совпадений с шаблонами
        best_match = None
        best_confidence = 0.0
        
        for template_name, template in self.templates.items():
            if template.category == "card":
                # Изменение размера шаблона под размер ячейки
                template_resized = cv2.resize(template.image, 
                                            (cell_image.shape[1], cell_image.shape[0]))
                
                # Сравнение шаблонов
                result = cv2.matchTemplate(cell_image, template_resized, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                
                if max_val > best_confidence and max_val > template.threshold:
                    best_confidence = max_val
                    best_match = template_name
        
        if best_match:
            self.stats.template_matches += 1
            return True, best_match, best_confidence
        
        # Если ничего не найдено, но ячейка не пустая
        return True, "unknown", 0.5
    
    async def analyze_mana(self, image_base64: str) -> ManaAnalysis:
        """Анализ уровня маны"""
        start_time = datetime.now()
        
        try:
            self._check_cv2_availability()
            
            # Преобразование изображения
            image = self._base64_to_image(image_base64)
            
            # Извлечение области маны
            mana_x = self.mana_config["mana_bar_x"]
            mana_y = self.mana_config["mana_bar_y"]
            mana_w = self.mana_config["mana_bar_width"]
            mana_h = self.mana_config["mana_bar_height"]
            
            mana_region = image[mana_y:mana_y+mana_h, mana_x:mana_x+mana_w]
            
            # Преобразование в HSV для лучшего определения цвета маны
            hsv = cv2.cvtColor(mana_region, cv2.COLOR_BGR2HSV)
            
            # Создание маски для цвета маны
            lower_bound = np.array(self.mana_config["mana_color_range"][0])
            upper_bound = np.array(self.mana_config["mana_color_range"][1])
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            
            # Подсчет пикселей маны
            mana_pixels = cv2.countNonZero(mask)
            total_pixels = mana_w * mana_h
            mana_percentage = (mana_pixels / total_pixels) * 100
            
            # Примерный расчет маны (предполагаем максимум 10)
            max_mana = 10
            current_mana = int((mana_percentage / 100) * max_mana)
            
            # Уверенность основана на четкости границ
            confidence = min(mana_percentage / 50, 1.0)  # Нормализация
            
            analysis = ManaAnalysis(
                current_mana=current_mana,
                max_mana=max_mana,
                mana_percentage=mana_percentage,
                confidence=confidence
            )
            
            # Обновление статистики
            self.stats.mana_analyses += 1
            self.stats.total_analyses += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_processing_time(processing_time)
            
            return analysis
            
        except Exception as e:
            # В случае ошибки возвращаем нулевые значения
            return ManaAnalysis(
                current_mana=0,
                max_mana=10,
                mana_percentage=0.0,
                confidence=0.0
            )
    
    async def recognize_unit(self, image_base64: str) -> UnitRecognition:
        """Распознавание типа и ранга юнита"""
        try:
            self._check_cv2_availability()
            
            # Преобразование изображения
            image = self._base64_to_image(image_base64)
            
            # Распознавание типа юнита
            unit_type, color_confidence = self._match_unit(image)
            
            # Распознавание ранга
            rank, rank_confidence = self._match_rank(image)
            
            # Общая уверенность
            overall_confidence = min(1.0 - (color_confidence / 2000.0), rank_confidence) if rank > 0 else 1.0 - (color_confidence / 2000.0)
            
            # Обновление статистики
            self.stats.unit_recognitions += 1
            if rank > 0:
                self.stats.rank_predictions += 1
            
            # Определение позиции (центр изображения)
            h, w = image.shape[:2]
            position = (w // 2, h // 2)
            
            return UnitRecognition(
                unit_type=unit_type.replace('.png', '') if unit_type != 'empty.png' else 'empty',
                confidence=max(0.0, overall_confidence),
                rank=rank,
                rank_confidence=rank_confidence,
                position=position
            )
            
        except Exception as e:
            return UnitRecognition(
                unit_type="unknown",
                confidence=0.0,
                rank=0,
                rank_confidence=0.0,
                position=(0, 0)
            )
    
    def _update_processing_time(self, processing_time: float):
        """Обновление времени обработки"""
        self.processing_times.append(processing_time)
        
        # Ограничиваем историю последними 100 измерениями
        if len(self.processing_times) > 100:
            self.processing_times = self.processing_times[-100:]
        
        # Обновляем среднее время
        self.stats.average_processing_time = sum(self.processing_times) / len(self.processing_times)
    
    def _extract_cell_image(self, image: Any, row: int, col: int) -> Optional[Any]:
        """Извлечение изображения ячейки по координатам"""
        try:
            x = (self.grid_config["grid_start_x"] + 
                 col * (self.grid_config["cell_width"] + self.grid_config["cell_spacing"]))
            y = (self.grid_config["grid_start_y"] + 
                 row * (self.grid_config["cell_height"] + self.grid_config["cell_spacing"]))
            
            cell_image = image[y:y+self.grid_config["cell_height"], 
                             x:x+self.grid_config["cell_width"]]
            
            return cell_image if cell_image.size > 0 else None
        except Exception:
            return None
    
    async def analyze_grid_status(self, image_base64: str) -> Dict[str, Any]:
        """Анализ статуса игровой сетки с распознаванием юнитов"""
        try:
            # Сначала выполняем обычный анализ сетки
            grid_analysis = await self.analyze_grid(image_base64)
            
            # Дополнительно анализируем каждую занятую ячейку
            unit_details = []
            image = self._base64_to_image(image_base64)
            
            if image is not None and grid_analysis.cells:
                for i, cell in enumerate(grid_analysis.cells):
                    if cell.occupied and cell.card_type != "unknown":
                        # Извлекаем изображение ячейки
                        row = i // self.grid_config['cols']
                        col = i % self.grid_config['cols']
                        cell_image = self._extract_cell_image(image, row, col)
                        
                        if cell_image is not None:
                            # Распознаем юнит
                            cell_base64 = self._image_to_base64(cell_image)
                            unit_recognition = await self.recognize_unit(cell_base64)
                            unit_details.append({
                                'position': {'row': row, 'col': col},
                                'unit_type': unit_recognition.unit_type,
                                'rank': unit_recognition.rank,
                                'confidence': unit_recognition.confidence
                            })
            
            return {
                'grid_analysis': grid_analysis.to_dict(),
                'unit_details': unit_details,
                'total_units': len([cell for cell in grid_analysis.cells if cell.occupied]),
                'recognized_units': len(unit_details),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики сервиса"""
        return self.stats.to_dict()
    
    async def clear_cache(self):
        """Очистка кэша"""
        self.cache.clear()
        self.stats.cache_hits = 0
        self.stats.cache_misses = 0
    
    async def update_grid_config(self, config: Dict[str, Any]):
        """Обновление конфигурации сетки"""
        for key, value in config.items():
            if key in self.grid_config:
                self.grid_config[key] = value
    
    async def update_mana_config(self, config: Dict[str, Any]):
        """Обновление конфигурации маны"""
        for key, value in config.items():
            if key in self.mana_config:
                self.mana_config[key] = value
    
    async def save_model(self, model_path: str) -> bool:
        """Сохранение обученной модели"""
        try:
            if self.rank_model is None or pickle is None:
                return False
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.rank_model, f)
            
            return True
        except Exception:
            return False
    
    async def get_grid_config(self) -> Dict[str, Any]:
        """Получение текущей конфигурации сетки"""
        return self.grid_config.copy()
    
    async def get_mana_config(self) -> Dict[str, Any]:
        """Получение текущей конфигурации маны"""
        return self.mana_config.copy()
    
    async def add_training_data(self, image_base64: str, rank: int) -> bool:
        """Добавление обучающих данных для модели распознавания рангов"""
        try:
            if cv2 is None:
                return False
            
            # Преобразование изображения
            image = self._base64_to_image(image_base64)
            if image is None:
                return False
            
            # Извлечение признаков (как в _match_rank)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            features = edges.flatten()
            
            # Сохранение в файл обучающих данных
            training_file = "training_data.csv"
            
            # Создание DataFrame
            if pd is not None:
                data = {
                    'rank': [rank],
                    **{f'feature_{i}': [features[i]] for i in range(len(features))}
                }
                df = pd.DataFrame(data)
                
                # Добавление к существующим данным или создание нового файла
                try:
                    existing_df = pd.read_csv(training_file)
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                except FileNotFoundError:
                    combined_df = df
                
                combined_df.to_csv(training_file, index=False)
                return True
            
            return False
            
        except Exception:
            return False
    
    async def quick_train_model(self, training_file: str = "training_data.csv") -> bool:
        """Быстрое обучение модели на основе сохраненных данных"""
        try:
            if pd is None or LogisticRegression is None:
                return False
            
            # Загрузка обучающих данных
            try:
                df = pd.read_csv(training_file)
            except FileNotFoundError:
                return False
            
            if len(df) < 2:  # Минимум данных для обучения
                return False
            
            # Подготовка данных
            X = df.drop('rank', axis=1).values
            y = df['rank'].values
            
            # Обучение модели
            self.rank_model = LogisticRegression(max_iter=1000, random_state=42)
            self.rank_model.fit(X, y)
            
            # Обновление статистики
            self.stats.model_loaded = True
            
            return True
            
        except Exception:
            return False
    
    async def get_training_stats(self) -> Dict[str, Any]:
        """Получение статистики обучающих данных"""
        try:
            training_file = "training_data.csv"
            if pd is None:
                return {'error': 'Pandas not available'}
            
            try:
                df = pd.read_csv(training_file)
                rank_counts = df['rank'].value_counts().to_dict()
                
                return {
                    'total_samples': len(df),
                    'rank_distribution': rank_counts,
                    'unique_ranks': len(rank_counts),
                    'model_trained': self.stats.model_loaded
                }
            except FileNotFoundError:
                return {
                    'total_samples': 0,
                    'rank_distribution': {},
                    'unique_ranks': 0,
                    'model_trained': self.stats.model_loaded
                }
                
        except Exception as e:
            return {'error': str(e)}

# Глобальный экземпляр сервиса
vision_service = VisionService()