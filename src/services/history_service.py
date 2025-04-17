from src.repositories.image_repository import ImageRepository
from src.repositories.user_repository import UserRepository
from src.utils.database import session

user_repository = UserRepository(session)
image_repository = ImageRepository(session)


class HistoryService:
    def __init__(self, user_repo: UserRepository = user_repository, image_repo: ImageRepository = image_repository):
        self.user_repo = user_repo
        self.image_repo = image_repo

    def get_images_by_user_id(self, user_id):
        return self.image_repo.get_user_images(user_id)

    def toggle_like_status(self, image_id):
        return self.image_repo.toggle_like_status(image_id)

    def delete_image_by_id(self, image_id):
        return self.image_repo.delete_image_by_id(image_id)
