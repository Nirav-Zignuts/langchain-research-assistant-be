from langchain_core.documents import Document

ASK_SYSTEM_PROMPT = """You are a research assistant that helps users understand their uploaded documents.

Respond clear, conversational, and helpful — not like a search engine dumping raw text.

Rules:
1. Use ONLY the retrieved excerpts in the user message. Do not use outside knowledge.
2. Synthesize and explain in your own words. Connect ideas across excerpts into one cohesive answer.
3. Do NOT copy sentences or paragraphs from the excerpts. Paraphrase everything.
   You may quote at most one short phrase (under 8 words) only for a proper noun, technical term, or exact number.
4. Do not invent facts, numbers, names, or conclusions not supported by the excerpts.
5. If the excerpts do not answer the question, respond exactly with:
   "I could not find this information in the uploaded documents."

Answer format:
- Open with 1–2 sentences that directly answer the question.
- Follow with supporting explanation in plain language (short paragraphs; bullets only when they help).
- Mention source filenames inline when useful (e.g., "According to report.pdf...")."""

COMPARE_SYSTEM_PROMPT = """You are a research assistant that compares uploaded documents.



Rules:
1. Use ONLY the document excerpts in the user message. Do not use outside knowledge.
2. Synthesize in your own words. Do NOT copy sentences or paragraphs from the excerpts.
3. Do not invent facts. If information is missing for a document, say so explicitly.
4. Write the comparison in markdown.

Structure:
- Brief overview answering the user's question.
- For each document: key points relevant to the question (in your own words).
- Similarities, differences, and contradictions across documents when present."""


def format_retrieved_excerpts(documents: list[Document]) -> str:
    if not documents:
        return ""

    blocks: list[str] = []
    for index, doc in enumerate(documents, start=1):
        metadata = doc.metadata
        blocks.append(
            "\n".join(
                [
                    f"[Excerpt {index}]",
                    f"Document ID: {metadata.get('document_id', 'unknown')}",
                    f"Filename: {metadata.get('filename', 'unknown')}",
                    f"Page: {metadata.get('page', 0) + 1}",
                    f"Chunk: {metadata.get('chunk_index', 0)}",
                    "",
                    doc.page_content.strip(),
                ]
            )
        )

    return "\n\n".join(blocks)


def build_ask_user_prompt(question: str, context: str) -> str:
    return f"""Below are excerpts retrieved from uploaded documents. They are reference material only — not a script to copy.

<retrieved_excerpts>
{context}
</retrieved_excerpts>

User question:
{question}

Write a conversational explanation based only on the excerpts above.
Do not paste or repeat excerpt text — paraphrase and synthesize."""


def build_compare_user_prompt(question: str, document_sections: list[str]) -> str:
    documents_block = "\n\n".join(document_sections)

    return f"""Compare the documents with respect to the user's question.

Question:
{question}

The excerpts below are reference material only — not text to copy verbatim.

<document_excerpts>
{documents_block}
</document_excerpts>

For each document:
- Summarize relevant information
- Identify key findings
- Highlight similarities
- Highlight differences
- Highlight contradictions if present

Return the response in markdown."""
