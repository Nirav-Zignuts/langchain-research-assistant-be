from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.embedding_model = OpenAIEmbeddings(api_key=settings.openai_api_key)

    def embed_documents(self, documents: list[Document]) -> list[list[float]]:
        return self.embedding_model.embed_documents(documents)

