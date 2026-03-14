"""
ui/screens/intro_screen.py
RAMon explica la dinámica del recorrido.
Avanza automáticamente luego de la narración (o con cualquier gesto).
El fondo es el video intro.mp4 (RAMon en pantalla completa).
"""
import pygame
import time
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2, SAFE_BOTTOM
from ui.screens.base_screen import BaseScreen
from data.places_content import get_text



class IntroScreen(BaseScreen):

    def on_enter(self):
        super().on_enter()
        self._lang = self.session.current_language()
        self._spoken   = False
        self._auto_advance_at = None
        self._text = get_text("tour_intro", self._lang)
        self._chars_shown = 0
        self._typewriter_speed = 30    # chars/seg
        self._elapsed = 0.0

        # Narrar en TTS
        self.tts.speak(self._text, lang=self._lang, block=False)
        self._spoken = True

    def update(self, dt, finger_count, gesture_engine):
        self._elapsed += dt

        # Efecto máquina de escribir
        self._chars_shown = min(
            len(self._text),
            int(self._elapsed * self._typewriter_speed)
        )

        text_done  = self._chars_shown >= len(self._text)
        audio_done = not self.tts.is_speaking()

        # Auto-avance: esperar a que termine el audio Y el texto, luego 3s de buffer
        if self._auto_advance_at is None and text_done and audio_done:
            self._auto_advance_at = time.time() + 3.0

        if self._auto_advance_at and time.time() >= self._auto_advance_at:
            return "places_menu"

        # Gesto manual solo disponible una vez que el texto está completo
        if text_done and finger_count > 0:
            gesture_engine.update(finger_count)
            if gesture_engine.pop_confirmed():
                return "places_menu"
        else:
            gesture_engine.reset()

        return None

    def draw(self, screen, renderer):
        renderer.draw_background()   # video intro.mp4 — RAMon ya aparece en el video
        renderer.draw_overlay(alpha=100)   # overlay ligero para legibilidad

        cx = SCREEN_WIDTH // 2

        # Burbuja de texto — ancho completo en la parte superior
        PAD      = 20
        BUBBLE_X = PAD
        BUBBLE_W = SCREEN_WIDTH - PAD * 2
        BUBBLE_Y = 10
        BUBBLE_H = 260   # altura fija compacta para no tapar a RAMon

        # Etiqueta
        self.draw_text(screen, "RAMon says:",
                       cx, BUBBLE_Y + 10,
                       size=20, color=(200, 200, 200), center=True)

        # Burbuja de texto
        self.draw_card(screen, BUBBLE_X, BUBBLE_Y, BUBBLE_W, BUBBLE_H, alpha=200)
        self.draw_text(screen, self._text[:self._chars_shown],
                       BUBBLE_X + 12, BUBBLE_Y + 44, size=22, color=COLOR_WHITE,
                       max_width=BUBBLE_W - 24)

        # Indicador "continuar"
        if self._chars_shown >= len(self._text):
            blink = int(time.time() * 2) % 2 == 0
            if blink:
                self.draw_text(screen,
                               "▶  " + {
                                   "en": "Any gesture to continue",
                                   "es": "Cualquier gesto para continuar",
                               }.get(self._lang, "Continue..."),
                               cx, SAFE_BOTTOM - 50,
                               size=20, color=COLOR_ACCENT2, center=True)

    def _draw_ramon_placeholder(self, screen, cx, cy):
        """
        Placeholder visual para RAMon (fallback si no hay assets disponibles).
        """
        # Cuerpo
        pygame.draw.ellipse(screen, (30, 90, 180), (cx - 60, cy - 100, 120, 160))
        # Cabeza
        pygame.draw.circle(screen, (240, 200, 140), (cx, cy - 130), 55)
        # Ojos
        pygame.draw.circle(screen, (30, 30, 30), (cx - 18, cy - 140), 8)
        pygame.draw.circle(screen, (30, 30, 30), (cx + 18, cy - 140), 8)
        # Sonrisa
        pygame.draw.arc(screen, (30, 30, 30),
                        (cx - 20, cy - 126, 40, 22), 3.14, 0, 3)
        # Cuernos de RAM
        pygame.draw.arc(screen, (180, 140, 70),
                        (cx - 60, cy - 200, 35, 55), 0, 3.14, 6)
        pygame.draw.arc(screen, (180, 140, 70),
                        (cx + 25, cy - 200, 35, 55), 0, 3.14, 6)

