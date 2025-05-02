import os
import shutil
import uuid
from datetime import datetime

from src.entities.image import ImageAddDTO
from src.repositories.image_repository import ImageRepository
from src.repositories.user_repository import UserRepository
from src.settings.ml_settings import ml_settings
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

    def add_image(self, user_id, is_liked, temp_folder, upload_folder, filename):
        self.save_temp_image(temp_folder, upload_folder, filename)
        image_data = ImageAddDTO(
            user_id=user_id,
            fix_datetime=datetime.now(),
            is_liked=is_liked,
            defected_path=os.path.join(upload_folder, "defected", filename),
            fixed_path=os.path.join(upload_folder, "fixed", filename),
            masked_path=os.path.join(upload_folder, "masked", filename),
            segmented_path=os.path.join(upload_folder, "segmented", filename)
        )
        self.image_repo.add_image(image_data)

    def decrease_attempts_count(self, user_id):
        return self.user_repo.decrease_attempts_count(user_id)

    def image_processing(self, uploaded_image, filepath, filename):
        image = Image.open(uploaded_image).convert('RGB')
        image_np = np.array(image)

        mask_filepath = os.path.join(filepath, "masked")
        path_to_weights = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ml_settings.path_to_yolo)
        segmentation = ImageSegmentation(path_to_weights, mask_filepath)
        masked_image = segmentation.segment_image(image_np, filename)
        print(f"2 {filename}")
        mask_np = np.array(masked_image)

        inpainting = Inpainting(image=image_np, mask=mask_np)
        inpainted_image = inpainting.inpaint()
        # inpainted_image = Image.open(inpainting.out)

        return inpainted_image, masked_image

    def generate_unique_filename(self, original_filename: str) -> str:
        ext = original_filename.split('.')[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex
        return f"{timestamp}_{unique_id}.{ext}"

    def handle_processing(self, st, upload_folder, filename):
        print(f"1 {filename}")
        processed_image, masked_image = self.image_processing(st.session_state.uploaded_image, upload_folder, filename)
        print(f"4 {filename}")
        st.session_state.original_image = st.session_state.uploaded_image
        st.session_state.masked_image = masked_image
        st.session_state.result_image = processed_image

        defected_image = Image.open(st.session_state.original_image)
        defected_image.save(upload_folder + "/defected/" + filename)
        st.session_state.result_image.save(upload_folder + "/fixed/" + filename)

    def delete_temp_image(self, temp_folder, filename):
        defected_file_path = os.path.join(temp_folder, "defected", filename)
        fixed_file_path = os.path.join(temp_folder, "fixed", filename)
        masked_file_path = os.path.join(temp_folder, "masked", filename)
        segmented_file_path = os.path.join(temp_folder, "segmented", filename)

        files_to_remove = [defected_file_path, fixed_file_path, masked_file_path, segmented_file_path]

        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)

    def save_temp_image(self, temp_folder, upload_folder, filename):
        defected_file_path = os.path.join(temp_folder, "defected", filename)
        fixed_file_path = os.path.join(temp_folder, "fixed", filename)
        masked_file_path = os.path.join(temp_folder, "masked", filename)
        segmented_file_path = os.path.join(temp_folder, "segmented", filename)

        upload_defected_path = os.path.join(upload_folder, "defected", filename)
        upload_fixed_path = os.path.join(upload_folder, "fixed", filename)
        upload_masked_path = os.path.join(upload_folder, "masked", filename)
        upload_segmented_path = os.path.join(upload_folder, "segmented", filename)

        files_to_copy = [
            (defected_file_path, upload_defected_path),
            (fixed_file_path, upload_fixed_path),
            (masked_file_path, upload_masked_path),
            (segmented_file_path, upload_segmented_path)
        ]

        for original_path, destination_path in files_to_copy:
            if os.path.exists(original_path):
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                shutil.copy(original_path, destination_path)
