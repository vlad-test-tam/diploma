import os
from datetime import datetime

from src.entities.image import ImageAddDTO
from src.repositories.image_repository import ImageRepository
from src.repositories.user_repository import UserRepository
from src.utils.database import session
from PIL import Image
import numpy as np

from src.ml_pipeline.test.deepfill.test import Inpainting
from src.ml_pipeline.test.yolov11.test_segment import ImageSegmentation

user_repository = UserRepository(session)
image_repository = ImageRepository(session)


class MainService:
    def __init__(self, user_repo: UserRepository = user_repository, image_repo: ImageRepository = image_repository):
        self.user_repo = user_repo
        self.image_repo = image_repo

    # TODO остановился здесь
    def add_image(self, user_id, is_liked, defected_path, segmented_path, masked_path, fixed_path):
        image_data = ImageAddDTO(
            user_id=user_id,
            fix_datetime=datetime.now(),
            is_liked=is_liked,
            defected_path=defected_path,
            fixed_path=segmented_path,
            masked_path=masked_path,
            segmented_path=fixed_path
        )

        self.image_repo.add_image(image_data)

    def decrease_attempts_count(self, user_id):
        return self.user_repo.decrease_attempts_count(user_id)

    def image_processing(self, uploaded_image, filepath, filename):
        # Открытие изображения и маски
        image = Image.open(uploaded_image)

        # Преобразуем изображения в np.array для сегментации
        image_np = np.array(image)

        # Сегментация (можно заменить на вашу логику сегментации)
        mask_filepath = os.path.join(filepath, "masked")
        segmentation = ImageSegmentation(
            r"D:\Projects\Python\diploma_project\src\ml_pipeline\results\yolo_best.pt",
            mask_filepath
        )
        masked_image = segmentation.segment_image(image_np, filename)
        mask_np = np.array(masked_image)

        # Инстанцируем объект Inpainting для восстановления
        inpainting = Inpainting(image=image_np, mask=mask_np, out="output_inpainting.png")

        # Восстановление изображения
        inpainting.inpaint()

        # Открытие восстановленного изображения
        inpainted_image = Image.open(inpainting.out)

        return inpainted_image, masked_image
