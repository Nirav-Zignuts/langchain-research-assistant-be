from datetime import datetime, timezone
from pathlib import Path
from pprint import pprint
import uuid
from fastapi import HTTPException, UploadFile
from langchain_core.documents import Document
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.document_repository import DocumentRepository, format_uploaded_at
from app.models.schemas import (
    DeleteDocumentResponse,
    DocumentDetailResponse,
    DocumentResponse,
    UploadResponse,
)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.vector_store_service import VectorStoreService

vector_store_service = VectorStoreService()


class DocumentService:
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_document(self, file: UploadFile) -> UploadResponse:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed",
            )

        try:
            document_id = str(uuid.uuid4())
            uploaded_at = datetime.now(timezone.utc)

            destination = (
                self.upload_dir
                / f"{document_id}_{file.filename}"
            )

            content = await file.read()
            destination.write_bytes(content)

            documents = self.load_documents(str(destination))
            pprint(documents[0].metadata)
            pprint(documents[0].page_content[:500])
            for document in documents:
                document.metadata["document_id"] = document_id
                document.metadata["filename"] = file.filename
                document.metadata["path"] = str(destination)
                document.metadata["uploaded_at"] = uploaded_at.isoformat()

            chunks = self.chunk_documents(documents)
            print("-" * 100)
            pprint(len(documents))
            pprint(len(chunks))
            print("-" * 100)
            for index, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = index

            print("-" * 100)
            pprint(chunks[0].metadata)
            print("-" * 100)
            for chunk in chunks[:5]:
                print(
                    f"page={chunk.metadata['page']}, "
                    f"chunk={chunk.metadata.get('chunk_index')}"
                )
            print(f"Storing {len(chunks)} chunks in Chroma")
            vector_store_service.add_documents(chunks)
            print("Chunks stored successfully")
            with SessionLocal() as db:
                DocumentRepository(db).create(
                    document_id=document_id,
                    filename=file.filename,
                    file_path=str(destination),
                    uploaded_at=uploaded_at,
                )
            return UploadResponse(
                document_id=document_id,
                filename=file.filename,
                path=str(destination),
                message="Document uploaded successfully",
            )

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload document: {str(e)}",
            )
    def load_documents(self, file_path: str):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents

    def chunk_documents(self, documents: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        return chunks

    def list_documents(self) -> list[DocumentResponse]:
        try:
            with SessionLocal() as db:
                records = DocumentRepository(db).list_all()
                return [
                    DocumentResponse(
                        document_id=record.document_id,
                        filename=record.filename,
                        uploaded_at=format_uploaded_at(record.uploaded_at),
                    )
                    for record in records
                ]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list documents: {str(e)}",
            )

    def get_document(self, document_id: str) -> DocumentDetailResponse:
        try:
            with SessionLocal() as db:
                record = DocumentRepository(db).get_by_id(document_id)
                if not record:
                    raise HTTPException(
                        status_code=404,
                        detail="Document not found",
                    )
                return DocumentDetailResponse(
                    document_id=record.document_id,
                    filename=record.filename,
                    file_path=record.file_path,
                    uploaded_at=format_uploaded_at(record.uploaded_at),
                )
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get document: {str(e)}",
            )

    def delete_document(self, document_id: str) -> DeleteDocumentResponse:
        try:
            with SessionLocal() as db:
                repository = DocumentRepository(db)
                record = repository.get_by_id(document_id)
                if not record:
                    raise HTTPException(
                        status_code=404,
                        detail="Document not found",
                    )

                try:
                    vector_store_service.delete_documents_by_document_id(document_id)
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to delete document chunks: {str(e)}",
                    )

                file_path = Path(record.file_path)
                try:
                    if file_path.exists():
                        file_path.unlink()
                except OSError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to delete document file: {str(e)}",
                    )

                repository.delete(record)
                return DeleteDocumentResponse(message="Document deleted successfully")
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete document metadata: {str(e)}",
            )