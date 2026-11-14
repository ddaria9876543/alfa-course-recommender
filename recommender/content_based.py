
import os
import re
from pathlib import Path

import numpy as np
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# ALFA-COURSE | CONTENT-BASED RECOMMENDER
# TF-IDF + персонализация + Cold Start
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5433"))
DB_USER = os.getenv("POSTGRES_USER", "alfa_user")
DB_NAME = os.getenv("POSTGRES_DB", "alfa_course")


# ============================================================
# ВЕСА РЕКОМЕНДАТЕЛЬНОЙ МОДЕЛИ
# ============================================================

MIN_SIMILARITY = 0.08

TITLE_INDUSTRY_BONUS = 0.08
DESCRIPTION_INDUSTRY_BONUS = 0.03
CATEGORY_BONUS = 0.01
NORMALIZED_INDUSTRY_BONUS = 0.08

FORMAT_BONUS = 0.025
STAGE_BONUS = 0.05
EXPERIENCE_BONUS = 0.06

VALID_FORMATS = {
    "article",
    "course",
    "document",
}

STAGE_TAGS = {
    "planning": "Старт бизнеса",
    "running": "Развитие бизнеса",
}

INDUSTRY_ALIASES = {
    "интернет-магазин": "ECom",
    "ecom": "ECom",
    "маркетплейсы": "ECom",
    "розница": "Розница",
    "розничная торговля": "Розница",
    "услуги": "Услуги",
    "кафе": "HoReСa",
    "horeca": "HoReСa",
    "производство": "Производство",
    "строительство": "Строительство и недвижимость",
    "логистика": "Транспорт и логистика",
    "оптовая торговля": "Оптовая торговля",
    "b2b": "B2B",
    "b2g": "B2G",
}

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
    """Приводит текст к единому формату."""
    return re.sub(
        r"\s+",
        " ",
        str(value or "").lower(),
    ).strip()


def normalize_preferred_formats(profile):
    """
    Возвращает множество предпочитаемых форматов.

    Поддерживает новый параметр:
        preferred_formats: ["article", "course"]

    И старый:
        preferred_format: "article"

    Если оба параметра отсутствуют, возвращает пустое множество.
    """

    profile = profile or {}

    values = profile.get("preferred_formats")

    if values is None:
        values = profile.get("preferred_format")

    if isinstance(values, str):
        values = [values]

    if not isinstance(values, (list, tuple, set)):
        return set()

    return {
        normalized
        for value in values
        if (normalized := normalize_text(value)) in VALID_FORMATS
    }


