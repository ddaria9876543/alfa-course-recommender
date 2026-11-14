
from uuid import uuid4

from recommender.service import get_recommendations
from recommender.personalized_selection import (
    select_personalized_materials,
)
from recommender.content_based import (
    INDUSTRY_ALIASES,
    normalize_text,
)

from backend.schemas.models import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackRequest,
)


# Временное хранение маршрутов и обратной связи.
# После перезапуска Backend данные сбрасываются.
ROUTE_STORAGE = {}
FEEDBACK_STORAGE = []


# Количество кандидатов, запрашиваемых у ML.
CANDIDATE_POOL_SIZE = 100

# Максимальное количество рекомендаций на одну цель.
MAX_RECOMMENDATIONS = 30

# Первые три материала выбираются персонализированной логикой.
PERSONALIZED_TOP_K = 3


def _normalize_formats(
    preferred_format=None,
    preferred_formats=None,
):
    """
    Нормализует предпочтительные форматы.

    Поддерживает:
    - preferred_format: "article"
    - preferred_formats: ["article", "course"]

    Если передан список, используем его.
    """

    valid_formats = {
        "article",
        "course",
        "document",
    }

    if preferred_formats is not None:
        values = preferred_formats
    elif preferred_format:
        values = [preferred_format]
    else:
        values = []

    if isinstance(values, str):
        values = [values]

    normalized = []
    seen = set()

    for value in values:
        format_name = normalize_text(value)

        if (
            format_name in valid_formats
            and format_name not in seen
        ):
            normalized.append(format_name)
            seen.add(format_name)

    return normalized


def _normalize_reasons(material, industry):
    """
    Подготавливает объяснения рекомендаций.
    """

    reasons = material.get("reasons") or []

    if isinstance(reasons, str):
        reasons = [reasons]

    elif not isinstance(reasons, list):
        reasons = []

    reasons = [
        str(reason)
        for reason in reasons
        if reason
    ]

    # Объяснение отраслевой персонализации.
    industry_tags = material.get("industry_tags") or []

    if industry and industry_tags:
        selected_industry = INDUSTRY_ALIASES.get(
            normalize_text(industry)
        )

        if (
            selected_industry
            and selected_industry in industry_tags
        ):
            industry_reason = (
                "Подобрано с учётом вашей сферы бизнеса"
            )

            if industry_reason not in reasons:
                reasons.append(industry_reason)

    return reasons


def _select_recommendations(candidates, profile):
    """
    Формирует расширенную подборку.

    1. Сначала персонализированный Top-3.
    2. Затем остальные кандидаты по ML-score.
    3. Исключает дубликаты.
    """

    if not candidates:
        return []

    primary = select_personalized_materials(
        candidates=candidates,
        profile=profile,
        top_k=PERSONALIZED_TOP_K,
    )

    selected = []
    selected_ids = set()

    # Добавляем персонализированную тройку.
    for material in primary:
        material_id = str(
            material["material_id"]
        )

        if material_id in selected_ids:
            continue

        selected.append(material)
        selected_ids.add(material_id)

    # Сортируем оставшихся кандидатов по score.
    remaining = sorted(
        candidates,
        key=lambda material: float(
            material.get("score") or 0.0
        ),
        reverse=True,
    )

    for material in remaining:
        if len(selected) >= MAX_RECOMMENDATIONS:
            break

        material_id = str(
            material["material_id"]
        )

        if material_id in selected_ids:
            continue

        selected.append(material)
        selected_ids.add(material_id)

    return selected[:MAX_RECOMMENDATIONS]


