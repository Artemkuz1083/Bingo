import asyncio

from app.db.init_db import init_db
from app.services.events import consume_user_registered_events


async def main() -> None:
    await init_db()
    await consume_user_registered_events()
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
