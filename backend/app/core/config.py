import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AI_PROVIDER: str = "gemini"  # "gemini" (default) or "openai"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "nexus_ai"
    FRONTEND_URL: str = "http://localhost:5173"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def effective_gemini_key(self) -> str:
        return (
            self.GEMINI_API_KEY.strip()
            or os.environ.get("GOOGLE_API_KEY", "").strip()
            or os.environ.get("GEMINI_API_KEY", "").strip()
        )


settings = Settings()
