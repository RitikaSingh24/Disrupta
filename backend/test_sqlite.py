import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base import Base
import app.models

async def main():
    engine = create_async_engine('sqlite+aiosqlite:///./test.db')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("CREATED ALL TABLES SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
