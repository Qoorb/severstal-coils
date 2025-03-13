import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Dict, Iterator

from app.core.database import get_db
from app.domain.models import Base
from app.main import app


SQLITE_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Create tables in the database
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Iterator[Session]:
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session: Session) -> TestClient:
    """Create a test client that uses the override_get_db fixture."""

    def override_get_db() -> Iterator[Session]:
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def coil_payload() -> Dict[str, float]:
    """Generate a coil payload."""
    return {"length": 100.0, "weight": 500.0}


@pytest.fixture()
def coil_payload_updated() -> Dict[str, float]:
    """Generate an updated coil payload."""
    return {"length": 150.0, "weight": 600.0}
