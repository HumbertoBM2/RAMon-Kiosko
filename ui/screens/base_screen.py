"""
ui/screens/base_screen.py
Clase base para todas las pantallas del kiosko.
Cada pantalla hereda esta clase e implementa update() y draw().
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2, COLOR_DARK_GRAY


# ── Fuentes cacheadas ──────────────────────────────────────────────────────
_font_cache: dict[tuple, pygame.font.Font] = {}
_cjk_cache:  dict[int,   pygame.font.Font] = {}

# Iosevka Nerd Font Propo — para todo el UI (Latin, Cirílico, simbolos)
_IOSEVKA_REGULAR = "/home/humberto/.local/share/fonts/Iosevka/IosevkaNerdFontPropo-Regular.ttf"
_IOSEVKA_BOLD    = "/home/humberto/.local/share/fonts/Iosevka/IosevkaNerdFontPropo-Bold.ttf"
# NotoSansCJK — solo para japonés y coreano
_NOTO_CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        path = _IOSEVKA_BOLD if bold else _IOSEVKA_REGULAR
        try:
            _font_cache[key] = pygame.font.Font(path, size)
        except FileNotFoundError:
            _font_cache[key] = pygame.font.SysFont("notosans,dejavusans", size, bold=bold)
    return _font_cache[key]


def get_cjk_font(size: int) -> pygame.font.Font:
    if size not in _cjk_cache:
        try:
            _cjk_cache[size] = pygame.font.Font(_NOTO_CJK, size)
        except FileNotFoundError:
            _cjk_cache[size] = pygame.font.SysFont("notosans,dejavusans", size)
    return _cjk_cache[size]


def _has_cjk(text: str) -> bool:
    """True si el texto contiene caracteres CJK (chino, japonés, coreano)."""
    for ch in text:
        cp = ord(ch)
        if (0x3000 <= cp <= 0x9FFF or   # CJK unificado, hiragana, katakana
                0xAC00 <= cp <= 0xD7AF or   # Hangul (coreano)
                0xF900 <= cp <= 0xFAFF):    # CJK compatibilidad
            return True
    return False


class BaseScreen:
    """
    Clase base abstracta para pantallas del kiosko.

    Subclases deben implementar:
        update(dt, finger_count, gesture_engine) → str | None
            Retorna el nombre de la próxima pantalla o None para quedarse.
        draw(screen, renderer)
            Dibuja la pantalla sobre la superficie y el renderer.
    """

    def __init__(self, session_manager, tts, dispatcher):
        self.session  = session_manager
        self.tts      = tts
        self.dispatch = dispatcher
        self._entered = False

    def on_enter(self):
        """Llamado una vez al entrar a la pantalla."""
        self._entered = True

    def on_exit(self):
        """Llamado una vez al salir de la pantalla."""
        self._entered = False
        try:
            self.tts.stop()
        except Exception:
            pass

    def update(self, dt: float, finger_count: int, gesture_engine) -> str | None:
        """
        dt: delta time en segundos
        finger_count: dedos detectados en el frame actual
        gesture_engine: instancia de GestureEngine
        Retorna: nombre de la siguiente pantalla o None
        """
        raise NotImplementedError

    def draw(self, screen: pygame.Surface, renderer) -> None:
        raise NotImplementedError

    # ── Helpers de dibujo ──────────────────────────────────────────

    def draw_text(self, screen: pygame.Surface, text: str,
                  x: int, y: int,
                  size: int = 28, color: tuple = COLOR_WHITE,
                  bold: bool = False, center: bool = False,
                  max_width: int = 0,
                  font: pygame.font.Font = None) -> int:
        """
        Dibuja texto y retorna la y final (para encadenar textos).
        max_width > 0: hace word-wrap.
        font: fuente personalizada (None = Iosevka por defecto).
        """
        if font is None:
            font = get_cjk_font(size) if _has_cjk(text) else get_font(size, bold)
        f = font
        if max_width > 0:
            return self._draw_wrapped(screen, text, x, y, f, color, center, max_width)
        surface = f.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.centerx = x
        else:
            rect.x = x
        rect.y = y
        screen.blit(surface, rect)
        return y + rect.height + 4

    def _draw_wrapped(self, screen, text, x, y, font, color, center, max_width) -> int:
        words = text.split()
        lines, line = [], ""
        for word in words:
            test = f"{line} {word}".strip()
            if font.size(test)[0] <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        for ln in lines:
            surf = font.render(ln, True, color)
            rect = surf.get_rect()
            if center:
                rect.centerx = x
            else:
                rect.x = x
            rect.y = y
            screen.blit(surf, rect)
            y += rect.height + 6
        return y

    def draw_card(self, screen: pygame.Surface, x: int, y: int,
                  w: int, h: int,
                  color: tuple = COLOR_DARK_GRAY,
                  alpha: int = 200, radius: int = 16):
        """Dibuja un rectángulo redondeado semi-transparente."""
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color, alpha), (0, 0, w, h), border_radius=radius)
        screen.blit(surf, (x, y))

    def draw_progress_bar(self, screen: pygame.Surface,
                          x: int, y: int, w: int, h: int,
                          progress: float,
                          fg_color: tuple = COLOR_ACCENT,
                          bg_color: tuple = (40, 40, 40)):
        """Dibuja una barra de progreso (0.0 → 1.0)."""
        pygame.draw.rect(screen, bg_color, (x, y, w, h), border_radius=h // 2)
        if progress > 0:
            fill_w = int(w * min(progress, 1.0))
            pygame.draw.rect(screen, fg_color, (x, y, fill_w, h), border_radius=h // 2)

    def draw_finger_indicator(self, screen: pygame.Surface,
                              count: int, hold_progress: float,
                              x: int = None, y: int = None):
        """Muestra los dedos detectados + barra de confirmación (abajo-izquierda)."""
        if x is None:
            x = 10
        if y is None:
            y = SCREEN_HEIGHT - 82

        self.draw_card(screen, x, y, 155, 68, color=(20, 20, 20), alpha=190)
        self.draw_text(screen, f"{count} dedos", x + 78, y + 8,
                       size=20, bold=True, center=True)
        self.draw_progress_bar(screen, x + 10, y + 44, 135, 12, hold_progress)

    def draw_camera_preview(self, screen: pygame.Surface, cam_surface: pygame.Surface,
                            x: int = None, y: int = None):
        """Dibuja el preview de la webcam en la esquina inferior derecha."""
        from config import CAMERA_PREVIEW_W, CAMERA_PREVIEW_H
        if x is None:
            x = SCREEN_WIDTH - CAMERA_PREVIEW_W - 10
        if y is None:
            y = SCREEN_HEIGHT - CAMERA_PREVIEW_H - 10
        if cam_surface:
            preview = pygame.transform.scale(cam_surface, (CAMERA_PREVIEW_W, CAMERA_PREVIEW_H))
            pygame.draw.rect(screen, COLOR_ACCENT,
                             (x - 2, y - 2, CAMERA_PREVIEW_W + 4, CAMERA_PREVIEW_H + 4),
                             border_radius=6)
            screen.blit(preview, (x, y))

    def draw_visited_badges(self, screen: pygame.Surface,
                            visited_ids: list, y: int = 10):
        """Muestra íconos de los lugares visitados (para gamificación)."""
        from config import PLACES
        icons = {p["id"]: p["icon"] for p in PLACES.values()}
        x = 10
        for place_id, info in PLACES.items():
            pid = info["id"]
            icon_c = COLOR_ACCENT if pid in visited_ids else (60, 60, 60)
            self.draw_text(screen, info["icon"], x, y,
                           size=28, color=icon_c)
            x += 40
