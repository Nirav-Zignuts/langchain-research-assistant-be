from fastapi import APIRouter, UploadFile, File

from app.models.schemas import (
    CompareRequest,
    CompareResponse,
    DeleteDocumentResponse,
    DocumentDetailResponse,
    DocumentResponse,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    UploadResponse,
)

from app.services.document_service import DocumentService
from app.services.retrieval_service import RetrievalService
from app.services.compare_service import CompareService

router = APIRouter()

document_service = DocumentService()
retrieval_service = RetrievalService()
compare_service = CompareService()

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")

@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents() -> list[DocumentResponse]:
    return document_service.list_documents()


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: str) -> DocumentDetailResponse:
    return document_service.get_document(document_id)


@router.delete("/documents/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(document_id: str) -> DeleteDocumentResponse:
    return document_service.delete_document(document_id)


@router.post("/documents", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    return await document_service.save_document(file)


@router.post("/ask", response_model=QueryResponse)
async def query_documents(request: QueryRequest) -> QueryResponse:
    return retrieval_service.ask_documents(request)


@router.post("/compare", response_model=CompareResponse)
async def compare(request: CompareRequest) -> CompareResponse:
    return compare_service.compare_documents(request)
