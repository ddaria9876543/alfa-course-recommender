
from uuid import uuid4

from backend.schemas.models import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackRequest,
)

def generate_recommendations(
    request: RecommendationRequest
) -> RecommendationResponse:

    return RecommendationResponse(
        route_id=str(uuid4()),
        user_id=request.user_id,
        goal=request.goal,
        recommendations=[
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
    )

FEEDBACK_STORAGE = []


def save_feedback(feedback: FeedbackRequest):
    feedback_data = feedback.model_dump()

    FEEDBACK_STORAGE.append(feedback_data)

    return {
        "status": "success",
        "message": "Обратная связь сохранена",
        "route_id": feedback.route_id,
        "material_id": feedback.material_id,
        "feedback_type": feedback.feedback_type
    }


def save_feedback(feedback: FeedbackRequest):
    feedback_data = feedback.model_dump()
    FEEDBACK_STORAGE.append(feedback_data)

    return {
        "status": "success",
        "message": "Обратная связь сохранена",
        "route_id": feedback.route_id,
        "material_id": feedback.material_id,
        "feedback_type": feedback.feedback_type
    }