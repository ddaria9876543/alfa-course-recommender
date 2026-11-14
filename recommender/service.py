
"""
ALFA-COURSE | RECOMMENDATION SERVICE

Единый интерфейс рекомендательной системы
для последующей интеграции с FastAPI.
"""

import json
from functools import lru_cache

try:
    from .content_based import (
        ContentBasedRecommender,
        load_materials,
    )
except ImportError:
    from content_based import (
        ContentBasedRecommender,
        load_materials,
    )


@lru_cache(maxsize=1)
def get_recommender():
    """
    Загружаем каталог и строим TF-IDF один раз
    на процесс Python.
    """
    materials = load_materials()
    return ContentBasedRecommender(materials)


def reload_recommender():
    """Сбрасывает кэш и пересобирает модель на свежих данных из БД."""
    get_recommender.cache_clear()
    return get_recommender()


def get_recommendations(profile=None, top_k=5):
    """
    Основная функция для backend.

    profile: dict с информацией о предпринимателе
    top_k: количество рекомендаций
    """

    if profile is None:
        profile = {}

    if not isinstance(profile, dict):
        raise ValueError("Profile must be a dictionary")

    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise ValueError("top_k must be an integer")

    if not 1 <= top_k <= 100:
        raise ValueError("top_k must be between 1 and 100")
    model = get_recommender()

    recommendations = model.recommend(
        profile=profile,
        top_k=top_k,
    )

    mode = (
        "personalized"
        if str(profile.get("goal") or "").strip()
        else "cold_start"
    )

    items = []

    for rec in recommendations:
        items.append({
            "material_id": rec["material_id"],
            "material_type": rec["material_type"],
            "title": rec["title"],
            "industry_tags": rec.get("industry_tags") or [],
            "audience_experience": rec.get("audience_experience"),
            "slug": rec["url"],
            "payment_status": rec["payment_status"],
            "topics": rec.get("topics", ""),
            "industries": rec.get("industries", ""),
            "score": rec["score"],
            "similarity": rec["similarity"],
            "reasons": rec["reasons"],
            "next_step": rec["next_step"],
        })

    return {
        "mode": mode,
        "total": len(items),
        "recommendations": items,
    }


def recommend(goal: str, top_k: int = 10) -> list[dict]:
    """
    Программный интерфейс по ТЗ Задачи №1.
    Принимает бизнес-цель строкой и возвращает список словарей
    с полями: material_id, material_type, title, url, score, topics.
    """
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("goal must be a non-empty string")

    response = get_recommendations(profile={"goal": goal}, top_k=top_k)

    results = []
    for item in response["recommendations"]:
        results.append({
            "material_id": item["material_id"],
            "material_type": item["material_type"],
            "title": item["title"],
            "url": item["slug"],
            "score": item["score"],
            "topics": item.get("topics", ""),
            "reasons": item["reasons"],
        })

    return results


if __name__ == "__main__":
    test_profile = {
        "goal": "Как увеличить продажи и привлечь клиентов",
        "industry": "красота",
        "preferred_format": "article",
    }

    response = get_recommendations(
        test_profile,
        top_k=5,
    )

    print(
        json.dumps(
            response,
            ensure_ascii=False,
            indent=2,
        )
    )
