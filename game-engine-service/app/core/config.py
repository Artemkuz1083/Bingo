from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "game-engine-service"
    redis_host: str
    redis_port: int = 6379
    redis_db: int = 0
    redis_key_prefix: str = "bingo"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    cors_origins: str = "*"
    draw_interval_seconds: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

settings = Settings()
