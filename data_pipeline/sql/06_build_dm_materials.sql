
-- ============================================================
-- ALFA-COURSE | DATA MART: MATERIALS
-- Единый каталог материалов для рекомендательной системы
-- ============================================================

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.dm_materials AS
WITH

-- 1. Объединяем три типа материалов
source_materials AS (

    SELECT
        "Id" AS material_id,
        'article'::text AS material_type,
        "Title"::text AS title,
        "Description"::text AS description,
        "Url"::text AS url,
        "StatusId" AS status_id,
        "Published" AS published_at,
        "IsDeleted" AS is_deleted,
        "IsClosed" AS is_closed,
        "IsPublic" AS is_public,
        NULL::integer AS cost
    FROM public."Articles"

    UNION ALL

    SELECT
        "Id",
        'course'::text,
        "Title"::text,
        "Description"::text,
        "Url"::text,
        "StatusId",
        "Published",
        "IsDeleted",
        "IsClosed",
        true,
        "Cost"
    FROM public."Courses"

    UNION ALL

    SELECT
        "Id",
        'document'::text,
        "Title"::text,
        "Description"::text,
        "Url"::text,
        "StatusId",
        "Published",
        "IsDeleted",
        false,
        true,
        NULL::integer
    FROM public."Documents"
),

-- 2. Собираем темы материалов
material_topics AS (
    SELECT
        cst."ContentSettingsId" AS content_settings_id,
        STRING_AGG(
            DISTINCT t."Title"::text,
            ', ' ORDER BY t."Title"::text
        ) AS topics
    FROM public."ContentSettingsTopics" cst
    JOIN public."Topics" t
        ON t."Id" = cst."TopicId"
    WHERE t."IsDeleted" = false
    GROUP BY cst."ContentSettingsId"
),

-- 3. Собираем теги
material_tags AS (
    SELECT
        cst."ContentSettingsId" AS content_settings_id,
        STRING_AGG(
            DISTINCT t."Title"::text,
            ', ' ORDER BY t."Title"::text
        ) AS tags
    FROM public."ContentSettingsTags" cst
    JOIN public."Tags" t
        ON t."Id" = cst."TagId"
    WHERE t."IsDeleted" = false
    GROUP BY cst."ContentSettingsId"
),

-- 4. Собираем отрасли бизнеса
material_industries AS (
    SELECT
        csi."ContentSettingsId" AS content_settings_id,
        STRING_AGG(
            DISTINCT i."Title"::text,
            ', ' ORDER BY i."Title"::text
        ) AS industries
    FROM public."ContentSettingsIndustries" csi
    JOIN public."Industries" i
        ON i."Id" = csi."IndustryId"
    WHERE i."IsDeleted" = false
    GROUP BY csi."ContentSettingsId"
),

-- 5. Объединяем каталог с настройками и классификаторами
enriched_materials AS (
    SELECT
        sm.material_id,
        sm.material_type,
        sm.title,
        sm.description,
        sm.url,
        sm.cost,
        sm.published_at,
        sm.is_deleted,
        sm.is_closed,
        sm.is_public,

        cs."IsDeleted" AS settings_deleted,
        cs."Published" AS settings_published_at,

        cs."StatusId" AS settings_status_id,
        sm.status_id AS source_status_id,

        mt.topics,
        mtag.tags,
        mi.industries

    FROM source_materials sm

    JOIN public."ContentSettings" cs
        ON cs."EntityId" = sm.material_id

    JOIN public."Statuses" cs_status
        ON cs_status."Id" = cs."StatusId"

    JOIN public."Statuses" source_status
        ON source_status."Id" = sm.status_id

    LEFT JOIN material_topics mt
        ON mt.content_settings_id = cs."Id"

    LEFT JOIN material_tags mtag
        ON mtag.content_settings_id = cs."Id"

    LEFT JOIN material_industries mi
        ON mi.content_settings_id = cs."Id"
)

-- 6. Финальная витрина
SELECT
    material_id,
    material_type,

    TRIM(title) AS title,
    NULLIF(TRIM(description), '') AS description,

    NULLIF(TRIM(url), '') AS url,

    COALESCE(topics, '') AS topics,
    COALESCE(tags, '') AS tags,
    COALESCE(industries, '') AS industries,

    CASE
        WHEN material_type = 'course' AND cost > 0
            THEN 'paid'
        ELSE 'unknown'
    END AS payment_status,

    cost,
    published_at,

    -- Текст для TF-IDF / content-based рекомендаций
    TRIM(CONCAT_WS(
        ' ',
        title,
        description,
        topics,
        tags,
        industries
    )) AS search_text

FROM enriched_materials

WHERE
    -- Исключаем удалённые записи
    is_deleted = false
    AND settings_deleted = false

    -- Исключаем закрытые материалы
    AND is_closed = false
    AND is_public = true

    -- Только опубликованные материалы
    AND settings_status_id = '61f12dbc-3cd4-4c14-b64b-1709548b904e'
    AND source_status_id = '61f12dbc-3cd4-4c14-b64b-1709548b904e'

    -- Документы не имеют даты публикации в исходной БД
    AND (
        material_type = 'document'
        OR (
            published_at IS NOT NULL
            AND published_at <= NOW()
            AND settings_published_at IS NOT NULL
            AND settings_published_at <= NOW()
        )
    )

    -- Материал должен иметь название
    AND title IS NOT NULL
    AND TRIM(title) <> '';
