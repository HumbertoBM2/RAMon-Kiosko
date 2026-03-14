"""
ui/screens/places_menu.py
Menú principal de lugares turísticos.
1 dedo → Barrio Antiguo
2 dedos → Fashion Drive
3 dedos → Estadio BBVA
4 dedos → Santiago Pueblo Mágico
5 dedos → Finalizar sesión
"""
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2, COLOR_SUCCESS,
    PLACES, END_SESSION_FINGER, SAFE_BOTTOM
)
from ui.screens.base_screen import BaseScreen
from data.places_content import get_text, PLACES_CONTENT


class PlacesMenuScreen(BaseScreen):

    def on_enter(self):
        super().on_enter()
        self._lang = self.session.current_language()
        self._all_visited = self.session.all_places_visited()

    def update(self, dt, finger_count, gesture_engine):
        self._lang = self.session.current_language()
        self._all_visited = self.session.all_places_visited()

        if 1 <= finger_count <= END_SESSION_FINGER:
            gesture_engine.update(finger_count)
            confirmed = gesture_engine.pop_confirmed()
            if confirmed:
                if confirmed == END_SESSION_FINGER:
                    return "farewell"
                # Seleccionar lugar
                for place_num, place_info in PLACES.items():
                    if confirmed == place_num:
                        # Guardar qué lugar fue seleccionado en app context
                        self._app_context = place_info["id"]
                        return f"place_{place_info['id']}"
        else:
            gesture_engine.reset()

        return None

    def draw(self, screen, renderer):
        renderer.draw_background()
        renderer.draw_overlay(alpha=140)

        cx = SCREEN_WIDTH // 2
        lang = self._lang

        # Título (cámara abajo, tope libre)
        self.draw_text(screen, get_text("places_menu_title", lang),
                       cx, 8, size=30, bold=True,
                       color=COLOR_ACCENT2, center=True)

        # Badges de visitados (debajo del título)
        visited = self.session.visited_place_ids
        self.draw_visited_badges(screen, visited, y=46)

        # Cards 2×2 (compact para 900x900)
        cols    = 2
        card_w  = 415
        card_h  = 195
        gap_x   = 20
        gap_y   = 14
        start_x = (SCREEN_WIDTH - (cols * card_w + (cols - 1) * gap_x)) // 2
        card_y  = 88

        for i, (place_num, place_info) in enumerate(PLACES.items()):
            col  = i % cols
            row  = i // cols
            pid  = place_info["id"]
            x    = start_x + col * (card_w + gap_x)
            y    = card_y  + row * (card_h + gap_y)
            pc   = PLACES_CONTENT.get(pid, {})
            name = (pc.get("name") or {}).get(lang, pid)
            icon = place_info["icon"]
            been_there = pid in visited

            bg_color = (20, 100, 60) if been_there else (30, 30, 60)
            self.draw_card(screen, x, y, card_w, card_h,
                           color=bg_color, alpha=200)

            self.draw_text(screen, icon, x + card_w // 2, y + 16,
                           size=40, center=True)
            self.draw_text(screen, f"{place_num}",
                           x + card_w // 2, y + 74,
                           size=38, bold=True,
                           color=COLOR_ACCENT if not been_there else COLOR_SUCCESS,
                           center=True)
            self.draw_text(screen, name,
                           x + card_w // 2, y + 130,
                           size=18, color=COLOR_WHITE,
                           center=True, max_width=card_w - 20)
            if been_there:
                self.draw_text(screen, "\u2713",
                               x + card_w - 30, y + 12,
                               size=26, bold=True, color=COLOR_SUCCESS)

        rows  = (len(PLACES) + cols - 1) // cols
        end_y = card_y + rows * (card_h + gap_y) + 15
        self.draw_card(screen, cx - 200, end_y, 400, 60,
                       color=(80, 20, 20), alpha=200)
        self.draw_text(screen, get_text("places_menu_end", lang),
                       cx, end_y + 16, size=22, color=(240, 100, 100),
                       center=True)

        # ── Indicador "todos visitados" ────────────────────────────────
        if self._all_visited:
            self.draw_card(screen, cx - 380, end_y + 75, 760, 52,
                           color=(20, 80, 20), alpha=210)
            self.draw_text(screen,
                           "★ " + {
                               "en": "You visited all places! End Session for your prize!",
                               "es": "¡Visitaste todos! Finaliza sesión para tu premio.",
                           }.get(lang, "All places visited!"),
                           cx, end_y + 89, size=18,
                           color=COLOR_SUCCESS, center=True, max_width=740)

        # Instrucción inferior
        self.draw_text(screen,
                       {
                           "en": "Hold fingers to select  (hold 1.5 sec)",
                           "es": "Mantén los dedos para seleccionar  (1.5 seg)",
                       }.get(lang, "Hold fingers to select"),
                       cx, SAFE_BOTTOM - 30, size=18,
                       color=(120, 120, 120), center=True)
