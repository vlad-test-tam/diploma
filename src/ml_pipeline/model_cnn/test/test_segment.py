import os
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO


class ImageSegmentation:
    def __init__(self, model, save_segment_dir: str, save_mask_dir: str):
        self.model = model
        self.save_segment_dir = save_segment_dir
        self.save_mask_dir = save_mask_dir
        os.makedirs(self.save_mask_dir, exist_ok=True)
        os.makedirs(self.save_segment_dir, exist_ok=True)

    def segment_image(self, image: np.array, save_filename: str):
        # Преобразуем изображение в формате BGR (если это нужно) для YOLO
        results = self.model(image, task="segment")

        # Сохранение масок, если они есть
        if results[0].masks is not None:
            segment_image = results[0].plot()
            segment_path = os.path.join(self.save_segment_dir, save_filename)
            cv2.imwrite(segment_path, cv2.cvtColor(segment_image, cv2.COLOR_RGB2BGR))

            masks = results[0].masks.data.cpu().numpy()  # [N, H, W]
            orig_shape = results[0].orig_shape

            combined_mask = np.any(masks, axis=0).astype(np.uint8) * 255

            if masks.shape[1:] != orig_shape:
                combined_mask = cv2.resize(
                    combined_mask,
                    (orig_shape[1], orig_shape[0]),
                    interpolation=cv2.INTER_NEAREST
                )
            mask_path = os.path.join(self.save_mask_dir, save_filename)
            cv2.imwrite(mask_path, combined_mask)
            return Image.fromarray(cv2.cvtColor(segment_image, cv2.COLOR_RGB2BGR)), Image.fromarray(combined_mask)
        else:
            print("Маски не обнаружены.")
            print(results)
            return None

    def segment_image_from_path(self, image_path: str):
        # Загружаем изображение из пути
        image = cv2.imread(image_path)
        self.segment_image(image, "photo.jpg")


if __name__ == '__main__':
    image_segmentation_v1 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\results\yolo_best.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\test\v1",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\mask\v1"

    )
    image_segmentation_v2 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\results\yolo_best_v2.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\test\v2",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\mask\v2"
    )
    image_segmentation_v3 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\results\yolo_best_v3.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\test\v3",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\mask\v3"
    )
    image_segmentation_v4 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\results\yolo_best_v4.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\test\v4",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\mask\v4"
    )

    image_segmentation_v5 = ImageSegmentation(
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\results\weights.pt",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\test\v5",
        r"D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\mask\v5"
    )

    image_segmentation_v1.segment_image_from_path(r"D:\Dataset\dataset1\defected\pics\test_scratch\002159.jpg")
    image_segmentation_v2.segment_image_from_path(r"D:\Dataset\dataset1\defected\pics\test_scratch\002159.jpg")
    image_segmentation_v3.segment_image_from_path(r"D:\Dataset\dataset1\defected\pics\test_scratch\002159.jpg")
    image_segmentation_v4.segment_image_from_path(r"D:\Dataset\dataset1\defected\pics\test_scratch\002159.jpg")
    image_segmentation_v5.segment_image_from_path(r"D:\Dataset\dataset1\defected\pics\test_scratch\002159.jpg")
