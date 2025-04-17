import numpy as np
from PIL import Image

def create_segmentation_mask(yolo_file, image_shape):
    # Создаем пустую маску
    mask = np.zeros(image_shape, dtype=np.uint8)

    with open(yolo_file, 'r') as file:
        for line in file:
            data = list(map(float, line.strip().split()))
            # Предполагаем, что первый элемент - это класс, остальные - координаты
            coords = data[1:]  # Координаты в формате [x_center, y_center, width, height, ...]
            # Преобразовываем относительные координаты в абсолютные
            for i in range(0, len(coords), 2):
                x_center = int(coords[i] * image_shape[1])
                y_center = int(coords[i + 1] * image_shape[0])
                # Рисуем точку в маске
                mask[y_center, x_center] = 255

    return mask

def save_mask(mask, output_file):
    img = Image.fromarray(mask)
    img.save(output_file)

# Пример использования
txt_file = r'D:\Projects\Python\diploma_application\src\ml_pipeline\dataset\labels\train\000003.txt'  # Путь к вашему текстовому файлу
image_shape = (375, 500)      # Размеры изображения (высота, ширина)
output_file = 'segmentation_mask.png'

mask = create_segmentation_mask(txt_file, image_shape)
save_mask(mask, output_file)
