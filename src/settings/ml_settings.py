import os

from pydantic import Field, StrictStr
from pydantic_settings import BaseSettings


class MlSettings(BaseSettings):
    path_to_cnn: StrictStr = Field(..., validation_alias="PATH_TO_CNN")
    path_to_gan: StrictStr = Field(..., validation_alias="PATH_TO_GAN")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.envs', 'ml.env')
        env_file_encoding = 'utf-8'


ml_settings = MlSettings()
