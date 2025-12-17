import sys
import os
import pytest

sys.path.append(os.getcwd())

@pytest.fixture(scope="session")
def event_loop():
    """Создает экземпляр event loop для асинхронных тестов."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()