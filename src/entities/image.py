from datetime import datetime

from pydantic import BaseModel


class ImageAddDTO(BaseModel):
    user_id: int
    fix_datetime: datetime
    is_liked: bool = False
    defected_path: str
    fixed_path: str
    masked_path: str
    segmented_path: str


class ImageDTO(ImageAddDTO):
    id: int
