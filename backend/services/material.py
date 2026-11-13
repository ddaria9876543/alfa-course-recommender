
from psycopg.rows import dict_row

from backend.db.database import get_connection


def get_material_by_id(material_id: str):
    query = """
        SELECT
            material_id::text AS material_id,
            material_type,
            title,
            COALESCE(description, '') AS description,
            COALESCE(topics, '') AS topics,
            COALESCE(tags, '') AS tags,
            COALESCE(industries, '') AS industries,
            url,
            payment_status
        FROM analytics.dm_materials
        WHERE material_id::text = %s
        LIMIT 1
    """

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (material_id,))
            material = cursor.fetchone()

    return material
