from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, RegenerateRequest
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])

STREAMING_HEADERS = {
    "Content-Type": "text/event-stream; charset=utf-8",
    "Cache-Control": "no-cache, no-transform",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@router.post(
    "",
    summary="Send chat message and stream response",
    description="Processes a new user prompt, saves context in MongoDB, and streams tokens via Server-Sent Events (SSE).",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": "Server-Sent Events streaming chunks of the AI assistant response.",
        },
        400: {"description": "Invalid prompt or configuration error."},
        500: {"description": "Internal server or database error."},
    },
)
async def chat_stream(request: ChatRequest):
    try:
        generator = chat_service.stream_chat(
            conversation_id=request.conversation_id,
            user_message=request.message,
            tone=request.tone,
        )
        return StreamingResponse(generator, headers=STREAMING_HEADERS)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat generation failed: {str(exc)}",
        )


@router.post(
    "/regenerate",
    summary="Regenerate last assistant response",
    description="Regenerates the last assistant response with the current tone and updates MongoDB.",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": "Server-Sent Events streaming chunks of the regenerated response.",
        },
        400: {"description": "Invalid request parameters."},
        404: {"description": "Conversation not found."},
        500: {"description": "Internal server error."},
    },
)
async def regenerate_stream(request: RegenerateRequest):
    try:
        generator = chat_service.stream_regenerate(
            conversation_id=request.conversation_id,
            user_message=request.message,
            tone=request.tone,
        )
        return StreamingResponse(generator, headers=STREAMING_HEADERS)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Regeneration failed: {str(exc)}",
        )
