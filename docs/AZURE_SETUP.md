# 🔷 AZURE SETUP — Kiosko RAMon 2026

Guía para conectar el kiosko a Azure y empezar a recolectar datos de sesiones.

---

## Opción A: Azure Table Storage (Recomendada para empezar)

Azure Table Storage es una base de datos NoSQL simple y económica.
Perfecta para guardar sesiones y consultarlas desde Power BI.

### 1. Crear una cuenta de almacenamiento

1. Ve al portal de Azure: https://portal.azure.com
2. Crea un recurso → **Storage Account**
3. Configuración recomendada:
   - **Resource group**: `kiosko-ramon-rg`
   - **Storage account name**: `kioskodatamonterrey` (único global)
   - **Region**: `East US` o `South Central US` (más cercano a Monterrey)
   - **Performance**: Standard
   - **Redundancy**: LRS (Locally Redundant Storage) — suficiente para el proyecto
4. Clic en **Create**

### 2. Obtener la connection string

1. Entra a tu Storage Account → **Access keys** (menú izquierdo)
2. Copia la **Connection string** del Key 1
3. Pégala en tu archivo `.env`:

```env
AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=kioskodatamonterrey;AccountKey=TU_KEY==;EndpointSuffix=core.windows.net
AZURE_TABLE_NAME=KioskoSessions
```

### 3. La tabla se crea automáticamente

El código Python (`data/azure_client.py`) crea la tabla `KioskoSessions` 
automáticamente al arrancar si no existe.

### 4. Verificar los datos

En el portal de Azure → tu Storage Account → **Storage Explorer** →
Tables → KioskoSessions

---

## Opción B: Azure IoT Hub (Telemetría en tiempo real)

Usa esto si quieres ver eventos en tiempo real (lenguaje seleccionado, preguntas, etc.)
Más complejo pero da datos granulares.

### 1. Crear el IoT Hub

1. Crear recurso → **IoT Hub**
2. Nombre: `kiosko-ramon-hub`
3. Tier: **Free** (500 mensajes/día) o Basic para producción

### 2. Registrar el dispositivo

1. IoT Hub → **Devices** → New
2. Device ID: `kiosko-monterrey-01`
3. Copiar la **Primary connection string** del dispositivo

```env
AZURE_IOT_HUB_CONN_STR=HostName=kiosko-ramon-hub.azure-devices.net;DeviceId=kiosko-monterrey-01;SharedAccessKey=TU_KEY=
```

---

## Conectar Power BI a Azure Table Storage

1. Abrir Power BI Desktop
2. **Get Data** → **Azure** → **Azure Table Storage**
3. Cuenta de almacenamiento: `kioskodatamonterrey`
4. Llave de cuenta → desde Azure Portal → Access Keys
5. Seleccionar la tabla `KioskoSessions`

### Métricas sugeridas en Power BI:

| Visualización         | Campo(s)                          |
|-----------------------|-----------------------------------|
| KPI: Total sesiones   | COUNT(session_id)                 |
| Promedio de duración  | AVG(duration_seconds) / 60        |
| Idiomas (pie chart)   | language → count                  |
| Lugares más visitados | most_visited_place → count        |
| Preguntas totales     | SUM(total_questions)              |
| Timeline de sesiones  | start_time (agrupado por día)     |
| % tour completo       | SUM(completed_tour) / COUNT(*)    |

---

## Monitorear con Azure Application Insights (opcional)

1. Crear recurso → Application Insights
2. Obtener **Instrumentation Key**
3. Agregar al `.env` si decides integrar monitoreo de errores de la app Python

---

## Datos que se envían al final de cada sesión

```json
{
  "PartitionKey":       "MonterreyKiosko2026",
  "RowKey":             "<UUID de sesión>",
  "session_id":         "abc123-...",
  "start_time":         "2026-06-14T18:30:00Z",
  "end_time":           "2026-06-14T18:45:30Z",
  "duration_seconds":   930.5,
  "language":           "ja",
  "places_visited":     "barrio_antiguo,estadio_bbva,fashion_drive,santiago_pm",
  "most_visited_place": "estadio_bbva",
  "total_questions":    3,
  "photo_taken":        true,
  "email_provided":     true,
  "visitor_email":      "visitor@email.com",
  "completed_tour":     true
}
```

---

## Troubleshooting

| Error                          | Solución                                                        |
|--------------------------------|-----------------------------------------------------------------|
| `AuthorizationFailure`         | Verificar connection string en `.env`                          |
| `ResourceNotFound`             | La tabla no existe → se crea automáticamente al primer envío   |
| `azure-data-tables not found`  | `pip install azure-data-tables`                                |
| Sesión guardada localmente     | Ver carpeta `failed_uploads/` → se reenvían al próximo inicio  |
