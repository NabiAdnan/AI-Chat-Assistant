import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId
import uuid

from app.database.mongodb import get_conversations_collection
from app.models.message import utc_now
from app.schemas.conversation import ConversationResponse, ConversationListItem
from app.utils.helpers import (
    build_id_query,
    doc_to_conversation_response,
    doc_to_conversation_list_item,
    is_valid_object_id,
)

logger = logging.getLogger("nexus_ai.conversation_service")


class ConversationService:
    @property
    def collection(self):
        return get_conversations_collection()

    async def get_conversations(
        self, limit: int = 50, skip: int = 0
    ) -> List[ConversationListItem]:
        """Retrieve conversations sorted by updated_at descending with pagination."""
        cursor = (
            self.collection.find({})
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [doc_to_conversation_list_item(doc) for doc in docs]

    async def get_conversation(self, conversation_id: str) -> Optional[ConversationResponse]:
        """Retrieve a single conversation by ID with complete message history."""
        query = build_id_query(conversation_id)
        doc = await self.collection.find_one(query)
        if not doc:
            return None
        return doc_to_conversation_response(doc)

    async def get_raw_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the raw document for internal logic."""
        query = build_id_query(conversation_id)
        return await self.collection.find_one(query)

    async def create_conversation(
        self,
        title: str = "New Conversation",
        preferred_id: Optional[str] = None,
    ) -> ConversationResponse:
        """Create a new conversation document."""
        now = utc_now()
        if preferred_id:
            conv_id: Any = (
                ObjectId(preferred_id)
                if is_valid_object_id(preferred_id)
                else preferred_id
            )
        else:
            conv_id = ObjectId()

        doc: Dict[str, Any] = {
            "_id": conv_id,
            "title": title,
            "messages": [],
            "created_at": now,
            "updated_at": now,
        }
        await self.collection.insert_one(doc)
        logger.info("Created conversation %s with title '%s'", conv_id, title)
        return doc_to_conversation_response(doc)

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by ID."""
        query = build_id_query(conversation_id)
        result = await self.collection.delete_one(query)
        logger.info("Deleted conversation %s: %s", conversation_id, result.deleted_count > 0)
        return result.deleted_count > 0

    async def rename_conversation(
        self, conversation_id: str, new_title: str
    ) -> Optional[ConversationResponse]:
        """Update conversation title and updated_at timestamp."""
        query = build_id_query(conversation_id)
        now = utc_now()
        result = await self.collection.find_one_and_update(
            query,
            {"$set": {"title": new_title, "updated_at": now}},
            return_document=True,
        )
        if not result:
            return None
        return doc_to_conversation_response(result)

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        message_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Append a message to the conversation's messages list and update timestamp."""
        query = build_id_query(conversation_id)
        now = utc_now()
        msg_obj = {
            "id": message_id or f"msg-{uuid.uuid4().hex[:12]}",
            "role": role,
            "content": content,
            "timestamp": now,
        }
        if error:
            msg_obj["error"] = error

        await self.collection.update_one(
            query,
            {
                "$push": {"messages": msg_obj},
                "$set": {"updated_at": now},
            },
        )
        return msg_obj

    async def replace_or_update_assistant_message(
        self,
        conversation_id: str,
        content: str,
        message_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> bool:
        """
        Replace or update the assistant message.
        If regenerating, updates the last assistant message or appends if none exists.
        """
        doc = await self.get_raw_conversation(conversation_id)
        if not doc:
            return False

        messages: list[dict] = doc.get("messages", [])
        now = utc_now()

        # Find the last assistant message to replace
        last_assistant_idx = None
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].get("role") == "assistant":
                last_assistant_idx = i
                break

        if last_assistant_idx is not None:
            # Replace in-place
            msg_id = message_id or messages[last_assistant_idx].get("id") or f"msg-{uuid.uuid4().hex[:12]}"
            messages[last_assistant_idx] = {
                "id": msg_id,
                "role": "assistant",
                "content": content,
                "timestamp": now,
            }
            if error:
                messages[last_assistant_idx]["error"] = error
        else:
            # Append as new assistant message
            messages.append({
                "id": message_id or f"msg-{uuid.uuid4().hex[:12]}",
                "role": "assistant",
                "content": content,
                "timestamp": now,
            })

        query = build_id_query(conversation_id)
        await self.collection.update_one(
            query,
            {
                "$set": {
                    "messages": messages,
                    "updated_at": now,
                }
            },
        )
        return True


conversation_service = ConversationService()
