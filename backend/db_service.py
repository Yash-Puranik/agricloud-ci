from datetime import datetime
import os
import sqlite3
from config import Config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "agricloud.db")


def init_sqlite():
  with sqlite3.connect(SQLITE_PATH) as conn:
    conn.execute("""
            CREATE TABLE IF NOT EXISTS agri_telemetry_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                node_id TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                soil_moisture REAL NOT NULL,
                crop_queried TEXT NOT NULL,
                suitability_verdict TEXT NOT NULL,
                advisory_text TEXT NOT NULL,
                is_satellite_fallback INTEGER DEFAULT 0
            );
        """)
    conn.commit()


init_sqlite()


def get_pg_connection():
  import psycopg2

  return psycopg2.connect(
      host=Config.DB_HOST,
      port=Config.DB_PORT,
      dbname=Config.DB_NAME,
      user=Config.DB_USER,
      password=Config.DB_PASSWORD,
      connect_timeout=1,
  )


def log_telemetry_event(
    node_id: str,
    temp: float,
    hum: float,
    soil: float,
    crop: str,
    verdict: str,
    advisory: str,
    is_fallback: bool = False,
) -> bool:

  try:
    with get_pg_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
            """
                    INSERT INTO agri_telemetry_logs
                    (node_id, temperature, humidity, soil_moisture, crop_queried, suitability_verdict, advisory_text, is_satellite_fallback)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
            (
                node_id,
                temp,
                hum,
                soil,
                crop,
                verdict,
                advisory,
                bool(is_fallback),
            ),
        )
        conn.commit()
    return True
  except Exception:
    with sqlite3.connect(SQLITE_PATH) as conn:
      conn.execute(
          """
                INSERT INTO agri_telemetry_logs
                (timestamp, node_id, temperature, humidity, soil_moisture, crop_queried, suitability_verdict, advisory_text, is_satellite_fallback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
          (
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              node_id,
              float(temp),
              float(hum),
              float(soil),
              crop,
              verdict,
              advisory,
              1 if is_fallback else 0,
          ),
      )
      conn.commit()
    return True


def get_recent_logs(limit: int = 20) -> list:
  try:
    from psycopg2.extras import RealDictCursor

    with get_pg_connection() as conn:
      with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
                    SELECT id, timestamp, node_id, temperature, humidity, soil_moisture,
                           crop_queried, suitability_verdict, advisory_text, is_satellite_fallback
                    FROM agri_telemetry_logs
                    ORDER BY id DESC
                    LIMIT %s;
                """,
            (limit,),
        )
        rows = cur.fetchall()
        for r in rows:
          if r.get("timestamp"):
            r["timestamp"] = str(r["timestamp"])
        return list(rows)
  except Exception:
    with sqlite3.connect(SQLITE_PATH) as conn:
      conn.row_factory = sqlite3.Row
      cur = conn.cursor()
      cur.execute(
          """
                SELECT id, timestamp, node_id, temperature, humidity, soil_moisture,
                       crop_queried, suitability_verdict, advisory_text, is_satellite_fallback
                FROM agri_telemetry_logs
                ORDER BY id DESC
                LIMIT ?;
            """,
          (limit,),
      )
      rows = [dict(row) for row in cur.fetchall()]
      return rows