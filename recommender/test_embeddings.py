
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def main():
    print("Загружаем семантическую модель...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu",
    )

    query = "Как сократить расходы и увеличить прибыль кафе"

    materials = [
        "Ресторан в цифрах: ключевые показатели экономики",
        "Списания в общепите: как снизить потери",
        "Как создать программу лояльности для салона красоты",
        "Туристический налог в 2026 году",
        "Как уменьшить затраты на персонал",
    ]

    texts = [query] + materials

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    similarities = cosine_similarity(
        embeddings[0:1],
        embeddings[1:],
    )[0]

    results = sorted(
        zip(materials, similarities),
        key=lambda item: item[1],
        reverse=True,
    )

    print("\nЗАПРОС:", query)
    print("=" * 65)

    for rank, (title, score) in enumerate(results, 1):
        print(f"{rank}. {title} (similarity={score:.4f})")


if __name__ == "__main__":
    main()
