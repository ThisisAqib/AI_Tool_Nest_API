# AI Tool Nest API

A powerful, production-ready REST API service that provides advanced AI-powered text and image processing capabilities. Built with FastAPI and modern Python, it offers enterprise-grade features including robust authentication, rate limiting, and comprehensive monitoring.

## Features

### Core Capabilities
- Advanced text summarization with customizable parameters
- Context-aware text paraphrasing with style options
- Image-to-text conversion with OCR capabilities
- Dual authentication system (JWT & API Keys)
- Comprehensive usage analytics

### Technical Features
- Built with FastAPI and Python 3.11+
- Async database operations with PostgreSQL
- Groq API integration for AI processing
- Modern dependency management with UV
- Granular rate limiting per endpoint
- Structured JSON logging with rotation
- Database schema management with Alembic
- Health check endpoint for monitoring

## Documentation

Our documentation is organized into several key sections:

1. **Interactive Web Documentation**
   - Beautiful, single-page documentation at `http://localhost:8002`
   - Dark mode interface
   - Syntax-highlighted code examples
   - Mobile-responsive design

2. **API Documentation**
   - [API Examples](docs/api_examples.md) - Practical code examples for all endpoints
   - [Architecture Documentation](docs/architecture.md) - System design and component relationships
   - [Technical Documentation](docs/technical.md) - Technical specifications and implementation details
   - [Database Migrations Guide](docs/database_migrations.md) - Managing database schema with Alembic

3. **OpenAPI Documentation**
   - Interactive API documentation (Swagger UI) at `http://localhost:8002/docs`
   - Alternative API documentation (ReDoc) at `http://localhost:8002/redoc`

## Getting Started

### Prerequisites

- Python 3.11 or higher
- UV package manager (install using `python -m pip install uv`)
- PostgreSQL database

### Installation

1. Clone the repository:
```bash
git clone https://github.com/thisisaqib/ai_tool_nest_api.git
cd ai_tool_nest_api
```

2. Install dependencies using UV:
```bash
# This will automatically create a virtual environment and install all dependencies
uv sync
```

3. Set up environment variables:
```bash
# Copy the example environment file
cp .env-example .env
```

Then edit the `.env` file with your configuration:
```env
# Security Configuration
SECRET_KEY="your-secure-secret-key"

# Groq API Configuration
GROK_API_KEY="your-groq-api-key"

# PostgreSQL Database Configuration
POSTGRES_USER="your_username"
POSTGRES_PASSWORD="your_password"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="ai_tool_nest_db"

# FastAPI Settings
HOST="0.0.0.0"
PORT=8002
RELOAD=True
```

### Running the API

Start the development server:
```bash
uv run main.py
```

Or using uvicorn directly:
```bash
uv run uvicorn main:app --host ${HOST} --port ${PORT} --reload
```

The API will be available at `http://localhost:8002`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI) at `http://localhost:8002/docs`
- Alternative API documentation (ReDoc) at `http://localhost:8002/redoc`

## Quick Reference

For detailed code examples of all endpoints, see our [API Examples](docs/api_examples.md) documentation.

### Available Endpoints

1. **Authentication**
   - User Registration and Login
   - API Key Management

2. **AI Tools**
   - Text Summarization
   - Text Paraphrasing
   - Image to Text

3. **System**
   - Health Check
   - Usage Statistics

Each endpoint supports both JWT token (`Authorization: Bearer <token>`) and API key (`X-API-Key: <api-key>`) authentication.

For detailed endpoint documentation and implementation examples, see:
- [API Examples](docs/api_examples.md) - Code examples for all endpoints
- [Technical Documentation](docs/technical.md) - Implementation details and specifications

## Project Structure

```
.
├── app/
│   ├── api/            # API endpoints and versioning
│   │   └── v1/        # Version 1 JSON endpoints
│   ├── web/           # Web routes for HTML pages
│   │   └── docs.py    # Documentation page routes
│   ├── core/          # Core configuration and utilities
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic models
│   ├── services/      # Business logic
│   ├── static/        # Static files (CSS, JS)
│   └── templates/     # Jinja2 HTML templates
├── alembic/           # Database migrations
├── docs/             # Project documentation
├── logs/             # Application logs
└── main.py          # Application entry point
```

The project follows a clean separation of concerns:
- `app/api/` - REST API endpoints returning JSON responses
- `app/web/` - Web routes serving HTML pages (documentation)
- `app/core/` - Core functionality and configuration
- `app/services/` - Business logic and external integrations

For detailed architecture information, see [Architecture Documentation](docs/architecture.md).

## Development

For development guidelines and best practices, refer to:

1. **Backend Development**
   - Database changes: [Database Migrations Guide](docs/database_migrations.md)
   - Technical patterns: [Technical Documentation](docs/technical.md)

2. **Frontend Development**
   - Templates are in `app/templates/`
   - Static files (CSS, JS) in `app/static/`
   - Uses Tailwind CSS for styling
   - Dark/light mode support
   - Mobile-responsive design

3. **Adding New Features**
   - API endpoints go in `app/api/v1/endpoints/`
   - Web pages go in `app/web/`
   - Database models in `app/models/`
   - Business logic in `app/services/`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
