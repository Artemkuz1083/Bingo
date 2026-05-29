import json

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError

from app.core.config import settings
from app.core.redis import redis_client
from app.schemas.winners import WinnerClaimMessage
from app.services.processor import process_winner_claim
from app.services.storage import WinnerStorage


async def open_channel() -> aio_pika.abc.AbstractChannel:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    return await connection.channel()


async def declare_claims_topology(
    channel: aio_pika.abc.AbstractChannel,
) -> aio_pika.abc.AbstractExchange:
    exchange = await channel.declare_exchange(
        settings.winner_claims_exchange,
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )
    queue = await channel.declare_queue(
        settings.winner_claims_queue,
        durable=True,
    )
    await queue.bind(
        exchange,
        routing_key=settings.winner_claim_submitted_routing_key,
    )
    return exchange


async def ensure_winner_claims_queue() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await declare_claims_topology(channel)


async def publish_winner_claim(
    claim_id: str,
    game_id: str,
    user_id: str,
    token: str,
) -> None:
    payload = WinnerClaimMessage(
        claim_id=claim_id,
        game_id=game_id,
        user_id=user_id,
        token=token,
    )

    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        exchange = await declare_claims_topology(channel)
        await exchange.publish(
            aio_pika.Message(
                body=payload.model_dump_json().encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=settings.winner_claim_submitted_routing_key,
        )


async def handle_winner_claim(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        try:
            raw_payload = json.loads(message.body.decode("utf-8"))
            payload = WinnerClaimMessage.model_validate(raw_payload)
        except (json.JSONDecodeError, ValidationError):
            return

        storage = WinnerStorage(redis_client)
        await process_winner_claim(payload, storage)


async def consume_winner_claims() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    await declare_claims_topology(channel)
    queue = await channel.declare_queue(
        settings.winner_claims_queue,
        durable=True,
    )
    await queue.consume(handle_winner_claim)
