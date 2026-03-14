"""
ui/screens/photo_screen.py
Pantalla de foto con RAMon (premio por visitar todos los lugares).
Muestra QR para que el usuario comparta su correo y reciba la foto.
5 dedos → tomar foto y guardar.
"""
import pygame
import os
import time
import datetime
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2, COLOR_SUCCESS,
    PHOTO_SAVE_DIR, GOOGLE_FORMS_URL, RAMON_PHOTO_IMAGE, SAFE_BOTTOM
)
from ui.screens.base_screen import BaseScreen
from data.places_content import get_text


class PhotoScreen(BaseScreen):

    STATE_PREVIEW   = "preview"
    STATE_COUNTDOWN = "countdown"
    STATE_CAPTURED  = "captured"
    STATE_QR        = "qr"

    def __init__(self, session_manager, tts, dispatcher, cam_frame_getter=None):
        super().__init__(session_manager, tts, dispatcher)
        self._get_cam_frame = cam_frame_getter   # función () → np.ndarray | None

    def on_enter(self):
        super().on_enter()
        self._lang     = self.session.current_language()
        self._state    = self.STATE_PREVIEW
        self._countdown = 3
        self._cd_start  = None
        self._photo_path = None
        self._qr_surface = None
        self._spoken    = False

        self.tts.speak(get_text("photo_prompt", self._lang),
                        lang=self._lang, block=False)

        # Cargar foto de RAMon para mostrar en pantalla de preview
        self._ramon_photo: pygame.Surface | None = None
        if os.path.isfile(RAMON_PHOTO_IMAGE):
            try:
                img = pygame.image.load(RAMON_PHOTO_IMAGE).convert_alpha()
                self._ramon_photo = pygame.transform.scale(img, (260, 380))
            except Exception as e:
                print(f"[Photo] Error cargando foto RAMon: {e}")

        os.makedirs(PHOTO_SAVE_DIR, exist_ok=True)
        self._generate_qr()

    def _generate_qr(self):
        try:
            import qrcode
            qr = qrcode.QRCode(box_size=4, border=2)
            qr.add_data(GOOGLE_FORMS_URL)
            qr.make(fit=True)
            img = qr.make_image(fill_color="white", back_color="black")
            # Convertir PIL image → Pygame surface
            img_rgb = img.convert("RGB")
            raw = img_rgb.tobytes()
            w, h = img_rgb.size
            self._qr_surface = pygame.image.fromstring(raw, (w, h), "RGB")
            print(f"[Photo] QR generado para: {GOOGLE_FORMS_URL}")
        except ImportError:
            print("[Photo] 'qrcode' no instalado. pip install qrcode[pil]")
        except Exception as e:
            print(f"[Photo] Error al generar QR: {e}")

    def update(self, dt, finger_count, gesture_engine):
        if self._state == self.STATE_PREVIEW:
            if finger_count == 5:
                gesture_engine.update(5)
                if gesture_engine.pop_confirmed():
                    self._state    = self.STATE_COUNTDOWN
                    self._cd_start = time.time()
            elif finger_count == 2:
                gesture_engine.update(2)
                if gesture_engine.pop_confirmed():
                    return "privacy"
            else:
                gesture_engine.reset()

        elif self._state == self.STATE_COUNTDOWN:
            elapsed = time.time() - self._cd_start
            self._countdown = max(0, 3 - int(elapsed))
            if elapsed >= 3.5:
                self._take_photo()
                self._state = self.STATE_CAPTURED

        elif self._state == self.STATE_CAPTURED:
            # Mostrar 3 segundos → ir a QR
            if not hasattr(self, "_cap_time"):
                self._cap_time = time.time()
                self.tts.speak(
                    {"en": "Great photo! Scan the QR code to receive it.",
                     "es": "¡Excelente foto! Escanea el QR para recibirla."}
                    .get(self._lang, "Scan the QR!"),
                    lang=self._lang, block=False
                )
            if time.time() - self._cap_time > 3.0:
                self._state = self.STATE_QR

        elif self._state == self.STATE_QR:
            # Cualquier gesto → ir a despedida
            if finger_count > 0:
                gesture_engine.update(finger_count)
                if gesture_engine.pop_confirmed():
                    return "farewell"
            else:
                gesture_engine.reset()

        return None

    def _take_photo(self):
        try:
            import cv2
            import numpy as np
            if self._get_cam_frame:
                frame = self._get_cam_frame()
                if frame is not None:
                    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = os.path.join(PHOTO_SAVE_DIR, f"foto_{ts}.jpg")
                    cv2.imwrite(path, frame)
                    self._photo_path = path
                    self.session.mark_photo_taken()
                    print(f"[Photo] Foto guardada: {path}")
        except Exception as e:
            print(f"[Photo] Error al tomar foto: {e}")

    def draw(self, screen, renderer):
        renderer.draw_background()
        renderer.draw_overlay(alpha=140)

        cx = SCREEN_WIDTH // 2
        lang = self._lang

        # Título
        self.draw_text(screen, get_text("prize_title", lang),
                       cx, 25, size=32, bold=True,
                       color=COLOR_ACCENT2, center=True)

        if self._state == self.STATE_PREVIEW:
            self.draw_text(screen, get_text("photo_prompt", lang),
                           cx, 90, size=24, color=COLOR_WHITE,
                           center=True, max_width=820)

            # RAMon centrado para la foto
            if self._ramon_photo:
                rx = SCREEN_WIDTH // 2 - 130
                ry = 105
                screen.blit(self._ramon_photo, (rx, ry))
            else:
                self._draw_ramon_photo_placeholder(screen, cx, 460)

            # Instrucciones (dos opciones)
            self.draw_card(screen, cx - 330, SAFE_BOTTOM - 90, 660, 72,
                           color=(15, 40, 15), alpha=220)
            self.draw_text(screen,
                           {"en": "Show 5 fingers to take photo!",
                            "es": "¡Muestra 5 dedos para la foto!"}
                           .get(lang, "5 fingers → Photo"),
                           cx, SAFE_BOTTOM - 80,
                           size=22, bold=True, color=COLOR_SUCCESS, center=True)
            self.draw_text(screen,
                           {"en": "2 fingers → Privacy Notice",
                            "es": "2 dedos → Aviso de privacidad"}
                           .get(lang, "2 fingers → Privacy"),
                           cx, SAFE_BOTTOM - 50,
                           size=18, color=(180, 200, 255), center=True)

            # QR preview (debajo de la cámara, esquina derecha)
            if self._qr_surface:
                qr_x = SCREEN_WIDTH - 190
                qr_y = 185
                screen.blit(self._qr_surface, (qr_x, qr_y))
                self.draw_text(screen,
                               {"en": "Share your email", "es": "Comparte tu correo"}
                               .get(lang, "Email"),
                               qr_x + self._qr_surface.get_width() // 2,
                               qr_y + self._qr_surface.get_height() + 6,
                               size=15, color=(180, 180, 180), center=True)

        elif self._state == self.STATE_COUNTDOWN:
            self.draw_text(screen, str(self._countdown + 1) if self._countdown < 3
                           else "3",
                           cx, SCREEN_HEIGHT // 2 - 40,
                           size=140, bold=True, color=COLOR_ACCENT2, center=True)
            self.draw_text(screen,
                           {"en": "Get ready!", "es": "¡Prepárate!"}
                           .get(lang, "Ready!"),
                           cx, SCREEN_HEIGHT // 2 + 90,
                           size=30, color=COLOR_WHITE, center=True)

        elif self._state in (self.STATE_CAPTURED, self.STATE_QR):
            self.draw_text(screen,
                           {"en": "[foto] Photo taken!", "es": "[foto] ¡Foto tomada!"}
                           .get(lang, "[foto] Done!"),
                           cx, 90, size=36, bold=True, color=COLOR_SUCCESS, center=True)

            if self._qr_surface:
                qr_s = pygame.transform.scale(self._qr_surface, (260, 260))
                screen.blit(qr_s, (cx - 130, 130))
                self.draw_text(screen,
                               {"en": "Scan to send yourself this photo by email!",
                                "es": "¡Escanea para recibir la foto en tu correo!"}
                               .get(lang, "Scan QR"),
                               cx, 400, size=22, color=COLOR_WHITE, center=True)

            if self._state == self.STATE_QR:
                self.draw_text(screen,
                               {"en": "Any gesture → Goodbye screen",
                                "es": "Cualquier gesto → Pantalla de despedida"}
                               .get(lang, "Continue..."),
                               cx, SCREEN_HEIGHT - 40,
                               size=18, color=(140, 140, 140), center=True)

    def _draw_ramon_photo_placeholder(self, screen, cx, cy):
        """Placeholder para foto con RAMon. Reemplazar con imagen real."""
        # Marco de foto
        pygame.draw.rect(screen, (200, 160, 80),
                         (cx - 200, cy - 240, 400, 320), 4, border_radius=12)
        # RAMon (placeholder simple)
        pygame.draw.circle(screen, (240, 200, 140), (cx, cy - 110), 60)
        pygame.draw.circle(screen, (30, 30, 30), (cx - 20, cy - 120), 9)
        pygame.draw.circle(screen, (30, 30, 30), (cx + 20, cy - 120), 9)
        pygame.draw.arc(screen, (30, 30, 30),
                        (cx - 22, cy - 103, 44, 24), 3.14, 0, 3)
        pygame.draw.ellipse(screen, (30, 90, 180), (cx - 65, cy - 40, 130, 160))
        # Etiqueta
        self.draw_text(screen, "[RAMon Photo Placeholder]",
                       cx, cy + 130, size=15, color=(100, 100, 100), center=True)
        # TODO: cuando tengas la imagen de RAMon:
        # ramon_img = pygame.image.load(RAMON_PHOTO_IMAGE).convert_alpha()
        # screen.blit(ramon_img, (cx - ramon_img.get_width()//2, cy - 200))
