
import csv
import io
import re
import subprocess

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# ALFA-COURSE | CONTENT-BASED RECOMMENDER
# TF-IDF + персонализация + Cold Start
# ============================================================

CONTAINER = "alfa_course_postgres"
DB_USER = "alfa_user"
DB_NAME = "alfa_course"

# Экспериментальные веса персонализации
MIN_SIMILARITY = 0.08
TITLE_INDUSTRY_BONUS = 0.08
DESCRIPTION_INDUSTRY_BONUS = 0.03
CATEGORY_BONUS = 0.01
FORMAT_BONUS = 0.025


# Соответствие пользовательских отраслей категориям каталога
INDUSTRY_MAPPING = {
    "красота": {
        "categories": ["Услуги"],
        "keywords": [
            "салон красоты",
            "салонов красоты",
            "маникюр",
            "парикмахер",
            "косметолог",
            "бьюти",
        ],
    },
    "интернет-магазин": {
        "categories": ["ECom"],
        "keywords": [
            "интернет-магазин",
            "маркетплейс",
            "онлайн-магазин",
            "электронная коммерция",
        ],
    },
    "кафе": {
        "categories": ["HoReСa"],
        "keywords": [
            "кафе",
            "ресторан",
            "общепит",
            "кофейня",
        ],
    },
    "розница": {
        "categories": ["Розница"],
        "keywords": [
            "розничная торговля",
            "розничный магазин",
            "розничные продажи",
        ],
    },
}


# Темы для стартовой подборки
STARTER_TOPICS = [
    (
        "Старт бизнеса",
        "Как открыть бизнес и с чего начать",
    ),
    (
        "Финансы и учет",
        "Как вести финансы и контролировать расходы",
    ),
    (
        "Маркетинг",
        "Как продвигать бизнес и привлекать клиентов",
    ),
    (
        "Продажи и переговоры",
        "Как увеличить продажи и работать с клиентами",
    ),
    (
        "Управление командой",
        "Как управлять сотрудниками и командой",
    ),
]


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def normalize_text(value):
    """Приведение текста к единому формату."""
    return re.sub(
        r"\s+",
        " ",
        str(value or "").lower(),
    ).strip()


def contains_phrase(text, phrase):
    """
    Приблизительное сопоставление фраз с учётом окончаний.

    Например:
    'салон красоты' ~ 'салона красоты'

    Это эвристика, а не полноценная лемматизация.
    """
    text = normalize_text(text)
    phrase = normalize_text(phrase)

    if not phrase:
        return False

    words = phrase.split()

    pattern = (
        r"(?<!\w)"
        + r"\s+".join(
            re.escape(word) + r"\w*"
            for word in words
        )
        + r"(?!\w)"
    )

    return bool(re.search(pattern, text))


def matches_category(metadata, categories):
    """Проверяет совпадение категорий материала."""
    items = {
        normalize_text(item)
        for item in (metadata or "").split(",")
    }

    return any(
        normalize_text(category) in items
        for category in categories
    )


def matches_topic(material_topics, topic):
    """Проверяет наличие темы среди тем материала."""
    topics = {
        normalize_text(item)
        for item in (material_topics or "").split(",")
    }

    return normalize_text(topic) in topics


# ============================================================
# ЗАГРУЗКА ДАННЫХ ИЗ POSTGRESQL
# ============================================================

def load_materials():
    """Загружает материалы из analytics.dm_materials."""

    query = """
    COPY (
        SELECT
            material_id,
            material_type,
            title,
            COALESCE(description, '') AS description,
            COALESCE(topics, '') AS topics,
            COALESCE(tags, '') AS tags,
            COALESCE(industries, '') AS industries,
            url,
            payment_status,
            search_text
        FROM analytics.dm_materials
        ORDER BY material_type, material_id
    ) TO STDOUT WITH (FORMAT CSV, HEADER TRUE);
    """

    command = [
        "docker",
        "exec",
        "-i",
        CONTAINER,
        "psql",
        "-X",
        "-v",
        "ON_ERROR_STOP=1",
        "-U",
        DB_USER,
        "-d",
        DB_NAME,
        "-c",
        query,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Ошибка загрузки материалов: {exc.stderr}"
        ) from exc

    materials = list(
        csv.DictReader(io.StringIO(result.stdout))
    )

    if not materials:
        raise RuntimeError(
            "Каталог материалов пуст"
        )

    return materials


