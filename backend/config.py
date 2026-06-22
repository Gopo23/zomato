"""
Application configuration using Pydantic Settings.

Loads environment variables from .env file in the backend directory.
All settings are validated at startup — missing required fields
(e.g., GROQ_API_KEY) will raise a clear error immediately.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the Zomato recommendation system."""

    # ── Groq LLM ──────────────────────────────────────────────
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000

    # ── Data ──────────────────────────────────────────────────
    dataset_cache_path: str = os.path.join(
        os.path.dirname(__file__), "data", "zomato_dataset.csv"
    )

    # ── API ───────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"]
    rate_limit_per_minute: int = 10

    model_config = {
        "env_file": os.path.join(os.path.dirname(__file__), ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton instance — import this wherever settings are needed
settings = Settings()
