"""
ui/screens/language_screen.py
Selección de idioma con dedos (1-8).
"""
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2,
    LANGUAGES, DEFAULT_LANGUAGE
)
from ui.screens.base_screen import BaseScreen, get_cjk_font
from data.places_content import get_text


_LANG_ITEMS = list(LANGUAGES.items())   # [(1, {...}), (2, {...}), ...]

# Idiomas que requieren NotoSansCJK para renderizar correctamente
_CJK_CODES = {"ja", "ko"}


class LanguageScreen(BaseScreen):

    def on_enter(self):
        super().on_enter()
        self._selected_lang = None
        self._tts_spoken = False
        if not self._tts_spoken:
            self.tts.speak(get_text("ramon_greeting", "en"), lang="en", block=False)
            self._tts_spoken = True

    def update(self, dt, finger_count, gesture_engine):
        if 1 <= finger_count <= len(LANGUAGES):
            gesture_engine.update(finger_count)
            confirmed = gesture_engine.pop_confirmed()
            if confirmed and confirmed in LANGUAGES:
                lang_info = LANGUAGES[confirmed]
                self.session.set_language(lang_info["code"])
                self.dispatch.emit_event(
                    "language_selected",
                    self.session._session.session_id if self.session._session else "",
                    {"language": lang_info["code"]}
                )
                return "intro"
        else:
            gesture_engine.reset()
        return None

    def draw(self, screen, renderer):
        renderer.draw_background()
        renderer.draw_overlay(alpha=130)

        cx = SCREEN_WIDTH // 2

        # Título
        self.draw_text(screen, "Hold up the number of fingers for your language:",
                       cx, 30, size=26, bold=True,
                       color=COLOR_ACCENT2, center=True)

        # Grid 2 col x 4 filas — portrait 900px
        col_w   = 430
        gap     = 20
        start_x = [10, 10 + col_w + gap]   # 10 y 460
        start_y = 125
        row_h   = 140

        for i, (finger, lang) in enumerate(_LANG_ITEMS):
            col = i % 2
            row = i // 2
            card_x  = start_x[col]
            card_cy = start_y + row * row_h   # centro vertical de la card

            # Card
            self.draw_card(screen, card_x, card_cy - 52,
                           col_w, 104, alpha=170)

            # Numero de dedo (izquierda, grande)
            self.draw_text(screen, str(finger),
                           card_x + 54, card_cy - 28,
                           size=44, bold=True, color=COLOR_ACCENT, center=True)

            # Separador vertical sutil
            pygame.draw.line(screen, (80, 80, 80),
                             (card_x + 84, card_cy - 38),
                             (card_x + 84, card_cy + 38), 1)

            # Nombre del idioma (usa NotoSansCJK para ja/ko)
            name_x   = card_x + 94
            name_y   = card_cy - 22
            name_txt = lang["name"]
            if lang["code"] in _CJK_CODES:
                cjk_f = get_cjk_font(34)
                self.draw_text(screen, name_txt, name_x, name_y,
                               size=34, bold=False, color=COLOR_WHITE,
                               font=cjk_f)
            else:
                self.draw_text(screen, name_txt, name_x, name_y,
                               size=34, bold=True, color=COLOR_WHITE)

        # Instrucción inferior
        self.draw_text(screen,
                       "Hold fingers still for 1.5 seconds to confirm",
                       cx, SCREEN_HEIGHT - 38,
                       size=16, color=(140, 140, 140), center=True)
