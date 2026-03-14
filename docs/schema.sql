-- schema.sql — Kiosko RAMon 2026
-- Uso: mysql -u root -p < docs/schema.sql

CREATE DATABASE IF NOT EXISTS kiosko_ramon
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE kiosko_ramon;

-- ── Tabla de sesiones ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
  id              INT           PRIMARY KEY AUTO_INCREMENT,
  session_id      VARCHAR(64)   NOT NULL UNIQUE,
  language        VARCHAR(10)   NOT NULL DEFAULT 'es',
  start_time      DATETIME      NOT NULL,
  end_time        DATETIME,
  duration_secs   INT,
  places_visited  JSON,          -- array de IDs visitados
  questions_asked INT           DEFAULT 0,
  photo_taken     TINYINT(1)    DEFAULT 0,
  email           VARCHAR(255),
  created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Tabla de eventos individuales ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
  id          INT           PRIMARY KEY AUTO_INCREMENT,
  session_id  VARCHAR(64)   NOT NULL,
  event_type  VARCHAR(50)   NOT NULL,  -- e.g. 'gesture', 'place_visit', 'qa', 'photo'
  payload     JSON,
  ts          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Vista resumen para el dashboard ───────────────────────────────────────
CREATE OR REPLACE VIEW v_session_summary AS
SELECT
  DATE(start_time)           AS day,
  language,
  COUNT(*)                   AS total_sessions,
  AVG(duration_secs)         AS avg_duration_secs,
  SUM(questions_asked)       AS total_questions,
  SUM(photo_taken)           AS total_photos
FROM sessions
GROUP BY DATE(start_time), language;
