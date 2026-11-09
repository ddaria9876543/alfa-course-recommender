
-- =====================================================
-- ALFA-COURSE: диагностика пустой витрины
-- =====================================================

WITH materials AS (
    SELECT
        'article' AS material_type,
        "Id" AS material_id,
        "StatusId" AS status_id,
        "Published" AS published_at,
        "IsDeleted" AS is_deleted,
        "IsClosed" AS is_closed,
        "IsPublic" AS is_public
    FROM public."Articles"

    UNION ALL

    SELECT
        'course',
        "Id",
        "StatusId",
        "Published",
        "IsDeleted",
        "IsClosed",
        true
    FROM public."Courses"

    UNION ALL

    SELECT
        'document',
        "Id",
        "StatusId",
        "Published",
        "IsDeleted",
        false,
        true
    FROM public."Documents"
),

checks AS (
    SELECT
        m.*,
        cs."IsDeleted" AS settings_deleted,
        cs."Published" AS settings_published_at,
        ss."Title"::text AS source_status,
        css."Title"::text AS settings_status

    FROM materials m

    JOIN public."ContentSettings" cs
        ON cs."EntityId" = m.material_id

    JOIN public."Statuses" ss
        ON ss."Id" = m.status_id

    JOIN public."Statuses" css
        ON css."Id" = cs."StatusId"
)

SELECT
    material_type,

    COUNT(*) AS after_joins,

    COUNT(*) FILTER (
        WHERE is_deleted = false
          AND settings_deleted = false
    ) AS after_deleted_filter,

    COUNT(*) FILTER (
        WHERE is_deleted = false
          AND settings_deleted = false
          AND is_closed = false
          AND is_public = true
    ) AS after_access_filter,

    COUNT(*) FILTER (
        WHERE is_deleted = false
          AND settings_deleted = false
          AND is_closed = false
          AND is_public = true
          AND settings_status = 'Опубликовано'
          AND source_status = 'Опубликовано'
    ) AS after_status_filter,

    COUNT(*) FILTER (
        WHERE is_deleted = false
          AND settings_deleted = false
          AND is_closed = false
          AND is_public = true
          AND settings_status = 'Опубликовано'
          AND source_status = 'Опубликовано'
          AND (
              material_type = 'document'
              OR (
                  published_at IS NOT NULL
                  AND published_at <= NOW()
                  AND settings_published_at IS NOT NULL
                  AND settings_published_at <= NOW()
              )
          )
    ) AS after_publication_filter

FROM checks
GROUP BY material_type
ORDER BY material_type;
