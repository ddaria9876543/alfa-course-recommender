
import csv
import math
from collections import defaultdict
from pathlib import Path


REPORTS = Path(__file__).resolve().parent / "reports"

OLD_LABELS = REPORTS / "manual_relevance_labeled.csv"
NEW_LABELS = REPORTS / "hybrid_relevance_to_label.csv"
OLD_RANKINGS = REPORTS / "evaluation_details.csv"
NEW_RANKINGS = REPORTS / "hybrid_rankings.csv"

LABELED_OUTPUT = REPORTS / "hybrid_relevance_labeled.csv"
METRICS_OUTPUT = REPORTS / "comparison_metrics.csv"

K = 5

# Оценки, которые мы согласовали.
NEW_SCORES = {
    ("beauty_sales", "Как вернуть клиентов в салон красоты"): 2,
    ("beauty_sales", "Как сформировать вау-сервис"): 2,
    ("beauty_sales", "Экономика заботы: как сервис влияет на выручку в 2026 году"): 1,
    ("beauty_sales", "Бизнес в спорте: как начать и масштабировать"): 0,

    ("business_start", "Бизнес-идеи в Тюмени для начинающих и опытных предпринимателей"): 1,
    ("business_start", "Какие документы нужны для открытия кафе"): 0,
    ("business_start", "Как начинающему фермеру получить грант"): 0,

    ("online_store", "Пошаговая инструкция по открытию ПВЗ"): 0,
    ("online_store", "Как зарегистрироваться на Wildberries как продавец"): 1,
    ("online_store", "Готовимся к распродаже: частые ошибки начинающих селлеров"): 0,
    ("online_store", "Реклама на Ozon: способы попадать в топ для неволшебников"): 0,
    ("online_store", "Как выходить на маркетплейсы"): 1,
}


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Не найден файл: {path}")

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        return list(csv.DictReader(file))


def write_csv(path, rows, columns):
    with path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=columns, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def item_key(row):
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

    for row in ranking:
        key = item_key(row)

        if key not in labels:
            raise ValueError(
                f"Нет оценки для материала: {key}"
            )

        grades.append(labels[key])

    precision = sum(
        grade >= 1 for grade in grades
    ) / K

    relevant_total = sum(
        grade >= 1
        for key, grade in labels.items()
        if key[0] == profile
    )

    recall = (
        sum(grade >= 1 for grade in grades)
        / relevant_total
        if relevant_total else 0.0
    )

    dcg = sum(
        (2 ** grade - 1) / math.log2(i + 2)
        for i, grade in enumerate(grades)
    )

    ideal = sorted(
        [
            grade
            for key, grade in labels.items()
            if key[0] == profile
        ],
        reverse=True,
    )[:K]

    idcg = sum(
        (2 ** grade - 1) / math.log2(i + 2)
        for i, grade in enumerate(ideal)
    )

    ndcg = dcg / idcg if idcg else 0.0

    return {
        "precision_at_5": precision,
        "recall_at_5": recall,
        "ndcg_at_5": ndcg,
    }

def normalize_title(value):
    """Приводит пробелы в названиях к единому виду."""
    return " ".join(str(value or "").split())

def main():
    old_labels = read_csv(OLD_LABELS)
    candidate_labels = read_csv(NEW_LABELS)

    old_rankings = read_csv(OLD_RANKINGS)
    hybrid_rankings = read_csv(NEW_RANKINGS)

    # Проверяем, что сохранились старые оценки.
    old_by_key = {
        item_key(row): int(row["relevance"])
        for row in old_labels
    }

    if len(old_by_key) != len(old_labels):
        raise ValueError(
            "В старой разметке обнаружены дубликаты"
        )

    normalized_scores = {
        (profile, normalize_title(title)): score
        for (profile, title), score in NEW_SCORES.items()
    }

    updated = []
    labels = {}
    used_new_scores = set()

    for row in candidate_labels:
        key = item_key(row)

        if key in labels:
            raise ValueError(
                f"Дубликат материала: {key}"
            )

        if key in old_by_key:
            score = old_by_key[key]

        else:
            score_key = (
                row["profile"],
                normalize_title(row["title"]),
            )

            if score_key not in normalized_scores:
                raise ValueError(
                    f"??? ????? ??????: {score_key}"
                )

            score = normalized_scores[score_key]
            used_new_scores.add(score_key)

        if score not in (0, 1, 2):
            raise ValueError(
                f"Недопустимая оценка: {score}"
            )

        labels[key] = score
        updated.append({
            **row,
            "relevance": score,
        })

    if set(old_by_key) - set(labels):
        raise ValueError(
            "Часть старых оценок потерялась"
        )

    unused = set(normalized_scores) - used_new_scores

    if unused:
        raise ValueError(
            f"Неиспользованные оценки: {unused}"
        )

    # Группируем выдачу всех четырёх алгоритмов.
    grouped = defaultdict(list)

    for row in old_rankings + hybrid_rankings:
        key = (row["profile"], row["algorithm"])
        grouped[key].append(row)

    algorithms = [
        "baseline",
        "tfidf",
        "personalized",
        "hybrid",
    ]

    profiles = sorted({
        row["profile"]
        for row in old_labels
    })

    results = []

    for profile in profiles:
        for algorithm in algorithms:
            key = (profile, algorithm)

            if key not in grouped:
                raise ValueError(
                    f"Отсутствует выдача: {key}"
                )

            metrics = calculate_metrics(
                grouped[key],
                labels,
                profile,
            )

            results.append({
                "profile": profile,
                "algorithm": algorithm,
                **metrics,
            })

    # Файлы создаём только после всех проверок.
    write_csv(
        LABELED_OUTPUT,
        updated,
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

    print("ALFA-COURSE | MODEL COMPARISON")
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

    for algorithm in algorithms:
        subset = [
            row for row in results
            if row["algorithm"] == algorithm
        ]

        print(f"\n{algorithm}")

        for metric in [
            "precision_at_5",
            "recall_at_5",
            "ndcg_at_5",
        ]:
            average = sum(
                row[metric] for row in subset
            ) / len(subset)

            print(f"  {metric}: {average:.4f}")

    print("\nРазмечено материалов:", len(labels))
    print("Сохранено:", METRICS_OUTPUT)


if __name__ == "__main__":
    main()
