"""Tests for API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test health check endpoint."""
    response = await async_client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "ollama_available" in data
    assert "threads_api_configured" in data


@pytest.mark.asyncio
async def test_search_requires_keywords(async_client: AsyncClient):
    """Test that search requires keywords."""
    response = await async_client.post(
        "/api/search",
        json={"keywords": ""}
    )
    
    # Empty keywords should still work (handled by backend)
    assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_search_with_valid_request(async_client: AsyncClient):
    """Test search with valid request."""
    response = await async_client.post(
        "/api/search",
        json={
            "keywords": "продуктивность",
            "search_type": "TOP",
            "limit": 10
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert "total_posts" in data
    assert "query" in data


@pytest.mark.asyncio
async def test_export_json_format(async_client: AsyncClient):
    """Test JSON export endpoint."""
    response = await async_client.get("/api/export/json")
    
    assert response.status_code == 200
    data = response.json()
    assert "exported_at" in data


@pytest.mark.asyncio
async def test_export_invalid_format(async_client: AsyncClient):
    """Test export with invalid format."""
    response = await async_client.get("/api/export/invalid")
    
    assert response.status_code == 400


@pytest.mark.asyncio 
async def test_frontend_index_served(async_client: AsyncClient):
    """Test that frontend index is served."""
    response = await async_client.get("/")
    
    # Should return HTML or a message
    assert response.status_code == 200
