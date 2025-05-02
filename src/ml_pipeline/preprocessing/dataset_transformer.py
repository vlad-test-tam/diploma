import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
import random


class DatasetTransformer:
    def __init__(self, rotation_angles=None, brightness_range=(0.5, 1.5)):
        self.rotation_angles = rotation_angles if rotation_angles is not None else [15, 30, 45, 60]
        self.brightness_range = brightness_range

    def rotate_image(self, image, angle):
        return image.rotate(angle, expand=False)

    def change_brightness(self, image):
        factor = random.uniform(*self.brightness_range)
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor), factor

    def flip_image(self, image):
        if random.random() > 0.5:
            return image.transpose(Image.FLIP_LEFT_RIGHT), True
        return image, False

    def augment(self, image, yolo_labels):
        # Flip the image
        image, flipped = self.flip_image(image)

        # Rotate the image using fixed angles
        angle = random.choice(self.rotation_angles)
        if random.random() > 0.5:
            angle = -angle
        image = self.rotate_image(image, angle)

        width, height = image.size  # получить размер уже после всех трансформаций

        # Change brightness
        image, brightness_factor = self.change_brightness(image)

        # Update YOLO segmentation labels
        new_labels = []
        for label in yolo_labels:
            class_id = int(label[0])
            points = label[1:]
            new_points = []

            for i in range(0, len(points), 2):
                x = points[i] * width
                y = points[i + 1] * height

                # Flip
                if flipped:
                    x = width - x

                # Rotate
                x, y = self.rotate_point(x, y, angle, width / 2, height / 2)

                # Normalize back
                x /= width
                y /= height
                new_points.extend([x, y])

            new_labels.append([class_id] + new_points)

        return image, new_labels

    def rotate_point(self, x, y, angle, cx, cy):
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

            # Преобразуем нормализованные координаты в пиксельные
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
    image_path = r"D:\Projects\Python\diploma_project\src\ml_pipeline\dataset2\images\train\050000.jpg"
    labels_path = r"D:\Projects\Python\diploma_project\src\ml_pipeline\dataset2\labels\train\050000.txt"

    image = Image.open(image_path)
    with open(labels_path, 'r') as f:
        yolo_labels = [list(map(float, line.strip().split())) for line in f.readlines()]

    transformer = DatasetTransformer(rotation_angles=[15, 30, 45, 60])
    augmented_image, augmented_labels = transformer.augment(image, yolo_labels)

    augmented_image.show()
    transformer.save_mask(augmented_image, augmented_labels, "output_mask.png")