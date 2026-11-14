from recommender.service import get_recommender
from recommender.content_based import normalize_text
from sklearn.metrics.pairwise import cosine_similarity

model = get_recommender()
goal = "Увеличить продажи"

query = model.vectorizer.transform([goal])
similarities = cosine_similarity(query, model.matrix).ravel()

for industry in ["ECom", "Розница"]:
    print(f"\n=== ОТРАСЛЬ: {industry} ===")

    candidates = []

    for idx, material in enumerate(model.materials):
        if industry in (material.get("industry_tags") or []):
            candidates.append((
                float(similarities[idx]),
                material["title"],
                material["topics"],
            ))

    candidates.sort(reverse=True)

    print("Всего материалов с меткой:", len(candidates))

    for similarity, title, topics in candidates[:10]:
        print(f"{similarity:.4f} | {title} | {topics}")
