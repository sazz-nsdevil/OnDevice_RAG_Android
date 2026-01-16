# Cloud Server Side - OnDevice RAG

Backend server for the OnDevice RAG Android application. Handles document ingestion, text chunking, vector embeddings, and knowledge base export.

## Features

- 📄 **Document Upload & Processing**: Parse PDF, DOCX, and TXT files
- 🔀 **Intelligent Chunking**: LangChain-based recursive text splitting with configurable overlap
- 🧠 **Vector Embeddings**: ONNX-based embeddings (dragonkue-KoEn-E5-Tiny-ONNX, 384-dim vectors)
- 📊 **API Documentation**: Swagger UI for interactive API testing
- 💾 **Knowledge Base Export**: Download course knowledge bases as SQLite databases
- 🔄 **Automatic Model Caching**: HuggingFace models downloaded and cached locally

## Prerequisites

- **Python 3.12** (required for full compatibility)
- [uv](https://docs.astral.sh/uv/) package manager (fast, deterministic dependency management)

## Installation & Setup

### 1. Create Virtual Environment
```bash
uv venv
```

### 2. Activate Virtual Environment
```bash
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Run Migrations
```bash
uv run python manage.py migrate
```

### 5. Start Development Server
```bash
uv run python manage.py runserver
```

Server runs at `http://127.0.0.1:8000/`

## API Documentation

### Swagger UI
Interactive API documentation available at: **`http://127.0.0.1:8000/swagger/`**

### Main Endpoints

#### Courses
- `GET /api/knowledge/courses/` - List all courses
- `POST /api/knowledge/courses/` - Create a course
- `GET /api/knowledge/courses/{id}/` - Get course details with documents
- `GET /api/knowledge/courses/{id}/download_knowledge_base/` - Download course as SQLite vector database

#### Documents
- `GET /api/knowledge/documents/` - List all documents (filter by `course_id` query param)
- `POST /api/knowledge/documents/` - Upload and process a document
- `GET /api/knowledge/documents/{id}/` - Get document with chunks (no vectors)
- `GET /api/knowledge/documents/{id}/chunks/` - Get document chunks with metadata

#### Data Processing Pipeline
When you upload a document:
1. **Parse**: Extract text from PDF/DOCX/TXT
2. **Chunk**: Split text using RecursiveCharacterTextSplitter (200 char size, 50 char overlap)
3. **Embed**: Generate 384-dim vectors using ONNX model
4. **Store**: Save chunks with vectors to SQLite

## Project Structure

```
.
├── core/                           # Django project settings
│   ├── settings.py                 # Django configuration
│   ├── urls.py                     # URL routing
│   ├── wsgi.py                     # WSGI entry point
│   └── asgi.py                     # ASGI entry point
├── knowledge/                      # Main app for RAG functionality
│   ├── models.py                   # Database models (Course, Document, Chunk)
│   ├── views.py                    # API endpoints (ViewSets)
│   ├── serializers.py              # DRF serializers (API response formatting)
│   ├── services.py                 # Business logic (parsing, chunking, embedding)
│   ├── urls.py                     # App-level URL routing
│   ├── admin.py                    # Django admin configuration
│   └── migrations/                 # Database migrations
├── media/                          # Uploaded documents (git-ignored)
│   └── documents/                  # PDF, DOCX, TXT files
├── pretrained_models/              # ONNX model cache (git-ignored)
│   └── models--{organization}--{model-name}/  # Downloaded models
├── manage.py                       # Django management script
├── pyproject.toml                  # Project metadata & dependencies (uv)
├── db.sqlite3                      # SQLite database (git-ignored, auto-generated)
└── README.md                       # This file
```

## Understanding pretrained_models/

The `pretrained_models/` folder stores locally-cached machine learning models downloaded from HuggingFace Hub.

### What's Inside?
```
pretrained_models/
└── models--exp-models--dragonkue-KoEn-E5-Tiny-ONNX/
    ├── blobs/                      # Model weights in binary format
    ├── refs/                       # Git refs (tracking which commit)
    └── snapshots/
        └── {hash}/                 # Specific model version
            ├── config.json         # Model configuration
            ├── tokenizer.json      # Text tokenizer (converts words → tokens)
            ├── special_tokens_map.json  # Mapping for special tokens
            └── onnx/               # ONNX runtime model files
                ├── model.onnx      # Full precision model
                └── model_qint8_arm64.onnx  # Quantized for ARM64 (mobile)
```

### Why ONNX?
- **ONNX (Open Neural Network Exchange)**: Standardized ML model format
- **Performance**: Optimized inference, lower memory footprint
- **Portability**: Same model runs on cloud (Python) and Android (Java/Kotlin)
- **Quantized ARM64 version**: For efficient execution on mobile devices

### Auto-Caching Behavior
- On first `/documents/` POST request, the system downloads the ONNX model from HuggingFace
- Model is cached in `pretrained_models/` for subsequent requests (no re-download)
- Folder structure matches HuggingFace Hub's cache format for compatibility

## Reproducibility

This project is fully reproducible using `uv`:

- **Deterministic dependencies**: `uv` locks all package versions in `uv.lock`
- **Python 3.12**: All development done with Python 3.12; specify this version for full compatibility
- **No requirements.txt**: Use `uv sync` to install exact same versions everywhere
- **Fresh Database**: Run `uv run python manage.py migrate` to recreate schema
- **Model Caching**: ONNX models auto-downloaded on first use, no manual setup needed

### Quick Fresh Start
```bash
# Clean database
rm db.sqlite3

# Create fresh database
uv run python manage.py migrate

# Run server
uv run python manage.py runserver
```

## Development Notes

- Database (`db.sqlite3`) is git-ignored and regenerated locally
- Uploaded documents (`media/`) are git-ignored for file management simplicity
- Pretrained models (`pretrained_models/`) are git-ignored because they're large binary files
- Always use `uv run` to execute Python commands within the virtual environment
- Admin panel available at `http://127.0.0.1:8000/admin/` (create superuser with `uv run python manage.py createsuperuser`)
