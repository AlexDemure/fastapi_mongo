from fastapi import APIRouter

from backend.src.api.routers.statistics import router as statistics_router

api_router = APIRouter()

api_router.include_router(statistics_router, tags=["statistics"], prefix='/statistics')
