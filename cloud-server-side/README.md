# Cloud Server Side - OnDevice RAG

This is the cloud server component for the OnDevice RAG Android application, built with Django.

## Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) package manager

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
uv pip install -r requirements.txt
```

### 4. Run Migrations
```bash
uv run python manage.py migrate
```

### 5. Start Development Server
```bash
uv run python manage.py runserver
```

The server will be running at `http://127.0.0.1:8000/`

## Project Structure

- `core/` - Django project configuration
- `db.sqlite3` - SQLite database (development only)
- `manage.py` - Django management script
- `pyproject.toml` - Project metadata and dependencies

## Notes

- The `db.sqlite3` file is ignored by git and should be regenerated locally
- Use `uv run` to execute commands within the virtual environment
