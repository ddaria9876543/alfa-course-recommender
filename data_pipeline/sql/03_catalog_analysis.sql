
-- ALFA-COURSE: исследование каталога

-- 1. Структура таблиц с текстами и тематическими связями
SELECT
    table_name,
    column_name,
    data_type,
    udt_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'ArticleEmbedItems',
      'LessonEmbedItems',
      'ContentSettings',
      'ContentSettingsIndustries',
      'Industries',
      'Statuses'
  )
ORDER BY table_name, ordinal_position;


-- 2. Как ContentSettings связаны с материалами
SELECT
    COUNT(*) AS total_settings,
    COUNT(DISTINCT "EntityId") AS unique_entities,
    COUNT(DISTINCT "EntityTypeId") AS entity_types
FROM public."ContentSettings";


-- 3. Какие типы сущностей представлены
SELECT
    "EntityTypeId",
    COUNT(*) AS records_count
FROM public."ContentSettings"
GROUP BY "EntityTypeId"
ORDER BY records_count DESC;


-- 4. Проверяем связь ContentSettings с каталогом
SELECT
    COUNT(*) FILTER (WHERE a."Id" IS NOT NULL) AS linked_articles,
    COUNT(*) FILTER (WHERE c."Id" IS NOT NULL) AS linked_courses,
    COUNT(*) FILTER (WHERE d."Id" IS NOT NULL) AS linked_documents,
    COUNT(*) FILTER (WHERE w."Id" IS NOT NULL) AS linked_webinars,
    COUNT(*) FILTER (
        WHERE a."Id" IS NULL
          AND c."Id" IS NULL
          AND d."Id" IS NULL
          AND w."Id" IS NULL
    ) AS other_entities
FROM public."ContentSettings" cs
LEFT JOIN public."Articles" a ON a."Id" = cs."EntityId"
LEFT JOIN public."Courses" c ON c."Id" = cs."EntityId"
LEFT JOIN public."Documents" d ON d."Id" = cs."EntityId"
LEFT JOIN public."Webinars" w ON w."Id" = cs."EntityId";


-- 5. Примеры названий и описаний курсов
SELECT
    "Title",
    LEFT("Description"::text, 150) AS description_sample,
    "Cost",
    "IsClosed",
    "Published"
FROM public."Courses"
LIMIT 10;


-- 6. Примеры названий и описаний статей
SELECT
    "Title",
    LEFT("Description"::text, 150) AS description_sample,
    "IsPublic",
    "IsClosed"
FROM public."Articles"
LIMIT 10;


-- 7. Проверяем основные типы текстовых блоков статей
SELECT
    "Type",
    COUNT(*) AS blocks_count
FROM public."ArticleEmbedItems"
GROUP BY "Type"
ORDER BY blocks_count DESC;
