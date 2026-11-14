
from recommender.service import get_recommender
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = get_recommender()

GOAL = "Увеличить продажи"

INDUSTRY_QUERIES = {
    "ECom": "маркетплейсы онлайн торговля продвижение товаров продажи",
    "Розница": "розничная торговля магазин товары продажи",
}

goal_vector = model.vectorizer.transform([GOAL])
goal_scores = cosine_similarity(goal_vector, model.matrix).ravel()

for industry, industry_query in INDUSTRY_QUERIES.items():
    industry_vector = model.vectorizer.transform([industry_query])
    industry_scores = cosine_similarity(
        industry_vector, model.matrix
    ).ravel()

    scores = 0.75 * goal_scores + 0.25 * industry_scores

    ranked = np.argsort(-scores)

    print(f"\n=== {industry} ===")

    count = 0

    for idx in ranked:
        material = model.materials[int(idx)]

        # Пока проверяем кандидатов из темы продаж.
        topics = material.get("topics", "")

        if not any(
            topic in topics
            for topic in (
                "Продажи",
                "Маркетинг",
                "Клиентский сервис",
            )
        ):
            continue

        print(
            f"{scores[idx]:.4f} | "
            f"{material['title']} | "
            f"{material.get('industries', '')}"
        )

        count += 1

        if count >= 10:
            break
