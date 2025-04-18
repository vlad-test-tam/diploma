import os
import uuid
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

    def generate_unique_filename(self, original_filename: str) -> str:
        ext = original_filename.split('.')[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex
        return f"{timestamp}_{unique_id}.{ext}"

    def handle_processing(self, st, upload_folder, filename):
        processed_image, masked_image = self.image_processing(st.session_state.uploaded_image, upload_folder, filename)
        st.session_state.original_image = st.session_state.uploaded_image
        st.session_state.masked_image = masked_image
        st.session_state.result_image = processed_image

        defected_image = Image.open(st.session_state.original_image)
        defected_image.save(upload_folder + "/defected/" + filename)
        st.session_state.result_image.save(upload_folder + "/fixed/" + filename)
