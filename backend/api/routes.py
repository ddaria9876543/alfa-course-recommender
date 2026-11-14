
import psycopg
from fastapi import APIRouter, HTTPException

from backend.schemas.models import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackRequest,
)
from backend.services import recommendation as recommendation_service
from backend.services import user as user_service
from backend.services.material import get_material_by_id


router = APIRouter(prefix="/api")


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend работает успешно"
    }


@router.get("/demo-users")
def get_demo_users():
    return user_service.get_demo_users()


@router.get("/users/{user_id}/profile")
def get_user_profile(user_id: int):
    user = user_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return user


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    responses={
        503: {
            "description": "Рекомендательная система временно недоступна"
        }
    }
)
def create_recommendations(request: RecommendationRequest):
    user = user_service.get_user_by_id(request.user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    try:
        return recommendation_service.generate_recommendations(request)

    except (RuntimeError, psycopg.Error, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Рекомендательная система временно недоступна"
        ) from exc


@router.post("/recommendations/feedback")
def submit_feedback(feedback: FeedbackRequest):
    try:
        return recommendation_service.save_feedback(feedback)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/materials/{material_id}",
    responses={
        503: {
            "description": "База данных временно недоступна"
        }
    }
)
def get_material(material_id: str):
    try:
        material = get_material_by_id(material_id)

    except (psycopg.Error, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail="База данных временно недоступна"
        ) from exc

    if material is None:
        raise HTTPException(
            status_code=404,
            detail="Материал не найден"
        )

    return material