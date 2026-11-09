
# ============================================================
# ALFA-COURSE | RECOMMENDER EVALUATION
# Baseline vs TF-IDF vs Personalized TF-IDF
# ============================================================

import csv
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from content_based import (
    ContentBasedRecommender,
    load_materials,
    normalize_text,
    MIN_SIMILARITY,
)


BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
TOP_K = 5


# ============================================================
# ТЕСТОВЫЕ ПРОФИЛИ
# ============================================================
# relevant_slugs: предварительная экспертная разметка.
# Это НЕ полный список релевантных материалов каталога.

TEST_PROFILES = [
    {
        "name": "beauty_sales",
        "profile": {
            "goal": "Как увеличить продажи и привлечь клиентов",
            "industry": "красота",
            "experience": "beginner",
            "business_stage": "growing",
            "preferred_format": "article",
        },
        "baseline_topic": "Клиентский сервис",
        "relevant_slugs": {
            "kak-uvelichit-povtornye-prodazhi",
            "kak-sozdat-programmu-loyalnosti-dlya-klientov-salona-krasoty",
            "referalnaya-programma-chto-ehto-takoe-i-kak-sozdat",
        },
    },
    {
        "name": "online_store",
        "profile": {
            "goal": "Как открыть интернет-магазин",
            "industry": "интернет-магазин",
            "experience": "beginner",
            "business_stage": "starting",
            "preferred_format": "article",
        },
        "baseline_topic": "Старт бизнеса",
        "relevant_slugs": {
            "kak-podklyuchit-onlajn-kassu-k-internet-magazinu-instrukciya",
            "internet-marketing-dlya-malogo-biznesa",
        },
    },
    {
        "name": "business_start",
        "profile": {
            "goal": "Как открыть ИП и начать свой бизнес",
            "industry": "",
            "experience": "beginner",
            "business_stage": "starting",
            "preferred_format": "article",
        },
        "baseline_topic": "Старт бизнеса",
        "relevant_slugs": {
            "pervyj-mesyac-posle-otkrytiya-ip-chto-nuzhno-sdelat",
            "mozhno-li-otkryt-ip-esli-oficialno-trudoustroen",
        },
    },
]


def material_key(material):
    return (
        material["material_type"],
        material["material_id"],
    )


def split_topics(value):
    return {
        normalize_text(item)
        for item in (value or "").split(",")
        if normalize_text(item)
    }


# ============================================================
# BASELINE: ПОДБОР ПО ТЕМЕ
# ============================================================

def baseline_recommend(materials, topic, top_k=5):
    """
    Простой baseline:
    фильтрация по теме и алфавитная сортировка.

    Не использует ML и историю пользователей.
    """

    candidates = [
        material
        for material in materials
        if normalize_text(topic) in split_topics(
            material["topics"]
        )
    ]

    candidates.sort(
        key=lambda material: (
            normalize_text(material["title"]),
            material["material_type"],
            material["material_id"],
        )
    )

    return candidates[:top_k]


# ============================================================
# ОБЫЧНЫЙ TF-IDF
# ============================================================

def tfidf_recommend(model, goal, top_k=5):
    """
    Текстовые рекомендации без персональных бонусов.
    """

    query_vector = model.vectorizer.transform([goal])

    similarities = cosine_similarity(
        query_vector,
        model.matrix,
    ).ravel()

    ranked_indices = np.argsort(
        -similarities,
        kind="stable",
    )

    results = []

    for idx in ranked_indices:
        idx = int(idx)

        if len(results) >= top_k:
            break

        if similarities[idx] < MIN_SIMILARITY:
            break

        results.append(model.materials[idx])

    return results


# ============================================================
# МЕТРИКИ
# ============================================================

def calculate_metrics(recommendations, relevant_slugs, k=5):
    """
    Бинарные метрики относительно заданного
    набора размеченных релевантных материалов.

    ВНИМАНИЕ:
    Неразмеченные материалы здесь считаются
    нерелевантными. Поэтому результаты
    являются предварительной оценкой.
    """

    recommended_slugs = [
        material["url"]
        for material in recommendations[:k]
    ]

    hits = [
        1 if slug in relevant_slugs else 0
        for slug in recommended_slugs
    ]

    hits_count = sum(hits)

    precision = hits_count / k

    recall = (
        hits_count / len(relevant_slugs)
        if relevant_slugs else 0.0
    )

    # Discounted Cumulative Gain
    dcg = sum(
        hit / np.log2(position + 2)
        for position, hit in enumerate(hits)
    )

    # Ideal DCG для бинарной релевантности
    ideal_hits = min(len(relevant_slugs), k)

    idcg = sum(
        1 / np.log2(position + 2)
        for position in range(ideal_hits)
    )

    ndcg = dcg / idcg if idcg > 0 else 0.0

    return {
        "precision_at_5": round(precision, 4),
        "recall_at_5": round(recall, 4),
        "ndcg_at_5": round(ndcg, 4),
        "hits": hits_count,
    }


