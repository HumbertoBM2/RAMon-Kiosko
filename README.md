# Kiosko RAMon — Interactive Tourism Kiosk for FIFA World Cup 2026

An interactive tourism kiosk built for the FIFA World Cup 2026 hosting city of Monterrey, Nuevo León, México. Visitors navigate through local landmarks using hand gestures, explore each destination in their native language, and ask RAMon — the kiosk mascot — questions answered in real time by a locally-running large language model.

Developed as a Digital Transformation capstone project in collaboration with **Woohoo Agency** (Tec de Monterrey).

---

## Overview

RAMon is a touchless, gesture-driven kiosk designed for high-traffic public spaces. A webcam detects hand gestures via MediaPipe. Visitors select a language, browse four landmark destinations, ask spoken questions (answered by Ollama + llama3.2 running entirely on-device), and optionally take a photo and submit feedback. Session analytics are logged locally to MySQL and optionally forwarded to Azure Table Storage.

### Interaction flow

```
Greeting gesture (5 fingers, 2 s)
        |
Language selection (1–8 fingers)
        |
RAMon welcome screen (intro video)
        |
Places menu (1–4 fingers)  <--------------------------+
        |                                              |
Place detail (photos, description, highlights)         |
        |                                              |
Voice Q&A with RAMon (STT + Ollama)                    |
        |                                              |
  1 finger  -> ask again                               |
  2 fingers -> back to menu  -------------------------+
        |
  5 fingers on menu -> end tour
        |
Photo-op screen + feedback QR
        |
Farewell + session summary
```

---

## Features

- Touchless gesture navigation via MediaPipe hand detection
- 8 supported languages (English, Spanish, French, Japanese, Korean, Polish, Swedish, Ukrainian)
- Voice Q&A powered by Ollama (llama3.2, fully offline after setup)
- Speech recognition via Google STT or OpenAI Whisper
- Text-to-speech via gTTS (online) or pyttsx3 (offline fallback)
- Session analytics persisted locally (MySQL) with optional Azure Table Storage sync
- Photo-op screen with QR code linking to a feedback form
- Privacy notice screen with QR code for the privacy policy
- Fullscreen kiosk mode at 900x900 with pygame.SCALED

---

## Landmarks covered

| # | Place | Location |
|---|-------|----------|
| 1 | Barrio Antiguo | Historic downtown district |
| 2 | Fashion Drive | Premium retail and entertainment |
| 3 | Estadio BBVA | Home of C.F. Monterrey |
| 4 | Santiago Pueblo Magico | Mountain town south of the city |

---

## Languages

Selections correspond to national teams playing at Estadio BBVA during the 2026 World Cup:

| Finger | Language | Region |
|--------|----------|--------|
| 1 | English | International |
| 2 | Espanol | Mexico (host) |
| 3 | Francais | Tunisia |
| 4 | Nihongo | Japan |
| 5 | Hangugeo | South Korea |
| 6 | Polski | Poland |
| 7 | Svenska | Sweden |
| 8 | Ukrainska | Ukraine |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| UI and main loop | Python 3.10 + Pygame |
| Hand detection | MediaPipe + OpenCV |
| Speech to text | Google STT (default) / OpenAI Whisper (local) |
| Text to speech | gTTS / pyttsx3 |
| LLM | Ollama (llama3.2) |
| REST API | Node.js + Express |
| Local database | MySQL 8 |
| Optional cloud | Azure Table Storage + Azure IoT Hub |
| Dashboard | Plain HTML + JS (served locally) |

---

## Requirements

### Hardware

- x86_64 or ARM64 machine (tested on Ubuntu 22.04)
- Webcam (built-in or USB)
- Microphone
- Speakers or audio output
- 8 GB RAM minimum (16 GB recommended — llama3.2 loads ~2.6 GB into RAM)
- 5 GB free disk space for the Ollama model

### Software

