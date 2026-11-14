
from recommender.service import get_recommendations

TEST_GOALS = [
    "Увеличить продажи",
    "Привлечь новых клиентов",
    "Открыть свой бизнес",
    "Разобраться с налогами",
    "Наладить управление командой",
    "Увеличить повторные покупки",
]

for goal in TEST_GOALS:
    print("\n" + "=" * 75)
    print(f"БИЗНЕС-ЦЕЛЬ: {goal}")
    print("=" * 75)

    result = get_recommendations(
        profile={"goal": goal},
        top_k=5,
    )

    for index, item in enumerate(result["recommendations"], start=1):
        print(f"\n{index}. {item['title']}")
        print(f"   Тип: {item['material_type']}")
        print(f"   Темы: {item.get('topics', '')}")
        print(f"   Score: {item['score']}")
        print(f"   Similarity: {item['similarity']}")

    if not result["recommendations"]:
        print("Подходящие материалы не найдены.")
