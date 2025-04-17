import json
import os
import time

import cv2
import numpy as np

from src.ml_pipeline.preprocessing.defects_generator.scratch_generator import ScratchGenerator


class PicsProcessor:
    def __init__(self, source_dir: str, images_dir: str, labels_dir: str, masks_dir: str, train_images_num: int = 10000):
        self.source_dir = source_dir
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.masks_dir = masks_dir
        self.train_images_num = train_images_num
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.labels_dir, exist_ok=True)
        os.makedirs(self.masks_dir, exist_ok=True)

    def process_images(self):
        """Обрабатывает все изображения в исходном каталоге."""
        current_image_num = 0
        for filename in os.listdir(self.source_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_path = os.path.join(self.source_dir, filename)
                self._process_image(image_path, filename, current_image_num)
                current_image_num += 1

    def _process_image(self, source_path: str, filename: str, current_image_num: int):
        """Обрабатывает одно изображение и сохраняет результат."""
        # Генерация дефектов
        generator = ScratchGenerator(source_path)
        generator.generate_defects()

        if current_image_num < self.train_images_num:
            images_path = os.path.join(self.images_dir, "train")
            labels_path = os.path.join(self.labels_dir, "train")
            masks_path = os.path.join(self.masks_dir, "train")

        else:
            images_path = os.path.join(self.images_dir, "val")
            labels_path = os.path.join(self.labels_dir, "val")
            masks_path = os.path.join(self.masks_dir, "val")

        images_path = os.path.join(images_path, filename)
        masks_path = os.path.join(masks_path, filename)
        base_name = os.path.splitext(os.path.basename(masks_path))[0]
        labels_path = os.path.join(labels_path, f"{base_name}.txt")

        cv2.imwrite(images_path, generator.defected_image)

        yolo_lines = self._mask_to_yolo_format(generator.defect_mask, filename)

        # Сохранение маски
        cv2.imwrite(masks_path, generator.defect_mask)

        # Сохранение аннотации в YOLO формате

        with open(labels_path, 'w') as f:
            f.write("\n".join(yolo_lines))
        print(f"Image {filename} has been processed")

    def _mask_to_yolo_format(self, mask: np.ndarray, filename: str):
        """Преобразует маску в формат YOLO и возвращает аннотацию."""
        class_id = 0  # Если один класс, можно оставить 0

        # Убедимся, что маска в градациях серого
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        h, w = mask.shape

        # Бинаризация (на случай если не строго 0 и 255)
        _, binary_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        # Поиск контуров
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        yolo_lines = []

        for contour in contours:
            if len(contour) < 3:
                continue  # Пропускаем слишком маленькие области

            # Нормализация координат
            points = contour.squeeze()
            if len(points.shape) != 2:
                continue

            norm_points = [(x / w, y / h) for x, y in points]
            line = f"{class_id} " + " ".join(f"{x:.6f} {y:.6f}" for x, y in norm_points)
            yolo_lines.append(line)

        return yolo_lines


if __name__ == '__main__':
    processor = PicsProcessor(
        r'D:\Projects\Python\diploma_project\src\ml_pipeline\original_images\yolov11\scratch',
        r'D:\Projects\Python\diploma_project\src\ml_pipeline\dataset\images',
        r'D:\Projects\Python\diploma_project\src\ml_pipeline\dataset\labels',
        r'D:\Projects\Python\diploma_project\src\ml_pipeline\dataset\masks'
    )
    processor.process_images()
