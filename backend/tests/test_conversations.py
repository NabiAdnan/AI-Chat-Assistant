import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db_manager


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Connect to test MongoDB instance and clean up test data."""
    await connect_to_mongo()
    # Clean test conversations before each test
    col = db_manager.db["conversations"]
    await col.delete_many({"title": {"$regex": "^Test"}})
    yield
    # Cleanup after test
    await col.delete_many({"title": {"$regex": "^Test"}})
    await close_mongo_connection()


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert data["service"] == "Nexus AI Backend"


@pytest.mark.asyncio
async def test_create_and_get_conversation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create
        create_res = await ac.post("/api/conversations", json={"title": "Test Creation"})
        assert create_res.status_code == 201
        created = create_res.json()
        assert created["title"] == "Test Creation"
        assert "id" in created
        conv_id = created["id"]

        # Get by ID
        get_res = await ac.get(f"/api/conversations/{conv_id}")
        assert get_res.status_code == 200
        fetched = get_res.json()
        assert fetched["id"] == conv_id
        assert fetched["title"] == "Test Creation"
        assert isinstance(fetched["messages"], list)


@pytest.mark.asyncio
async def test_list_conversations_with_pagination():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create 3 conversations
        await ac.post("/api/conversations", json={"title": "Test Conv 1"})
        await ac.post("/api/conversations", json={"title": "Test Conv 2"})
        await ac.post("/api/conversations", json={"title": "Test Conv 3"})

        list_res = await ac.get("/api/conversations?limit=2&skip=0")
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) <= 2
        for item in items:
            assert "id" in item
            assert "title" in item
            assert "updatedAt" in item


@pytest.mark.asyncio
async def test_rename_conversation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_res = await ac.post("/api/conversations", json={"title": "Test Original Title"})
        conv_id = create_res.json()["id"]

        # Rename
        patch_res = await ac.patch(
            f"/api/conversations/{conv_id}",
            json={"title": "Test Updated Title"},
        )
        assert patch_res.status_code == 200
        updated = patch_res.json()
        assert updated["title"] == "Test Updated Title"

        # Verify invalid blank rename rejected
        invalid_res = await ac.patch(
            f"/api/conversations/{conv_id}",
            json={"title": "   "},
        )
        assert invalid_res.status_code == 422


@pytest.mark.asyncio
async def test_delete_conversation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_res = await ac.post("/api/conversations", json={"title": "Test To Delete"})
        conv_id = create_res.json()["id"]

        # Delete
        del_res = await ac.delete(f"/api/conversations/{conv_id}")
        assert del_res.status_code == 200

        # Verify not found after deletion
        get_res = await ac.get(f"/api/conversations/{conv_id}")
        assert get_res.status_code == 404

        # Delete again returns 404
        del_again = await ac.delete(f"/api/conversations/{conv_id}")
        assert del_again.status_code == 404
