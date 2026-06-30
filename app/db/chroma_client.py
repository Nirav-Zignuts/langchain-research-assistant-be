import chromadb
from chromadb.api import ClientAPI

from app.core.config import settings


def get_chroma_client() -> ClientAPI:
    return chromadb.PersistentClient(path=settings.chroma_dir)


def get_document_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(settings.chroma_collection_name)
