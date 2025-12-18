from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = None
async_session = None


def setup_database(db_path: str):
    """
    Настройка базы данных.

    :param db_path: Путь к базе данных
    :type db_path: str
    """
    global engine, async_session

    database_url = f"sqlite+aiosqlite:///{db_path}"

    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session


async def init_db():
    """Создание таблиц"""
    if engine is None:
        raise RuntimeError(
            "База данных не инициализирована. Вызовите setup_database() для начала."
        )

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
