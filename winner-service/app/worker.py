import asyncio

from app.services.queue import consume_winner_claims


async def main() -> None:
    await consume_winner_claims()
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