# ============================================================
# РЕКОМЕНДАТЕЛЬНАЯ МОДЕЛЬ
# ============================================================

class ContentBasedRecommender:

    def __init__(self, materials):
        self.materials = materials

        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            sublinear_tf=True,
            max_features=50000,
            lowercase=True,
        )

        texts = [
            material["search_text"] or ""
            for material in materials
        ]

        self.matrix = self.vectorizer.fit_transform(texts)

    # --------------------------------------------------------
    # Отраслевая персонализация
    # --------------------------------------------------------

    def get_industry_bonus(self, material, industry):
        industry = normalize_text(industry)
        config = INDUSTRY_MAPPING.get(industry)

        if not config:
            return 0.0, None

        keywords = config["keywords"]

        # Самый сильный сигнал — название материала
        if any(
            contains_phrase(material["title"], keyword)
            for keyword in keywords
        ):
            return (
                TITLE_INDUSTRY_BONUS,
                "Материал посвящён вашей сфере бизнеса",
            )

        # Более слабый сигнал — описание, темы или теги
        extended_text = " ".join([
            material["description"],
            material["topics"],
            material["tags"],
        ])

        if any(
            contains_phrase(extended_text, keyword)
            for keyword in keywords
        ):
            return (
                DESCRIPTION_INDUSTRY_BONUS,
                "Материал затрагивает вашу сферу бизнеса",
            )

        # Общая категория — небольшой бонус
        if matches_category(
            material["industries"],
            config["categories"],
        ):
            return (
                CATEGORY_BONUS,
                "Материал относится к вашей отрасли",
            )

        return 0.0, None

    # --------------------------------------------------------
    # Cold Start
    # --------------------------------------------------------

    def recommend_cold_start(self, top_k=5):
        """
        Рекомендации новому пользователю без истории
        и без заполненной анкеты.

        Формирует подборку по базовым бизнес-темам.
        """

        if top_k <= 0:
            return []

        recommendations = []
        used_materials = set()

        for topic, query in STARTER_TOPICS:

            query_vector = self.vectorizer.transform([query])

            similarities = cosine_similarity(
                query_vector,
                self.matrix,
            ).ravel()

            candidates = []

            for idx, material in enumerate(self.materials):

                if not matches_topic(
                    material["topics"],
                    topic,
                ):
                    continue

                material_key = (
                    material["material_type"],
                    material["material_id"],
                )

                if material_key in used_materials:
                    continue

                candidates.append(
                    (idx, float(similarities[idx]))
                )

            if not candidates:
                continue

            best_idx, best_score = max(
                candidates,
                key=lambda item: item[1],
            )

            if best_score <= 0:
                continue

            material = self.materials[best_idx]

            material_key = (
                material["material_type"],
                material["material_id"],
            )

            used_materials.add(material_key)

            recommendations.append({
                "material_id": material["material_id"],
                "material_type": material["material_type"],
                "title": material["title"],
                "url": material["url"],
                "payment_status": material["payment_status"],
                "similarity": round(best_score, 4),
                "score": round(best_score, 4),
                "reasons": [
                    f"Стартовый материал по теме: {topic}"
                ],
                "next_step": (
                    "Изучите материал и выберите "
                    "интересующее направление"
                ),
            })

        return recommendations[:top_k]

    # --------------------------------------------------------
    # Персонализированные рекомендации
    # --------------------------------------------------------

    def recommend(self, profile, top_k=5):
        """
        Подбирает материалы по пользовательскому профилю.

        Поддерживает:
        - пользователя без профиля;
        - пользователя только с бизнес-задачей;
        - пользователя с отраслью и форматом.
        """

        if top_k <= 0:
            return []

        profile = profile or {}

        goal = normalize_text(
            profile.get("goal")
        )
        industry = normalize_text(
            profile.get("industry")
        )
        preferred_format = normalize_text(
            profile.get("preferred_format")
        )

        # Холодный старт без бизнес-задачи
        if not goal:
            return self.recommend_cold_start(
                top_k=top_k
            )

        # Основная текстовая релевантность
        query_vector = self.vectorizer.transform([goal])

        similarities = cosine_similarity(
            query_vector,
            self.matrix,
        ).ravel()

        scores = similarities.copy()
        industry_reasons = {}

        for idx, material in enumerate(self.materials):
            similarity = float(similarities[idx])

            # Отсекаем слишком слабые совпадения
            if similarity < MIN_SIMILARITY:
                continue

            industry_bonus, industry_reason = (
                self.get_industry_bonus(
                    material,
                    industry,
                )
            )

            # Масштабируем бонус по текстовой релевантности
            confidence = min(
                1.0,
                similarity / 0.20,
            )

            scores[idx] += industry_bonus * confidence

            if industry_bonus > 0:
                industry_reasons[idx] = industry_reason

            if (
                preferred_format
                and normalize_text(
                    material["material_type"]
                ) == preferred_format
            ):
                scores[idx] += FORMAT_BONUS * confidence

        ranked_indices = np.argsort(
            -scores,
            kind="stable",
        )

        recommendations = []

        for idx in ranked_indices:

            if len(recommendations) >= top_k:
                break

            idx = int(idx)
            similarity = float(similarities[idx])

            if similarity < MIN_SIMILARITY:
                continue

            material = self.materials[idx]

            reasons = [
                "Материал связан с вашей бизнес-задачей"
            ]

            if idx in industry_reasons:
                reasons.append(
                    industry_reasons[idx]
                )

            if (
                preferred_format
                and normalize_text(
                    material["material_type"]
                ) == preferred_format
            ):
                reasons.append(
                    "Соответствует предпочитаемому формату"
                )

            recommendations.append({
                "material_id": material["material_id"],
                "material_type": material["material_type"],
                "title": material["title"],
                "url": material["url"],
                "payment_status": material["payment_status"],
                "similarity": round(similarity, 4),
                "score": round(
                    float(scores[idx]), 4
                ),
                "reasons": reasons,
                "next_step": (
                    "Откройте материал, чтобы "
                    "изучить рекомендации подробнее"
                ),
            })

        return recommendations


