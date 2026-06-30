from app.core.prompts import format_retrieved_excerpts
from app.models.schemas import QueryRequest, QueryResponse
from app.services.vector_store_service import VectorStoreService
from app.services.llm_service import LLMService, MISSING_INFORMATION_MESSAGE


class RetrievalService:
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.llm_service = LLMService()

    def _build_sources(self, results):
        sources = []
        seen_sources = set()

        for doc in results:
            metadata = doc.metadata
            page = metadata.get("page", 0) + 1
            chunk_index = metadata.get("chunk_index", 0)
            source_key = (
                metadata.get("document_id", ""),
                metadata.get("filename", ""),
                page,
                chunk_index,
            )

            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)
            sources.append(
                {
                    "document_id": metadata.get("document_id", ""),
                    "filename": metadata.get("filename", ""),
                    "page": page,
                    "chunk": chunk_index,
                    "chunk_index": chunk_index,
                }
            )

        return sources

    def ask_documents(self, request: QueryRequest) -> QueryResponse:
        results = self.vector_store_service.search_similar_documents(
            request.query,
            request.top_k,
            filter=(
                {"document_id": request.document_id} if request.document_id else None
            ),
        )
        if not results:
            return QueryResponse(
                answer=MISSING_INFORMATION_MESSAGE,
                sources=[],
            )

        context = format_retrieved_excerpts(results)
        answer = self.llm_service.generate_answer(
            question=request.query,
            context=context,
        )
        return QueryResponse(
            answer=answer,
            sources=self._build_sources(results),
        )
