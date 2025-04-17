from pydantic import Field, StrictStr, SecretStr
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    host: StrictStr = Field(..., validation_alias="HOST")
    user: StrictStr = Field(..., validation_alias="USER")
    password: SecretStr = Field(..., validation_alias="PASSWORD")
    db_name: StrictStr = Field(..., validation_alias="DB_NAME")
