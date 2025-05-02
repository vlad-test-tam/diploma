import os

from pydantic import Field, StrictStr, SecretStr
from pydantic_settings import BaseSettings


class CookiesSettings(BaseSettings):
    cookies_prefix: StrictStr = Field(..., validation_alias="COOKIES_PREFIX")
    cookies_password: SecretStr = Field(..., validation_alias="COOKIES_PASSWORD")
    cookies_username: StrictStr = Field(..., validation_alias="COOKIES_USERNAME")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.envs', 'auth.env')
        env_file_encoding = 'utf-8'


if __name__ == '__main__':
    settings = CookiesSettings()
