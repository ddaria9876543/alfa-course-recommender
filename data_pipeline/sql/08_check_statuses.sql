
-- Проверяем соответствие статусов исходных материалов и ContentSettings

WITH materials AS (
    SELECT
        'article' AS material_type,
        "Id" AS material_id,
        "StatusId" AS status_id
    FROM public."Articles"

    UNION ALL

    SELECT
        'course',
        "Id",
        "StatusId"
    FROM public."Courses"

    UNION ALL

    SELECT
        'document',
        "Id",
        "StatusId"
    FROM public."Documents"
)

SELECT
    m.material_type,
    ss."Title"::text AS source_status,
    css."Title"::text AS settings_status,
    COUNT(*) AS materials_count

FROM materials m

JOIN public."ContentSettings" cs
    ON cs."EntityId" = m.material_id

JOIN public."Statuses" ss
    ON ss."Id" = m.status_id

JOIN public."Statuses" css
    ON css."Id" = cs."StatusId"

GROUP BY
    m.material_type,
    ss."Title",
    css."Title"

ORDER BY
    m.material_type,
    materials_count DESC;