def contains_phrase(text, phrase):
    """
    Приблизительное сопоставление фраз с учётом окончаний.

    Например:
        салон красоты ~ салона красоты
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

    if isinstance(metadata, (list, tuple, set)):
        values = metadata
    else:
        values = str(metadata or "").split(",")

    items = {
        normalize_text(item)
        for item in values
    }

    return any(
        normalize_text(category) in items
        for category in categories
    )


def matches_topic(material_topics, topic):
    """Проверяет совпадение тем материала."""
    return matches_category(material_topics, [topic])


def get_normalized_industry_bonus(material, industry):
    """Сопоставляет отрасль с нормализованными тегами."""

    if not industry:
        return 0.0, None

    normalized_industry = INDUSTRY_ALIASES.get(
        normalize_text(industry)
    )

    if not normalized_industry:
        return 0.0, None

    material_industries = (
        material.get("industry_tags") or []
    )

    if normalized_industry in material_industries:
        return (
            NORMALIZED_INDUSTRY_BONUS,
            "Материал соответствует вашей сфере бизнеса",
        )

    return 0.0, None


def get_goal_topics(goal: str) -> list[str]:
    """Определяет подходящие темы для известных бизнес-целей."""

    goal = normalize_text(goal)

    if "налог" in goal:
        return [
            "Налоги и законы",
            "Финансы и учет",
            "Финансы",
        ]

    if "повторн" in goal and (
        "покуп" in goal or "продаж" in goal
    ):
        return [
            "Продажи и переговоры",
            "Продажи",
            "Маркетинг",
            "Клиентский сервис",
        ]

    if "продаж" in goal or "клиент" in goal:
        return [
            "Продажи и переговоры",
            "Продажи",
            "Маркетинг",
            "Клиентский сервис",
        ]

    if "открыть" in goal or "запустить бизнес" in goal:
        return [
            "Старт бизнеса",
            "Первые шаги",
            "Регистрация бизнеса",
        ]

    if "команд" in goal or "сотрудник" in goal:
        return ["Управление командой"]

    return []


def has_direct_goal_match(material: dict, goal: str) -> bool:
    """Проверяет прямое совпадение цели с названием материала."""

    goal = normalize_text(goal)
    title = normalize_text(material.get("title", ""))

    if "продаж" in goal:
        return bool(
            re.search(r"(?<!\w)продаж\w*", title)
        )

    return False


INTENT_KEYWORDS = {
    "taxes": [
        "налог",
        "усн",
        "ндс",
        "аусн",
        "енс",
        "енп",
        "взнос",
        "декларац",
        "налогооблож",
        "фнс",
    ],
    "retention": [
        "повторн",
        "удержан",
        "лояльност",
        "вернуть клиент",
        "возврат клиент",
        "клиентск",
        "рассылк",
        "crm",
    ],
}


def detect_goal_intent(goal: str) -> str | None:
    """Определяет уточнённое намерение пользователя."""

    goal = normalize_text(goal)

    if "налог" in goal:
        return "taxes"

    if "повторн" in goal and (
        "покуп" in goal or "продаж" in goal
    ):
        return "retention"

    return None


def get_intent_bonus(material: dict, intent: str | None) -> float:
    """Начисляет бонус за совпадение с намерением."""

    if not intent:
        return 0.0

    keywords = INTENT_KEYWORDS.get(intent, [])

    title = normalize_text(material["title"])
    description = normalize_text(material["description"])

    if any(keyword in title for keyword in keywords):
        return 0.15

    if any(keyword in description for keyword in keywords):
        return 0.05

    return 0.0


# ============================================================
# ЗАГРУЗКА ДАННЫХ ИЗ POSTGRESQL
# ============================================================

def load_materials():
    """Загружает материалы из аналитических витрин PostgreSQL."""

    query = """
        SELECT
            m.material_id::text AS material_id,
            m.material_type,
            m.title,
            COALESCE(m.description, '') AS description,
            COALESCE(m.topics, '') AS topics,
            COALESCE(m.tags, '') AS tags,
            COALESCE(m.industries, '') AS industries,
            m.url,
            m.payment_status,
            m.search_text,
            f.industry_tags,
            f.audience_experience,
            f.is_new
        FROM analytics.dm_materials AS m
        LEFT JOIN analytics.dm_material_features AS f
            ON m.material_id = f.material_id
        ORDER BY m.material_type, m.material_id
    """

    password = os.getenv("POSTGRES_PASSWORD")

    if not password:
        raise RuntimeError(
            "POSTGRES_PASSWORD не задан. "
            "Проверьте .env или переменные окружения."
        )

    try:
        with psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=password,
            connect_timeout=10,
        ) as connection:
            with connection.cursor(
                row_factory=dict_row
            ) as cursor:
                cursor.execute(query)
                materials = cursor.fetchall()

    except psycopg.Error as exc:
        raise RuntimeError(
            "Не удалось получить материалы из PostgreSQL. "
            "Проверьте подключение и аналитические витрины."
        ) from exc

    if not materials:
        raise RuntimeError(
            "Каталог материалов пуст"
        )

    return materials


def prepare_materials(raw_materials):
    """
    Удаляет дубликаты и обрабатывает пропуски.

    При отсутствии поискового текста формирует
    его из доступных метаданных.
    """

    cleaned = []
    seen_keys = set()
    seen_titles = set()

    for item in raw_materials:
        key = (
            normalize_text(item.get("material_type")),
            str(item.get("material_id") or "").strip(),
        )

        title_norm = normalize_text(item.get("title"))

        if (
            not title_norm
            or key in seen_keys
            or title_norm in seen_titles
        ):
            continue

        seen_keys.add(key)
        seen_titles.add(title_norm)

        material = dict(item)

        material["description"] = str(
            material.get("description") or ""
        ).strip()

        material["topics"] = str(
            material.get("topics") or ""
        ).strip()

        material["tags"] = str(
            material.get("tags") or ""
        ).strip()

        material["industries"] = str(
            material.get("industries") or ""
        ).strip()

        search_text = str(
            material.get("search_text") or ""
        ).strip()

        if not search_text or not material["description"]:
            fallback_parts = [
                material["title"],
                material["description"],
                material["topics"],
                material["tags"],
                material["industries"],
            ]

            search_text = " ".join(
                part
                for part in fallback_parts
                if part
            )

        material["search_text"] = search_text

        cleaned.append(material)

    return cleaned


# ============================================================
# CONTENT-BASED RECOMMENDER
# ============================================================

class ContentBasedRecommender:

    def __init__(self, materials):
        self.materials = prepare_materials(materials)

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
            for material in self.materials
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

        if any(
            contains_phrase(material["title"], keyword)
            for keyword in keywords
        ):
            return (
                TITLE_INDUSTRY_BONUS,
                "Материал посвящён вашей сфере бизнеса",
            )

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
        Стартовая подборка для пользователя,
        который ещё не указал бизнес-задачу.
        """

        if top_k <= 0:
            return []

        starter_materials = [
            (
                "Старт бизнеса",
                "Первый месяц после открытия ИП: что нужно сделать",
            ),
            (
                "Финансы и учет",
                "5 базовых документов для нового бизнеса",
            ),
            (
                "Маркетинг",
                "Личный бренд предпринимателя: практическое руководство",
            ),
            (
                "Продажи и переговоры",
                "Как правильно составить прайс-лист",
            ),
            (
                "Клиентский сервис",
                "Где и как вести учёт клиентов",
            ),
        ]

        materials_by_title = {}

        for material in self.materials:
            title = normalize_text(material["title"])

            materials_by_title.setdefault(
                title, []
            ).append(material)

        recommendations = []
        used_materials = set()

        for topic, title in starter_materials:
            candidates = materials_by_title.get(
                normalize_text(title),
                [],
            )

            candidates = [
                material
                for material in candidates
                if material["material_type"] == "article"
                and matches_topic(
                    material["topics"],
                    topic,
                )
            ]

            if not candidates:
                print(
                    f"WARNING: Starter material not found: {title}"
                )
                continue

            material = candidates[0]

            material_key = (
                material["material_type"],
                material["material_id"],
            )

            if material_key in used_materials:
                continue

            used_materials.add(material_key)

            recommendations.append({
                "material_id": material["material_id"],
                "material_type": material["material_type"],
                "title": material["title"],
                "url": material["url"],
                "payment_status": material["payment_status"],
                "topics": material.get("topics", ""),
                "industries": material.get("industries", ""),
                "similarity": None,
                "score": None,
                "reasons": [
                    f"Рекомендуем для знакомства с темой: {topic}"
                ],
                "next_step": (
                    "Изучите материал или укажите "
                    "свою бизнес-задачу для персонального подбора"
                ),
            })

        return recommendations[:top_k]

    # --------------------------------------------------------
    # Персонализированное ранжирование
    # --------------------------------------------------------

    def recommend(self, profile, top_k=5):
        """
        Ранжирует материалы по бизнес-задаче и профилю.

        Поддерживает:
        - business goal;
        - отрасль;
        - стадию бизнеса;
        - уровень опыта;
        - несколько предпочитаемых форматов;
        - старый параметр preferred_format.
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

        business_stage = normalize_text(
            profile.get("business_stage")
        )

        experience = normalize_text(
            profile.get("experience")
        )

        # Новый мультивыбор форматов.
        preferred_formats = normalize_preferred_formats(
            profile
        )

        allowed_topics = get_goal_topics(goal)
        goal_intent = detect_goal_intent(goal)

        # Cold Start
        if not goal:
            return self.recommend_cold_start(
                top_k=top_k
            )

        # TF-IDF по тексту бизнес-задачи.
        query_vector = self.vectorizer.transform(
            [goal]
        )

        similarities = cosine_similarity(
            query_vector,
            self.matrix,
        ).ravel()

        scores = similarities.copy()

        industry_reasons = {}

        # ----------------------------------------------------
        # Расчёт бонусов персонализации
        # ----------------------------------------------------

        for idx, material in enumerate(self.materials):
            similarity = float(similarities[idx])

            if similarity < MIN_SIMILARITY:
                continue

            # Бонусы уменьшаются для материалов
            # со слабым текстовым соответствием.
            confidence = min(
                1.0,
                similarity / 0.20,
            )

            # Отрасль: совпадения в тексте.
            industry_bonus, industry_reason = (
                self.get_industry_bonus(
                    material,
                    industry,
                )
            )

            # Отрасль: нормализованные категории.
            normalized_bonus, normalized_reason = (
                get_normalized_industry_bonus(
                    material,
                    industry,
                )
            )

            # Отраслевые бонусы не суммируем.
            best_industry_bonus = max(
                industry_bonus,
                normalized_bonus,
            )

            scores[idx] += (
                best_industry_bonus * confidence
            )

            if normalized_bonus > industry_bonus:
                industry_reasons[idx] = normalized_reason
            elif industry_bonus > 0:
                industry_reasons[idx] = industry_reason

            # Намерение пользователя.
            intent_bonus = get_intent_bonus(
                material,
                goal_intent,
            )

            scores[idx] += intent_bonus * confidence

            # Стадия бизнеса.
            stage_tag = STAGE_TAGS.get(business_stage)

            if stage_tag and matches_category(
                material.get("tags", ""),
                [stage_tag],
            ):
                scores[idx] += STAGE_BONUS * confidence

            # Уровень опыта.
            if (
                experience
                and material.get("audience_experience")
                == experience
            ):
                scores[idx] += (
                    EXPERIENCE_BONUS * confidence
                )

            # Несколько предпочитаемых форматов.
            # Один бонус, если формат материала
            # входит в выбранное множество.
            material_format = normalize_text(
                material["material_type"]
            )

            if material_format in preferred_formats:
                scores[idx] += (
                    FORMAT_BONUS * confidence
                )

        # ----------------------------------------------------
        # Сортировка по итоговому score
        # ----------------------------------------------------

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

            # Тематический отбор.
            topic_match = any(
                matches_topic(
                    material["topics"],
                    topic,
                )
                for topic in allowed_topics
            )

            direct_match = has_direct_goal_match(
                material,
                goal,
            )

            if allowed_topics and not (
                topic_match or direct_match
            ):
                continue

            reasons = [
                "Материал связан с вашей бизнес-задачей"
            ]

            # Объяснение отраслевой персонализации.
            if idx in industry_reasons:
                reasons.append(
                    industry_reasons[idx]
                )

            # Объяснение формата.
            material_format = normalize_text(
                material["material_type"]
            )

            if material_format in preferred_formats:
                reasons.append(
                    "Соответствует предпочитаемому формату"
                )

            # Объяснение стадии.
            stage_tag = STAGE_TAGS.get(
                business_stage
            )

            if stage_tag and matches_category(
                material.get("tags", ""),
                [stage_tag],
            ):
                reasons.append(
                    "Учитывает стадию вашего бизнеса"
                )

            # Объяснение уровня опыта.
            if (
                experience
                and material.get("audience_experience")
                == experience
            ):
                reasons.append(
                    "Курс соответствует вашему уровню опыта"
                )

            recommendations.append({
                "material_id": material["material_id"],
                "material_type": material["material_type"],
                "title": material["title"],
                "industry_tags": (
                    material.get("industry_tags") or []
                ),
                "audience_experience": material.get(
                    "audience_experience"
                ),
                "url": material["url"],
                "payment_status": material["payment_status"],
                "topics": material.get("topics", ""),
                "industries": material.get(
                    "industries", ""
                ),
                "similarity": round(
                    similarity,
                    4,
                ),
                "score": round(
                    float(scores[idx]),
                    4,
                ),
                "reasons": reasons,
                "next_step": (
                    "Откройте материал, чтобы "
                    "изучить рекомендации подробнее"
                ),
            })

        return recommendations


# ============================================================
# РУЧНОЕ ТЕСТИРОВАНИЕ
# ============================================================

if __name__ == "__main__":

    print("Loading materials from PostgreSQL...")

    materials = load_materials()

    print(f"Loaded {len(materials)} materials")
    print("Building TF-IDF index...")

    recommender = ContentBasedRecommender(
        materials
    )

    test_profiles = [
        {
            "name": "Несколько форматов",
            "profile": {
                "goal": "Увеличить продажи",
                "industry": "розница",
                "business_stage": "running",
                "experience": "beginner",
                "preferred_formats": [
                    "article",
                    "course",
                ],
            },
        },
        {
            "name": "Один формат",
            "profile": {
                "goal": "Увеличить продажи",
                "preferred_formats": [
                    "course",
                ],
            },
        },
        {
            "name": "Старый параметр формата",
            "profile": {
                "goal": "Увеличить продажи",
                "preferred_format": "article",
            },
        },
        {
            "name": "Без предпочтений",
            "profile": {
                "goal": "Увеличить продажи",
            },
        },
    ]

    for test in test_profiles:
        print("\n" + "=" * 60)
        print(test["name"].upper())
        print("=" * 60)

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
            print(
                f"{position}. {item['title']}"
            )
            print(
                f"   Type: {item['material_type']}"
            )
            print(
                f"   Similarity: {item['similarity']}"
            )
            print(
                f"   Score: {item['score']}"
            )
            print(
                f"   Reasons: {'; '.join(item['reasons'])}"
            )
