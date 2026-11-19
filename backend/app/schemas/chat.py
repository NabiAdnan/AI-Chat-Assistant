from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

from app.core.prompts import ToneType


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(
        default=None,
        description="ID of the conversation. If omitted or new, a conversation is created.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=15000,
        description="The user prompt to process.",
    )
    tone: ToneType = Field(
        default=ToneType.PROFESSIONAL,
        description="Desired AI persona/tone: Professional, Casual, or Concise.",
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message cannot be empty or only whitespace.")
        return stripped


class RegenerateRequest(BaseModel):
    conversation_id: str = Field(
        ...,
        min_length=1,
        description="ID of the conversation where the response should be regenerated.",
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional original user prompt. If omitted, the last user message in the conversation is used.",
    )
    tone: ToneType = Field(
        default=ToneType.PROFESSIONAL,
        description="Desired AI persona/tone: Professional, Casual, or Concise.",
    )


class ChatMessageResponse(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    createdAt: str
    feedback: Optional[Literal["up", "down"]] = None
    error: Optional[str] = None
