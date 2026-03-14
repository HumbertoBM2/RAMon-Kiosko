"""
ui/screens/welcome_screen.py
Pantalla de bienvenida — espera saludo con mano abierta (5 dedos, 2 segundos).
"""
import pygame
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2
from ui.screens.base_screen import BaseScreen
from data.places_content import get_text


class WelcomeScreen(BaseScreen):

    def on_enter(self):
        super().on_enter()
        self._pulse = 0.0
        self._hint_alpha = 255

    def update(self, dt, finger_count, gesture_engine):
        self._pulse = (self._pulse + dt * 2.0) % (2 * math.pi)

        # Iniciar nueva sesión cuando llegue a esta pantalla
        if not self.session.is_active():
            self.session.start()

        # Detectar saludo
        if gesture_engine.update_wave(finger_count):
            return "language"

        return None

    def draw(self, screen, renderer):
        renderer.draw_background()

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # Círculo pulsante
        pulse_r = int(8 + 6 * math.sin(self._pulse))
        for i in range(3):
            r = 120 + i * 30 + pulse_r
            alpha = max(0, 180 - i * 55)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*COLOR_ACCENT, alpha), (r, r), r, 3)
            screen.blit(surf, (cx - r, cy - 180 - r + 60))

        # Icono de mano (ASCII, sin emoji)
        self.draw_text(screen, "[  ]", cx, cy - 220, size=80, center=True)

        # Título
        self.draw_text(screen, get_text("welcome_title", "en"),
                       cx, cy - 100, size=48, bold=True,
                       color=COLOR_ACCENT2, center=True)

        # Subtítulo
        self.draw_text(screen, get_text("welcome_subtitle", "en"),
                       cx, cy - 30, size=24, color=COLOR_WHITE,
                       center=True, max_width=820)

        # Barra de progreso del saludo
        prog = getattr(pygame, '_wave_progress', 0.0)
        if finger_count_global := getattr(screen, '_finger_count', 0):
            pass

        # Instrucción inferior
        self.draw_text(screen,
                       "Welcome to Nuevo León  •  Bienvenido a Nuevo León",
                       cx, SCREEN_HEIGHT - 50,
                       size=18, color=(140, 140, 140), center=True)


# El WelcomeScreen recibe finger_count y gesture_engine en update(), no aquí directamente.
# La barra de progreso se maneja en kiosk_app.py pasando gesture_engine.hold_progress.