# ============================================================
# ТЕСТИРОВАНИЕ
# ============================================================

if __name__ == "__main__":

    print("Loading materials from PostgreSQL...")

    materials = load_materials()

    print(f"Loaded {len(materials)} materials")
    print("Building TF-IDF index...")

    recommender = ContentBasedRecommender(materials)

    test_profiles = [
        {
            "name": "Персонализированный профиль",
            "profile": {
                "business_stage": "growing",
                "industry": "красота",
                "experience": "beginner",
                "goal": "Как увеличить продажи и привлечь клиентов",
                "preferred_format": "article",
            },
        },
        {
            "name": "Только бизнес-задача",
            "profile": {
                "goal": "Как открыть интернет-магазин",
            },
        },
        {
            "name": "Новый пользователь без истории",
            "profile": {},
        },
    ]

    for test in test_profiles:

        print("\n" + "=" * 65)
        print(test["name"].upper())
        print("=" * 65)

        recommendations = recommender.recommend(
            test["profile"],
            top_k=5,
        )

        if not recommendations:
            print("Подходящие материалы не найдены")
            continue

        for position, item in enumerate(
            recommendations,
            start=1,
        ):
            print(f"\n{position}. {item['title']}")
            print(f"   Type: {item['material_type']}")
            print(f"   Similarity: {item['similarity']}")
            print(f"   Final score: {item['score']}")
            print(f"   Payment: {item['payment_status']}")
            print(f"   Slug: {item['url']}")
            print(
                f"   Reasons: {'; '.join(item['reasons'])}"
            )
            print(
                f"   Next step: {item['next_step']}"
            )
