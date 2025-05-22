from pathlib import Path
from typing import Any, Dict

from ultralytics import YOLO


# Загрузка модели для сегментации
class SegmentationTrainer:

    def __init__(self, model_path: str = 'yolov11n-seg.pt'):
        """
        Инициализация тренера YOLO.

        Args:
            model_path: Путь к предобученной модели (.pt файл) или версия модели (например, 'yolov8n-seg.pt')
        """
        self.model = YOLO(model_path)
        self._check_device()

    def _check_device(self) -> None:
        """Проверяет доступность GPU и выводит информацию об устройстве."""
        from torch import cuda
        self.device = 'cuda' if cuda.is_available() else 'cpu'
        print(f"Используется устройство: {self.device.upper()}")

    def train(
            self,
            data_config: str,
            epochs: int = 100,
            image_size: int = 640,
            batch_size: int = 16,
            task: str = 'segment',
            **kwargs
    ) -> Dict[str, Any]:
        """
        Обучение модели сегментации.

        Args:
            data_config: Путь к YAML-файлу с конфигурацией данных
            epochs: Количество эпох
            image_size: Размер изображения (квадрат)
            batch_size: Размер батча
            task: Тип задачи ('segment' для сегментации)
            **kwargs: Дополнительные параметры для YOLO.train()

        Returns:
            Словарь с результатами обучения
        """
        if not Path(data_config).exists():
            raise FileNotFoundError(f"Файл конфигурации {data_config} не найден")

        results = self.model.train(
            data=data_config,
            epochs=epochs,
            imgsz=image_size,
            batch=batch_size,
            task=task,
            device=self.device,
            **kwargs
        )

        print(f"Обучение завершено. Результаты сохранены в {self.model.save_dir}")
        return results
