# Research Assistant API

A FastAPI-based research assistant that lets you upload PDF documents, store them in a vector database, and ask questions or compare documents using **Retrieval-Augmented Generation (RAG)**.

The API returns conversational, grounded answers — based only on content retrieved from your uploaded files.

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Architecture Overview](#architecture-overview)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Installation](#installation)
7. [Environment Variables](#environment-variables)
8. [Running the Server](#running-the-server)
9. [API Reference](#api-reference)
10. [How RAG Works](#how-rag-works-in-this-project)
11. [Data Storage](#data-storage)
12. [Configuration & Tuning](#configuration--tuning)
13. [Troubleshooting](#troubleshooting)
14. [Development Notes](#development-notes)

---

## Features

- PDF upload with automatic text extraction and chunking
- Vector embeddings stored in ChromaDB for semantic search
- Ask questions across all documents or a single document
- Compare two or more documents with structured markdown output
- Document management: list, view details, and delete
- Conversational answers with hallucination protection
- Source citations (document ID, filename, page, chunk index)
- Persistent metadata in SQLite
- CORS enabled for local frontend (`http://localhost:5173`)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI + Uvicorn |
| Language | Python 3.12+ |
| LLM | Groq (`llama-3.3-70b-versatile` via langchain-groq) |
| Embeddings | Cohere (`embed-english-v3.0`) or OpenAI (`text-embedding-3-small`) |
| Vector Database | ChromaDB (persistent local storage) |
| Metadata Database | SQLite (SQLAlchemy) |
| PDF Processing | PyPDF + LangChain document loaders |
| Chunking | RecursiveCharacterTextSplitter (LangChain) |

---

## Architecture Overview

### Upload Flow

```
PDF file
  → Save to disk (data/uploads/)
  → Extract text per page (PyPDFLoader)
  → Split into chunks (1000 chars, 200 overlap)
  → Embed chunks (Cohere or OpenAI)
  → Store in ChromaDB with metadata
  → Save document record in SQLite
```

### Ask Flow

```
User question
  → Embed query and search ChromaDB (top_k similar chunks)
  → Format retrieved excerpts with metadata labels
  → Send to LLM with system + user prompts (RAG)
  → Return conversational answer + source references
```

### Compare Flow

```
User question + document IDs (2 or more)
  → Retrieve relevant chunks per document
  → Build structured prompt with per-document sections
  → LLM generates markdown comparison
  → Return comparison + deduplicated sources
```

### Layered Design

| Layer | Location | Responsibility |
|-------|----------|----------------|
| App entry | `main.py` | FastAPI app, CORS, startup DB init |
| Routes | `app/api/routes.py` | HTTP endpoints |
| Services | `app/services/` | Upload, retrieval, compare, LLM |
| Database | `app/db/` | SQLite models and repository |
| Core | `app/core/` | Config, constants, RAG prompts |
| Schemas | `app/models/` | Pydantic request/response models |

---

## Project Structure

```
research_assistence/
├── main.py                         # FastAPI entry point
├── requirements.txt                # Python dependencies (pinned versions)
├── runtime.txt                     # Python version (3.12.4)
├── README.md                       # This file
├── .env                            # API keys and config (not committed)
│
├── app/
│   ├── api/
│   │   └── routes.py               # All REST API endpoints
│   ├── core/
│   │   ├── config.py               # Settings loaded from environment
│   │   ├── constants.py            # Default paths and collection name
│   │   └── prompts.py              # RAG system/user prompts
│   ├── db/
│   │   ├── database.py             # SQLAlchemy engine and session
│   │   ├── models.py               # DocumentRecord table
│   │   ├── document_repository.py  # CRUD for document metadata
│   │   └── chroma_client.py        # Chroma client helper
│   ├── models/
│   │   └── schemas.py              # Pydantic API schemas
│   └── services/
│       ├── document_service.py     # Upload, list, get, delete
│       ├── vector_store_service.py # Chroma search and storage
│       ├── retrieval_service.py    # Ask / question answering
│       ├── compare_service.py      # Multi-document comparison
│       ├── llm_service.py          # Groq LLM integration
│       └── embedding_service.py    # Embedding helper (legacy/unused in main flow)
│
├── data/                           # Created at runtime
│   ├── uploads/                    # Stored PDF files
│   ├── chroma/                     # ChromaDB persistent data
│   └── research_assistant.db       # SQLite metadata database
│
└── tests/
    └── .gitkeep                    # Test directory placeholder
```

---

## Prerequisites

- Python 3.12 or newer
- pip (Python package manager)
- API keys (at minimum):
  - `GROQ_API_KEY` — required for LLM answers
  - `COHERE_API_KEY` — required for embeddings (unless using OpenAI)
  - **OR** `OPENAI_API_KEY` — alternative for embeddings

Get API keys:

- Groq: https://console.groq.com/
- Cohere: https://dashboard.cohere.com/
- OpenAI: https://platform.openai.com/

---

## Installation

**Step 1:** Navigate to the project directory

```bash
cd research_assistence
```

**Step 2:** Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

**Step 3:** Install dependencies

```bash
pip install -r requirements.txt
```

**Step 4:** Create a `.env` file in the project root (see [Environment Variables](#environment-variables))

**Step 5:** Run the server

```bash
uvicorn main:app --reload --port 8001
```

The API will be available at:

- API: http://127.0.0.1:8001
- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc

---

## Environment Variables

Create a `.env` file in the project root:

### Required

```env
GROQ_API_KEY=your_groq_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
```

### Optional

```env
OPENAI_API_KEY=your_openai_api_key_here
APP_NAME=Research Assistant
APP_VERSION=0.1.0
API_PREFIX=/api
UPLOAD_DIR=data/uploads
CHROMA_DIR=data/chroma
CHROMA_COLLECTION_NAME=research_documents
DATABASE_URL=sqlite:///data/research_assistant.db
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.35
```

**Notes:**

- If `OPENAI_API_KEY` is set, OpenAI embeddings are used instead of Cohere.
- `LLM_TEMPERATURE` controls answer creativity (`0.0` = strict, `1.0` = creative). Default `0.35` balances grounded answers with a natural conversational tone.
- Never commit `.env` to version control. It is listed in `.gitignore`.

---

## Running the Server

**Development (auto-reload on code changes):**

```bash
uvicorn main:app --reload --port 8001
```

**Production-style (no reload):**

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

**Health check:**

```bash
curl http://127.0.0.1:8001/
curl http://127.0.0.1:8001/api/health
```

Expected response:

```json
{"status": "ok"}
```

---

## API Reference

**Base URL:** `http://127.0.0.1:8001/api`

All endpoints except `GET /` and `GET /api/health` are under the `/api` prefix.

### `GET /api/health`

Check if the API is running.

**Response:**

```json
{"status": "ok"}
```

---

### `POST /api/documents`

Upload a PDF document.

- **Content-Type:** `multipart/form-data`
- **Body:** `file` (PDF only)

```bash
curl -X POST http://127.0.0.1:8001/api/documents \
  -F "file=@/path/to/document.pdf"
```

**Response:**

```json
{
  "filename": "document.pdf",
  "path": "data/uploads/<uuid>_document.pdf",
  "message": "Document uploaded successfully",
  "document_id": "<uuid>"
}
```

**Errors:** `400` (non-PDF file), `500` (upload or processing failure)

---

### `GET /api/documents`

List all uploaded documents.

```bash
curl http://127.0.0.1:8001/api/documents
```

**Response:**

```json
[
  {
    "document_id": "<uuid>",
    "filename": "document.pdf",
    "uploaded_at": "2026-06-26T11:59:45.366254Z"
  }
]
```

---

### `GET /api/documents/{document_id}`

Get details for a single document.

```bash
curl http://127.0.0.1:8001/api/documents/<document_id>
```

**Response:**

```json
{
  "document_id": "<uuid>",
  "filename": "document.pdf",
  "file_path": "data/uploads/<uuid>_document.pdf",
  "uploaded_at": "2026-06-26T11:59:45.366254Z"
}
```

**Errors:** `404` (document not found)

---

### `DELETE /api/documents/{document_id}`

Delete a document and all associated data (Chroma chunks, file, DB record).

```bash
curl -X DELETE http://127.0.0.1:8001/api/documents/<document_id>
```

**Response:**

```json
{"message": "Document deleted successfully"}
```

**Errors:** `404` (document not found), `500` (failed to delete chunks or file)

---

### `POST /api/ask`

Ask a question about uploaded documents using RAG.

- **Content-Type:** `application/json`

**Request body:**

```json
{
  "query": "What is the main topic of the document?",
  "top_k": 4,
  "document_id": "<uuid>"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `query` | Yes | Question to ask (min 1 character) |
| `top_k` | No | Number of chunks to retrieve (default: 4, max: 20) |
| `document_id` | No | Limit search to one document |

```bash
curl -X POST http://127.0.0.1:8001/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is git commit used for?",
    "top_k": 4,
    "document_id": "<document_id>"
  }'
```

**Response:**

```json
{
  "answer": "Git commit is used to save changes...",
  "sources": [
    {
      "document_id": "<uuid>",
      "filename": "git-cheat-sheet.pdf",
      "page": 1,
      "chunk": 0,
      "chunk_index": 0
    }
  ]
}
```

**Notes:**

- Answers are conversational and synthesized, not raw chunk dumps.
- If no relevant content is found, the answer will be: `"I could not find this information in the uploaded documents."`

---

### `POST /api/compare`

Compare two or more documents.

- **Content-Type:** `application/json`

**Request body:**

```json
{
  "document_ids": ["<uuid-1>", "<uuid-2>"],
  "query": "What are the key differences in approach?"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `document_ids` | Yes | List of at least 2 document UUIDs |
| `query` | No | Focus question for the comparison |

```bash
curl -X POST http://127.0.0.1:8001/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": ["<document_id_1>", "<document_id_2>"],
    "query": "Compare the learning paths described in each document"
  }'
```

**Response:**

```json
{
  "comparison": "## Overview\n\n...",
  "sources": [
    {
      "document_id": "<uuid>",
      "filename": "doc1.pdf",
      "page": 2,
      "chunk": 3,
      "chunk_index": 3
    }
  ]
}
```

**Notes:**

- Supports comparing more than 2 documents.
- Comparison is returned as markdown text.
- Returns `"Not enough documents found for comparison."` if fewer than 2 documents have retrievable content.

---

## How RAG Works in This Project

Retrieval-Augmented Generation (RAG) combines document search with an LLM so answers are grounded in your uploaded files instead of the model's general training data.

### Prompt Design (`app/core/prompts.py`)

- **System prompt** defines assistant behavior, tone, and strict grounding rules.
- **User prompt** wraps retrieved excerpts in `<retrieved_excerpts>` tags and separates them from the user's question.
- Instructions explicitly tell the model to paraphrase and synthesize, not copy long passages verbatim.
- Missing information triggers a fixed fallback message instead of guessing.

### LLM Integration (`app/services/llm_service.py`)

- Uses proper chat messages: `SystemMessage` + `HumanMessage`.
- Groq `ChatGroq` with configurable model and temperature.
- Separate methods for ask (`generate_answer`) and compare (`generate_comparison`).

### Chunking Strategy

- **Chunk size:** 1000 characters
- **Chunk overlap:** 200 characters
- Each chunk stores metadata: `document_id`, `filename`, `page`, `chunk_index`, upload timestamp, and file path.

---

## Data Storage

| Location | Purpose |
|----------|---------|
| `data/uploads/` | Original PDF files (named `<uuid>_<filename>.pdf`) |
| `data/chroma/` | ChromaDB vector index (embeddings + chunk metadata) |
| `data/research_assistant.db` | SQLite table: `documents` (id, filename, path, date) |

Deleting a document removes:

1. All Chroma chunks matching `document_id`
2. The physical PDF file
3. The SQLite metadata record

---

## Configuration & Tuning

### Improve answer quality

- Increase `top_k` (up to 20) to retrieve more context per question.
- Adjust `LLM_TEMPERATURE` in `.env` (try `0.2` for stricter, `0.5` for more natural).
- Upload documents with clear, text-based PDFs (scanned images without OCR will produce poor results).

### Improve retrieval quality

- Chunk size and overlap are in `document_service.py` (`chunk_documents` method).
- Smaller chunks = more precise retrieval; larger chunks = more context per hit.

### CORS

CORS is configured in `main.py` for `http://localhost:5173` (Vite default). Add other frontend origins there if needed.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `"No embedding model provided"` | Set `COHERE_API_KEY` or `OPENAI_API_KEY` in `.env` and restart the server. |
| `"Could not import module app.main"` | Run uvicorn from the project root: `uvicorn main:app` (not `app.main:app`). |
| Port already in use | Kill the existing process or use a different port: `lsof -ti :8001 \| xargs kill -9` |
| Changes not reflected after editing code | Restart the server, or run with `--reload` flag. |
| ChromaDB readonly or import errors | Reinstall from `requirements.txt`: `pip install -r requirements.txt --force-reinstall`, then restart uvicorn. |
| Answers copy raw document text | Ensure latest code with `app/core/prompts.py` and `llm_service.py` using `SystemMessage` + `HumanMessage`. Restart the server. |
| Empty or poor answers | Verify PDF has extractable text, try increasing `top_k`, check upload via `GET /api/documents`. |
| API key errors from Groq or Cohere | Verify keys in `.env`, ensure no extra spaces or quotes, and restart. |

---

## Development Notes

**Key dependency pins** (see `requirements.txt`):

- `langchain==0.3.27`
- `langchain-chroma==0.2.6`
- `chromadb==1.3.5`
- `langchain-groq==0.3.8`
- `langchain-cohere==0.4.5`

Version mismatches between `langchain-chroma` and `chromadb` have caused import and runtime errors in the past. Always install from `requirements.txt`.

- The `tests/` directory is a placeholder. Automated tests are not included yet.
- Debug print statements exist in `document_service.py` during upload (chunk counts and metadata). These can be replaced with proper logging in a future cleanup.
- **Frontend integration:** CORS allows `http://localhost:5173`. All API routes are prefixed with `/api` (configurable via `API_PREFIX` env var).
