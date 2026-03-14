"""
ui/screens/farewell_screen.py
Pantalla de despedida. Muestra resumen de sesión, envía datos y vuelve al inicio.
"""
import pygame
import time
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2, COLOR_SUCCESS, SAFE_BOTTOM
)
from ui.screens.base_screen import BaseScreen
from data.places_content import get_text, PLACES_CONTENT


class FarewellScreen(BaseScreen):

    AUTO_RETURN_SECONDS = 15     # Segundos antes de volver a bienvenida

    def on_enter(self):
        super().on_enter()
        self._lang = self.session.current_language()

        # Cerrar sesión y obtener datos
        session_data = self.session.end()
        self._session_summary = session_data.to_dict() if session_data else {}

        # Enviar datos a todos los backends
        if session_data:
            self.dispatch.dispatch_session(session_data.to_dict())

        # Narración de despedida
        farewell = get_text("farewell", self._lang)
        self.tts.speak(farewell, lang=self._lang, block=False)

        self._enter_time = time.time()
        self._return_timer = self.AUTO_RETURN_SECONDS

    def update(self, dt, finger_count, gesture_engine):
        elapsed = time.time() - self._enter_time
        self._return_timer = max(0, self.AUTO_RETURN_SECONDS - elapsed)

        if self._return_timer <= 0:
            return "welcome"

        # Gesto para volver manualmente
        if finger_count > 0:
            gesture_engine.update(finger_count)
            if gesture_engine.pop_confirmed():
                return "welcome"
        else:
            gesture_engine.reset()

        return None

    def draw(self, screen, renderer):
        renderer.draw_background()
        renderer.draw_overlay(alpha=140)

        cx = SCREEN_WIDTH // 2
        lang = self._lang
        summary = self._session_summary

        # Cámara ahora está en la esquina inferior — tope libre
        CONTENT_TOP = 20

        # Título
        self.draw_text(screen, get_text("farewell", lang),
                       cx, CONTENT_TOP, size=34, bold=True,
                       color=COLOR_ACCENT2, center=True, max_width=SCREEN_WIDTH - 40)

        # ── Resumen de sesión ──────────────────────────────────────
        card_top = CONTENT_TOP + 48
        card_h   = 380
        self.draw_card(screen, cx - 420, card_top, 840, card_h,
                       color=(15, 30, 50), alpha=200)

        y = card_top + 22
        dur = summary.get("duration_seconds", 0)
        mins, secs = divmod(int(dur), 60)

        # Lugares: list para renderizar uno por línea
        places_list = self._format_places_list(summary.get("places_visited", ""), lang)

        stats = [
            ("-",  {"en": "Duration",         "es": "Duración"},           [f"{mins}m {secs}s"]),
            ("-",  {"en": "Language",          "es": "Idioma"},             [summary.get("language", "").upper()]),
            ("-",  {"en": "Places visited",    "es": "Lugares visitados"},  places_list),
            ("-",  {"en": "Questions asked",   "es": "Preguntas realizadas"},[str(summary.get("total_questions", 0))]),
            ("-",  {"en": "Photo taken",       "es": "Foto tomada"},
                   [{"en": "Yes" if summary.get("photo_taken") else "No",
                     "es": "Sí"  if summary.get("photo_taken") else "No"}.get(lang, "-")]),
        ]

        for icon, label_dict, lines in stats:
            label = label_dict.get(lang, label_dict.get("en", ""))
            self.draw_text(screen, f"{icon}  {label}:",
                           cx - 390, y, size=20, bold=True, color=COLOR_ACCENT)
            for i, line in enumerate(lines):
                self.draw_text(screen, line,
                               cx - 60, y + i * 26, size=20, color=COLOR_WHITE)
            y += max(36, len(lines) * 26 + 8)

        # Trophy si completó tour
        if summary.get("completed_tour"):
            self.draw_text(screen, "★  " + {
                "en": "You completed the full tour!",
                "es": "¡Completaste el recorrido completo!",
            }.get(lang, "Full tour completed!"),
                           cx, y + 20, size=26, bold=True, color=COLOR_SUCCESS, center=True)

        # Contador de retorno
        self.draw_card(screen, cx - 250, SAFE_BOTTOM - 68, 500, 52,
                       color=(15, 15, 15), alpha=200)
        self.draw_text(screen,
                       {"en": f"Returning to start in {int(self._return_timer)}s...",
                        "es": f"Volviendo al inicio en {int(self._return_timer)}s..."}
                       .get(lang, f"{int(self._return_timer)}s..."),
                       cx, SAFE_BOTTOM - 55,
                       size=20, color=(140, 140, 140), center=True)

    def _format_places_list(self, places_str: str, lang: str) -> list:
        """Devuelve lista de strings, uno por lugar visitado."""
        if not places_str:
            return ["-"]
        ids = [p.strip() for p in places_str.split(",") if p.strip()]
        names = []
        for pid in ids:
            pc   = PLACES_CONTENT.get(pid, {})
            name = (pc.get("name") or {}).get(lang, pid)
            if name not in names:
                names.append(name)
        return [f"  {n}" for n in names] if names else ["-"]
