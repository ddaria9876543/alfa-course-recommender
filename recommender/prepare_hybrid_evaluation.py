
import csv
from collections import defaultdict
from pathlib import Path

from recommender.service import get_recommendations
from recommender.content_based import load_materials


BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

LABELS_FILE = REPORTS_DIR / "manual_relevance_labeled.csv"
OUTPUT_FILE = REPORTS_DIR / "hybrid_relevance_to_label.csv"
RANKINGS_FILE = REPORTS_DIR / "hybrid_rankings.csv"

TOP_K = 5

# Дополнительные параметры профилей.
# Бизнес-задачи берём из существующей разметки.
PROFILE_SETTINGS = {
    "beauty_sales": {
        "industry": "красота",
        "business_stage": "growing",
        "experience": "beginner",
        "preferred_format": "article",
    },
    "online_store": {
        "industry": "интернет-магазин",
        "business_stage": "starting",
        "experience": "beginner",
        "preferred_format": "article",
    },
    "business_start": {
        "industry": "",
        "business_stage": "starting",
        "experience": "beginner",
        "preferred_format": "article",
    },
}


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def write_csv(path, fieldnames, rows):
    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    if not LABELS_FILE.exists():
        raise FileNotFoundError(
            f"Не найдена разметка: {LABELS_FILE}"
        )

    old_labels = read_csv(LABELS_FILE)

    # Группируем исходные задачи по профилям.
    goals = defaultdict(set)

    for row in old_labels:
        goals[row["profile"]].add(
            row["business_goal"].strip()
        )

    # Одна бизнес-задача на один профиль.
    for profile, profile_goals in goals.items():
        if len(profile_goals) != 1:
            raise ValueError(
                f"У профиля {profile} несколько задач: "
                f"{sorted(profile_goals)}"
            )

    # Индекс существующих оценок.
    known = {}

    for row in old_labels:
        key = (
            row["profile"],
            row["material_type"],
            row["slug"],
        )

        if key in known:
            raise ValueError(
                f"Дубликат в разметке: {key}"
            )

        known[key] = row

    # Каталог нужен для описаний новых материалов.
    materials = load_materials()

    catalog = {
        (
            material["material_type"],
            material["url"],
        ): material
        for material in materials
    }

    # Сохраняем все прежние оценки.
    combined = []

    for row in old_labels:
        combined.append({
            **row,
            "source": "previous",
        })

    ranking_rows = []
    new_count = 0

    for profile_name, profile_goals in sorted(
        goals.items()
    ):
        goal = next(iter(profile_goals))

        profile = {
            "goal": goal,
            **PROFILE_SETTINGS.get(profile_name, {}),
        }

        print("\n" + "=" * 65)
        print("PROFILE:", profile_name)
        print("GOAL:", goal)
        print("=" * 65)

        response = get_recommendations(
            profile=profile,
            top_k=TOP_K,
        )

        for rank, rec in enumerate(
            response["recommendations"],
            start=1,
        ):
            key = (
                profile_name,
                rec["material_type"],
                rec["slug"],
            )

            ranking_rows.append({
                "profile": profile_name,
                "algorithm": "hybrid",
                "rank": rank,
                "material_type": rec["material_type"],
                "slug": rec["slug"],
                "title": rec["title"],
                "score": rec["score"],
            })

            if key in known:
                print(
                    f"{rank}. [ОЦЕНЕНО] {rec['title']}"
                )
                continue

            material = catalog.get((
                rec["material_type"],
                rec["slug"],
            ))

            if material is None:
                raise ValueError(
                    f"Материал отсутствует в каталоге: {key}"
                )

            combined.append({
                "profile": profile_name,
                "business_goal": goal,
                "material_type": rec["material_type"],
                "slug": rec["slug"],
                "title": rec["title"],
                "description": material["description"],
                "topics": material["topics"],
                "relevance": "",
                "source": "hybrid_new",
            })

            new_count += 1

            print(
                f"{rank}. [НОВЫЙ] {rec['title']}"
            )

    write_csv(
        OUTPUT_FILE,
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
        combined,
    )

    write_csv(
        RANKINGS_FILE,
        [
            "profile",
            "algorithm",
            "rank",
            "material_type",
            "slug",
            "title",
            "score",
        ],
        ranking_rows,
    )

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    print("Старых оценок:", len(old_labels))
    print("Новых материалов для оценки:", new_count)
    print("Всего строк:", len(combined))
    print("Таблица разметки:", OUTPUT_FILE)
    print("Рекомендации модели:", RANKINGS_FILE)


if __name__ == "__main__":
    main()
