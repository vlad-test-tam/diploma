from pydantic import Field, StrictStr, SecretStr
from pydantic_settings import BaseSettings


class CookiesSettings(BaseSettings):
    cookies_prefix: StrictStr = Field(..., validation_alias="COOKIES_PREFIX")
    cookies_password: SecretStr = Field(..., validation_alias="COOKIES_PASSWORD")
