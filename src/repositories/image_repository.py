import os
from typing import Optional

from sqlalchemy.orm import Session

from src.entities.image import ImageDTO, ImageAddDTO
from src.models.image import Image


class ImageRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_image(self, image_data: ImageAddDTO) -> ImageDTO:
        db_image = Image(
            user_id=image_data.user_id,
            fix_datetime=image_data.fix_datetime,
            is_liked=image_data.is_liked,
            defected_path=image_data.defected_path,
            fixed_path=image_data.fixed_path,
            masked_path=image_data.masked_path,
            segmented_path=image_data.segmented_path
        )
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)

        return ImageDTO(
            id=db_image.id,
            user_id=db_image.user_id,
            fix_datetime=db_image.fix_datetime,
            is_liked=db_image.is_liked,
            defected_path=db_image.defected_path,
            fixed_path=db_image.fixed_path,
            masked_path=db_image.masked_path,
            segmented_path=db_image.segmented_path
        )

    def get_image_by_id(self, image_id: int) -> Optional[ImageDTO]:
        db_image = self.db.query(Image).filter(Image.id == image_id).first()

        if not db_image:
            return None

        return ImageDTO(
            id=db_image.id,
            user_id=db_image.user_id,
            fix_datetime=db_image.fix_datetime,
            is_liked=db_image.is_liked,
            defected_path=db_image.defected_path,
            fixed_path=db_image.fixed_path,
            masked_path=db_image.masked_path,
            segmented_path=db_image.segmented_path
        )

    def get_user_images(self, user_id: int) -> list[ImageDTO]:
        db_images = self.db.query(Image).filter(Image.user_id == user_id).all()

        return [
            ImageDTO(
                id=image.id,
                user_id=image.user_id,
                fix_datetime=image.fix_datetime,
                is_liked=image.is_liked,
                defected_path=image.defected_path,
                fixed_path=image.fixed_path,
                masked_path=image.masked_path,
                segmented_path=image.segmented_path
            )
            for image in db_images
        ]

    def toggle_like_status(self, image_id: int) -> Optional[bool]:
        db_image = self.db.query(Image).filter(Image.id == image_id).first()

        if not db_image:
            return None

        # Меняем статус
        db_image.is_liked = not db_image.is_liked
        self.db.commit()

        return db_image.is_liked

    def delete_image_by_id(self, image_id: int) -> bool:
        image = self.db.query(Image).filter(Image.id == image_id).first()
        if not image:
            return False
        try:
            for file_path in [
                image.defected_path,
                image.fixed_path,
                image.masked_path,
                image.segmented_path
            ]:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            self.db.delete(image)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Ошибка при удалении изображения: {str(e)}")