from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from src.entities.image import ImageDTO


class UserAddDTO(BaseModel):
    registration_datetime: datetime
    username: str
    email: str
    password: str
    is_subscription_active: bool = False
    subscriptions_end_datetime: Optional[datetime] = None
    free_attempts_count: int = 5


class UserDTO(UserAddDTO):
    id: int
    images: list[ImageDTO] = []

    class Config:
        from_attributes = True
