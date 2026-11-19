import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from app.main import app
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db_manager


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await connect_to_mongo()
    col = db_manager.db["conversations"]
    await col.delete_many({"title": {"$regex": "^Test"}})
    yield
    await col.delete_many({"title": {"$regex": "^Test"}})
    await close_mongo_connection()


async def mock_stream_tokens(messages, model=None):
    """Simulates OpenAI streaming token generator."""
    tokens = ["Hello", " world", "!", " This is a test."]
    for token in tokens:
        yield token


async def mock_stream_error(messages, model=None):
    """Simulates OpenAI streaming error."""
    yield "Partial"
    raise RuntimeError("OpenAI rate limit reached during generation")


@pytest.mark.asyncio
async def test_chat_streaming_success():
    with patch(
        "app.services.chat_service.ai_service.stream_chat_completion",
        side_effect=mock_stream_tokens,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/chat",
                json={
                    "message": "Test prompt for Nexus AI",
                    "tone": "Professional",
                },
            )
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]

            content = response.text
            assert "Hello" in content
            assert "[DONE]" in content
            assert "completed" in content


@pytest.mark.asyncio
async def test_chat_tone_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Invalid tone should fail with 422
        bad_tone_res = await ac.post(
            "/api/chat",
            json={
                "message": "Hello",
                "tone": "Sarcastic",  # Not in [Professional, Casual, Concise]
            },
        )
        assert bad_tone_res.status_code == 422

        # Valid tones should succeed (mocked)
        with patch(
            "app.services.chat_service.ai_service.stream_chat_completion",
            side_effect=mock_stream_tokens,
        ):
            for valid_tone in ["Professional", "Casual", "Concise"]:
                res = await ac.post(
                    "/api/chat",
                    json={"message": "Hello", "tone": valid_tone},
                )
                assert res.status_code == 200


@pytest.mark.asyncio
async def test_chat_empty_message_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/chat",
            json={"message": "   ", "tone": "Professional"},
        )
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_chat_message_persistence_in_mongodb():
    with patch(
        "app.services.chat_service.ai_service.stream_chat_completion",
        side_effect=mock_stream_tokens,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                "/api/chat",
                json={"message": "Test persistence message", "tone": "Casual"},
            )
            assert res.status_code == 200

            # Find the conversation in MongoDB
            col = db_manager.db["conversations"]
            conv = await col.find_one({"title": {"$regex": "Test persistence message"}})
            assert conv is not None
            messages = conv.get("messages", [])
            assert len(messages) == 2
            assert messages[0]["role"] == "user"
            assert messages[0]["content"] == "Test persistence message"
            assert messages[1]["role"] == "assistant"
            assert messages[1]["content"] == "Hello world! This is a test."


@pytest.mark.asyncio
async def test_regenerate_flow():
    with patch(
        "app.services.chat_service.ai_service.stream_chat_completion",
        side_effect=mock_stream_tokens,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. Send first message
            chat_res = await ac.post(
                "/api/chat",
                json={"message": "Test for regenerate", "tone": "Concise"},
            )
            assert chat_res.status_code == 200

            col = db_manager.db["conversations"]
            conv = await col.find_one({"title": {"$regex": "Test for regenerate"}})
            assert conv is not None
            conv_id = str(conv["_id"])

            # 2. Call regenerate
            regen_res = await ac.post(
                "/api/chat/regenerate",
                json={"conversation_id": conv_id, "tone": "Professional"},
            )
            assert regen_res.status_code == 200
            assert "[DONE]" in regen_res.text

            # 3. Check MongoDB has replaced the assistant message and NOT duplicated user message
            updated_conv = await col.find_one({"_id": conv["_id"]})
            assert updated_conv is not None
            assert len(updated_conv["messages"]) == 2
            assert updated_conv["messages"][0]["role"] == "user"
            assert updated_conv["messages"][1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_streaming_error_handling():
    with patch(
        "app.services.chat_service.ai_service.stream_chat_completion",
        side_effect=mock_stream_error,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                "/api/chat",
                json={"message": "Test error simulation", "tone": "Professional"},
            )
            assert res.status_code == 200
            text = res.text
            assert "error" in text.lower()
            assert "[DONE]" in text


@pytest.mark.asyncio
async def test_gemini_streaming_provider():
    from app.services.ai_service import ai_service
    from unittest.mock import AsyncMock, MagicMock

    class MockChunk:
        def __init__(self, text):
            self.text = text

    async def mock_async_chunks():
        for chunk in [MockChunk("Gemini"), MockChunk(" streaming"), MockChunk(" works!")]:
            yield chunk

    mock_client = MagicMock()
    mock_client.aio.models.generate_content_stream = AsyncMock(return_value=mock_async_chunks())

    with patch.object(ai_service, "_gemini_client", mock_client):
        collected = []
        async for token in ai_service._stream_gemini([
            {"role": "system", "content": "You are Gemini."},
            {"role": "user", "content": "Hi"}
        ]):
            collected.append(token)

        assert "".join(collected) == "Gemini streaming works!"
        mock_client.aio.models.generate_content_stream.assert_called_once()
