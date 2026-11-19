import json
from typing import Any, AsyncGenerator


def format_sse_event(data: Any, event: str | None = None) -> str:
    """Format data as a Server-Sent Events (SSE) data frame."""
    lines: list[str] = []
    if event:
        lines.append(f"event: {event}")

    if isinstance(data, (dict, list)):
        payload = json.dumps(data)
    else:
        payload = str(data)

    for line in payload.splitlines():
        lines.append(f"data: {line}")

    return "\n".join(lines) + "\n\n"


def sse_chunk(content: str) -> str:
    """Format an AI token chunk for SSE."""
    return format_sse_event({"content": content})


def sse_completion(conversation_id: str) -> str:
    """Format a completion event containing the conversation ID."""
    return format_sse_event({
        "status": "completed",
        "conversation_id": conversation_id,
    })


def sse_done() -> str:
    """Standard SSE termination event."""
    return "data: [DONE]\n\n"


def sse_error(message: str) -> str:
    """Format an error message event."""
    return format_sse_event({"error": message})
