
from sklearn.metrics.pairwise import cosine_similarity

from recommender.content_based import (
    ContentBasedRecommender,
    load_materials,
)


SCENARIOS = [
    {
        "name": "Открытие интернет-магазина",
        "goal": "Как открыть интернет-магазин с нуля",
        "targets": [
            "Как выходить на маркетплейсы",
            "выбрать товар",
            "Маркетплейсы: с чего начать",
            "Как подключить онлайн-кассу",
            "Pop-up магазины",
        ],
    },
    {
        "name": "Сокращение расходов кафе",
        "goal": "Как сократить расходы и увеличить прибыль кафе",
        "targets": [
            "Ресторан в цифрах",
            "Списания в общепите",
            "сократить расходы на персонал",
            "Оптимизация логистики",
            "себестоимость маникюра",
        ],
    },
]


def main():
    materials = load_materials()
    model = ContentBasedRecommender(materials)

    for scenario in SCENARIOS:
        print("\n" + "=" * 70)
        print(scenario["name"])
        print("=" * 70)

        query_vector = model.vectorizer.transform([
            scenario["goal"]
        ])

        similarities = cosine_similarity(
            query_vector,
            model.matrix,
        ).ravel()

        ranking = similarities.argsort()[::-1]
        ranks = {
            int(index): position
            for position, index in enumerate(ranking, 1)
        }

        for target in scenario["targets"]:
            found = [
                (idx, material)
                for idx, material in enumerate(materials)
                if target.lower() in material["title"].lower()
            ]

            if not found:
                print(f"\nНЕ НАЙДЕНО: {target}")
                continue

            for idx, material in found:
                print(f"\nНазвание: {material['title']}")
                print(f"Тип: {material['material_type']}")
                print(f"Темы: {material['topics']}")
                print(f"Отрасль: {material['industries']}")
                print(f"TF-IDF similarity: {similarities[idx]:.4f}")
                print(f"Позиция по TF-IDF: {ranks[idx]}")
                print(
                    "Проходит порог 0.08:",
                    "ДА" if similarities[idx] >= 0.08 else "НЕТ"
                )


if __name__ == "__main__":
    main()
