import psycopg2
from ingestion.config import get_db_connection_params


def get_connection():
    return psycopg2.connect(**get_db_connection_params())


def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.weather_daily (
                city TEXT NOT NULL,
                logical_date DATE NOT NULL,
                date DATE NOT NULL,
                temperature_2m_max DOUBLE PRECISION,
                temperature_2m_min DOUBLE PRECISION,
                precipitation_sum DOUBLE PRECISION,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
    conn.commit()


def load_city(conn, city_name: str, logical_date: str, payload: dict):
    daily = payload["daily"]
    with conn.cursor() as cur:
        # Idempotency mechanism: delete this city+date's rows before re-inserting.
        # Re-running the same logical_date always ends up with exactly one set
        # of rows for that city/date, never duplicates.
        cur.execute(
            "DELETE FROM raw.weather_daily WHERE city = %s AND logical_date = %s",
            (city_name, logical_date),
        )
        for i, date in enumerate(daily["time"]):
            cur.execute(
                """
                INSERT INTO raw.weather_daily
                    (city, logical_date, date, temperature_2m_max,
                     temperature_2m_min, precipitation_sum)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    city_name,
                    logical_date,
                    date,
                    daily["temperature_2m_max"][i],
                    daily["temperature_2m_min"][i],
                    daily["precipitation_sum"][i],
                ),
            )
    conn.commit()


def load_all(logical_date: str, extracted: dict[str, dict]):
    conn = get_connection()
    try:
        ensure_schema(conn)
        for city_name, payload in extracted.items():
            load_city(conn, city_name, logical_date, payload)
    finally:
        conn.close()