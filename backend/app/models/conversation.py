from datetime import datetime, timezone
from typing import Any, List
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.message import MessageModel, utc_now


class ConversationModel(BaseModel):
    id: Any = Field(default_factory=ObjectId, alias="_id")
    title: str = "New Conversation"
    messages: List[MessageModel] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
