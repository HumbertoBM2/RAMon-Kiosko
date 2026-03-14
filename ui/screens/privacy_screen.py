"""
ui/screens/privacy_screen.py
Pantalla de aviso de privacidad.
Muestra QR para el PDF del aviso y texto informativo.
Cualquier gesto → regresar a la pantalla de foto.
"""
import pygame
import os
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2, SAFE_BOTTOM
)
from ui.screens.base_screen import BaseScreen

PRIVACY_URL = (
    "https://tecmx-my.sharepoint.com/:b:/g/personal/a01236733_tec_mx/"
    "IQBlUKFpr3ZCQbCjhESB9X-oARZEyb46FB2DqB14PoJNWUc?e=fh5pyM"
)

_QR_CACHE: pygame.Surface | None = None   # se genera una sola vez


def _build_qr(url: str, size: int) -> "pygame.Surface | None":
    global _QR_CACHE
    if _QR_CACHE is not None:
        return pygame.transform.scale(_QR_CACHE, (size, size))
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=5, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="white", back_color=(20, 20, 40))
        img_rgb = img.convert("RGB")
        raw = img_rgb.tobytes()
        w, h = img_rgb.size
        surf = pygame.image.fromstring(raw, (w, h), "RGB")
        _QR_CACHE = surf
        return pygame.transform.scale(surf, (size, size))
    except Exception as e:
        print(f"[Privacy] QR error: {e}")
        return None


class PrivacyScreen(BaseScreen):

    def on_enter(self):
        super().on_enter()
        self._lang = self.session.current_language()
        self._qr   = _build_qr(PRIVACY_URL, 240)

    def update(self, dt, finger_count, gesture_engine):
        if finger_count > 0:
            gesture_engine.update(finger_count)
            if gesture_engine.pop_confirmed():
                return "photo"
        else:
            gesture_engine.reset()
        return None

    def draw(self, screen, renderer):
        renderer.draw_background()
        renderer.draw_overlay(alpha=200)

        cx = SCREEN_WIDTH // 2
        PAD = 30
        W   = SCREEN_WIDTH - PAD * 2

        # ── Título ─────────────────────────────────────────────────
        self.draw_text(screen,
                       {"en": "Privacy Notice", "es": "Aviso de Privacidad"}
                       .get(self._lang, "Privacy Notice"),
                       cx, 22, size=36, bold=True,
                       color=COLOR_ACCENT2, center=True)

        # ── Línea separadora ───────────────────────────────────────
        pygame.draw.line(screen, COLOR_ACCENT,
                         (PAD, 72), (SCREEN_WIDTH - PAD, 72), 2)

        # ── Texto del aviso ────────────────────────────────────────
        texts = {
            "en": [
                "Your photo will be stored on this kiosk temporarily",
                "and may be sent to the email you provide.",
                "",
                "The data collected (email, photo) is used exclusively",
                "for sending you the souvenir photo of your visit.",
                "",
                "We do not share your data with third parties.",
                "Scan the QR code to read the full privacy notice.",
            ],
            "es": [
                "Tu foto se almacenará temporalmente en este kiosko",
                "y podrá enviarse al correo que proporciones.",
                "",
                "Los datos recabados (correo, foto) se usan exclusivamente",
                "para enviarte la foto recuerdo de tu visita.",
                "",
                "No compartimos tus datos con terceros.",
                "Escanea el código QR para leer el aviso completo.",
            ],
        }
        lines = texts.get(self._lang, texts["es"])
        text_x = PAD
        text_y = 88
        for line in lines:
            if line:
                self.draw_text(screen, line, text_x, text_y,
                               size=20, color=COLOR_WHITE, max_width=W - 270)
            text_y += 28

        # ── QR ─────────────────────────────────────────────────────
        if self._qr:
            qr_x = SCREEN_WIDTH - PAD - 240
            qr_y = 85
            # Marco
            pygame.draw.rect(screen, COLOR_ACCENT,
                             (qr_x - 4, qr_y - 4, 248, 248), 2,
                             border_radius=6)
            screen.blit(self._qr, (qr_x, qr_y))
            self.draw_text(screen,
                           {"en": "Full notice", "es": "Aviso completo"}
                           .get(self._lang, "Full notice"),
                           qr_x + 120, qr_y + 252,
                           size=16, color=(180, 180, 180), center=True)

        # ── Botón de regreso ───────────────────────────────────────
        self.draw_card(screen, cx - 260, SAFE_BOTTOM - 68,
                       520, 52, color=(40, 20, 20), alpha=220)
        self.draw_text(screen,
                       {"en": "Any gesture → Back to photo",
                        "es": "Cualquier gesto → Volver a foto"}
                       .get(self._lang, "Any gesture → Back"),
                       cx, SAFE_BOTTOM - 55,
                       size=20, color=COLOR_ACCENT2, center=True)
