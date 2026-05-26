from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "user-service"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bingo_users"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    user_events_exchange: str = "user.events"
    user_registered_routing_key: str = "user.registered"
    user_registered_queue: str = "user-service.user-registered"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
