import pytest
import pytest_asyncio
import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    from config import settings
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(settings.database_url, echo=False)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db(db_engine) -> AsyncGenerator:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
