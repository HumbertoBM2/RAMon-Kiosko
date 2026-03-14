"""
ui/screens/place_detail.py
Pantalla de detalle de un lugar.
Muestra: descripción, highlights, slideshow de fotos.
Al terminar la narración → opción de preguntar con voz.
"""
import pygame
import os
import time
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2, CAMERA_PREVIEW_W, SAFE_BOTTOM,
    RAMON_WAVE_GIF
)
from ui.screens.base_screen import BaseScreen
from data.places_content import get_place, get_text

_RAMON_IDLE_W = 100
_RAMON_IDLE_H = 150


def _load_gif_frames(path: str, width: int, height: int):
    """Carga frames de un GIF como superficies Pygame escaladas."""
    try:
        from PIL import Image, ImageSequence
        gif = Image.open(path)
        frames, delays = [], []
        for frame in ImageSequence.Iterator(gif):
            frame_rgba = frame.convert("RGBA").resize((width, height))
            raw = frame_rgba.tobytes("raw", "RGBA")
            surf = pygame.image.fromstring(raw, (width, height), "RGBA").convert_alpha()
            frames.append(surf)
            delays.append(frame.info.get("duration", 80))
        return frames, delays
    except Exception as e:
        print(f"[PlaceDetail] GIF error: {e}")
        return [], []


