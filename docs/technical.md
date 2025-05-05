# AI Tool Nest - Technical Documentation

## Technology Stack

### Backend
- **FastAPI** 
  - Modern, fast web framework
  - Automatic API documentation
  - Type hints and validation
  - Async support
  - OAuth2 with Password Flow
  - API Key authentication

### Authentication & Security
- **JWT Authentication**
  - Token-based authentication with OAuth2 Password Flow
  - Password hashing with bcrypt
  - Token expiration and secure validation
  - See [API Examples](api_examples.md) for implementation details

- **API Key Authentication**
  - Secure key generation with SHA-256 hashing
  - Key prefix system for efficient lookups
  - Usage tracking and analytics
  - See [API Examples](api_examples.md) for implementation details

### Rate Limiting
- **Slowapi**
  - IP-based rate limiting
  - Per-endpoint configuration
  - Fixed window strategy
  - Async support

### Database
- **PostgreSQL with asyncpg**
  - Async database operations
  - Connection pooling
  - Type-safe queries
  - Migration support via Alembic

### AI Integration
- **Groq API Integration**
  - OpenAI-compatible API endpoints
  - Text processing capabilities
  - Async request handling

### Development Tools
- **UV**
  - Fast package installation
  - Dependency resolution
  - Lock file management
  - Virtual environment management

## Core Components

### Settings Management (`app/core/config.py`)
```python
class Settings(BaseSettings):
    # Base application settings
    PROJECT_NAME: str = "AI Tool Nest API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str
    
    # Groq API Settings
    GROK_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.groq.com/openai/v1"
    OPENAI_MODEL_NAME: str = "deepseek-r1-distill-llama-70b"

    # PostgreSQL Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    # FastAPI Settings
    HOST: str 
    PORT: int 
    RELOAD: bool

    @property
    def get_postgres_url(self) -> str:
        """Generate PostgreSQL URL with proper URL encoding."""
        return (
            f"postgresql+asyncpg://{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
```

## Monitoring

### Health Check Endpoint
```
GET /v1/endpoints/health
```

Features:
- Returns status information
- Rate limited to 5 requests per minute per IP
- Suitable for monitoring tools integration

Example response:
```json
{
  "status": "healthy"
}
```

### Logging System
- JSON formatted logs in `logs/app.log`
- Automatic rotation at 10MB
- Keep 5 backup files
- Includes:
  - Request/response details
  - Rate limit violations
  - Security events
  - Performance metrics

For architectural details, see [Architecture Documentation](architecture.md).
For API examples, see [API Examples](api_examples.md).
For database management, see [Database Migrations Guide](database_migrations.md). 