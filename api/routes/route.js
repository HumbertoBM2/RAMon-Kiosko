// api/routes/route.js
const express = require('express');
const sessions = require('../api/sessions');
const router = express.Router();

// ── Sesiones ───────────────────────────────────────────────────────────────
router.post('/api/sessions', sessions.insertSession);
router.get('/api/sessions', sessions.getSessions);
router.get('/api/sessions/summary', sessions.getSummary);
router.get('/api/sessions/:id', sessions.getSessionById);

// ── Eventos de telemetría ──────────────────────────────────────────────────
router.post('/api/events', sessions.insertEvent);

module.exports = router;
