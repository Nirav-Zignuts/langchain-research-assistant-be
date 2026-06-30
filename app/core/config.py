import os

from dotenv import load_dotenv
from pydantic import BaseModel

from app.core.constants import CHROMA_DIR, DATABASE_URL, DEFAULT_COLLECTION_NAME, UPLOAD_DIR


load_dotenv()


class Settings(BaseModel):
    app_name: str = "Research Assistant"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    upload_dir: str = UPLOAD_DIR
    chroma_dir: str = CHROMA_DIR
    chroma_collection_name: str = DEFAULT_COLLECTION_NAME
    database_url: str = DATABASE_URL
    openai_api_key: str | None = None
    cohere_api_key: str | None = None
    groq_api_key: str | None = None
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.35


settings = Settings(
    app_name=os.getenv("APP_NAME", "Research Assistant"),
    app_version=os.getenv("APP_VERSION", "0.1.0"),
    api_prefix=os.getenv("API_PREFIX", "/api"),
    upload_dir=os.getenv("UPLOAD_DIR", UPLOAD_DIR),
    chroma_dir=os.getenv("CHROMA_DIR", CHROMA_DIR),
    chroma_collection_name=os.getenv(
        "CHROMA_COLLECTION_NAME",
        DEFAULT_COLLECTION_NAME,
    ),
    database_url=os.getenv("DATABASE_URL", DATABASE_URL),
    openai_api_key=os.getenv("OPENAI_API_KEY") or None,
    cohere_api_key=os.getenv("COHERE_API_KEY") or None,
    groq_api_key=os.getenv("GROQ_API_KEY") or None,
    llm_model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
    llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.35")),
)
