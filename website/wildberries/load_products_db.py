from data.database import get_connection


def _load_products() -> list[dict]:
    """достаём список товаров из базы данных для проверки цен."""

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            p.id,
            p.url,
            (SELECT MIN(price_now) FROM price_history WHERE product_id = p.id) AS price_min,
            (SELECT MAX(price_now) FROM price_history WHERE product_id = p.id) AS price_max
        FROM products AS p
        """
    )
    raw_products = cursor.fetchall()
    conn.close()

    # sqlite3.Row не поддерживает .get(), поэтому преобразуем к обычным dict.
    return [dict(row) for row in raw_products]
