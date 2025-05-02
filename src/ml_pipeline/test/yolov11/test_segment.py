import os
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO


class ImageSegmentation:
    def __init__(self, model_path: str, save_dir: str):
        self.model = YOLO(model_path)  # Загрузка модели
        self.save_dir = save_dir  # Путь для сохранения масок
        os.makedirs(self.save_dir, exist_ok=True)  # Создаём директорию для масок

    def segment_image(self, image: np.array, save_filename: str):
        # Преобразуем изображение в формате BGR (если это нужно) для YOLO
        results = self.model(image, task="segment")

        # Сохранение масок, если они есть
        if results[0].masks is not None:
            masks = results[0].masks.data.cpu().numpy()  # [N, H, W]
            orig_shape = results[0].orig_shape  # Исходная форма изображения

            # Суммируем все маски по оси 0
            combined_mask = np.sum(masks, axis=0)
            combined_mask = (combined_mask > 0).astype(np.uint8) * 255  # Преобразуем в чёрно-белую

            # Приводим к оригинальному размеру изображения
            combined_mask_resized = cv2.resize(combined_mask, (orig_shape[1], orig_shape[0]))

            # Сохраняем итоговую объединённую маску
            mask_path = os.path.join(self.save_dir, save_filename)
            print(f"3 {save_filename}")
            cv2.imwrite(mask_path, combined_mask_resized)
            print(f"Маска сохранена: {mask_path}")
            return Image.fromarray(combined_mask_resized)
        else:
            print("Маски не обнаружены.")
            print(results)
            return None

        # if results[0].masks is not None:
        #     masks = results[0].masks.data.cpu().numpy()  # [N, H, W]
        #     orig_shape = results[0].orig_shape  # Исходная форма изображения
        #
        #     # Создаем список для хранения масок
        #     mask_list = []
        #
        #     for i in range(masks.shape[0]):
        #         mask = masks[i]
        #         mask = (mask > 0).astype(np.uint8) * 255  # Преобразуем в чёрно-белую
        #
        #         # Приводим к оригинальному размеру изображения
        #         mask_resized = cv2.resize(mask, (orig_shape[1], orig_shape[0]))
        #
        #         # Сохраняем маску в список
        #         mask_list.append(Image.fromarray(mask_resized))
        #
        #         # Сохраняем итоговую маску на диск, если нужно
        #         mask_path = os.path.join(self.save_dir, f"{save_filename}_{i}.png")
        #         cv2.imwrite(mask_path, mask_resized)
        #         print(f"Маска сохранена: {mask_path}")
        #
        #     return mask_list  # Возвращаем список масок
        # else:
        #     print("Маски не обнаружены.")
        #     print(results)
        #     return None

    def segment_image_from_path(self, image_path: str):
        # Загружаем изображение из пути
        image = cv2.imread(image_path)
        self.segment_image(image, self.save_dir + r"\photo.jpg")


if __name__ == '__main__':
    image_segmentation_v1 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\results\yolo_best.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\test\yolov11\new_test\v1"

    )
    image_segmentation_v2 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\results\yolo_best_v2.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\test\yolov11\new_test\v2"
    )
    image_segmentation_v3 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\results\yolo_best_v3.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\test\yolov11\new_test\v3"
    )
    image_segmentation_v4 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\results\yolo_best_v4.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\test\yolov11\new_test\v4"
    )

    image_segmentation_v1.segment_image_from_path(r"D:\Projects\Python\diploma_project\src\ml_pipeline\dataset2\images\train\050011.jpg")
    image_segmentation_v2.segment_image_from_path(r"D:\Projects\Python\diploma_project\src\ml_pipeline\dataset2\images\train\050011.jpg")
    image_segmentation_v3.segment_image_from_path(r"D:\Projects\Python\diploma_project\src\ml_pipeline\dataset2\images\train\050011.jpg")
    image_segmentation_v4.segment_image_from_path(r"D:\Projects\Python\diploma_project\src\ml_pipeline\dataset2\images\train\050011.jpg")
