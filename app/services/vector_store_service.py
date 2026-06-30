from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from app.core.config import settings


class VectorStoreService:
    def __init__(self):
        if settings.openai_api_key:
            self.embedding_model = OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                model="text-embedding-3-small",
            )
            print("Using OpenAI embedding model")
        elif settings.cohere_api_key:
            self.embedding_model = CohereEmbeddings(
                cohere_api_key=settings.cohere_api_key,
                model="embed-english-v3.0",
            )
            print("Using Cohere embedding model")
        else:
            print("No embedding model provided")
            raise ValueError("No embedding model provided")

        self.vector_store = Chroma(
            collection_name=settings.chroma_collection_name,
            persist_directory=settings.chroma_dir,
            embedding_function=self.embedding_model,
        )

    def add_documents(self, chunks: list[Document]) -> None:
        self.vector_store.add_documents(chunks)

    def search_similar_documents(
        self,
        query: str,
        k: int = 4,
        filter: dict | None = None,
    ) -> list[Document]:
        if filter:
            return self.vector_store.similarity_search(query, k, filter=filter)
        else:
            return self.vector_store.similarity_search(query, k)

    def delete_documents_by_document_id(self, document_id: str) -> None:
        self.vector_store.delete(where={"document_id": document_id})
