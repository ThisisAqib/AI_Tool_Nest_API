from fastapi import APIRouter
from app.api.v1.endpoints import endpoints_router

v1_router = APIRouter()

# Include endpoints router without additional prefix to avoid path duplication
v1_router.include_router(endpoints_router, prefix="/endpoints")
