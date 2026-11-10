
from recommender.service import get_recommendations

profiles = [
    {
        "name": "Начинающий владелец интернет-магазина",
        "goal": "Как открыть интернет-магазин с нуля",
        "industry": "интернет-магазин",
        "business_stage": "starting",
        "experience": "beginner",
        "preferred_format": "article",
    },
    {
        "name": "Владелец салона красоты",
        "goal": "Как увеличить продажи и привлечь клиентов",
        "industry": "красота",
        "business_stage": "growing",
        "experience": "beginner",
        "preferred_format": "article",
    },
    {
        "name": "Владелец кафе",
        "goal": "Как сократить расходы и увеличить прибыль кафе",
        "industry": "кафе",
        "business_stage": "growing",
        "experience": "experienced",
        "preferred_format": "article",
    },
    {
        "name": "Предприниматель с сотрудниками",
        "goal": "Как правильно нанимать сотрудников и управлять командой",
        "industry": "услуги",
        "business_stage": "growing",
        "experience": "beginner",
        "preferred_format": "article",
    },
]


def main():
    for profile in profiles:
        print("\n" + "=" * 65)
        print(profile["name"])
        print("=" * 65)

        response = get_recommendations(
            profile=profile,
            top_k=5,
        )

        if not response["recommendations"]:
            print("Подходящие материалы не найдены")
            continue

        for i, material in enumerate(
            response["recommendations"], 1
        ):
            print(
                f"{i}. {material['title']} "
                f"(score={material['score']})"
            )


if __name__ == "__main__":
    main()
