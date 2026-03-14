"""
data/local_db.py
Gestión de base de datos MySQL local.
Guarda sesiones y métricas para el dashboard local (Node.js API + mini front).

Documentación de setup: docs/LOCAL_DB_MYSQL.md
"""
import json
from datetime import datetime
from config import (
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD,
    DB_NAME, DB_ENABLED
)

# SQL de creación de tablas (también en docs/LOCAL_DB_MYSQL.md)
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    session_id      VARCHAR(36)  NOT NULL UNIQUE,
    start_time      DATETIME     NOT NULL,
    end_time        DATETIME,
    duration_seconds FLOAT,
    language        VARCHAR(10),
    places_visited  TEXT,
    most_visited_place VARCHAR(50),
    total_questions INT          DEFAULT 0,
    photo_taken     TINYINT(1)   DEFAULT 0,
    email_provided  TINYINT(1)   DEFAULT 0,
    visitor_email   VARCHAR(255),
    completed_tour  TINYINT(1)   DEFAULT 0,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    session_id  VARCHAR(36)  NOT NULL,
    event_type  VARCHAR(50)  NOT NULL,
    payload     JSON,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_event_type (event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


class LocalDB:
    """
    Capa de acceso a MySQL local.

    Uso:
        db = LocalDB()
        db.save_session(session_dict)
        db.log_event("language_selected", {"session_id": ..., "language": "ja"})
    """

    def __init__(self):
        self._conn = None
        if DB_ENABLED:
            self._connect()

    def _connect(self):
        try:
            import mysql.connector
            self._conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                charset="utf8mb4",
                autocommit=True,
                connection_timeout=10,
            )
            self._ensure_tables()
            print("[DB] Conectado a MySQL local.")
        except ImportError:
            print("[DB] 'mysql-connector-python' no instalado. "
                  "pip install mysql-connector-python")
        except Exception as e:
            print(f"[DB] Error al conectar: {e}")
            self._conn = None

    def _ensure_tables(self):
        cursor = self._conn.cursor()
        cursor.execute(CREATE_SESSIONS_TABLE)
        cursor.execute(CREATE_EVENTS_TABLE)
        cursor.close()

    # ── API pública ────────────────────────────────────────────────

    def save_session(self, session_dict: dict) -> bool:
        """Inserta o actualiza una sesión completa."""
        if not self._ready():
            return False
        sql = """
            INSERT INTO sessions
                (session_id, start_time, end_time, duration_seconds,
                 language, places_visited, most_visited_place,
                 total_questions, photo_taken, email_provided,
                 visitor_email, completed_tour)
            VALUES
                (%(session_id)s, %(start_time)s, %(end_time)s, %(duration_seconds)s,
                 %(language)s, %(places_visited)s, %(most_visited_place)s,
                 %(total_questions)s, %(photo_taken)s, %(email_provided)s,
                 %(visitor_email)s, %(completed_tour)s)
            ON DUPLICATE KEY UPDATE
                end_time         = VALUES(end_time),
                duration_seconds = VALUES(duration_seconds),
                places_visited   = VALUES(places_visited),
                most_visited_place = VALUES(most_visited_place),
                total_questions  = VALUES(total_questions),
                photo_taken      = VALUES(photo_taken),
                email_provided   = VALUES(email_provided),
                visitor_email    = VALUES(visitor_email),
                completed_tour   = VALUES(completed_tour)
        """
        try:
            params = {
                "session_id":       session_dict["session_id"],
                "start_time":       session_dict["start_time"],
                "end_time":         session_dict.get("end_time"),
                "duration_seconds": session_dict.get("duration_seconds", 0),
                "language":         session_dict.get("language", "en"),
                "places_visited":   session_dict.get("places_visited", ""),
                "most_visited_place": session_dict.get("most_visited_place", ""),
                "total_questions":  session_dict.get("total_questions", 0),
                "photo_taken":      int(session_dict.get("photo_taken", False)),
                "email_provided":   int(session_dict.get("email_provided", False)),
                "visitor_email":    session_dict.get("visitor_email", ""),
                "completed_tour":   int(session_dict.get("completed_tour", False)),
            }
            cursor = self._conn.cursor()
            cursor.execute(sql, params)
            cursor.close()
            print(f"[DB] Sesión guardada: {session_dict['session_id']}")
            return True
        except Exception as e:
            print(f"[DB] Error al guardar sesión: {e}")
            return False

    def log_event(self, event_type: str, payload: dict) -> bool:
        """Registra un evento puntual (language_selected, place_visited, etc.)."""
        if not self._ready():
            return False
        sql = """
            INSERT INTO events (session_id, event_type, payload)
            VALUES (%s, %s, %s)
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, (
                payload.get("session_id", ""),
                event_type,
                json.dumps(payload, ensure_ascii=False),
            ))
            cursor.close()
            return True
        except Exception as e:
            print(f"[DB] Error al registrar evento: {e}")
            return False

    def get_summary(self) -> dict:
        """Retorna métricas agregadas para el dashboard."""
        if not self._ready():
            return {}
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    COUNT(*)                         AS total_sessions,
                    AVG(duration_seconds)            AS avg_duration,
                    SUM(photo_taken)                 AS photos_taken,
                    SUM(completed_tour)              AS completed_tours,
                    SUM(total_questions)             AS total_questions,
                    MIN(start_time)                  AS first_session,
                    MAX(start_time)                  AS last_session
                FROM sessions
            """)
            row = cursor.fetchone()

            cursor.execute("""
                SELECT language, COUNT(*) AS count
                FROM sessions
                GROUP BY language
                ORDER BY count DESC
            """)
            langs = cursor.fetchall()

            cursor.execute("""
                SELECT most_visited_place AS place, COUNT(*) AS count
                FROM sessions
                WHERE most_visited_place != ''
                GROUP BY most_visited_place
                ORDER BY count DESC
                LIMIT 10
            """)
            places = cursor.fetchall()
            cursor.close()

            return {
                "totals":          row,
                "languages":       langs,
                "top_places":      places,
            }
        except Exception as e:
            print(f"[DB] Error en summary: {e}")
            return {}

    def close(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass

    def _ready(self) -> bool:
        if not DB_ENABLED or self._conn is None:
            return False
        try:
            self._conn.ping(reconnect=True, attempts=2, delay=1)
            return True
        except Exception:
            return False
