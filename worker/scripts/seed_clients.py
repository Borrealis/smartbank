import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import async_session
from app.models import Client

clients_data = [
    {"id": "client_66", "status": "active", "tariff_plan": "Premium"},
    {"id": "client_711", "status": "active", "tariff_plan": "Base"},
    {"id": "client_911", "status": "blocked", "tariff_plan": "Diamond"},
]


async def seed_clients() -> None:
    async with async_session() as session:
        for client_data in clients_data:
            client = Client(**client_data)
            session.add(client)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_clients())
