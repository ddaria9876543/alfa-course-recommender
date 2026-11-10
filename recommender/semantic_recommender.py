
import numpy as np
from sentence_transformers import SentenceTransformer

from recommender.content_based import load_materials


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

TEST_PROFILES = [
    {
        "name": "Начинающий владелец интернет-магазина",
        "goal": "Как открыть интернет-магазин с нуля",
    },
    {
        "name": "Владелец салона красоты",
        "goal": "Как увеличить продажи и привлечь клиентов салона красоты",
    },
    {
        "name": "Владелец кафе",
        "goal": "Как сократить расходы и увеличить прибыль кафе",
    },
    {
        "name": "Предприниматель с сотрудниками",
        "goal": "Как правильно нанимать сотрудников и управлять командой",
    },
]


def build_document_text(material):
    """
    Используем название и описание материала.
    Категории пока не добавляем, чтобы отдельно
    проверить качество семантического поиска.
    """
    title = str(material.get("title") or "").strip()
    description = str(
        material.get("description") or ""
    ).strip()

    return f"{title}. {description}"


def main():
    print("Загружаем каталог PostgreSQL...")
    materials = load_materials()

    print(f"Материалов: {len(materials)}")

    print("Загружаем Sentence Transformer...")
    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu",
    )

    texts = [
        build_document_text(material)
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

    goals = [
        profile["goal"]
        for profile in TEST_PROFILES
    ]

    query_vectors = model.encode(
        goals,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    for profile, query_vector in zip(
        TEST_PROFILES,
        query_vectors,
    ):
        similarities = (
            document_vectors @ query_vector
        )

        ranked_indices = np.argsort(
            -similarities,
            kind="stable",
        )[:5]

        print("\n" + "=" * 65)
        print(profile["name"])
        print("=" * 65)

        for rank, idx in enumerate(
            ranked_indices,
            start=1,
        ):
            idx = int(idx)
            material = materials[idx]

            print(
                f"{rank}. {material['title']} "
                f"(similarity={similarities[idx]:.4f})"
            )

            print(
                f"   Тип: {material['material_type']}"
            )
            print(
                f"   Темы: {material['topics']}"
            )
            print(
                f"   Отрасли: {material['industries']}"
            )


if __name__ == "__main__":
    main()
