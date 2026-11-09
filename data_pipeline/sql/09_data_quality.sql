
-- ============================================================
-- ALFA-COURSE | DATA QUALITY: MATERIALS
-- Проверки качества витрины analytics.dm_materials
-- Read-only: исходные данные не изменяются
-- ============================================================

WITH checks AS (

    -- 1. Уникальность составного ключа
    SELECT
        'duplicate_material_keys' AS check_name,
        'ERROR' AS severity,
        COUNT(*)::bigint AS failed_rows
    FROM (
        SELECT material_type, material_id
        FROM analytics.dm_materials
        GROUP BY material_type, material_id
        HAVING COUNT(*) > 1
    ) duplicates

    UNION ALL

    -- 2. Отсутствие NULL в ключевых полях
    SELECT
        'null_material_keys',
        'ERROR',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE material_id IS NULL
       OR material_type IS NULL

    UNION ALL

    -- 3. Заполненность названий
    SELECT
        'empty_titles',
        'ERROR',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE title IS NULL
       OR BTRIM(title) = ''

    UNION ALL

    -- 4. Заполненность текста для рекомендательной модели
    SELECT
        'empty_search_text',
        'ERROR',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE search_text IS NULL
       OR BTRIM(search_text) = ''

    UNION ALL

    -- 5. Корректность slug материала
    SELECT
        'invalid_slugs',
        'ERROR',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE url IS NULL
       OR BTRIM(url) !~ '^[a-z0-9]+(-[a-z0-9]+)*$'

    UNION ALL

    -- 6. Допустимые типы материалов
    SELECT
        'invalid_material_types',
        'ERROR',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE material_type IS NULL
       OR material_type NOT IN (
           'article',
           'course',
           'document'
       )

    UNION ALL

    -- 7. Проверка доступности и публикации материалов
    SELECT
        'ineligible_materials',
        'ERROR',
        COUNT(*)
    FROM analytics.dm_materials dm
    WHERE NOT EXISTS (
        SELECT 1
        FROM (
            SELECT
                "Id" AS material_id,
                'article'::text AS material_type,
                "StatusId" AS status_id,
                "Published" AS published_at,
                "IsDeleted" AS is_deleted,
                "IsClosed" AS is_closed,
                "IsPublic" AS is_public
            FROM public."Articles"

            UNION ALL

            SELECT
                "Id",
                'course'::text,
                "StatusId",
                "Published",
                "IsDeleted",
                "IsClosed",
                true
            FROM public."Courses"

            UNION ALL

            SELECT
                "Id",
                'document'::text,
                "StatusId",
                "Published",
                "IsDeleted",
                false,
                true
            FROM public."Documents"
        ) src

        JOIN public."ContentSettings" cs
            ON cs."EntityId" = src.material_id

        WHERE src.material_id = dm.material_id
          AND src.material_type = dm.material_type

          -- Исключаем удалённые материалы
          AND src.is_deleted = false
          AND cs."IsDeleted" = false

          -- Исключаем закрытые и непубличные материалы
          AND src.is_closed = false
          AND src.is_public = true

          -- Оба статуса должны быть "Опубликовано"
          AND src.status_id =
              '61f12dbc-3cd4-4c14-b64b-1709548b904e'
          AND cs."StatusId" =
              '61f12dbc-3cd4-4c14-b64b-1709548b904e'

          -- Проверяем даты публикации
          -- Для документов дата не обязательна
          AND (
              src.material_type = 'document'
              OR (
                  src.published_at IS NOT NULL
                  AND src.published_at <= NOW()
                  AND cs."Published" IS NOT NULL
                  AND cs."Published" <= NOW()
              )
          )
    )

    UNION ALL

    -- 8. Отсутствующие темы
    SELECT
        'empty_topics',
        'WARNING',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE topics IS NULL
       OR BTRIM(topics) = ''

    UNION ALL

    -- 9. Отсутствующие теги
    SELECT
        'empty_tags',
        'WARNING',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE tags IS NULL
       OR BTRIM(tags) = ''

    UNION ALL

    -- 10. Пустые элементы внутри списка тем
    SELECT
        'empty_topic_elements',
        'WARNING',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE topics IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM regexp_split_to_table(topics, ',') AS t(value)
          WHERE BTRIM(t.value) = ''
      )

    UNION ALL

    -- 11. Пустые элементы внутри списка тегов
    SELECT
        'empty_tag_elements',
        'WARNING',
        COUNT(*)
    FROM analytics.dm_materials
    WHERE tags IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM regexp_split_to_table(tags, ',') AS t(value)
          WHERE BTRIM(t.value) = ''
      )
)

-- Итоговый отчёт DQ
SELECT
    check_name,
    severity,
    failed_rows,
    CASE
        WHEN failed_rows = 0 THEN 'PASS'
        WHEN severity = 'WARNING' THEN 'WARN'
        ELSE 'FAIL'
    END AS status
FROM checks
ORDER BY
    CASE severity
        WHEN 'ERROR' THEN 1
        ELSE 2
    END,
    check_name;
