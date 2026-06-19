from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database Configuration
    database_url: str = "postgresql://rupeeradar:secure_password@localhost:5432/rupeeradar_db"
    redis_url: str = "redis://localhost:6379/0"
    
    # Session Configuration
    session_ttl_minutes: int = 60
    
    # CORS Configuration
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # LLM Configuration
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    enable_llm: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
