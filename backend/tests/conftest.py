"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def async_client():
    """Create async HTTP client for API testing."""
    from main import app
    
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client


@pytest.fixture
def sample_posts():
    """Sample posts for testing."""
    return [
        "Искал приложение для продуктивности, но все слишком сложные",
        "Устал от того что нет нормального решения для тайм-менеджмента",
        "Хочу простой трекер задач без лишних функций"
    ]


@pytest.fixture
def mock_analysis_result():
    """Mock analysis result for testing."""
    from models import AnalysisResult
    
    return AnalysisResult(
        pains=["Сложные интерфейсы", "Отсутствие интеграций"],
        needs=["Простота использования", "Автоматизация"],
        app_ideas=["Минималистичный трекер задач"],
        sentiment="negative",
        keywords_found=["продуктивность", "тайм-менеджмент"]
    )