class PlaceDetailScreen(BaseScreen):

    def __init__(self, session_manager, tts, dispatcher, place_id: str):
        super().__init__(session_manager, tts, dispatcher)
        self.place_id = place_id

    def on_enter(self):
        super().on_enter()
        self._lang   = self.session.current_language()
        self._place  = get_place(self.place_id, self._lang)
        self._spoken = False

        # Registrar visita
        self.session.visit_place(self.place_id)
        self.dispatch.emit_event(
            "place_visited",
            self.session._session.session_id if self.session._session else "",
            {"place": self.place_id}
        )

        # Slideshow de imágenes
        self._images: list[pygame.Surface] = []
        self._slide_idx  = 0
        self._slide_timer = 0.0
        self._slide_interval = 4.0    # segundos por imagen
        self._load_images()

        # Scroll de highlights
        self._show_highlights_at = 3.0
        self._elapsed = 0.0
        self._chars_shown = 0
        self._text = self._place["description"]
        self._typewriter_speed = 40    # chars/seg

        # Narración
        self.tts.speak(
            self._place["name"] + ". " + self._text,
            lang=self._lang, block=False
        )

        # RAMon idle GIF
        self._ramon_frames = []
        self._ramon_delays = []
        self._ramon_idx    = 0
        self._ramon_tick   = 0
        if os.path.isfile(RAMON_WAVE_GIF):
            self._ramon_frames, self._ramon_delays = _load_gif_frames(
                RAMON_WAVE_GIF, _RAMON_IDLE_W, _RAMON_IDLE_H
            )

    def _load_images(self):
        for path in self._place.get("images", []):
            if os.path.isfile(path):
                try:
                    img = pygame.image.load(path).convert()
                    self._images.append(img)
                except Exception:
                    pass
        # Si no hay imágenes, usar placeholder
        if not self._images:
            placeholder = pygame.Surface((640, 360))
            placeholder.fill((30, 30, 50))
            font = pygame.font.SysFont("dejavusans", 22)
            t = font.render(f"[ Photo: {self._place['name']} ]", True, (120, 120, 180))
            placeholder.blit(t, (320 - t.get_width() // 2, 165))
            self._images.append(placeholder)

    def update(self, dt, finger_count, gesture_engine):
        self._elapsed += dt
        self._chars_shown = min(len(self._text),
                                int(self._elapsed * self._typewriter_speed))

        # Slideshow
        self._slide_timer += dt
        if self._slide_timer >= self._slide_interval:
            self._slide_idx = (self._slide_idx + 1) % len(self._images)
            self._slide_timer = 0.0

        # Avanzar frame del GIF de RAMon
        if self._ramon_frames:
            now = pygame.time.get_ticks()
            delay = self._ramon_delays[self._ramon_idx] if self._ramon_delays else 80
            if now - self._ramon_tick >= delay:
                self._ramon_idx = (self._ramon_idx + 1) % len(self._ramon_frames)
                self._ramon_tick = now

        # Gestos: 1 dedo → preguntar, 2 dedos → volver al menú
        if finger_count in (1, 2):
            gesture_engine.update(finger_count)
            confirmed = gesture_engine.pop_confirmed()
            if confirmed == 1:
                return "qa"
            if confirmed == 2:
                return "places_menu"
        else:
            gesture_engine.reset()

        return None

    def draw(self, screen, renderer):
        renderer.draw_background()
        renderer.draw_overlay(alpha=150)

        cx   = SCREEN_WIDTH // 2
        lang = self._lang
        place = self._place
        PAD  = 20
        W    = SCREEN_WIDTH - PAD * 2   # 860px

        # ── Badges visitados ───────────────────────────────────────
        self.draw_visited_badges(screen, self.session.visited_place_ids, y=6)

        # ── Nombre ────────────────────────────────────────────────
        self.draw_text(screen, place['name'],
                       cx, 8, size=28, bold=True,
                       color=COLOR_ACCENT2, center=True, max_width=W)

        # ── Foto (ancho completo, altura compacta) ─────────────────
        IMG_H = 230
        img_y = 46
        if self._images:
            img = pygame.transform.scale(
                self._images[self._slide_idx], (W, IMG_H))
            screen.blit(img, (PAD, img_y))
            pygame.draw.rect(screen, COLOR_ACCENT,
                             (PAD - 2, img_y - 2, W + 4, IMG_H + 4), 2,
                             border_radius=8)
            dot_y = img_y + IMG_H + 8
            for i in range(len(self._images)):
                c = COLOR_ACCENT if i == self._slide_idx else (60, 60, 60)
                pygame.draw.circle(screen, c, (PAD + 14 + i * 16, dot_y), 5)

        # ── Descripción (ancho completo, debajo de foto) ───────────
        desc_y = img_y + IMG_H + 24
        DESC_H = 150
        self.draw_card(screen, PAD, desc_y, W, DESC_H, alpha=170)
        self.draw_text(screen, self._text[:self._chars_shown],
                       PAD + 10, desc_y + 10, size=17, color=COLOR_WHITE,
                       max_width=W - 20)

        # ── Highlights en 2 columnas ───────────────────────────────
        hl_y = desc_y + DESC_H + 10
        if self._elapsed >= self._show_highlights_at:
            self.draw_text(screen, 'Highlights:',
                           PAD, hl_y, size=17, bold=True, color=COLOR_ACCENT)
            hl_y += 24
            highlights = place.get('highlights', [])[:6]
            col_w = W // 2
            for i, hl in enumerate(highlights):
                hx = PAD if i % 2 == 0 else PAD + col_w
                hy = hl_y + (i // 2) * 24
                self.draw_text(screen, f'  • {hl}', hx, hy,
                               size=15, color=COLOR_WHITE, max_width=col_w - 10)

        # ── RAMon idle (centrado, entre highlights y barra de nav) ──
        ramon_y = SAFE_BOTTOM - 60 - _RAMON_IDLE_H - 8
        if self._ramon_frames:
            surf = self._ramon_frames[self._ramon_idx]
            screen.blit(surf, (cx - _RAMON_IDLE_W // 2, ramon_y))

        # ── Barra de navegación ────────────────────────────────────
        nav_y = SAFE_BOTTOM - 60
        self.draw_card(screen, PAD, nav_y, W, 50, color=(20, 20, 50), alpha=200)
        qa_l   = {'en': '1 → Ask RAMon',   'es': '1 → Preguntar'}.get(lang, '1 → Ask')
        menu_l = {'en': '2 → Places Menu', 'es': '2 → Menú'}.get(lang, '2 → Menu')
        self.draw_text(screen, f'{qa_l}   |   {menu_l}',
                       cx, nav_y + 13, size=18, color=COLOR_WHITE, center=True)
