
import csv
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from recommender.content_based import load_materials


REPORTS_DIR = Path(__file__).resolve().parent / "reports"

LABELS_FILE = REPORTS_DIR / "hybrid_relevance_labeled.csv"
OUTPUT_FILE = REPORTS_DIR / "semantic_relevance_to_label.csv"
RANKINGS_FILE = REPORTS_DIR / "semantic_rankings.csv"

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

PROFILES = {
    "beauty_sales": (
        "Салон красоты: увеличить продажи и привлечь клиентов"
    ),
    "business_start": (
        "Начинающий предприниматель: открыть ИП и начать бизнес"
    ),
    "online_store": (
        "Начинающий предприниматель: открыть интернет-магазин"
    ),
}


def read_csv(path):
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


def main():
    if not LABELS_FILE.exists():
        raise FileNotFoundError(
            "Сначала необходимо выполнить compare_hybrid.py"
        )

    existing_labels = read_csv(LABELS_FILE)

    known = {
        (
            row["profile"],
            row["material_type"],
            row["slug"],
        )
        for row in existing_labels
    }

    materials = load_materials()

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu",
    )

    texts = [
        (
            f"{material['title']}. "
            f"{material['description']}"
        )
        for material in materials
    ]

    print("Строим embeddings каталога...")

    document_vectors = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    goals = list(PROFILES.values())

    query_vectors = model.encode(
        goals,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    new_rows = []
    ranking_rows = []

    for (profile, goal), query_vector in zip(
        PROFILES.items(),
        query_vectors,
    ):
        similarities = document_vectors @ query_vector

        indices = np.argsort(
            -similarities,
            kind="stable",
        )[:5]

        print("\n" + "=" * 65)
        print(profile)
        print("=" * 65)

        for rank, idx in enumerate(indices, 1):
            material = materials[int(idx)]

            key = (
                profile,
                material["material_type"],
                material["url"],
            )

            ranking_rows.append({
                "profile": profile,
                "algorithm": "semantic",
                "rank": rank,
                "material_type": material["material_type"],
                "slug": material["url"],
                "title": material["title"],
                "score": float(similarities[idx]),
            })

            if key in known:
                print(f"{rank}. [ОЦЕНЕНО] {material['title']}")
                continue

            new_rows.append({
                "profile": profile,
                "business_goal": goal,
                "material_type": material["material_type"],
                "slug": material["url"],
                "title": material["title"],
                "description": material["description"],
                "topics": material["topics"],
                "relevance": "",
                "source": "semantic_new",
            })

            print(f"{rank}. [НОВЫЙ] {material['title']}")

    write_csv(
        OUTPUT_FILE,
        existing_labels + new_rows,
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
        RANKINGS_FILE,
        ranking_rows,
        [
            "profile",
            "algorithm",
            "rank",
            "material_type",
            "slug",
            "title",
            "score",
        ],
    )

    print("\nСуществующих оценок:", len(existing_labels))
    print("Новых материалов:", len(new_rows))
    print("Всего:", len(existing_labels) + len(new_rows))


if __name__ == "__main__":
    main()
