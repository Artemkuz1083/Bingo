from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str
    redis_host: str
    redis_port: int
    redis_db: int
    redis_key_prefix: str
    jwt_secret_key: str
    jwt_algorithm: str
    draw_interval_seconds: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings