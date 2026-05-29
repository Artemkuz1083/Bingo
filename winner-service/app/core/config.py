from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "winner-service"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    cors_origins: str = "*"

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    winner_claims_exchange: str = "winner.claims"
    winner_claim_submitted_routing_key: str = "winner.claim.submitted"
    winner_claims_queue: str = "winner-service.claims"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_key_prefix: str = "bingo"

    card_service_url: str = "http://localhost:8004"
    game_engine_service_url: str = "http://localhost:8005"
    user_service_url: str = "http://localhost:8002"
    reward_amount: Decimal = Decimal("100")
    http_timeout_seconds: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
