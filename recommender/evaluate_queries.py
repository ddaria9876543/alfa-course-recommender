import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from recommender.content_based import load_materials, normalize_text, prepare_materials
from recommender.service import recommend


TEST_QUERIES = [
    "Хочу увеличить продажи",
    "Как открыть свой бизнес?",
    "Как привлечь новых клиентов?",
    "Хочу разобраться с налогами",
    "Как управлять финансами бизнеса?",
]


def run_top10_evaluation():
    print("=" * 70)
    print("1. ПРОВЕРКА 5 БИЗНЕС-ЗАПРОСОВ (TOP-10)")
    print("=" * 70)

    for query in TEST_QUERIES:
        results = recommend(query, top_k=10)
        keys = [(r["material_type"], r["material_id"]) for r in results]
        has_duplicates = len(keys) != len(set(keys))

        print(f"\nЗапрос: «{query}» | Найдено: {len(results)} | Дубликаты: {has_duplicates}")
        for idx, item in enumerate(results, start=1):
            print(
                f"  {idx:2d}. [{item['material_type']:8s}] {item['title']} "
                f"(score={item['score']}, topics={item['topics'] or '-'})"
            )


def compare_tfidf_configs():
    print("\n" + "=" * 70)
    print("2. СРАВНЕНИЕ НАСТРОЕК TF-IDF: char_wb (3, 5) vs word (1, 2)")
    print("=" * 70)

    materials = prepare_materials(load_materials())
    texts = [m["search_text"] for m in materials]

    configs = {
        "char_wb (3, 5)": TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            sublinear_tf=True,
            max_features=50000,
        ),
        "word (1, 2)": TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=50000,
        ),
    }

    matrices = {name: vec.fit_transform(texts) for name, vec in configs.items()}

    for query in TEST_QUERIES:
        q_norm = normalize_text(query)
        print(f"\nЗапрос: «{query}»")

        for name, vec in configs.items():
            q_vec = vec.transform([q_norm])
            sims = cosine_similarity(q_vec, matrices[name]).ravel()
            top_idx = np.argsort(-sims)[:3]
            top_titles = [
                f"{materials[i]['title']} ({sims[i]:.3f})"
                for i in top_idx
                if sims[i] > 0
            ]
            print(f"  {name:15s} -> {', '.join(top_titles) if top_titles else 'нет совпадений'}")


if __name__ == "__main__":
    run_top10_evaluation()
    compare_tfidf_configs()