# ============================================================
# ЗАПУСК ОЦЕНКИ
# ============================================================

def evaluate():
    print("ALFA-COURSE | RECOMMENDER EVALUATION")
    print("=" * 70)

    materials = load_materials()

    print(f"Loaded materials: {len(materials)}")
    print("Building TF-IDF index...")

    model = ContentBasedRecommender(materials)

    available_slugs = {
        material["url"]
        for material in materials
    }

    summary_rows = []
    detail_rows = []

    for test in TEST_PROFILES:
        name = test["name"]
        profile = test["profile"]
        relevant = test["relevant_slugs"]

        missing_slugs = relevant - available_slugs

        if missing_slugs:
            raise ValueError(
                f"Profile {name}: missing slugs "
                f"{sorted(missing_slugs)}"
            )

        # 1. Baseline
        baseline = baseline_recommend(
            materials,
            test["baseline_topic"],
            TOP_K,
        )

        # 2. TF-IDF
        tfidf = tfidf_recommend(
            model,
            profile["goal"],
            TOP_K,
        )

        # 3. Personalized TF-IDF
        personalized = model.recommend(
            profile,
            TOP_K,
        )

        material_lookup = {
            material_key(material): material
            for material in materials
        }

        algorithms = {
            "baseline": baseline,
            "tfidf": tfidf,
            "personalized": personalized,
        }

        print("\n" + "=" * 70)
        print(f"PROFILE: {name}")
        print(f"GOAL: {profile['goal']}")
        print("=" * 70)

        for algorithm_name, recommendations in algorithms.items():
            metrics = calculate_metrics(
                recommendations,
                relevant,
                TOP_K,
            )

            summary_rows.append({
                "profile": name,
                "algorithm": algorithm_name,
                **metrics,
            })

            print(f"\n{algorithm_name.upper()}")
            print(
                f"Precision@5: "
                f"{metrics['precision_at_5']:.4f}"
            )
            print(
                f"Recall@5:    "
                f"{metrics['recall_at_5']:.4f}"
            )
            print(
                f"NDCG@5:      "
                f"{metrics['ndcg_at_5']:.4f}"
            )

            for rank, item in enumerate(
                recommendations,
                start=1,
            ):
                source = material_lookup.get(
                    material_key(item),
                    item,
                )

                relevant_flag = int(
                    source["url"] in relevant
                )

                detail_rows.append({
                    "profile": name,
                    "algorithm": algorithm_name,
                    "rank": rank,
                    "title": source["title"],
                    "material_type": source["material_type"],
                    "slug": source["url"],
                    "is_labeled_relevant": relevant_flag,
                })

                print(
                    f"  {rank}. {source['title']} "
                    f"[label={relevant_flag}]"
                )

    # ========================================================
    # СРЕДНИЕ МЕТРИКИ
    # ========================================================

    print("\n" + "=" * 70)
    print("AVERAGE METRICS")
    print("=" * 70)

    for algorithm in [
        "baseline",
        "tfidf",
        "personalized",
    ]:
        subset = [
            row
            for row in summary_rows
            if row["algorithm"] == algorithm
        ]

        avg_precision = np.mean([
            row["precision_at_5"]
            for row in subset
        ])

        avg_recall = np.mean([
            row["recall_at_5"]
            for row in subset
        ])

        avg_ndcg = np.mean([
            row["ndcg_at_5"]
            for row in subset
        ])

        print(
            f"{algorithm:15} "
            f"P@5={avg_precision:.4f} "
            f"R@5={avg_recall:.4f} "
            f"NDCG@5={avg_ndcg:.4f}"
        )

    # ========================================================
    # СОХРАНЕНИЕ ОТЧЁТОВ
    # ========================================================

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_file = REPORT_DIR / "evaluation_summary.csv"
    detail_file = REPORT_DIR / "evaluation_details.csv"

    with summary_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "profile",
                "algorithm",
                "precision_at_5",
                "recall_at_5",
                "ndcg_at_5",
                "hits",
            ],
        )

        writer.writeheader()
        writer.writerows(summary_rows)

    with detail_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "profile",
                "algorithm",
                "rank",
                "title",
                "material_type",
                "slug",
                "is_labeled_relevant",
            ],
        )

        writer.writeheader()
        writer.writerows(detail_rows)

    print("\nReports saved:")
    print(summary_file)
    print(detail_file)
    print("\nEvaluation completed.")

    return 0


if __name__ == "__main__":
    sys.exit(evaluate())
