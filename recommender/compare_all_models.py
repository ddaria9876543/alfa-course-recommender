
import csv
import math
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

PREVIOUS_LABELS = REPORTS_DIR / "hybrid_relevance_labeled.csv"
SEMANTIC_CANDIDATES = (
    REPORTS_DIR / "semantic_relevance_to_label.csv"
)

OLD_RANKINGS = REPORTS_DIR / "evaluation_details.csv"
HYBRID_RANKINGS = REPORTS_DIR / "hybrid_rankings.csv"
SEMANTIC_RANKINGS = REPORTS_DIR / "semantic_rankings.csv"

LABELS_OUTPUT = REPORTS_DIR / "all_models_labeled.csv"
METRICS_OUTPUT = REPORTS_DIR / "all_models_comparison.csv"

K = 5

ALGORITHMS = [
    "baseline",
    "tfidf",
    "personalized",
    "hybrid",
    "semantic",
]

# Согласованные оценки 11 новых рекомендаций
NEW_SCORES = {
    (
        "beauty_sales",
        "СанПиН для салонов красоты 2026",
    ): 0,

    (
        "beauty_sales",
        "Как выходить на маркетплейсы",
    ): 0,

    (
        "beauty_sales",
        "Категорийный менеджмент: как сделать товары видимыми и прибыльными",
    ): 0,

    (
        "business_start",
        "Вендинговый бизнес: руководство по запуску",
    ): 1,

    (
        "business_start",
        "Путь серийного предпринимателя: проходим с экспертами",
    ): 1,

    (
        "business_start",
        "Нейросети для бизнеса: с чего начать",
    ): 1,

    (
        "business_start",
        "Просто о сложном: первые шаги в бизнесe",
    ): 2,

    (
        "online_store",
        "Вендинговый бизнес: руководство по запуску",
    ): 0,

    (
        "online_store",
        "Бизнес-идеи в Тюмени для начинающих и опытных предпринимателей",
    ): 0,

    (
        "online_store",
        "Как открыть ООО",
    ): 1,

    (
        "online_store",
        "Личный бренд предпринимателя: практическое руководство",
    ): 1,
}


def normalize_title(value):
    """Убирает различия между пробелами."""
    return " ".join(str(value or "").split()).casefold()


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Не найден файл: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def write_csv(path, rows, columns):
    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def material_key(row):
    return (
        row["profile"],
        row["material_type"],
        row["slug"],
    )


def calculate_metrics(ranking, labels, profile):
    ranking = sorted(
        ranking,
        key=lambda row: int(row["rank"]),
    )

    if len(ranking) != K:
        raise ValueError(
            f"{profile}: ожидалось {K} рекомендаций, "
            f"получено {len(ranking)}"
        )

    grades = []
    seen = set()

    for row in ranking:
        key = material_key(row)

        if key in seen:
            raise ValueError(
                f"Повтор материала в выдаче: {key}"
            )

        seen.add(key)

        if key not in labels:
            raise ValueError(
                f"Материал не размечен: {key}"
            )

        grades.append(labels[key])

    relevant_retrieved = sum(
        grade >= 1 for grade in grades
    )

    precision = relevant_retrieved / K

    # Recall относительно размеченного пула,
    # а НЕ всего каталога PostgreSQL.
    relevant_total = sum(
        grade >= 1
        for key, grade in labels.items()
        if key[0] == profile
    )

    recall = (
        relevant_retrieved / relevant_total
        if relevant_total else 0.0
    )

    dcg = sum(
        (2 ** grade - 1) / math.log2(i + 2)
        for i, grade in enumerate(grades)
    )

    ideal_grades = sorted(
        [
            grade
            for key, grade in labels.items()
            if key[0] == profile
        ],
        reverse=True,
    )[:K]

    idcg = sum(
        (2 ** grade - 1) / math.log2(i + 2)
        for i, grade in enumerate(ideal_grades)
    )

    ndcg = dcg / idcg if idcg else 0.0

    return {
        "precision_at_5": precision,
        "recall_at_5": recall,
        "ndcg_at_5": ndcg,
    }


