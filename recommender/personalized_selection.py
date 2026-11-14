
import re

from recommender.content_based import (
    get_goal_topics,
    matches_topic,
    normalize_text,
    INDUSTRY_ALIASES,
    has_direct_goal_match,
)



def select_personalized_materials(
    candidates: list[dict],
    profile: dict,
    top_k: int = 3,
    min_industry_similarity: float = 0.10,
) -> list[dict]:

    if top_k <= 0:
        return []

    goal = profile.get("goal", "")
    industry = normalize_text(profile.get("industry", ""))

    normalized_industry = INDUSTRY_ALIASES.get(industry)
    allowed_topics = get_goal_topics(goal)

    eligible = []

    for item in candidates:
        topic_match = (
            not allowed_topics
            or any(
                matches_topic(item.get("topics", ""), topic)
                for topic in allowed_topics
            )
        )

        direct_match = has_direct_goal_match(item, goal)

        if topic_match or direct_match:
            eligible.append(item)

    if not eligible:
        return []

    if not normalized_industry or top_k < 2:
        return eligible[:top_k]

    industry_candidates = [
        item
        for item in eligible
        if normalized_industry in (
            item.get("industry_tags") or []
        )
        and (item.get("similarity") or 0)
        >= min_industry_similarity
    ]

    # Для цели по продажам предпочитаем отраслевые
    # материалы с прямым совпадением в названии.
    if "продаж" in normalize_text(goal):
        industry_candidates = [
            item
            for item in industry_candidates
            if has_direct_goal_match(item, goal)
        ]

    if not industry_candidates:
        return eligible[:top_k]

    # Кандидаты приходят отсортированными по score.
    industry_material = industry_candidates[0]

    result = [
        item
        for item in eligible
        if item["material_id"]
        != industry_material["material_id"]
    ][:top_k - 1]

    result.append(industry_material)

    return result
