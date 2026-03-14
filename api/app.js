// api/app.js
// API Node.js del Kiosko RAMon — Monterrey 2026
require('dotenv').config();

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const router = require('./routes/route');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(router);

// Health check
app.get('/', (req, res) => {
    res.json({ status: 'ok', service: 'Kiosko RAMon API', version: '1.0.0' });
});

app.listen(PORT, () => {
    console.log(`🤖 Kiosko RAMon API corriendo en puerto ${PORT}`);
});
