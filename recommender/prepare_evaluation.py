
import csv
from pathlib import Path

from content_based import load_materials


BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

SOURCE_FILE = REPORTS_DIR / "evaluation_details.csv"
OUTPUT_FILE = REPORTS_DIR / "manual_relevance.csv"

PROFILE_GOALS = {
    "beauty_sales": (
        "Салон красоты: увеличить продажи "
        "и привлечь клиентов"
    ),
    "online_store": (
        "Начинающий предприниматель: "
        "открыть интернет-магазин"
    ),
    "business_start": (
        "Начинающий предприниматель: "
        "открыть ИП и начать бизнес"
    ),
}


def main():
    materials = load_materials()

    material_lookup = {
        (m["material_type"], m["url"]): m
        for m in materials
    }

    with SOURCE_FILE.open(
        encoding="utf-8-sig", newline=""
    ) as file:
        results = list(csv.DictReader(file))

    unique_pairs = {}
    for row in results:
        key = (
            row["profile"],
            row["material_type"],
            row["slug"],
        )
        unique_pairs[key] = row

    output = []

    for (profile, material_type, slug), row in unique_pairs.items():
        material = material_lookup.get(
            (material_type, slug)
        )

        if material is None:
            raise ValueError(
                f"Material not found: {material_type}/{slug}"
            )

        output.append({
            "profile": profile,
            "business_goal": PROFILE_GOALS[profile],
            "material_type": material_type,
            "slug": slug,
            "title": material["title"],
            "description": material["description"][:500],
            "topics": material["topics"],
            "relevance": "",
        })

    output.sort(
        key=lambda x: (
            x["profile"],
            x["title"],
        )
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "profile",
                "business_goal",
                "material_type",
                "slug",
                "title",
                "description",
                "topics",
                "relevance",
            ],
        )
        writer.writeheader()
        writer.writerows(output)

    print("ALFA-COURSE | MANUAL EVALUATION")
    print(f"Materials in catalog: {len(materials)}")
    print(f"Recommendations: {len(results)}")
    print(f"Unique profile-material pairs: {len(output)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
