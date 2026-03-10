# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = ""
    yandex_api_key: str = ""
    yandex_static_api_key: str = ""
    yandex_static_secret_key: str = ""
    yandex_folder_id: str = ""
    yandex_bucket: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