def main():
    previous_rows = read_csv(PREVIOUS_LABELS)
    candidate_rows = read_csv(SEMANTIC_CANDIDATES)

    old_rankings = read_csv(OLD_RANKINGS)
    hybrid_rankings = read_csv(HYBRID_RANKINGS)
    semantic_rankings = read_csv(SEMANTIC_RANKINGS)

    # Загружаем прежние оценки.
    previous_scores = {}

    for row in previous_rows:
        key = material_key(row)

        if key in previous_scores:
            raise ValueError(
                f"Дубликат старой оценки: {key}"
            )

        previous_scores[key] = int(
            row["relevance"]
        )

    # Нормализуем названия, поскольку в базе
    # встречаются неразрывные пробелы.
    normalized_new_scores = {
        (
            profile,
            normalize_title(title),
        ): score
        for (profile, title), score in NEW_SCORES.items()
    }

    labels = {}
    completed_rows = []
    used_new_scores = set()

    for row in candidate_rows:
        key = material_key(row)

        if key in labels:
            raise ValueError(
                f"Дубликат в общей разметке: {key}"
            )

        if key in previous_scores:
            grade = previous_scores[key]

        else:
            score_key = (
                row["profile"],
                normalize_title(row["title"]),
            )

            if score_key not in normalized_new_scores:
                raise ValueError(
                    f"Нет оценки для: {score_key}"
                )

            grade = normalized_new_scores[score_key]
            used_new_scores.add(score_key)

        if grade not in (0, 1, 2):
            raise ValueError(
                f"Недопустимая оценка: {grade}"
            )

        labels[key] = grade

        completed_rows.append({
            **row,
            "relevance": grade,
        })

    # Не допускаем потери старых оценок.
    missing_previous = (
        set(previous_scores) - set(labels)
    )

    if missing_previous:
        raise ValueError(
            f"Потеряны старые оценки: "
            f"{missing_previous}"
        )

    unused_scores = (
        set(normalized_new_scores) - used_new_scores
    )

    if unused_scores:
        raise ValueError(
            f"Новые оценки не использованы: "
            f"{unused_scores}"
        )

    # Проверяем, что оценки старых материалов
    # не были изменены.
    for key, old_grade in previous_scores.items():
        if labels[key] != old_grade:
            raise ValueError(
                f"Изменилась старая оценка: {key}"
            )

    # Собираем выдачи всех моделей.
    grouped_rankings = defaultdict(list)

    for row in (
        old_rankings
        + hybrid_rankings
        + semantic_rankings
    ):
        key = (
            row["profile"],
            row["algorithm"],
        )

        grouped_rankings[key].append(row)

    profiles = sorted({
        row["profile"]
        for row in previous_rows
    })

    results = []

    for profile in profiles:
        for algorithm in ALGORITHMS:
            key = (profile, algorithm)

            if key not in grouped_rankings:
                raise ValueError(
                    f"Нет рекомендаций: {key}"
                )

            metrics = calculate_metrics(
                grouped_rankings[key],
                labels,
                profile,
            )

            results.append({
                "profile": profile,
                "algorithm": algorithm,
                **metrics,
            })

    # Сохраняем результаты только после
    # успешного прохождения всех проверок.
    write_csv(
        LABELS_OUTPUT,
        completed_rows,
        [
            "profile",
            "business_goal",
            "material_type",
            "slug",
            "title",
            "description",
            "topics",
            "relevance",
            "source",
        ],
    )

    write_csv(
        METRICS_OUTPUT,
        results,
        [
            "profile",
            "algorithm",
            "precision_at_5",
            "recall_at_5",
            "ndcg_at_5",
        ],
    )

    print("ALFA-COURSE | ALL MODELS COMPARISON")
    print("=" * 65)

    for row in results:
        print(
            f"{row['profile']:16} "
            f"{row['algorithm']:13} "
            f"P@5={row['precision_at_5']:.4f} "
            f"R@5={row['recall_at_5']:.4f} "
            f"NDCG@5={row['ndcg_at_5']:.4f}"
        )

    print("\nAVERAGE METRICS")
    print("=" * 65)

    for algorithm in ALGORITHMS:
        subset = [
            row for row in results
            if row["algorithm"] == algorithm
        ]

        averages = {
            metric: sum(
                row[metric] for row in subset
            ) / len(subset)
            for metric in (
                "precision_at_5",
                "recall_at_5",
                "ndcg_at_5",
            )
        }

        print(
            f"{algorithm:13} "
            f"P@5={averages['precision_at_5']:.4f} "
            f"R@5={averages['recall_at_5']:.4f} "
            f"NDCG@5={averages['ndcg_at_5']:.4f}"
        )

    print("\nРазмечено пар:", len(labels))
    print("Новых оценок:", len(used_new_scores))
    print("Отчёт:", METRICS_OUTPUT)


if __name__ == "__main__":
    main()
