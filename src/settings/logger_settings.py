import os

from pydantic import Field, StrictStr
from pydantic_settings import BaseSettings


class LoggerSettings(BaseSettings):
    log_level: StrictStr = Field(..., validation_alias="LOG_LEVEL")
    log_directory: StrictStr = Field(..., validation_alias="LOG_DIRECTORY")
    config_file_path: StrictStr = Field(..., validation_alias="CONFIG_FILE_PATH")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.envs', 'logger.env')
        env_file_encoding = 'utf-8'
