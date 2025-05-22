from typing import Union, List, Tuple

import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
import random


class DatasetTransformer:
    def __init__(
            self, rotation_angles: Union[List[int], None] = None,
            brightness_range: tuple = (0.5, 1.5)
    ) -> None:
        self.rotation_angles = rotation_angles if rotation_angles is not None else [15, 30, 45, 60]
        self.brightness_range = brightness_range

    def rotate_image(self, image: Image.Image, angle: int) -> Image.Image:
        return image.rotate(angle, expand=False)

    def change_brightness(self, image: Image.Image) -> Tuple[Image.Image, float]:
        factor = random.uniform(*self.brightness_range)
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor), factor

    def flip_image(self, image: Image.Image) -> Tuple[Image.Image, bool]:
        if random.random() > 0.5:
            return image.transpose(Image.FLIP_LEFT_RIGHT), True
        return image, False

    def augment(self, image, yolo_labels):
        image, flipped = self.flip_image(image)

        angle = random.choice(self.rotation_angles)
        if random.random() > 0.5:
            angle = -angle
        image = self.rotate_image(image, -angle)

        width, height = image.size
        image, brightness_factor = self.change_brightness(image)
        new_labels = []
        for label in yolo_labels:
            class_id = int(label[0])
            points = label[1:]
            new_points = []

            for i in range(0, len(points), 2):
                x = points[i] * width
                y = points[i + 1] * height

                if flipped:
                    x = width - x

                x, y = self.rotate_point(x, y, angle, width / 2, height / 2)

                x /= width
                y /= height
                new_points.extend([x, y])

            new_labels.append([class_id] + new_points)

        return image, new_labels

    def rotate_point(
            self, x: float, y: float, angle: int,
            cx: float, cy: float
    ) -> Tuple[float, float]:
        angle_rad = np.deg2rad(angle)
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        x_new = cos_angle * (x - cx) - sin_angle * (y - cy) + cx
        y_new = sin_angle * (x - cx) + cos_angle * (y - cy) + cy
        return x_new, y_new

    def save_mask(self, image, labels, output_mask_path):
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)

        for label in labels:
            class_id = int(label[0])
            points = label[1:]

            polygon = []
            for i in range(0, len(points), 2):
                x = points[i] * image.width
                y = points[i + 1] * image.height
                polygon.append((x, y))

            if len(polygon) >= 3:
                draw.polygon(polygon, fill=255)

        mask.save(output_mask_path)


# Пример использования
if __name__ == "__main__":
    image_path = r"D:\Projects\Python\diploma_project\src\ml_pipeline\images\dataset\images\train\000035.jpg"
    labels_path = r"D:\Projects\Python\diploma_project\src\ml_pipeline\images\dataset\labels\train\000035.txt"

    image = Image.open(image_path)
    with open(labels_path, 'r') as f:
        yolo_labels = [list(map(float, line.strip().split())) for line in f.readlines()]

    transformer = DatasetTransformer(rotation_angles=[15, 30, 45, 60])
    augmented_image, augmented_labels = transformer.augment(image, yolo_labels)

    augmented_image.show()
    transformer.save_mask(augmented_image, augmented_labels, "output_mask.png")