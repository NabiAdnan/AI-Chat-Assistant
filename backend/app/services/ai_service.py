import asyncio
import logging
from typing import AsyncGenerator, Dict, List, Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError

import openai
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger("nexus_ai.ai_service")


class AIService:
    def __init__(self) -> None:
        self._gemini_client: genai.Client | None = None
        self._openai_client: AsyncOpenAI | None = None

    @property
    def gemini_client(self) -> genai.Client:
        if self._gemini_client is None:
            api_key = settings.effective_gemini_key
            if not api_key or api_key == "your_gemini_api_key":
                logger.warning("GEMINI_API_KEY is not configured or using placeholder.")
            self._gemini_client = genai.Client(api_key=api_key or "missing-gemini-key")
        return self._gemini_client

    @property
    def openai_client(self) -> AsyncOpenAI:
        if self._openai_client is None:
            api_key = settings.OPENAI_API_KEY.strip()
            self._openai_client = AsyncOpenAI(api_key=api_key or "missing-openai-key")
        return self._openai_client

    def reset_clients(self) -> None:
        """Reset cached clients when settings change."""
        self._gemini_client = None
        self._openai_client = None

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat tokens using the active provider: Google Gemini (default) or OpenAI.
        """
        provider = settings.AI_PROVIDER.lower().strip()
        if provider == "openai":
            async for token in self._stream_openai(messages, model=model):
                yield token
        else:
            async for token in self._stream_gemini(messages, model=model):
                yield token

    async def _stream_gemini(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream tokens via Google Gemini API using the official Google GenAI SDK.
        """
        target_model = model or settings.GEMINI_MODEL
        logger.info(
            "Sending streaming request to Google Gemini (model: %s, messages: %d)",
            target_model,
            len(messages),
        )

        # Separate system instruction from conversation turns
        system_instruction: Optional[str] = None
        contents: List[types.Content] = []

        for m in messages:
            role = m.get("role", "user")
            content_text = m.get("content", "")
            if role == "system":
                system_instruction = content_text
            else:
                gemini_role = "user" if role == "user" else "model"
                contents.append(
                    types.Content(
                        role=gemini_role,
                        parts=[types.Part.from_text(text=content_text)],
                    )
                )

        # Fallback if no content
        if not contents:
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="Hello")],
                )
            )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction if system_instruction else None,
            temperature=0.7,
        )

        try:
            response = await self.gemini_client.aio.models.generate_content_stream(
                model=target_model,
                contents=contents,
                config=config,
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except APIError as exc:
            logger.error("Gemini APIError: %s", exc)
            msg = str(exc)
            if "API_KEY_INVALID" in msg or "400" in msg or "403" in msg:
                raise RuntimeError(
                    "Google Gemini authentication failed. Please verify your GEMINI_API_KEY in backend/.env."
                ) from exc
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                raise RuntimeError(
                    "Google Gemini quota or rate limit exceeded. Please wait a moment and try again."
                ) from exc
            raise RuntimeError(f"Google Gemini service error: {exc.message}") from exc

        except asyncio.CancelledError:
            logger.info("Gemini generation stream was cancelled by client.")
            raise

        except Exception as exc:
            logger.error("Unexpected error in Gemini streaming: %s", exc)
            msg = str(exc)
            if "API_KEY_INVALID" in msg or "api key not valid" in msg.lower():
                raise RuntimeError(
                    "Google Gemini authentication failed. Please verify your GEMINI_API_KEY in backend/.env."
                ) from exc
            raise RuntimeError(f"Gemini AI error: {msg}") from exc

    async def _stream_openai(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream tokens via OpenAI API.
        """
        target_model = model or settings.OPENAI_MODEL
        logger.info(
            "Sending streaming request to OpenAI (model: %s, messages: %d)",
            target_model,
            len(messages),
        )

        try:
            response = await self.openai_client.chat.completions.create(
                model=target_model,
                messages=messages,  # type: ignore[arg-type]
                stream=True,
                timeout=60.0,
            )

            async for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content

        except openai.AuthenticationError as exc:
            logger.error("OpenAI Authentication Error: %s", exc)
            raise RuntimeError(
                "OpenAI authentication failed. Please verify your OPENAI_API_KEY in backend/.env."
            ) from exc

        except openai.RateLimitError as exc:
            logger.error("OpenAI Rate Limit Error: %s", exc)
            raise RuntimeError(
                "OpenAI rate limit exceeded. Please wait a moment and try again."
            ) from exc

        except openai.APITimeoutError as exc:
            logger.error("OpenAI Request Timeout: %s", exc)
            raise RuntimeError(
                "The OpenAI API request timed out. Please try again."
            ) from exc

        except openai.APIConnectionError as exc:
            logger.error("OpenAI Connection Error: %s", exc)
            raise RuntimeError(
                "Failed to connect to the OpenAI API. Please check your internet connection."
            ) from exc

        except openai.APIError as exc:
            logger.error("OpenAI API Error: %s", exc)
            raise RuntimeError(f"OpenAI service error: {exc.message}") from exc

        except asyncio.CancelledError:
            logger.info("OpenAI streaming generation was cancelled by client.")
            raise

        except Exception as exc:
            logger.error("Unexpected error in OpenAI streaming: %s", exc)
            raise RuntimeError(f"AI response generation error: {str(exc)}") from exc


ai_service = AIService()
