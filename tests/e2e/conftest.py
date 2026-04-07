"""
Pytest configuration for E2E tests.

Provides fixtures specific to HTTP end-to-end testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Import the main app
import sys
sys.path.insert(0, '/app')
from main import app as fastapi_app


@pytest.fixture
def client(db_session: Session):
    """
    Provide a FastAPI TestClient with a database session override.
    
    This allows HTTP-level testing while using the test database.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override the dependency
    from app.database import get_db
    fastapi_app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(fastapi_app) as client:
        yield client
    
    # Clean up overrides
    fastapi_app.dependency_overrides.clear()
