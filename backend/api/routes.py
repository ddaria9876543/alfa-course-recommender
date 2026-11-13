from backend.services import recommendation as recommendation_service
from fastapi import APIRouter, HTTPException
import psycopg
from backend.services.material import get_material_by_id
from backend.services import user as user_service
from backend.schemas.models import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackRequest,
)

router = APIRouter(prefix="/api")

DEMO_MATERIALS = [
    {
        "material_id": 1,
        "title": "Основы Python",
        "material_type": "course",
        "url": None,
        "description": "Вводный курс по программированию на Python"
    },
    {
        "material_id": 2,
        "title": "Введение в анализ данных",
        "material_type": "article",
        "url": None,
        "description": "Статья об основных инструментах анализа данных"
    }
]


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



@router.post(
    "/recommendations",
    response_model=RecommendationResponse
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



    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return {
        "route_id": str(uuid4()),
        "user_id": request.user_id,
        "goal": request.goal,
        "recommendations": [
            {
                "material_id": 1,
                "title": "Основы Python",
                "material_type": "course",
                "url": None,
                "score": 0.95,
                "reason_factors": [
                    "Соответствует цели обучения",
                    "Подходит для начального уровня"
                ],
                "explanation": "Материал поможет освоить основы Python.",
                "step": 1
            },
            {
                "material_id": 2,
                "title": "Введение в анализ данных",
                "material_type": "article",
                "url": None,
                "score": 0.87,
                "reason_factors": [
                    "Развивает навыки анализа данных"
                ],
                "explanation": "Материал поможет перейти к практическим задачам.",
                "step": 2
            }
        ]
    }

@router.post("/recommendations/feedback")
def submit_feedback(feedback: FeedbackRequest):
    return recommendation_service.save_feedback(feedback)

from fastapi import HTTPException
@router.get("/materials/{material_id}")
def get_material(material_id: str):
    try:
        material = get_material_by_id(material_id)

    except (psycopg.Error, OSError):
        raise HTTPException(
            status_code=503,
            detail="База данных временно недоступна"
        )

    if material is None:
        raise HTTPException(
            status_code=404,
            detail="Материал не найден"
        )

    return material


    raise HTTPException(
        status_code=404,
        detail="Материал не найден"
    )
