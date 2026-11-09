
import csv
import math
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

LABELS_FILE = REPORTS_DIR / "manual_relevance_labeled.csv"
RESULTS_FILE = REPORTS_DIR / "evaluation_details.csv"
OUTPUT_FILE = REPORTS_DIR / "evaluation_final.csv"

K = 5


def read_csv(path):
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        return list(csv.DictReader(file))


def calculate_metrics(recommendations, labels):
    gains = []
    relevant_retrieved = 0

    for item in recommendations[:K]:
        key = (
            item["profile"],
            item["material_type"],
            item["slug"],
        )

        relevance = labels[key]
        gains.append(relevance)

        if relevance >= 1:
            relevant_retrieved += 1

    precision = relevant_retrieved / K

    relevant_total = sum(
        score >= 1
        for score in labels.values()
    )

    # Recall считается отдельно для каждого профиля
    # по всем размеченным кандидатам.
    profile = recommendations[0]["profile"]

    relevant_for_profile = sum(
        score >= 1
        for (p, _, _), score in labels.items()
        if p == profile
    )

    recall = (
        relevant_retrieved / relevant_for_profile
        if relevant_for_profile else 0.0
    )

    dcg = sum(
        (2 ** gain - 1) / math.log2(i + 2)
        for i, gain in enumerate(gains)
    )

    ideal_gains = sorted(
        [
            score
            for (p, _, _), score in labels.items()
            if p == profile
        ],
        reverse=True,
    )[:K]

    idcg = sum(
        (2 ** gain - 1) / math.log2(i + 2)
        for i, gain in enumerate(ideal_gains)
    )

    ndcg = dcg / idcg if idcg else 0.0

    return {
        "precision_at_5": round(precision, 4),
        "recall_at_5": round(recall, 4),
        "ndcg_at_5": round(ndcg, 4),
    }


def main():
    labeled_rows = read_csv(LABELS_FILE)
    result_rows = read_csv(RESULTS_FILE)

    labels = {}

    for row in labeled_rows:
        key = (
            row["profile"],
            row["material_type"],
            row["slug"],
        )

        score = int(row["relevance"])

        if score not in (0, 1, 2):
            raise ValueError(f"Invalid relevance: {score}")

        labels[key] = score

    grouped = defaultdict(list)

    for row in result_rows:
        key = (
            row["profile"],
            row["algorithm"],
        )
        grouped[key].append(row)

    output = []

    for (profile, algorithm), recommendations in grouped.items():
        recommendations.sort(
            key=lambda row: int(row["rank"])
        )

        metrics = calculate_metrics(
            recommendations,
            labels,
        )

        output.append({
            "profile": profile,
            "algorithm": algorithm,
            **metrics,
        })

    print("ALFA-COURSE | FINAL EVALUATION")
    print("=" * 65)

    for row in output:
        print(
            f"{row['profile']:16} "
            f"{row['algorithm']:13} "
            f"P@5={row['precision_at_5']:.4f} "
            f"R@5={row['recall_at_5']:.4f} "
            f"NDCG@5={row['ndcg_at_5']:.4f}"
        )

    print("\nAVERAGE METRICS")
    print("=" * 65)

    for algorithm in ["baseline", "tfidf", "personalized"]:
        subset = [
            row for row in output
            if row["algorithm"] == algorithm
        ]

        if not subset:
            continue

        for metric in [
            "precision_at_5",
            "recall_at_5",
            "ndcg_at_5",
        ]:
            average = sum(
                row[metric] for row in subset
            ) / len(subset)

            print(
                f"{algorithm:13} "
                f"{metric:16} = {average:.4f}"
            )

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "profile",
                "algorithm",
                "precision_at_5",
                "recall_at_5",
                "ndcg_at_5",
            ],
        )
        writer.writeheader()
        writer.writerows(output)

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
