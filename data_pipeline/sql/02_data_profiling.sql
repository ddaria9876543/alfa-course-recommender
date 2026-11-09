
-- =====================================================
-- ALFA-COURSE: EDA / DATA PROFILING
-- =====================================================

-- 1. Пользователи и прохождение курсов
SELECT
    COUNT(*) AS total_course_bindings,
    COUNT(DISTINCT "UserId") AS unique_users,
    COUNT(DISTINCT "CourseId") AS unique_courses,
    COUNT(*) FILTER (WHERE "IsPaid" = true) AS paid_bindings,
    COUNT(DISTINCT "UserId") FILTER (
        WHERE "IsPaid" = true
    ) AS paying_users,
    COUNT(*) FILTER (
        WHERE "IsCompleted" = true
    ) AS completed_bindings,
    ROUND(AVG("LessonsCompleted"), 2) AS avg_lessons_completed
FROM public."CourseUserBindings"
WHERE "IsDeleted" = false;


-- 2. Активность пользователей
SELECT
    "UserId",
    COUNT(DISTINCT "CourseId") AS courses_count,
    COUNT(*) FILTER (WHERE "IsPaid" = true) AS paid_count,
    COUNT(*) FILTER (WHERE "IsCompleted" = true) AS completed_count
FROM public."CourseUserBindings"
WHERE "IsDeleted" = false
GROUP BY "UserId"
ORDER BY courses_count DESC
LIMIT 10;


-- 3. Распределение оценок
SELECT
    "Value" AS rating,
    COUNT(*) AS ratings_count,
    COUNT(DISTINCT "UserId") AS unique_users
FROM public."UserRatings"
WHERE "IsDeleted" = false
GROUP BY "Value"
ORDER BY "Value";


-- 4. Заполненность каталога курсов
SELECT
    COUNT(*) AS total_courses,
    COUNT(*) FILTER (WHERE "IsDeleted" = false) AS active_courses,
    COUNT(*) FILTER (WHERE "Published" IS NOT NULL) AS published_courses,
    COUNT(*) FILTER (WHERE "Description" IS NULL) AS missing_description,
    COUNT(*) FILTER (WHERE "Cost" IS NULL) AS missing_cost,
    COUNT(*) FILTER (WHERE "Rating" IS NULL) AS missing_rating,
    MIN("Cost") AS min_cost,
    MAX("Cost") AS max_cost
FROM public."Courses";


-- 5. Заполненность статей
SELECT
    COUNT(*) AS total_articles,
    COUNT(*) FILTER (WHERE "IsDeleted" = false) AS active_articles,
    COUNT(*) FILTER (WHERE "IsPublic" = true) AS public_articles,
    COUNT(*) FILTER (WHERE "Description" IS NULL) AS missing_description,
    COUNT(*) FILTER (WHERE "Content" IS NULL) AS missing_content
FROM public."Articles";


-- 6. Темы, теги и связи с материалами
SELECT
    (SELECT COUNT(*) FROM public."Topics") AS topics_count,
    (SELECT COUNT(*) FROM public."Tags") AS tags_count,
    (SELECT COUNT(*) FROM public."ContentSettings") AS content_settings_count,
    (SELECT COUNT(*) FROM public."ContentSettingsTopics") AS topic_bindings_count,
    (SELECT COUNT(*) FROM public."ContentSettingsTags") AS tag_bindings_count,
    (SELECT COUNT(DISTINCT "ContentSettingsId")
     FROM public."ContentSettingsTopics") AS materials_with_topics,
    (SELECT COUNT(DISTINCT "ContentSettingsId")
     FROM public."ContentSettingsTags") AS materials_with_tags;


-- 7. Существующие рекомендательные связи
SELECT
    COUNT(*) AS total_recommendations,
    COUNT(DISTINCT "ItemId") AS distinct_items,
    COUNT(DISTINCT "CourseId") AS linked_courses
FROM public."RecommendedItems";


-- 8. Уточняем пользовательские типы данных
SELECT
    table_name,
    column_name,
    udt_name,
    domain_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('Courses', 'Articles', 'Topics')
  AND column_name IN ('Title', 'Description', 'Content', 'Url')
ORDER BY table_name, column_name;
