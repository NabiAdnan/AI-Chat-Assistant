from enum import Enum


class ToneType(str, Enum):
    PROFESSIONAL = "Professional"
    CASUAL = "Casual"
    CONCISE = "Concise"


TONE_SYSTEM_PROMPTS: dict[ToneType, str] = {
    ToneType.PROFESSIONAL: (
        "Respond in a professional manner. Use structured explanations, "
        "clear language and appropriate technical terminology."
    ),
    ToneType.CASUAL: (
        "Respond in a friendly, conversational and approachable manner. "
        "Use simple language and natural expressions."
    ),
    ToneType.CONCISE: (
        "Respond briefly and directly. Focus on essential information "
        "and avoid unnecessary explanations."
    ),
}

DEFAULT_SYSTEM_BASE = (
    "You are Nexus AI, an intelligent, helpful, and versatile AI assistant. "
    "Always follow markdown best practices for formatting code blocks, bullet points, and headers."
)


def get_system_prompt_for_tone(tone: ToneType | str) -> str:
    """Return the validated system instruction for the given tone."""
    if isinstance(tone, str):
        try:
            tone_enum = ToneType(tone)
        except ValueError:
            tone_enum = ToneType.PROFESSIONAL
    else:
        tone_enum = tone

    tone_instruction = TONE_SYSTEM_PROMPTS.get(
        tone_enum, TONE_SYSTEM_PROMPTS[ToneType.PROFESSIONAL]
    )
    return f"{DEFAULT_SYSTEM_BASE}\n\nTone Instruction:\n{tone_instruction}"
