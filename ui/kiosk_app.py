"""
ui/kiosk_app.py
Motor principal del kiosko RAMon.
Maneja:
  - Loop de Pygame
  - Captura de webcam (OpenCV)
  - Detección de manos (MediaPipe)
  - Máquina de estados de pantallas
  - Integración TTS / STT / Ollama
  - Envío a Azure / MySQL / API
"""
import pygame
import cv2
import numpy as np
import sys
import time

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN, FPS,
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    COLOR_BG, COLOR_ACCENT, COLOR_WHITE, PLACES
)
from core.hand_detector import HandDetector
from core.gesture_engine import GestureEngine
from core.session_manager import SessionManager
from ui.renderer import MediaRenderer
from voice.text_to_speech import TextToSpeech
from voice.speech_to_text import SpeechToText
from voice.ollama_client import OllamaClient
from data.data_dispatcher import DataDispatcher

# ── Importar pantallas ─────────────────────────────────────────────────────
from ui.screens.welcome_screen  import WelcomeScreen
from ui.screens.language_screen import LanguageScreen
from ui.screens.intro_screen    import IntroScreen
from ui.screens.places_menu     import PlacesMenuScreen
from ui.screens.place_detail    import PlaceDetailScreen
from ui.screens.qa_screen       import QAScreen
from ui.screens.photo_screen    import PhotoScreen
from ui.screens.farewell_screen import FarewellScreen
from ui.screens.privacy_screen  import PrivacyScreen


