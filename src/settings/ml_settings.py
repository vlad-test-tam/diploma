import os

from pydantic import Field, StrictStr
from pydantic_settings import BaseSettings


class MlSettings(BaseSettings):
    path_to_yolo: StrictStr = Field(..., validation_alias="PATH_TO_YOLO")
    path_to_deepfill: StrictStr = Field(..., validation_alias="PATH_TO_DEEPFILL")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.envs', 'ml.env')
        env_file_encoding = 'utf-8'


ml_settings = MlSettings()