- Python 3.10 or later
- Node.js 18 or later
- MySQL 8.0 or later
- ffmpeg, portaudio19-dev, espeak (Ubuntu system packages detailed below)
- Ollama (installed via official script, see Installation)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/kiosko-ramon.git
cd kiosko-ramon
```

### 2. Install system dependencies (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install -y ffmpeg portaudio19-dev espeak python3-pip
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Open .env and fill in your MySQL password and any other values
```

See the Configuration section below for a full description of each variable.

### 5. Create the MySQL database

```bash
mysql -u root -p < SQL_Script_For_The_DB.sql
```


![mano18](Screenshots/edr.jpg)




### 6. Install and start Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
# Enable as a system service so it starts automatically on boot:
sudo systemctl enable --now ollama
```

The first question asked to RAMon will take 8-15 seconds while the model loads into RAM. Subsequent responses are fast.

### 7. Install and start the Node.js API

```bash
cd api/
npm install
cp ../.env.example .env    # or copy your filled .env
npm start                  # runs on port 3001 by default
cd ..
```

### 8. Run the kiosk

```bash
python main.py
```

---

## Configuration

Copy `.env.example` to `.env` and fill in your values. The file is excluded from version control by `.gitignore` — never commit it.

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL host | localhost |
| `DB_PORT` | MySQL port | 3306 |
| `DB_USER` | MySQL user | root |
| `DB_PASSWORD` | MySQL password | (required) |
| `DB_NAME` | Database name | kiosko_ramon |
| `DB_ENABLED` | Enable local DB logging | true |
| `API_BASE_URL` | Node.js API base URL | http://localhost:3001 |
| `API_ENABLED` | Enable API sync | true |
| `OLLAMA_BASE_URL` | Ollama server URL | http://localhost:11434 |
| `OLLAMA_MODEL` | Model name | llama3.2 |
| `AZURE_CONNECTION_STRING` | Azure Storage connection string | (optional) |
| `AZURE_TABLE_NAME` | Azure table name | KioskoSessions |
| `AZURE_IOT_HUB_CONN_STR` | Azure IoT Hub connection string | (optional) |
| `EMAIL_SENDER` | Sender address for email feature | (optional) |
| `EMAIL_PASSWORD` | App password for email sender | (optional) |

---

## Project structure

```
kiosko-ramon/
├── main.py                    # Entry point
├── config.py                  # Central configuration (reads .env)
├── requirements.txt
├── .env.example               # Template — copy to .env
├── SQL_Script_For_The_DB.sql  # Database schema
│
├── core/
│   ├── hand_detector.py       # MediaPipe hand detection
│   ├── gesture_engine.py      # Gesture timing and confirmation logic
│   └── session_manager.py     # Session data collection
│
├── ui/
│   ├── kiosk_app.py           # Main loop and screen state machine
│   ├── renderer.py            # Media engine (image / video / gif / color)
│   └── screens/
│       ├── welcome_screen.py  # Greeting gesture detection
│       ├── language_screen.py # Language selection
│       ├── intro_screen.py    # RAMon welcome video
│       ├── places_menu.py     # Landmark menu
│       ├── place_detail.py    # Individual landmark info
│       ├── qa_screen.py       # Voice Q&A with Ollama
│       ├── photo_screen.py    # Photo-op + feedback QR
│       ├── privacy_screen.py  # Privacy notice + QR
│       └── farewell_screen.py # Session summary
│
├── voice/
│   ├── text_to_speech.py      # TTS abstraction (gTTS / pyttsx3)
│   ├── speech_to_text.py      # STT abstraction (Google / Whisper)
│   └── ollama_client.py       # Ollama HTTP client (sync + async)
│
├── data/
│   ├── places_content.py      # Multilingual landmark content
│   ├── azure_client.py        # Azure Table Storage + IoT Hub
│   ├── local_db.py            # MySQL session logging
│   └── data_dispatcher.py     # Fan-out to all storage backends
│
├── api/                       # Node.js REST API
│   ├── app.js
│   ├── package.json
│   ├── database/db.js
│   ├── routes/route.js
│   └── api/                   # Route controllers
│
└── aesthetic/                 # Visual assets (not versioned — see below)
    ├── Fondos/                # Per-screen backgrounds
    ├── Gifs/                  # Animated mascot GIFs
    ├── Videos/                # Intro video
    ├── Fotos/                 # RAMon photos
    └── Lugares/               # Landmark photos
