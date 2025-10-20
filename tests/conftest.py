import pytest
from db.connection import get_pool, close_pool
from db.schema import create_tables
from utils.config import Settings

settings = Settings()


@pytest.fixture
def settings_fixture() -> Settings:
    """Return app settings (no test DB needed)."""
    return settings


@pytest.fixture(scope="session")
async def test_pool(postgresql_proc):
    """
    Create an async connection pool using pytest-postgresql's ephemeral DB.
    Initializes the schema once per test session.
    """
    db_url = (
        f"postgresql://{postgresql_proc.user}:"
        f"{postgresql_proc.password}@"
        f"{postgresql_proc.host}:{postgresql_proc.port}/"
        f"{postgresql_proc.dbname}"
    )

    pool = await get_pool(override_url=db_url)
    await create_tables()
    yield pool
    await close_pool()


@pytest.fixture
async def db_connection(test_pool):
    """
    Provide a database connection inside a rollback transaction.
    Ensures DB is pristine after each test.
    """
    async with test_pool.connection() as conn:
        async with conn.transaction():
            yield conn
