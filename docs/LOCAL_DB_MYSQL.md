# 🗄️ BASE DE DATOS LOCAL + MINI DASHBOARD — Kiosko RAMon 2026

Guía para correr MySQL localmente, inicializar la base de datos,
arrancar la API de Node.js y visualizar los datos en un mini front-end.

---

## 1. Instalar MySQL

### Ubuntu / Debian
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation   # configurar contraseña root
```

### macOS
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### Windows
Descargar MySQL Installer desde: https://dev.mysql.com/downloads/installer/

---

## 2. Crear la base de datos y tablas

Conéctate a MySQL:
```bash
mysql -u root -p
```

Luego ejecuta:
```sql
CREATE DATABASE IF NOT EXISTS kiosko_ramon
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE kiosko_ramon;

-- Tabla principal de sesiones
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

-- Tabla de eventos de telemetría puntual
CREATE TABLE IF NOT EXISTS events (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    session_id  VARCHAR(36)  NOT NULL,
    event_type  VARCHAR(50)  NOT NULL,
    payload     JSON,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_event_type (event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Vista de resumen diario (útil para dashboards)
CREATE OR REPLACE VIEW daily_summary AS
SELECT
    DATE(start_time)         AS date,
    COUNT(*)                 AS total_sessions,
    ROUND(AVG(duration_seconds)/60, 1) AS avg_duration_min,
    SUM(photo_taken)         AS photos,
    SUM(completed_tour)      AS full_tours,
    SUM(total_questions)     AS questions
FROM sessions
GROUP BY DATE(start_time)
ORDER BY date DESC;
```

---

## 3. Configurar el archivo .env

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=kiosko_ramon
DB_ENABLED=true
```

---

## 4. Arrancar la API de Node.js

```bash
cd api/
npm install
npm run dev    # Con nodemon (auto-reload)
# ó
npm start      # Sin auto-reload
```

La API queda disponible en: **http://localhost:3001**

### Endpoints disponibles:

| Método | Ruta                      | Descripción                          |
|--------|---------------------------|--------------------------------------|
| GET    | `/`                       | Health check                         |
| POST   | `/api/sessions`           | Crear/actualizar sesión              |
| GET    | `/api/sessions`           | Listar sesiones (`?limit=&offset=`)  |
| GET    | `/api/sessions/summary`   | Resumen estadístico                  |
| GET    | `/api/sessions/:id`       | Sesión por ID                        |
| POST   | `/api/events`             | Registrar evento                     |

---

## 5. Mini Dashboard Local (HTML+JS)

Crea el archivo `api/dashboard/index.html` y ábrelo en el navegador.
Consume la API de Node.js en tiempo real.

> El archivo ya está incluido en `api/dashboard/index.html`

Para abrirlo:
1. Con la API corriendo en puerto 3001
2. Abre `api/dashboard/index.html` directamente en el navegador
   (o usa Live Server en VS Code)

---

## 6. Verificar datos en MySQL

```sql
-- Ver todas las sesiones
SELECT * FROM sessions ORDER BY created_at DESC LIMIT 20;

-- Idiomas más usados
SELECT language, COUNT(*) AS total
FROM sessions GROUP BY language ORDER BY total DESC;

-- Lugares más visitados
SELECT most_visited_place, COUNT(*) AS veces
FROM sessions
WHERE most_visited_place != ''
GROUP BY most_visited_place ORDER BY veces DESC;

-- Duración promedio de sesión (en minutos)
SELECT ROUND(AVG(duration_seconds)/60, 2) AS avg_minutes FROM sessions;

-- Sesiones del día de hoy
SELECT * FROM sessions
WHERE DATE(start_time) = CURDATE();
```

---

## 7. Hacer backup de los datos

```bash
# Exportar toda la base de datos
mysqldump -u root -p kiosko_ramon > backup_$(date +%Y%m%d).sql

# Importar backup
mysql -u root -p kiosko_ramon < backup_20260614.sql
```

---

## Troubleshooting

| Error                         | Solución                                              |
|-------------------------------|-------------------------------------------------------|
| `Access denied for user root` | Verificar contraseña en `.env` y `api/database/db.js` |
| `Cannot connect to MySQL`     | `sudo service mysql start` o `brew services start mysql` |
| `Table doesn't exist`         | Ejecutar el SQL de creación de tablas (paso 2)        |
| `python mysql not installed`  | `pip install mysql-connector-python`                  |
| Puerto 3001 en uso            | Cambiar en `api/app.js` → `const PORT = 3002`        |
