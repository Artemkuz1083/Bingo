import json

import aio_pika
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.user import User


async def publish_user_registered(user: User) -> None:
    payload = {
        "event": "user_registered",
        "auth_user_id": user.id,
        "username": user.username,
        "email": user.email,
    }

    try:
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                settings.user_events_exchange,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode("utf-8"),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=settings.user_registered_routing_key,
            )
    except aio_pika.exceptions.AMQPException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Не удалось отправить событие регистрации пользователя.",
        ) from exc
