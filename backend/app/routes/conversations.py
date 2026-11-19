from typing import List
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationListItem,
    ConversationRenameRequest,
    ConversationResponse,
)
from app.services.conversation_service import conversation_service

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get(
    "",
    response_model=List[ConversationListItem],
    summary="Get all conversations",
    description="Retrieve conversations sorted by most recently updated with optional pagination.",
)
async def list_conversations(
    limit: int = Query(default=50, ge=1, le=100, description="Max conversations to return"),
    skip: int = Query(default=0, ge=0, description="Number of conversations to skip"),
) -> List[ConversationListItem]:
    try:
        return await conversation_service.get_conversations(limit=limit, skip=skip)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversations: {str(exc)}",
        )


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Explicitly initialize a new conversation with a title.",
)
async def create_conversation(
    payload: ConversationCreateRequest = ConversationCreateRequest(),
) -> ConversationResponse:
    try:
        title = payload.title or "New Conversation"
        return await conversation_service.create_conversation(title=title)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(exc)}",
        )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get individual conversation",
    description="Retrieve a specific conversation by ID including all message history.",
)
async def get_conversation(conversation_id: str) -> ConversationResponse:
    try:
        conv = await conversation_service.get_conversation(conversation_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found.",
            )
        return conv
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conversation: {str(exc)}",
        )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Rename conversation",
    description="Update the title of an existing conversation.",
)
async def rename_conversation(
    conversation_id: str, payload: ConversationRenameRequest
) -> ConversationResponse:
    try:
        updated = await conversation_service.rename_conversation(
            conversation_id=conversation_id, new_title=payload.title
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found.",
            )
        return updated
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename conversation: {str(exc)}",
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete conversation",
    description="Permanently delete a conversation and its messages.",
)
async def delete_conversation(conversation_id: str) -> dict:
    try:
        deleted = await conversation_service.delete_conversation(conversation_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found.",
            )
        return {"status": "success", "message": "Conversation deleted successfully."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(exc)}",
        )
