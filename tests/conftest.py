"""Shared pytest fixtures for FastAPI tests."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Provide a TestClient instance for API tests."""
    return TestClient(app)
