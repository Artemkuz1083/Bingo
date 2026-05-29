from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str
    jwt_secret_key: str
    jwt_algorithm: str
    cors_origins: str

    rabbitmq_url: str
    winner_claims_exchange: str
    winner_claim_submitted_routing_key: str
    winner_claims_queue: str

    redis_host: str
    redis_port: int
    redis_db: int
    redis_key_prefix: str

    card_service_url: str
    game_engine_service_url: str
    user_service_url: str
    reward_amount: Decimal
    http_timeout_seconds: float

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
