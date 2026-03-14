// api/api/sessions.js
// Controlador de sesiones del kiosko

const { getConnection } = require('../database/db');

// ── POST /api/sessions ─────────────────────────────────────────────────────
// Recibe la sesión completa al finalizar (desde Python via data_dispatcher)
const insertSession = (req, res) => {
    const {
        session_id, start_time, end_time, duration_seconds,
        language, places_visited, most_visited_place,
        total_questions, photo_taken, email_provided,
        visitor_email, completed_tour
    } = req.body;

    if (!session_id) {
        return res.status(400).json({ error: 'session_id requerido' });
    }

    const sql = `
        INSERT INTO sessions
          (session_id, start_time, end_time, duration_seconds,
           language, places_visited, most_visited_place,
           total_questions, photo_taken, email_provided,
           visitor_email, completed_tour)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
          end_time            = VALUES(end_time),
          duration_seconds    = VALUES(duration_seconds),
          places_visited      = VALUES(places_visited),
          most_visited_place  = VALUES(most_visited_place),
          total_questions     = VALUES(total_questions),
          photo_taken         = VALUES(photo_taken),
          email_provided      = VALUES(email_provided),
          visitor_email       = VALUES(visitor_email),
          completed_tour      = VALUES(completed_tour)
    `;
    const params = [
        session_id, start_time, end_time, duration_seconds || 0,
        language || 'en', places_visited || '', most_visited_place || '',
        total_questions || 0, photo_taken ? 1 : 0, email_provided ? 1 : 0,
        visitor_email || '', completed_tour ? 1 : 0
    ];

    const conn = getConnection();
    conn.connect();
    conn.query(sql, params, (err, results) => {
        conn.end();
        if (err) {
            console.error('[DB] Error insertSession:', err);
            return res.status(500).json({ error: err.message });
        }
        res.status(201).json({ ok: true, session_id });
    });
};

// ── GET /api/sessions ──────────────────────────────────────────────────────
// Retorna todas las sesiones (para dashboard local)
const getSessions = (req, res) => {
    const limit = parseInt(req.query.limit) || 100;
    const offset = parseInt(req.query.offset) || 0;

    const sql = `
        SELECT * FROM sessions
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    `;
    const conn = getConnection();
    conn.connect();
    conn.query(sql, [limit, offset], (err, results) => {
        conn.end();
        if (err) return res.status(500).json({ error: err.message });
        res.json(results);
    });
};

// ── GET /api/sessions/summary ──────────────────────────────────────────────
// Resumen estadístico para el dashboard
const getSummary = (req, res) => {
    const conn = getConnection();
    conn.connect();

    const q1 = `
        SELECT
            COUNT(*)                AS total_sessions,
            ROUND(AVG(duration_seconds), 1) AS avg_duration_sec,
            SUM(photo_taken)        AS total_photos,
            SUM(completed_tour)     AS completed_tours,
            SUM(total_questions)    AS total_questions
        FROM sessions
    `;
    const q2 = `
        SELECT language, COUNT(*) AS count
        FROM sessions
        GROUP BY language ORDER BY count DESC
    `;
    const q3 = `
        SELECT most_visited_place AS place, COUNT(*) AS count
        FROM sessions
        WHERE most_visited_place != ''
        GROUP BY most_visited_place ORDER BY count DESC LIMIT 10
    `;
    const q4 = `
        SELECT DATE(start_time) AS date, COUNT(*) AS sessions
        FROM sessions
        GROUP BY DATE(start_time) ORDER BY date DESC LIMIT 30
    `;

    let results = {};
    conn.query(q1, (e, r) => {
        if (e) { conn.end(); return res.status(500).json({ error: e.message }); }
        results.totals = r[0];
        conn.query(q2, (e2, r2) => {
            results.languages = r2 || [];
            conn.query(q3, (e3, r3) => {
                results.top_places = r3 || [];
                conn.query(q4, (e4, r4) => {
                    conn.end();
                    results.daily = r4 || [];
                    res.json(results);
                });
            });
        });
    });
};

// ── GET /api/sessions/:id ──────────────────────────────────────────────────
const getSessionById = (req, res) => {
    const { id } = req.params;
    const conn = getConnection();
    conn.connect();
    conn.query('SELECT * FROM sessions WHERE session_id = ?', [id], (err, r) => {
        conn.end();
        if (err) return res.status(500).json({ error: err.message });
        if (!r.length) return res.status(404).json({ error: 'Not found' });
        res.json(r[0]);
    });
};

// ── POST /api/events ───────────────────────────────────────────────────────
// Recibe eventos de telemetría puntuales
const insertEvent = (req, res) => {
    const { session_id, event_type, payload } = req.body;
    if (!session_id || !event_type) {
        return res.status(400).json({ error: 'session_id y event_type requeridos' });
    }
    const sql = `
        INSERT INTO events (session_id, event_type, payload)
        VALUES (?, ?, ?)
    `;
    const conn = getConnection();
    conn.connect();
    conn.query(sql, [session_id, event_type, JSON.stringify(payload || {})], (err) => {
        conn.end();
        if (err) return res.status(500).json({ error: err.message });
        res.status(201).json({ ok: true });
    });
};

module.exports = {
    insertSession,
    getSessions,
    getSummary,
    getSessionById,
    insertEvent,
};
