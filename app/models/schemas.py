from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class UploadResponse(BaseModel):
    filename: str
    path: str
    message: str
    document_id: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=4, ge=1, le=20)
    document_id: str | None = None


class Source(BaseModel):
    document_id: str
    filename: str
    page: int
    chunk: int
    chunk_index: int

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    uploaded_at: str


class DocumentDetailResponse(DocumentResponse):
    file_path: str


class DeleteDocumentResponse(BaseModel):
    message: str


class CompareRequest(BaseModel):
    document_ids: list[str] = Field(..., min_length=2)
    query: str | None = None


class CompareSource(BaseModel):
    document_id: str
    filename: str
    page: int
    chunk: int
    chunk_index: int


class CompareResponse(BaseModel):
    comparison: str
    sources: list[CompareSource] = Field(default_factory=list)

