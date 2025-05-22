import os

from pydantic import Field, StrictStr, SecretStr
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    host: StrictStr = Field(..., validation_alias="HOST")
    user: StrictStr = Field(..., validation_alias="USER")
    password: SecretStr = Field(..., validation_alias="PASSWORD")
    db_name: StrictStr = Field(..., validation_alias="DB_NAME")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.envs', 'database.env')
        env_file_encoding = 'utf-8'
