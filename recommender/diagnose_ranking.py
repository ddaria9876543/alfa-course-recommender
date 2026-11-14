
from recommender.content_based import (
    ContentBasedRecommender,
    load_materials,
    normalize_text,
)


PROFILES = [
    {
        "name": "Интернет-магазин",
        "goal": "Как открыть интернет-магазин с нуля",
        "industry": "интернет-магазин",
    },
    {
        "name": "Кафе",
        "goal": "Как сократить расходы и увеличить прибыль кафе",
        "industry": "кафе",
    },
]


def main():
    materials = load_materials()
    model = ContentBasedRecommender(materials)

    for profile in PROFILES:
        print("\n" + "=" * 75)
        print("СЦЕНАРИЙ:", profile["name"])
        print("ЗАПРОС:", profile["goal"])
        print("=" * 75)

        recommendations = model.recommend(
            profile,
            top_k=10,
        )

        by_id = {
            str(material["material_id"]): material
            for material in materials
        }

        for rank, rec in enumerate(
            recommendations,
            start=1,
        ):
            material = by_id[str(rec["material_id"])]

            industry_bonus, reason = (
                model.get_industry_bonus(
                    material,
                    profile["industry"],
                )
            )

            similarity = rec["similarity"] or 0.0
            confidence = min(
                1.0,
                similarity / 0.20,
            )

            actual_bonus = industry_bonus * confidence

            print(f"\n{rank}. {rec['title']}")
            print(f"   TF-IDF: {similarity:.4f}")
            print(f"   Отраслевой бонус: {actual_bonus:.4f}")
            print(f"   Итоговый score: {rec['score']:.4f}")
            print(f"   Отрасль: {material['industries']}")
            print(f"   Темы: {material['topics']}")
            print(f"   Причина бонуса: {reason or 'нет'}")

            print(
                "   Описание:",
                normalize_text(
                    material["description"]
                )[:220],
            )

            print(
                "   Search text:",
                normalize_text(
                    material["search_text"]
                )[:300],
            )


if __name__ == "__main__":
    main()
