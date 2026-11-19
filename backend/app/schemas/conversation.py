from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.schemas.chat import ChatMessageResponse


class ConversationRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=150, description="New title for the conversation.")

    @field_validator("title")
    @classmethod
    def validate_title_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace.")
        return stripped


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = Field(default="New Conversation", max_length=150)


class ConversationResponse(BaseModel):
    id: str
    title: str
    updatedAt: str
    createdAt: str
    messages: List[ChatMessageResponse] = Field(default_factory=list)


class ConversationListItem(BaseModel):
    id: str
    title: str
    updatedAt: str
    createdAt: str
    messages: List[ChatMessageResponse] = Field(default_factory=list)
