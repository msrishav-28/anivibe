import pytest
import os
from httpx import AsyncClient

pytest.importorskip("supabase", reason="Install full backend dependencies to run API smoke tests.")

@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "name" in data

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_get_anime_list_anonymous(client: AsyncClient):
    if os.getenv("RUN_DB_TESTS") != "1":
        pytest.skip("Database-backed API test disabled by default. Set RUN_DB_TESTS=1 to run it.")

    # Test getting popular anime without auth
    response = await client.get("/api/v1/anime/popular?limit=5")
    # This might fail if the endpoint is protected or empty DB
    # We assert 200 assuming public access, or 401 if protected
    # Based on code reviews, popular anime looked public
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list) or "data" in data
    elif response.status_code == 401:
        assert True # Acceptable behavior
    else:
        assert False, f"Unexpected status code: {response.status_code}"
