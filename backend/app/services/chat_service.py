import asyncio
import logging
from typing import AsyncGenerator, Dict, List, Optional

from app.core.prompts import ToneType, get_system_prompt_for_tone
from app.services.ai_service import ai_service
from app.services.conversation_service import conversation_service
from app.utils.streaming import sse_chunk, sse_completion, sse_done, sse_error

logger = logging.getLogger("nexus_ai.chat_service")


class ChatService:
    async def stream_chat(
        self,
        conversation_id: Optional[str],
        user_message: str,
        tone: ToneType | str = ToneType.PROFESSIONAL,
    ) -> AsyncGenerator[str, None]:
        """
        Handle a new user message:
        1. Resolve or create conversation.
        2. Append user message to MongoDB.
        3. Build context and stream AI completion.
        4. Save completed assistant message to MongoDB.
        5. Emit SSE completion and [DONE] events.
        """
        # 1. Resolve or create conversation
        conv_doc = None
        if conversation_id:
            conv_doc = await conversation_service.get_raw_conversation(conversation_id)

        if not conv_doc:
            # Generate title from user message
            title = user_message[:40] + ("…" if len(user_message) > 40 else "")
            new_conv = await conversation_service.create_conversation(
                title=title,
                preferred_id=conversation_id,
            )
            resolved_id = new_conv.id
            history_messages: List[Dict[str, str]] = []
        else:
            resolved_id = str(conv_doc["_id"])
            history_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in conv_doc.get("messages", [])
            ]

        # 2. Append user message to database
        await conversation_service.add_message(
            conversation_id=resolved_id,
            role="user",
            content=user_message,
        )

        # 3. Build OpenAI messages payload
        system_prompt = get_system_prompt_for_tone(tone)
        messages_payload: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            *history_messages,
            {"role": "user", "content": user_message},
        ]

        # 4. Stream response from AI service
        full_assistant_reply: list[str] = []
        interrupted = False
        error_msg: str | None = None

        try:
            async for token in ai_service.stream_chat_completion(messages_payload):
                full_assistant_reply.append(token)
                yield sse_chunk(token)

        except asyncio.CancelledError:
            logger.warning("Streaming cancelled by client for conversation %s", resolved_id)
            interrupted = True
            error_msg = "Generation cancelled by user."
            raise

        except Exception as exc:
            logger.error("Error during streaming for conversation %s: %s", resolved_id, exc)
            interrupted = True
            error_msg = str(exc)
            yield sse_error(str(exc))

        finally:
            accumulated_text = "".join(full_assistant_reply)
            if accumulated_text or interrupted:
                # Save assistant response (including partial if interrupted)
                await conversation_service.add_message(
                    conversation_id=resolved_id,
                    role="assistant",
                    content=accumulated_text or "(No response generated)",
                    error=error_msg,
                )

        # 5. Emit completion and termination
        yield sse_completion(resolved_id)
        yield sse_done()

    async def stream_regenerate(
        self,
        conversation_id: str,
        user_message: Optional[str] = None,
        tone: ToneType | str = ToneType.PROFESSIONAL,
    ) -> AsyncGenerator[str, None]:
        """
        Regenerate the last assistant response:
        1. Find conversation and historical context up to the last user message.
        2. Exclude previous assistant response from context.
        3. Stream replacement response.
        4. Replace last assistant response in MongoDB.
        """
        conv_doc = await conversation_service.get_raw_conversation(conversation_id)
        if not conv_doc:
            yield sse_error(f"Conversation '{conversation_id}' not found.")
            yield sse_done()
            return

        resolved_id = str(conv_doc["_id"])
        messages = conv_doc.get("messages", [])

        # Find the last user message
        last_user_idx = None
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].get("role") == "user":
                last_user_idx = i
                break

        if last_user_idx is None:
            yield sse_error("No user message found to regenerate response for.")
            yield sse_done()
            return

        target_prompt = user_message or messages[last_user_idx].get("content", "")

        # Build context from messages BEFORE the last user message, then add last user message
        prior_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages[:last_user_idx]
        ]

        system_prompt = get_system_prompt_for_tone(tone)
        messages_payload: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            *prior_messages,
            {"role": "user", "content": target_prompt},
        ]

        full_reply: list[str] = []
        interrupted = False
        error_msg: str | None = None

        try:
            async for token in ai_service.stream_chat_completion(messages_payload):
                full_reply.append(token)
                yield sse_chunk(token)

        except asyncio.CancelledError:
            logger.warning("Regeneration cancelled by client for conversation %s", resolved_id)
            interrupted = True
            error_msg = "Regeneration cancelled by user."
            raise

        except Exception as exc:
            logger.error("Error during regeneration for conversation %s: %s", resolved_id, exc)
            interrupted = True
            error_msg = str(exc)
            yield sse_error(str(exc))

        finally:
            accumulated_text = "".join(full_reply)
            if accumulated_text or interrupted:
                await conversation_service.replace_or_update_assistant_message(
                    conversation_id=resolved_id,
                    content=accumulated_text or "(No response generated)",
                    error=error_msg,
                )

        yield sse_completion(resolved_id)
        yield sse_done()


chat_service = ChatService()
