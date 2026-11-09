
-- Исследование структуры ключевых таблиц Альфа-Курса
-- Первый этап EDA

SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'Courses',
      'Articles',
      'Lessons',
      'Documents',
      'ContentSettings',
      'ContentSettingsTopics',
      'ContentSettingsTags',
      'CourseUserBindings',
      'CourseUserLessonBindings',
      'UserRatings',
      'RecommendedItems',
      'Topics',
      'Tags'
  )
ORDER BY table_name, ordinal_position;
