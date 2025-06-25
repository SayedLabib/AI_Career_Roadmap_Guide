from fastapi import APIRouter

from app.api.endpoints import survey, roadmap

api_router = APIRouter()

api_router.include_router(survey.router, prefix="/survey", tags=["survey"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])