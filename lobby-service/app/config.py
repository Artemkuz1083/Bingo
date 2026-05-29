import os


def env_bool(name: str) -> bool:
    return os.environ[name].lower() in {"1", "true", "yes"}


class Settings:
    service_name: str = os.environ["SERVICE_NAME"]
    database_url: str = os.environ["DATABASE_URL"]
    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]
    jwt_algorithm: str = os.environ["JWT_ALGORITHM"]
    cors_origins: str = os.environ["CORS_ORIGINS"]
    auto_create_tables: bool = env_bool("AUTO_CREATE_TABLES")

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
