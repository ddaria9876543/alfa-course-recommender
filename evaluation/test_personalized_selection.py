
from recommender.service import get_recommendations
from recommender.personalized_selection import (
    select_personalized_materials,
)

profiles = [
    {"goal": "Увеличить продажи"},
    {
        "goal": "Увеличить продажи",
        "industry": "интернет-магазин",
    },
    {
        "goal": "Увеличить продажи",
        "industry": "розница",
    },
]

for profile in profiles:
    print("\n" + "=" * 65)
    print("ПРОФИЛЬ:", profile)
    print("=" * 65)

    # Получаем расширенный пул кандидатов.
    response = get_recommendations(
        profile=profile,
        top_k=100,
    )

    # Выбираем 3 рекомендации с учётом отрасли.
    selected = select_personalized_materials(
        candidates=response["recommendations"],
        profile=profile,
        top_k=3,
    )

    for i, material in enumerate(selected, start=1):
        print(f"\nШаг {i}: {material['title']}")
        print("Score:", material["score"])
        print("Similarity:", material["similarity"])
        print("Отрасли:", material.get("industry_tags", []))

    print("\nВсего кандидатов:", response["total"])
