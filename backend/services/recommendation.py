
from uuid import uuid4
from recommender.service import get_recommendations
from backend.schemas.models import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackRequest,
)


def generate_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    # Передаём цель пользователя рекомендательной системе
    result = get_recommendations(
        profile={"goal": request.goal},
        top_k=5
    )

    recommendations = []

    for step, material in enumerate(result["recommendations"], start=1):
        reasons = material.get("reasons", [])

        # Приводим причины рекомендаций к списку строк
        if isinstance(reasons, str):
            reasons = [reasons]
        elif not isinstance(reasons, list):
            reasons = []

        recommendations.append({
            "material_id": material["material_id"],
            "title": material["title"],
            "material_type": material["material_type"],
            "url": material.get("slug"),
            "score": max(0.0, min(1.0, float(material["score"]))),
            "reason_factors": [str(reason) for reason in reasons],
            "explanation": "; ".join(str(reason) for reason in reasons)
                           or "Материал соответствует цели пользователя.",
            "step": step
        })

    return RecommendationResponse(
        route_id=str(uuid4()),
        user_id=request.user_id,
        goal=request.goal,
        recommendations=recommendations
    )

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