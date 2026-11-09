
-- ALFA-COURSE: проверка каталога перед созданием витрины

-- 1. Темы с количеством связанных материалов
SELECT
    t."Title"::text AS topic,
    COUNT(DISTINCT cst."ContentSettingsId") AS materials_count
FROM public."Topics" t
LEFT JOIN public."ContentSettingsTopics" cst
    ON cst."TopicId" = t."Id"
WHERE t."IsDeleted" = false
GROUP BY t."Id", t."Title"
ORDER BY materials_count DESC
LIMIT 20;


-- 2. Теги с количеством связанных материалов
SELECT
    t."Title"::text AS tag,
    COUNT(DISTINCT cst."ContentSettingsId") AS materials_count
FROM public."Tags" t
LEFT JOIN public."ContentSettingsTags" cst
    ON cst."TagId" = t."Id"
WHERE t."IsDeleted" = false
GROUP BY t."Id", t."Title"
ORDER BY materials_count DESC
LIMIT 20;


-- 3. Отрасли бизнеса
SELECT
    i."Title"::text AS industry,
    COUNT(DISTINCT csi."ContentSettingsId") AS materials_count
FROM public."Industries" i
LEFT JOIN public."ContentSettingsIndustries" csi
    ON csi."IndustryId" = i."Id"
WHERE i."IsDeleted" = false
GROUP BY i."Id", i."Title"
ORDER BY materials_count DESC;


-- 4. Статусы образовательных материалов
SELECT
    s."Title"::text AS status,
    COUNT(*) AS materials_count
FROM public."ContentSettings" cs
JOIN public."Statuses" s
    ON s."Id" = cs."StatusId"
GROUP BY s."Id", s."Title"
ORDER BY materials_count DESC;


-- 5. Опубликованные материалы по типам
SELECT
    CASE
        WHEN a."Id" IS NOT NULL THEN 'article'
        WHEN c."Id" IS NOT NULL THEN 'course'
        WHEN d."Id" IS NOT NULL THEN 'document'
        WHEN w."Id" IS NOT NULL THEN 'webinar'
        WHEN p."Id" IS NOT NULL THEN 'podcast'
        ELSE 'unknown'
    END AS material_type,
    COUNT(*) AS total,
    COUNT(*) FILTER (
        WHERE cs."Published" IS NOT NULL
          AND cs."Published" <= NOW()
          AND cs."IsDeleted" = false
    ) AS published_settings
FROM public."ContentSettings" cs
LEFT JOIN public."Articles" a ON a."Id" = cs."EntityId"
LEFT JOIN public."Courses" c ON c."Id" = cs."EntityId"
LEFT JOIN public."Documents" d ON d."Id" = cs."EntityId"
LEFT JOIN public."Webinars" w ON w."Id" = cs."EntityId"
LEFT JOIN public."Podcasts" p ON p."Id" = cs."EntityId"
GROUP BY 1
ORDER BY total DESC;


-- 6. Тарифы и стоимость курсов
SELECT
    c."Title"::text AS course,
    c."Cost",
    c."HasTrial",
    c."IsClosed",
    c."Published",
    COUNT(ctb.*) AS tariff_bindings
FROM public."Courses" c
LEFT JOIN public."CourseTariffBindings" ctb
    ON ctb."CourseId" = c."Id"
GROUP BY c."Id", c."Title", c."Cost",
         c."HasTrial", c."IsClosed", c."Published"
ORDER BY c."Cost" DESC NULLS LAST
LIMIT 40;
