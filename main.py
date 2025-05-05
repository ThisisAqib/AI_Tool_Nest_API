"""
FastAPI Application Entry Point

This module serves as the entry point for the FastAPI application.
It initializes the application and includes all API routers.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from app import include_routers
from app.core.logging_config import setup_logging, get_logger
from app.core.rate_limit import limiter
from app.core.database import init_db, close_db


# Initialize the root logger
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    # Set up logging configuration
    setup_logging()
    logger.info("Initializing AI Tool Nest API")

    app = FastAPI(
        title="AI Tool Nest API",
        description="REST API for AI Tool Nest",
        version="1.0.0",
        root_path="/ai-tool-nest-api",
    )

    # Configure rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    logger.info("Rate limiting configured")

    # Mount static directory for serving static files (CSS, JS, images)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Include all application routers
    include_routers(app)
    logger.info("All routers have been included")

    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Initialize database on startup."""
        logger.info("Initializing database")
        await init_db()
        logger.info("Database initialization completed")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Close database connections on shutdown."""
        logger.info("Closing database connections")
        await close_db()
        logger.info("Database connections closed")

    return app


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """
    Handle rate limit exceeded exceptions.

    Args:
        request: The incoming request that exceeded the rate limit
        exc: The rate limit exceeded exception

    Returns:
        JSONResponse: A JSON response with rate limit exceeded information
    """
    logger.warning(
        "Rate limit exceeded",
        extra={"client_ip": request.client.host, "path": request.url.path},
    )
    return JSONResponse(
        status_code=429, content={"error": "Rate limit exceeded", "detail": str(exc)}
    )


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings

    # Run the application with hot reload enabled for development
    logger.info("Starting development server")
    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD
    )
