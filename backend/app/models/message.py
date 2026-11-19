from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MessageModel(BaseModel):
    id: str = Field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:12]}")
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=utc_now)
    feedback: Optional[Literal["up", "down"]] = None
    error: Optional[str] = None
