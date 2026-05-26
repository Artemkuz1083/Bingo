import json

import aio_pika
from pydantic import ValidationError

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.schemas.user import UserCreateFromAuthEvent
from app.services.users import create_user_from_auth_event


async def handle_user_registered(message: aio_pika.IncomingMessage) -> None:
    async with message.process(requeue=False):
        try:
            raw_payload = json.loads(message.body.decode("utf-8"))
            if raw_payload.get("event") != "user_registered":
                return

            payload = UserCreateFromAuthEvent(
                auth_user_id=raw_payload["auth_user_id"],
                username=raw_payload["username"],
                email=raw_payload["email"],
            )
        except (json.JSONDecodeError, KeyError, ValidationError):
            return

        async with AsyncSessionLocal() as session:
            await create_user_from_auth_event(session, payload)


async def consume_user_registered_events() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    exchange = await channel.declare_exchange(
        settings.user_events_exchange,
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )
    queue = await channel.declare_queue(
        settings.user_registered_queue,
        durable=True,
    )
    await queue.bind(
        exchange,
        routing_key=settings.user_registered_routing_key,
    )
    await queue.consume(handle_user_registered)