def _build_route(
    user_id: int,
    goal: str,
    industry: str | None = None,
    preferred_format: str | None = None,
    preferred_formats: list[str] | None = None,
    business_stage: str | None = None,
    experience: str | None = None,
    excluded_ids=None,
) -> RecommendationResponse:
    """
    Формирует рекомендации для одной бизнес-цели.
    """

    excluded_ids = set(excluded_ids or [])

    # 1. Нормализуем выбранные форматы.
    normalized_formats = _normalize_formats(
        preferred_format=preferred_format,
        preferred_formats=preferred_formats,
    )

    # 2. Формируем профиль предпринимателя.
    profile = {
        "goal": goal,
        "industry": industry,
        "preferred_formats": normalized_formats,
        "business_stage": business_stage,
        "experience": experience,
    }

    # 3. Получаем кандидатов из ML.
    result = get_recommendations(
        profile=profile,
        top_k=CANDIDATE_POOL_SIZE,
    )

    all_candidates = result.get(
        "recommendations",
        [],
    )

    # 4. Исключаем материалы, отклонённые пользователем.
    candidates = [
        material
        for material in all_candidates
        if str(material["material_id"])
        not in excluded_ids
    ]

    # 5. Получаем персонализированную подборку.
    selected = _select_recommendations(
        candidates=candidates,
        profile=profile,
    )

    # 6. Преобразуем рекомендации в формат FastAPI.
    recommendations = []

    for index, material in enumerate(
        selected,
        start=1,
    ):
        material_id = str(
            material["material_id"]
        )

        reasons = _normalize_reasons(
            material=material,
            industry=industry,
        )

        score = float(
            material.get("score") or 0.0
        )

        recommendations.append(
            {
                "material_id": material_id,
                "title": material["title"],
                "material_type": material["material_type"],
                "url": material.get("slug"),
                "score": max(
                    0.0,
                    min(1.0, score),
                ),
                "reason_factors": reasons,
                "explanation": (
                    "; ".join(reasons)
                    or "Материал соответствует вашей бизнес-задаче."
                ),
                "step": index,
            }
        )

    # 7. Создаём идентификатор подборки.
    route_id = str(uuid4())

    # 8. Сохраняем профиль для пересчёта после обратной связи.
    ROUTE_STORAGE[route_id] = {
        "user_id": user_id,
        "goal": goal,
        "industry": industry,
        "preferred_format": preferred_format,
        "preferred_formats": normalized_formats,
        "business_stage": business_stage,
        "experience": experience,
        "excluded_ids": excluded_ids,
        "material_ids": {
            item["material_id"]
            for item in recommendations
        },
    }

    # 9. Возвращаем ответ.
    return RecommendationResponse(
        route_id=route_id,
        user_id=user_id,
        goal=goal,
        recommendations=recommendations,
    )


def generate_recommendations(
    request: RecommendationRequest,
) -> RecommendationResponse:
    """
    Первоначальный подбор рекомендаций.
    """

    return _build_route(
        user_id=request.user_id,
        goal=request.goal,
        industry=request.industry,
        preferred_format=request.preferred_format,
        preferred_formats=request.preferred_formats,
        business_stage=request.business_stage,
        experience=request.experience,
    )


def save_feedback(
    feedback: FeedbackRequest,
) -> RecommendationResponse:
    """
    Сохраняет обратную связь и пересчитывает
    рекомендации по той же бизнес-цели.
    """

    route = ROUTE_STORAGE.get(
        feedback.route_id
    )

    if route is None:
        raise ValueError(
            "Подборка не найдена. "
            "Получите рекомендации заново."
        )

    if (
        feedback.material_id
        not in route["material_ids"]
    ):
        raise ValueError(
            "Материал не принадлежит текущей подборке."
        )

    # Исключаем материал из новой подборки.
    excluded_ids = set(
        route["excluded_ids"]
    )

    excluded_ids.add(
        feedback.material_id
    )

    # Пересчитываем рекомендации с тем же профилем.
    updated_route = _build_route(
        user_id=route["user_id"],
        goal=route["goal"],
        industry=route.get("industry"),
        preferred_format=route.get(
            "preferred_format"
        ),
        preferred_formats=route.get(
            "preferred_formats"
        ),
        business_stage=route.get(
            "business_stage"
        ),
        experience=route.get(
            "experience"
        ),
        excluded_ids=excluded_ids,
    )

    # Сохраняем факт обратной связи.
    FEEDBACK_STORAGE.append(
        {
            "route_id": feedback.route_id,
            "material_id": feedback.material_id,
            "feedback_type": feedback.feedback_type,
        }
    )

    return updated_route
