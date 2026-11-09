
-- 1. Статусы материалов по типам
SELECT
    CASE
        WHEN a."Id" IS NOT NULL THEN 'article'
        WHEN c."Id" IS NOT NULL THEN 'course'
        WHEN d."Id" IS NOT NULL THEN 'document'
        WHEN w."Id" IS NOT NULL THEN 'webinar'
        WHEN p."Id" IS NOT NULL THEN 'podcast'
        ELSE 'unknown'
    END AS material_type,
    s."Title"::text AS status,
    COUNT(*) AS materials_count,
    COUNT(*) FILTER (
        WHERE cs."Published" IS NULL
    ) AS missing_publication_date,
    COUNT(*) FILTER (
        WHERE cs."Published" > NOW()
    ) AS future_publication_date
FROM public."ContentSettings" cs
JOIN public."Statuses" s
    ON s."Id" = cs."StatusId"
LEFT JOIN public."Articles" a
    ON a."Id" = cs."EntityId"
LEFT JOIN public."Courses" c
    ON c."Id" = cs."EntityId"
LEFT JOIN public."Documents" d
    ON d."Id" = cs."EntityId"
LEFT JOIN public."Webinars" w
    ON w."Id" = cs."EntityId"
LEFT JOIN public."Podcasts" p
    ON p."Id" = cs."EntityId"
GROUP BY 1, 2
ORDER BY 1, 2;

-- 2. Проверка доступности документов
SELECT
    s."Title"::text AS status,
    COUNT(*) AS total,
    COUNT(*) FILTER (
        WHERE d."IsDeleted"
    ) AS deleted,
    COUNT(*) FILTER (
        WHERE d."Published" IS NOT NULL
    ) AS has_published_date,
    COUNT(*) FILTER (
        WHERE d."Published" <= NOW()
    ) AS published_by_now
FROM public."Documents" d
JOIN public."Statuses" s
    ON s."Id" = d."StatusId"
GROUP BY 1
ORDER BY 1;

-- 3. Проверка стоимости курсов
SELECT
    COUNT(*) AS total,
    COUNT(*) FILTER (
        WHERE "Cost" > 0
    ) AS positive_cost,
    COUNT(*) FILTER (
        WHERE "Cost" = 0
    ) AS zero_cost,
    COUNT(*) FILTER (
        WHERE "Cost" IS NULL
    ) AS unknown_cost,
    COUNT(*) FILTER (
        WHERE "IsClosed"
    ) AS closed_courses
FROM public."Courses";
