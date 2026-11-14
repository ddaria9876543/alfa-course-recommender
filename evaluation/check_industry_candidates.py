
from recommender.service import get_recommender
from recommender.content_based import (
    MIN_SIMILARITY,
    get_goal_topics,
    matches_topic,
)
from sklearn.metrics.pairwise import cosine_similarity

model = get_recommender()
goal = "Увеличить продажи"

query_vector = model.vectorizer.transform([goal])
similarities = cosine_similarity(
    query_vector, model.matrix
).ravel()

allowed_topics = get_goal_topics(goal)

for industry in ["ECom", "Розница"]:
    candidates = []

    for idx, material in enumerate(model.materials):
        similarity = float(similarities[idx])

        if similarity < MIN_SIMILARITY:
            continue

        if not any(
            matches_topic(material["topics"], topic)
            for topic in allowed_topics
        ):
            continue

        if industry not in (material.get("industry_tags") or []):
            continue

        candidates.append((
            similarity,
            material["title"],
            material["topics"],
        ))

    candidates.sort(reverse=True)

    print(f"\n=== {industry} ===")
    print("Подходящих кандидатов:", len(candidates))

    for similarity, title, topics in candidates[:10]:
        print(f"{similarity:.4f} | {title} | {topics}")
