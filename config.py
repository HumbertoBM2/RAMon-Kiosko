"""
config.py
Kiosko RAMon - Configuración central del sistema
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# PANTALLA / DISPLAY
# ─────────────────────────────────────────────
SCREEN_WIDTH  = 900 #900
SCREEN_HEIGHT = 1000
FULLSCREEN    = False         # True para kiosko real con pantalla portrait
FPS           = 30

# ─────────────────────────────────────────────
# COLORES (RGB)
# ─────────────────────────────────────────────
COLOR_BG         = (0, 0, 0)
COLOR_WHITE      = (255, 255, 255)
COLOR_ACCENT     = (0, 180, 255)      # Azul cian Monterrey
COLOR_ACCENT2    = (255, 165, 0)      # Naranja RAMon
COLOR_GRAY       = (60, 60, 60)
COLOR_DARK_GRAY  = (30, 30, 30)
COLOR_SUCCESS    = (50, 200, 100)
COLOR_ERROR      = (220, 60, 60)

# ─────────────────────────────────────────────
# CÁMARA
# ─────────────────────────────────────────────
CAMERA_INDEX      = 0
CAMERA_WIDTH      = 640
CAMERA_HEIGHT     = 480
CAMERA_PREVIEW_W  = 200          # Tamaño del preview en pantalla
CAMERA_PREVIEW_H  = 150
# Límite inferior seguro para contenido (encima de la cámara + indicador de dedos)
SAFE_BOTTOM       = SCREEN_HEIGHT - CAMERA_PREVIEW_H - 30   # con 900 → 720

# ─────────────────────────────────────────────
# DETECCIÓN DE MANO (MediaPipe)
# ─────────────────────────────────────────────
WAVE_FINGERS_REQUIRED  = 5        # Dedos requeridos para saludo
WAVE_HOLD_SECONDS      = 1.5      # Segundos que debe mantenerse
GESTURE_HOLD_SECONDS   = 1.5      # Segundos para confirmar selección de dedo
GESTURE_COOLDOWN       = 0.8      # Cooldown entre gestos (segundos)
MIN_DETECTION_CONFIDENCE = 0.75
MIN_TRACKING_CONFIDENCE  = 0.75

# ─────────────────────────────────────────────
# IDIOMAS DISPONIBLES (Mundial 2026 - Monterrey)
# finger_count → label, code, display_name, tts_lang
# ─────────────────────────────────────────────
LANGUAGES = {
    1: {"code": "en", "name": "English",     "tts": "en"},
    2: {"code": "es", "name": "Español",     "tts": "es"},
    3: {"code": "fr", "name": "Français",    "tts": "fr"},   # Túnez
    4: {"code": "ja", "name": "日本語",       "tts": "ja"},   # Japón
    5: {"code": "ko", "name": "한국어",       "tts": "ko"},   # Corea del Sur
    6: {"code": "pl", "name": "Polski",      "tts": "pl"},   # Polonia
    7: {"code": "sv", "name": "Svenska",     "tts": "sv"},   # Suecia
    8: {"code": "uk", "name": "Українська",  "tts": "uk"},   # Ucrania
}
DEFAULT_LANGUAGE = "en"

# ─────────────────────────────────────────────
# LUGARES / PLACES
# ─────────────────────────────────────────────
PLACES = {
    1: {"id": "barrio_antiguo",  "icon": "[B]"},
    2: {"id": "fashion_drive",   "icon": "[F]"},
    3: {"id": "estadio_bbva",    "icon": "[E]"},
    4: {"id": "santiago_pm",     "icon": "[S]"},
}
TOTAL_PLACES = len(PLACES)
END_SESSION_FINGER = 5         # 5 dedos en menú de lugares = finalizar sesión

# ─────────────────────────────────────────────
# VOZ / VOICE
# ─────────────────────────────────────────────
TTS_ENGINE       = "gtts"      # "gtts" | "pyttsx3"
TTS_SPEED_GTTS   = 1.5
STT_ENGINE       = os.getenv("STT_ENGINE", "google")  # "whisper" | "google"  (whisper requiere ffmpeg + modelo descargado)
WHISPER_MODEL    = "base"      # tiny | base | small | medium
WHISPER_LANGUAGE = None        # None = auto-detect
AUDIO_SAMPLE_RATE = 16000
MAX_RECORD_SECONDS = 15        # Máximo de grabación para pregunta

# ─────────────────────────────────────────────
# OLLAMA (LLM LOCAL)
# ─────────────────────────────────────────────
OLLAMA_BASE_URL  = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL     = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT   = 60          # segundos
OLLAMA_SYSTEM_PROMPT_TEMPLATE = (
    "You are RAMon, the friendly tourism guide mascot for Nuevo León, México, "
    "during the FIFA World Cup 2026. You help international visitors discover "
    "amazing places in Monterrey. Answer warmly, briefly (2-4 sentences), "
    "and in the visitor's language ({lang}). "
    "Focus only on tourism, culture, food, and activities in Nuevo León. "
    "Currently talking about: {place}."
)

# ─────────────────────────────────────────────
# AZURE
# ─────────────────────────────────────────────
AZURE_CONNECTION_STRING  = os.getenv("AZURE_CONNECTION_STRING", "")
AZURE_TABLE_NAME         = os.getenv("AZURE_TABLE_NAME", "KioskoSessions")
AZURE_PARTITION_KEY      = "MonterreyKiosko2026"
AZURE_ENABLED            = bool(AZURE_CONNECTION_STRING)

# Azure IoT Hub (alternativa para telemetría en tiempo real)
AZURE_IOT_HUB_CONN_STR   = os.getenv("AZURE_IOT_HUB_CONN_STR", "")
AZURE_IOT_HUB_ENABLED    = bool(AZURE_IOT_HUB_CONN_STR)

# ─────────────────────────────────────────────
# BASE DE DATOS LOCAL (MySQL)
# ─────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "3306"))
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "MX00115462295")
DB_NAME     = os.getenv("DB_NAME", "kiosko_ramon")
DB_ENABLED  = os.getenv("DB_ENABLED", "true").lower() == "true"

# ─────────────────────────────────────────────
# NODE.JS API
# ─────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3001")
API_ENABLED  = os.getenv("API_ENABLED", "true").lower() == "true"

# ─────────────────────────────────────────────
# FOTOS / QR
# ─────────────────────────────────────────────
PHOTO_SAVE_DIR       = "captured_photos"
GOOGLE_FORMS_URL     = os.getenv(
    "GOOGLE_FORMS_URL",
    "https://forms.office.com/r/DdKraHJ5Qy"
)
EMAIL_SENDER         = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD       = os.getenv("EMAIL_PASSWORD", "")
EMAIL_SMTP_SERVER    = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT      = int(os.getenv("EMAIL_SMTP_PORT", "587"))
SEND_EMAIL_ENABLED   = bool(EMAIL_SENDER and EMAIL_PASSWORD)

# ─────────────────────────────────────────────
# ASSETS PATHS
# ─────────────────────────────────────────────
ASSETS_DIR          = "aesthetic"
BACKGROUNDS_DIR     = f"{ASSETS_DIR}/Fondos"
MASCOT_DIR          = f"{ASSETS_DIR}/Fotos"
PLACES_ASSETS_DIR   = f"{ASSETS_DIR}/Fondos"
FONTS_DIR           = "ui/assets/fonts"

# Archivos de mascota (apuntando a assets reales del equipo de arte)
RAMON_IDLE_VIDEO    = "aesthetic/Videos/intro.mp4"
RAMON_WAVE_GIF      = "aesthetic/Gifs/Idle 1_1giff.gif"
RAMON_TALK_GIF      = "aesthetic/Gifs/Idle 1_1giff.gif"
RAMON_PHOTO_IMAGE   = "aesthetic/Fotos/1.png"

# Fuente principal (si se agrega una fuente custom)
FONT_MAIN    = f"{FONTS_DIR}/main.ttf"     # Fallback → pygame default
FONT_TITLE   = f"{FONTS_DIR}/title.ttf"
