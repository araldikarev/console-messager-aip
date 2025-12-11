from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///server/database.db"

engine = create_async_engine(DATABASE_URL, echo=True)

async def init_db():
    """Создание таблиц"""
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
