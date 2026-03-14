// api/database/db.js
const mysql = require('mysql2');

function getConnection() {
    const connection = mysql.createConnection({
        host: process.env.DB_HOST || 'localhost',
        port: process.env.DB_PORT || 3306,
        user: process.env.DB_USER || 'root',
        password: process.env.DB_PASSWORD || 'password',   // ← Cambiar
        database: process.env.DB_NAME || 'kiosko_ramon',
        charset: 'utf8mb4',
    });
    return connection;
}

module.exports = { getConnection };
