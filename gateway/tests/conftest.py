from unittest.mock import AsyncMock, MagicMock

import pytest
from app.database import get_db
from app.main import app


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=mock_result)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def override_db(mock_db_session):
    async def _override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = _override_get_db

    yield mock_db_session

    app.dependency_overrides.clear()
