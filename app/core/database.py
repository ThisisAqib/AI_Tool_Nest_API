from typing import AsyncGenerator
import asyncpg
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def create_database():
    """Create database if it doesn't exist."""
    try:
        # Connect to default 'postgres' database to check if our database exists
        system_conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=int(settings.POSTGRES_PORT),
            database="postgres",
        )

        try:
            # Check if database exists
            exists = await system_conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", settings.POSTGRES_DB
            )

            if not exists:
                logger.info(f"Creating database {settings.POSTGRES_DB}")
                # Escape database name to prevent SQL injection
                escaped_db_name = settings.POSTGRES_DB.replace("'", "''")
                await system_conn.execute(f'CREATE DATABASE "{escaped_db_name}"')
                logger.info(f"Database {settings.POSTGRES_DB} created successfully")
        finally:
            await system_conn.close()
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise


# Create async engine - but don't connect immediately
engine = create_async_engine(
    settings.POSTGRES_URL, echo=settings.RELOAD, future=True, pool_pre_ping=True
)

# Create async session factory
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database by creating all tables."""
    try:
        # First ensure database exists
        await create_database()
        logger.info("Database exists or was created successfully")

        # Then create all tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


async def close_db():
    """Close database connections."""
    await engine.dispose()
