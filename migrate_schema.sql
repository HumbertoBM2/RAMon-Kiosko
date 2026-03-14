-- migrate_schema.sql
-- Alinea la tabla sessions con las columnas que usa la API Node.js
USE kiosko_ramon;

-- 1. duration_secs → duration_seconds (float para decimales)
ALTER TABLE sessions CHANGE duration_secs duration_seconds FLOAT DEFAULT 0;

-- 2. places_visited: de JSON a VARCHAR (la API manda string CSV)
ALTER TABLE sessions MODIFY places_visited VARCHAR(500) DEFAULT '';

-- 3. questions_asked → total_questions
ALTER TABLE sessions CHANGE questions_asked total_questions INT DEFAULT 0;

-- 4. email → visitor_email
ALTER TABLE sessions CHANGE email visitor_email VARCHAR(255) DEFAULT '';

-- 5. Columnas faltantes
ALTER TABLE sessions
  ADD COLUMN most_visited_place VARCHAR(100) DEFAULT '' AFTER places_visited,
  ADD COLUMN email_provided     TINYINT(1)   DEFAULT 0  AFTER visitor_email,
  ADD COLUMN completed_tour     TINYINT(1)   DEFAULT 0  AFTER email_provided;

-- 6. Recrear la view con los nombres correctos
CREATE OR REPLACE VIEW v_session_summary AS
SELECT
  DATE(start_time)           AS day,
  language,
  COUNT(*)                   AS total_sessions,
  AVG(duration_seconds)      AS avg_duration_secs,
  SUM(total_questions)       AS total_questions,
  SUM(photo_taken)           AS total_photos,
  SUM(completed_tour)        AS completed_tours
FROM sessions
GROUP BY DATE(start_time), language;

-- Verificar
DESCRIBE sessions;
SHOW FULL COLUMNS FROM sessions;
