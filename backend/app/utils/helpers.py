from datetime import datetime, timezone
from typing import Any, Dict
from bson import ObjectId
import uuid

from app.schemas.chat import ChatMessageResponse
from app.schemas.conversation import ConversationResponse, ConversationListItem


def is_valid_object_id(val: str) -> bool:
    """Check if the provided string is a valid 24-char hexadecimal ObjectId."""
    return ObjectId.is_valid(val)


def build_id_query(conversation_id: str) -> Dict[str, Any]:
    """
    Build a MongoDB query filter for a conversation ID.
    Supports both BSON ObjectId and string IDs (e.g., client UUIDs) seamlessly.
    """
    if is_valid_object_id(conversation_id):
        return {"$or": [{"_id": ObjectId(conversation_id)}, {"_id": conversation_id}]}
    return {"_id": conversation_id}


def format_iso(dt: Any) -> str:
    """Format a datetime to standard ISO 8601 string with UTC indicator."""
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    if isinstance(dt, str):
        return dt
    return datetime.now(timezone.utc).isoformat()


def doc_to_conversation_response(doc: Dict[str, Any]) -> ConversationResponse:
    """Convert a raw MongoDB conversation document into a ConversationResponse schema."""
    conv_id = str(doc.get("_id", ""))
    title = doc.get("title", "New Conversation")
    created_at = format_iso(doc.get("created_at"))
    updated_at = format_iso(doc.get("updated_at", doc.get("created_at")))

    raw_messages = doc.get("messages", [])
    messages: list[ChatMessageResponse] = []
    for msg in raw_messages:
        msg_id = msg.get("id") or f"msg-{uuid.uuid4().hex[:12]}"
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        ts = msg.get("timestamp") or msg.get("created_at") or msg.get("createdAt")
        msg_created = format_iso(ts)
        messages.append(
            ChatMessageResponse(
                id=msg_id,
                role=role,
                content=content,
                createdAt=msg_created,
                feedback=msg.get("feedback"),
                error=msg.get("error"),
            )
        )

    return ConversationResponse(
        id=conv_id,
        title=title,
        updatedAt=updated_at,
        createdAt=created_at,
        messages=messages,
    )


def doc_to_conversation_list_item(doc: Dict[str, Any]) -> ConversationListItem:
    """Convert a raw MongoDB document into a ConversationListItem schema."""
    conv_id = str(doc.get("_id", ""))
    title = doc.get("title", "New Conversation")
    created_at = format_iso(doc.get("created_at"))
    updated_at = format_iso(doc.get("updated_at", doc.get("created_at")))

    raw_messages = doc.get("messages", [])
    messages: list[ChatMessageResponse] = []
    for msg in raw_messages:
        msg_id = msg.get("id") or f"msg-{uuid.uuid4().hex[:12]}"
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        ts = msg.get("timestamp") or msg.get("created_at") or msg.get("createdAt")
        messages.append(
            ChatMessageResponse(
                id=msg_id,
                role=role,
                content=content,
                createdAt=format_iso(ts),
                feedback=msg.get("feedback"),
                error=msg.get("error"),
            )
        )

    return ConversationListItem(
        id=conv_id,
        title=title,
        updatedAt=updated_at,
        createdAt=created_at,
        messages=messages,
    )