```

### Visual assets

The `aesthetic/` folder is excluded from version control (files are large). The expected asset paths are defined in `config.py`. Place your files there before running the kiosk.

| Asset | Expected path |
|-------|--------------|
| Intro video | `aesthetic/Videos/intro.mp4` |
| RAMon idle GIF | `aesthetic/Gifs/Idle 1_1giff.gif` |
| RAMon photo | `aesthetic/Fotos/1.png` |
| Barrio Antiguo photo | `aesthetic/Lugares/barrio.jpeg` |
| Fashion Drive photo | `aesthetic/Lugares/fashion.jpg` |
| Estadio BBVA photo | `aesthetic/Lugares/bbva.jpg` |
| Santiago PM photo | `aesthetic/Lugares/santiago.jpeg` |
| Per-screen backgrounds | `aesthetic/Fondos/<name>.png` |

---

## Session data collected

| Field | Description |
|-------|-------------|
| `session_id` | UUID generated per visit |
| `duration_seconds` | Total session duration |
| `language` | Selected language code |
| `places_visited` | Ordered list of landmarks visited |
| `most_visited_place` | Landmark with the most time spent |
| `total_questions` | Number of voice questions asked |
| `photo_taken` | Whether the photo screen was reached |
| `completed_tour` | Whether all four landmarks were visited |

---

## Uninstalling

```bash
# Stop and disable the Ollama service
sudo systemctl stop ollama
sudo systemctl disable ollama

# Remove the Ollama binary and all downloaded models (~2 GB per model)
sudo rm -f /usr/local/bin/ollama
rm -rf ~/.ollama

# Remove the systemd service file
sudo rm -f /etc/systemd/system/ollama.service
sudo systemctl daemon-reload

# Drop the MySQL database
mysql -u root -p -e "DROP DATABASE IF EXISTS kiosko_ramon;"

# Remove the Python virtual environment (if used)
rm -rf venv/

# Remove the project folder
rm -rf /path/to/kiosko-ramon
```

---

## Development shortcuts

These keyboard shortcuts are available while the kiosk is running:

| Key | Action |
|-----|--------|
| Esc | Close the kiosk |
| F1 | Jump to welcome screen |
| F2 | Jump to language selection |
| F5 | Jump to places menu |

---

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for the full text.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of this software, provided the original copyright notice and permission notice are included.

---

## Credits

- Mascot design and visual assets: Woohoo Agency
- Development: Ingenieria + Escuela de Artes, Tec de Monterrey
- World Cup 2026 venue: Estadio BBVA, Guadalupe, Nuevo Leon, Mexico



## Screenshots 

![mano1](Screenshots/ss1.png)


![mano2](Screenshots/ss2.png)





![mano4](Screenshots/ss4.png)


![mano5](Screenshots/ss5.png)


![mano1](Screenshots/ss1.png)


![mano6](Screenshots/ss6.png)


![mano7](Screenshots/ss7.png)


![mano8](Screenshots/ss8.png)


![mano9](Screenshots/ss9.png)



![mano10](Screenshots/ss10.png)


![mano11](Screenshots/ss11.png)


![mano12](Screenshots/ss12.png)


![mano13](Screenshots/ss13.png)


![mano14](Screenshots/ss14.png)


![mano15](Screenshots/ss15.png)


![mano16](Screenshots/ss16.png)


![mano17](Screenshots/ss17.png)


![mano18](Screenshots/ss18.png)


