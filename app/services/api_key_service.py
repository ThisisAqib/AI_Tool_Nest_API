from datetime import datetime
from typing import List, Optional, Tuple, Dict
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import APIKey, User, KeyStatus, APIKeyUsage
from app.core.security import generate_api_key, verify_api_key, get_api_key_hash
from app.schemas.api_key import APIKeyUsageStats, APIKeyUsageEntry


class APIKeyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_api_key(self, user_id: int, name: str) -> Tuple[APIKey, str]:
        """
        Create a new API key for a user.

        Args:
            user_id: The ID of the user
            name: Name/description of the API key

        Returns:
            tuple[APIKey, str]: The created API key model and the raw API key
        """
        api_key = generate_api_key()
        key_hash = get_api_key_hash(api_key)
        key_prefix = api_key[:8]

        db_key = APIKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            status=KeyStatus.ACTIVE,
        )

        self.session.add(db_key)
        await self.session.commit()
        await self.session.refresh(db_key)

        return db_key, api_key

    async def get_user_api_keys(self, user_id: int) -> List[APIKey]:
        """
        Get all API keys for a user.

        Args:
            user_id: The ID of the user

        Returns:
            List[APIKey]: List of API keys
        """
        query = select(APIKey).where(
            and_(APIKey.user_id == user_id, APIKey.revoked_at.is_(None))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def revoke_api_key(self, key_id: int, user_id: int) -> Optional[APIKey]:
        """
        Revoke an API key.

        Args:
            key_id: The ID of the API key to revoke
            user_id: The ID of the user who owns the key

        Returns:
            Optional[APIKey]: The revoked API key if found and revoked
        """
        query = select(APIKey).where(
            and_(
                APIKey.id == key_id,
                APIKey.user_id == user_id,
                APIKey.revoked_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        api_key = result.scalar_one_or_none()

        if api_key:
            api_key.status = KeyStatus.REVOKED
            api_key.revoked_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(api_key)

        return api_key

    async def verify_and_update_key(self, api_key: str) -> Optional[APIKey]:
        """
        Verify an API key and update its last used timestamp.

        Args:
            api_key: The API key to verify

        Returns:
            Optional[APIKey]: The API key model if valid
        """
        # Get prefix from the API key
        key_prefix = api_key[:8]

        # Find the API key by prefix
        query = select(APIKey).where(
            APIKey.key_prefix == key_prefix, APIKey.status == KeyStatus.ACTIVE
        )
        result = await self.session.execute(query)
        db_key = result.scalar_one_or_none()

        if db_key and verify_api_key(api_key, db_key.key_hash):
            # Update last used timestamp
            db_key.last_used_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(db_key)
            return db_key

        return None

    async def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """
        Validate an API key and return the associated user.
        Returns None if the key is invalid or revoked.
        """
        # Get key hash for comparison
        key_hash = get_api_key_hash(api_key)
        key_prefix = api_key[:8]

        # Find the API key in the database
        query = select(APIKey).where(
            and_(
                APIKey.key_hash == key_hash,
                APIKey.key_prefix == key_prefix,
                APIKey.revoked_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        db_key = result.scalar_one_or_none()

        if not db_key:
            return None

        # Update last used timestamp
        db_key.last_used_at = datetime.utcnow()
        await self.session.commit()

        # Get and return the associated user
        user_query = select(User).where(User.id == db_key.user_id)
        result = await self.session.execute(user_query)
        return result.scalar_one_or_none()

    async def get_key_usage_stats(
        self, key_id: int, user_id: int
    ) -> Optional[APIKeyUsageStats]:
        """
        Get usage statistics for an API key.

        Args:
            key_id: The ID of the API key
            user_id: The ID of the user who owns the key

        Returns:
            Optional[APIKeyUsageStats]: Usage statistics if key exists and belongs to user
        """
        # Verify key belongs to user
        key_query = select(APIKey).where(
            and_(APIKey.id == key_id, APIKey.user_id == user_id)
        )
        result = await self.session.execute(key_query)
        if not result.scalar_one_or_none():
            return None

        # Get usage statistics
        usage_query = select(APIKeyUsage).where(APIKeyUsage.api_key_id == key_id)
        result = await self.session.execute(usage_query)
        usage_logs = list(result.scalars().all())

        if not usage_logs:
            return APIKeyUsageStats(
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                usage_by_endpoint={},
                recent_usage=[],
            )

        # Calculate statistics
        total_requests = len(usage_logs)
        successful_requests = sum(1 for log in usage_logs if log.status_code < 400)
        failed_requests = total_requests - successful_requests
        average_response_time = (
            sum(log.response_time for log in usage_logs) / total_requests
        )

        # Count requests by endpoint
        usage_by_endpoint: Dict[str, int] = {}
        for log in usage_logs:
            usage_by_endpoint[log.endpoint] = usage_by_endpoint.get(log.endpoint, 0) + 1

        # Get 10 most recent usage entries
        recent_usage = sorted(usage_logs, key=lambda x: x.created_at, reverse=True)[:10]
        recent_usage_entries = [
            APIKeyUsageEntry(
                endpoint=log.endpoint,
                method=log.method,
                status_code=log.status_code,
                response_time=log.response_time,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                created_at=log.created_at,
            )
            for log in recent_usage
        ]

        return APIKeyUsageStats(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            usage_by_endpoint=usage_by_endpoint,
            recent_usage=recent_usage_entries,
        )

    async def log_api_key_usage(
        self,
        api_key_id: int,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        ip_address: str,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Log usage of an API key.

        Args:
            api_key_id: The ID of the API key
            endpoint: The endpoint that was accessed
            method: HTTP method used
            status_code: Response status code
            response_time: Response time in seconds
            ip_address: Client IP address
            user_agent: Client user agent
        """
        usage_log = APIKeyUsage(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(usage_log)
        await self.session.commit()