class KioskApp:
    """
    Aplicación principal del kiosko.
    Inicializa subsistemas y corre el game loop.
    """

    def __init__(self):
        print("[Kiosko] Iniciando RAMon Kiosko 2026...")
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

        # ── Pantalla ───────────────────────────────────────────────
        # pygame.SCALED: el canvas lógico (900×1280) se escala automáticamente
        # al tamaño de la ventana/pantalla, manteniendo el aspect ratio.
        flags = pygame.SCALED
        if FULLSCREEN:
            flags |= pygame.FULLSCREEN
        else:
            # En modo ventana, calcular tamaño que quepa en el monitor
            info = pygame.display.Info()
            avail_h = info.current_h - 80   # margen para taskbar
            avail_w = info.current_w - 40
            scale   = min(avail_w / SCREEN_WIDTH, avail_h / SCREEN_HEIGHT)
            win_w   = int(SCREEN_WIDTH  * scale)
            win_h   = int(SCREEN_HEIGHT * scale)
            pygame.display.set_mode((win_w, win_h), flags)  # hint de tamaño
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), flags
        )
        pygame.display.set_caption("RAMon - Kiosko Turístico Monterrey 2026")
        self.clock = pygame.time.Clock()

        # ── Subsistemas ────────────────────────────────────────────
        self.session    = SessionManager()
        self.dispatcher = DataDispatcher()
        self.tts        = TextToSpeech()
        self.stt        = SpeechToText()
        self.ollama     = OllamaClient()
        self.renderer   = MediaRenderer(self.screen)
        self.hand_det   = HandDetector()
        self.gesture    = GestureEngine()

        # ── Cámara ─────────────────────────────────────────────────
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self._cam_frame_np: np.ndarray | None = None   # frame actual (numpy BGR)
        self._cam_surface:  pygame.Surface | None = None

        # ── Estado actual ──────────────────────────────────────────
        self._current_place_id = ""    # Para pantallas de detalle y Q&A
        self._screens: dict = {}
        self._current_screen_name: str = ""
        self._current_screen = None
        self._finger_count: int = 0

        self._build_screens()
        self._switch_to("welcome")
        print("[Kiosko] Listo. ¡Comienza la experiencia!")

    # ── Construcción de pantallas ──────────────────────────────────

    def _build_screens(self):
        """Crea todas las instancias de pantalla."""
        args = (self.session, self.tts, self.dispatcher)

        self._screens = {
            "welcome":      WelcomeScreen(*args),
            "language":     LanguageScreen(*args),
            "intro":        IntroScreen(*args),
            "places_menu":  PlacesMenuScreen(*args),
            "farewell":     FarewellScreen(*args),
        }

        # Pantallas de detalle (una por lugar)
        for place_num, place_info in PLACES.items():
            pid = place_info["id"]
            self._screens[f"place_{pid}"] = PlaceDetailScreen(*args, place_id=pid)

        # Q&A (instancia única, se actualiza el place_id)
        self._qa_screen = QAScreen(
            *args,
            stt=self.stt,
            ollama=self.ollama,
            place_id=""
        )
        self._screens["qa"] = self._qa_screen

        # Foto
        self._screens["photo"] = PhotoScreen(
            *args,
            cam_frame_getter=lambda: self._cam_frame_np
        )

        # Aviso de privacidad
        self._screens["privacy"] = PrivacyScreen(*args)

    # ── Cambio de pantalla ─────────────────────────────────────────

    def _switch_to(self, name: str):
        if self._current_screen:
            self._current_screen.on_exit()
            print(f"[Kiosko] ← Saliendo: {self._current_screen_name}")

        # Si vamos a Q&A, actualizar el place_id actual
        if name == "qa":
            self._qa_screen.set_place(self._current_place_id)

        screen = self._screens.get(name)
        if screen is None:
            print(f"[Kiosko] Pantalla desconocida: {name!r}, volviendo a welcome")
            screen = self._screens["welcome"]
            name   = "welcome"

        # Configurar fondo según pantalla/lugar
        self._set_screen_background(name)

        self._current_screen_name = name
        self._current_screen = screen
        screen.on_enter()
        self.gesture.reset()
        print(f"[Kiosko] → Entrando: {name}")

    def _set_screen_background(self, name: str):
        """Configura el fondo visual según la pantalla activa."""
        import os

        if name.startswith("place_"):
            place_id = name[len("place_"):]
            from data.places_content import PLACES_CONTENT
            pc = PLACES_CONTENT.get(place_id, {})
            self.renderer.load_place_background(
                pc.get("background_video", ""),
                pc.get("background_image", ""),
            )
        else:
            # Fondo global por pantalla usando assets reales del equipo de arte
            # intro → video de bienvenida de RAMon (el propio video ES RAMon)
            if name == "intro":
                self.renderer.set_background_video("aesthetic/Videos/intro.mp4")
                return

            bg_map = {
                "welcome":     "aesthetic/Fondos/mapa monterrey.png",
                "language":    "aesthetic/Fondos/select language.png",
                "places_menu": "aesthetic/Fondos/main menu.png",
                "qa":          "aesthetic/Fondos/Chatbox.png",
                "photo":       "aesthetic/Fondos/mapa monterrey.png",
                "privacy":     "aesthetic/Fondos/mapa monterrey.png",
                "farewell":    "aesthetic/Fondos/mapa monterrey.png",
            }
            bg_path = bg_map.get(name, "")
            if bg_path and os.path.isfile(bg_path):
                self.renderer.set_background_image(bg_path)
            else:
                self.renderer.set_background_color()  # Fondo negro

    # ── Loop principal ─────────────────────────────────────────────

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            # ── Eventos Pygame ──────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # Atajos de teclado para desarrollo / demo
                    elif event.key == pygame.K_F1:
                        self._switch_to("welcome")
                    elif event.key == pygame.K_F2:
                        self._switch_to("language")
                    elif event.key == pygame.K_F5:
                        self._switch_to("places_menu")

            # ── Captura de cámara ────────────────────────────────────
            self._finger_count = self._process_camera()

            # ── Actualizar pantalla activa ───────────────────────────
            next_screen = self._current_screen.update(
                dt, self._finger_count, self.gesture
            )

            # Guardar el lugar actual para Q&A
            if (self._current_screen_name.startswith("place_")
                    and next_screen == "qa"):
                self._current_place_id = self._current_screen_name[len("place_"):]

            # Transición especial: si all_places_visited y va a farewell → photo
            # (solo si NO venimos ya del photo screen para evitar el loop)
            if (next_screen == "farewell"
                    and self._current_screen_name != "photo"
                    and self.session.all_places_visited()):
                next_screen = "photo"

            if next_screen:
                self._switch_to(next_screen)

            # ── Dibujar ─────────────────────────────────────────────
            self._current_screen.draw(self.screen, self.renderer)

            # Preview de cámara + indicador de dedos (todas las pantallas)
            if self._cam_surface:
                self._current_screen.draw_camera_preview(
                    self.screen, self._cam_surface
                )
            self._current_screen.draw_finger_indicator(
                self.screen,
                self._finger_count,
                self.gesture.hold_progress
            )

            pygame.display.flip()

        self._shutdown()

    # ── Cámara + detección de manos ────────────────────────────────

    def _process_camera(self) -> int:
        """
        Lee frame de webcam, detecta manos y retorna número de dedos.
        Actualiza self._cam_surface para el preview.
        """
        ret, frame = self.cap.read()
        if not ret:
            return 0

        # Espejo horizontal (natural para el usuario)
        frame = cv2.flip(frame, 1)
        self._cam_frame_np = frame

        results = self.hand_det.process(frame)

        # Dibujar landmarks en el frame para el preview
        debug_frame = self.hand_det.draw_landmarks(frame.copy(), results)

        # Convertir a Pygame surface
        rgb = cv2.cvtColor(debug_frame, cv2.COLOR_BGR2RGB)
        self._cam_surface = pygame.surfarray.make_surface(
            np.transpose(rgb, (1, 0, 2))
        )

        return self.hand_det.count_fingers(results)

    # ── Cierre ─────────────────────────────────────────────────────

    def _shutdown(self):
        print("[Kiosko] Cerrando...")
        if self.session.is_active():
            data = self.session.end()
            if data:
                self.dispatcher.dispatch_session(data.to_dict())
        self.dispatcher.close()
        self.hand_det.release()
        self.cap.release()
        pygame.quit()
        print("[Kiosko] ¡Hasta luego!")
