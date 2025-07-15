# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data processing web application for extracting and structuring laptop/notebook specifications from text files. The system consists of a FastAPI backend with database ingestion capabilities and a vanilla JavaScript frontend.

## Development Commands

### Backend
```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run the FastAPI server
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run without reload for production
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Serve frontend (requires Python)
cd frontend && python -m http.server 8080

# Or use any static file server
cd frontend && npx serve .
```

### Database Setup
The application uses DuckDB and Milvus for data storage:
- DuckDB file: `sales_specs.db` (created automatically)
- Milvus connection: localhost:19530 (configurable via environment variables)

### Database Management Tools
Located in the `tools/` directory:
- **duckdbviewer.py**: View and export DuckDB data
- **db_cleaner.py**: Clean all data from databases (preserves structure)
- **milvusviewer.py**: View Milvus vector data (if available)

```bash
# Check database status
cd tools && python db_cleaner.py status

# Clear all data (with confirmation)
cd tools && python db_cleaner.py clear-all
```

## Architecture

### Backend Structure
- **FastAPI Application**: Main API server (`backend/app/main.py`)
- **Strategy Pattern**: Text parsing using pluggable strategies (`backend/app/strategies/`)
- **Data Models**: Pydantic models for API requests/responses (`backend/app/models.py`)
- **Parser Engine**: Orchestrates text processing using rules and strategies (`backend/app/parser.py`)
- **Database Ingestion**: Handles data insertion into DuckDB and Milvus (`backend/app/db_ingestor.py`)

### Core Components

#### Text Processing Pipeline
1. **Parser** (`parser.py`): Merges default and custom rules, orchestrates parsing
2. **Strategy Pattern** (`strategies/`): 
   - `BaseParsingStrategy`: Abstract base class
   - `RuleBasedStrategy`: Concrete implementation using regex rules
3. **Rules System** (`default_rules.json`): Field mapping for text extraction

#### Database Integration
- **DuckDB**: Structured data storage with SQL capabilities
- **Milvus**: Vector database for semantic search using SentenceTransformer embeddings
- **Dual Ingestion**: Data is stored in both systems simultaneously

### Frontend Architecture
- **Vanilla JavaScript**: No frameworks, uses native DOM manipulation
- **State Management**: Simple object-based state for UI data
- **API Integration**: RESTful communication with FastAPI backend
- **File Handling**: Supports both file upload and drag-and-drop

## Key Features

### Data Processing
- **Rule-based extraction**: Uses configurable JSON rules for field mapping
- **Model identification**: Extracts laptop model names from text sections
- **Field extraction**: Parses specifications like CPU, GPU, memory, storage, etc.
- **Custom rules**: Supports user-uploaded rule files to extend default extraction

### Data Storage
- **Structured storage**: DuckDB for SQL queries and data analysis
- **Vector storage**: Milvus for semantic similarity search
- **Embeddings**: Uses `all-MiniLM-L6-v2` model for generating text embeddings

### Web Interface
- **Text input**: Paste text directly or upload .txt files
- **Processing controls**: Custom rules and temporary regex patterns
- **Data editing**: Editable table interface for processed data
- **Export/Import**: CSV file support for data exchange
- **Database ingestion**: One-click ingestion to both databases

## Environment Variables

```bash
# Milvus configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

## Data Flow

1. **Text Input**: User provides text via upload or paste
2. **Rule Processing**: Parser merges default rules with custom rules
3. **Strategy Execution**: RuleBasedStrategy extracts structured data
4. **Data Presentation**: Results displayed in editable table
5. **Database Ingestion**: Data inserted into DuckDB and Milvus with embeddings

## Important Files

- `backend/app/default_rules.json`: Default field extraction rules
- `backend/app/strategies/concrete_strategies.py`: Core parsing logic
- `backend/app/db_ingestor.py`: Database insertion logic
- `frontend/app.js`: Complete frontend application logic

## Recent Security & Quality Improvements

### Security Enhancements (2025-01-08)

1. **CORS Configuration**: Restricted allowed origins to localhost:8080 and 127.0.0.1:8080 only
   - **File**: `backend/app/main.py:15-18`
   - **Change**: Replaced wildcard `allow_origins=["*"]` with specific origins
   - **Methods**: Limited to GET and POST only

2. **Input Validation**: Added regex pattern validation for user inputs
   - **File**: `backend/app/main.py:22-34, 45-47`
   - **Feature**: `validate_regex_patterns()` function validates user-provided regex patterns
   - **Protection**: Prevents regex injection attacks and malformed patterns

3. **Resource Management**: Improved database connection handling
   - **File**: `backend/app/db_ingestor.py:55-57`
   - **Change**: Used context manager (`with` statement) for DuckDB connections
   - **Benefit**: Prevents resource leaks and ensures proper connection cleanup

### Code Quality Improvements

- **Error Handling**: Enhanced exception handling in parser and database operations
- **Type Safety**: Improved input validation and error messages
- **Security**: Eliminated potential SQL injection and XSS vulnerabilities

### Dependencies

- Fixed dependency versions in `requirements.txt` for reproducible builds
- All packages pinned to specific versions for stability