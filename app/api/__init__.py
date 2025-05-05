from fastapi import APIRouter

# Main API router that includes all API version routers
api_router = APIRouter()


# Import version routers and documentation router
from app.api.v1 import v1_router

# Include API v1 routes
api_router.include_router(v1_router, prefix="/v1")
