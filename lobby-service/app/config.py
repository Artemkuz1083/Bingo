import os


def env_bool(name: str) -> bool:
    return os.environ[name].lower() in {"1", "true", "yes"}


def optional_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


class Settings:
    service_name: str = os.environ["SERVICE_NAME"]
    database_url: str = os.environ["DATABASE_URL"]
    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]
    jwt_algorithm: str = os.environ["JWT_ALGORITHM"]
    cors_origins: str = os.environ["CORS_ORIGINS"]
    auto_create_tables: bool = env_bool("AUTO_CREATE_TABLES")
    game_engine_service_url: str = optional_env("LOBBY_GAME_ENGINE_SERVICE_URL")
    http_timeout_seconds: float = float(optional_env("HTTP_TIMEOUT_SECONDS", "5"))
    internal_service_token: str = optional_env("INTERNAL_SERVICE_TOKEN")

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
