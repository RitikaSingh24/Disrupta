import asyncio
from app.db.session import AsyncSessionLocal
from app.models.flight import Flight
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Flight))
        flights = result.scalars().all()
        for f in flights:
            print(f"ID: {f.flight_id} | Number: '{f.flight_number}' | Airline: '{f.airline}' | Status: '{f.status}'")

if __name__ == "__main__":
    asyncio.run(main())
