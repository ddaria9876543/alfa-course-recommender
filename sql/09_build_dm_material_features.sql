
CREATE OR REPLACE VIEW analytics.dm_material_features AS
WITH normalized AS (
    SELECT
        m.material_id,
        m.material_type,
        m.title,
        m.topics,
        m.tags,
        m.industries,
        m.payment_status,

        ARRAY(
            SELECT DISTINCT BTRIM(value)
            FROM regexp_split_to_table(
                COALESCE(m.industries, ''),
                ','
            ) AS value
            WHERE BTRIM(value) IN (
                'ECom',
                'Розница',
                'Услуги',
                'Строительство и недвижимость',
                'HoReСa',
                'Транспорт и логистика',
                'B2B',
                'Производство',
                'Оптовая торговля',
                'B2G'
            )
            ORDER BY BTRIM(value)
        ) AS industry_tags,

        CASE
            WHEN m.material_type = 'course'
                 AND m.industries ILIKE '%Без опыта%'
                THEN 'beginner'

            WHEN m.material_type = 'course'
                 AND m.industries ILIKE '%С опытом%'
                THEN 'experienced'

            ELSE NULL
        END AS audience_experience,

        CASE
            WHEN m.industries LIKE '%NEW%'
                THEN TRUE
            ELSE FALSE
        END AS is_new

    FROM analytics.dm_materials m
)
SELECT *
FROM normalized;
