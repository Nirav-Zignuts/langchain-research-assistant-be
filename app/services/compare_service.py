from app.core.prompts import format_retrieved_excerpts
from app.models.schemas import (
    CompareRequest,
    CompareResponse,
)
from app.services.llm_service import LLMService
from app.services.vector_store_service import VectorStoreService


class CompareService:
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.llm_service = LLMService()

    def _build_source(self, doc):
        metadata = doc.metadata
        page = metadata.get("page", 0) + 1
        chunk_index = metadata.get("chunk_index", 0)
        return {
            "document_id": metadata.get("document_id", ""),
            "filename": metadata.get("filename", ""),
            "page": page,
            "chunk": chunk_index,
            "chunk_index": chunk_index,
        }

    def _build_document_section(self, document_id: str, filename: str, results) -> str:
        return "\n".join(
            [
                f"## Document: {filename}",
                f"Document ID: {document_id}",
                "",
                format_retrieved_excerpts(results),
            ]
        )

    def compare_documents(
        self,
        request: CompareRequest,
    ) -> CompareResponse:

        document_sections = []
        sources = []
        seen_sources = set()
        question = request.query or "No specific question provided."

        for document_id in request.document_ids:

            results = self.vector_store_service.search_similar_documents(
                query=question,
                k=4,
                filter={"document_id": document_id},
            )

            if not results:
                continue

            filename = results[0].metadata.get("filename", "unknown")

            document_sections.append(
                self._build_document_section(document_id, filename, results)
            )

            for doc in results:
                source = self._build_source(doc)
                source_key = (
                    source["document_id"],
                    source["filename"],
                    source["page"],
                    source["chunk_index"],
                )

                if source_key in seen_sources:
                    continue

                seen_sources.add(source_key)
                sources.append(source)

        if len(document_sections) < 2:
            return CompareResponse(
                comparison="Not enough documents found for comparison.",
                sources=sources,
            )

        comparison = self.llm_service.generate_comparison(
            question=question,
            document_sections=document_sections,
        )

        return CompareResponse(
            comparison=comparison,
            sources=sources,
        )
