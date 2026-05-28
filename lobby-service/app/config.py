import os


class Settings:
    service_name: str = os.getenv("SERVICE_NAME", "lobby-service")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/lobby_service",
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    auto_create_tables: bool = os.getenv("AUTO_CREATE_TABLES", "true").lower() in {
        "1",
        "true",
        "yes",
    }

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
