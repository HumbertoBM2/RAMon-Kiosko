"""
ui/renderer.py
Motor de renderizado de medios para el kiosko.
Soporta:
  - Fondo sólido (color)
  - Imagen estática (.jpg, .png)
  - GIF animado (via Pillow)
  - Video en loop (via OpenCV)
Uso:
    renderer = MediaRenderer(screen)
    renderer.set_background_color((0, 0, 0))
    renderer.set_background_image("path/to/image.jpg")
    renderer.set_background_video("path/to/video.mp4")
    # En el loop principal:
    renderer.draw_background()
"""
import os
import pygame
import numpy as np
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG


class MediaRenderer:
    """
    Renderiza fondos (color sólido, imagen, GIF, video) sobre una superficie Pygame.
    Los textos/widgets de la pantalla se dibujan ENCIMA después de llamar draw_background().
    """

    MODE_COLOR = "color"
    MODE_IMAGE = "image"
    MODE_GIF   = "gif"
    MODE_VIDEO = "video"

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._mode  = self.MODE_COLOR
        self._color = COLOR_BG

        # Imagen estática
        self._bg_surface: pygame.Surface | None = None

        # GIF animado
        self._gif_frames: list[pygame.Surface] = []
        self._gif_idx: int = 0
        self._gif_delays: list[int] = []     # ms por frame
        self._gif_last_tick: int = 0

        # Video (OpenCV)
        self._video_cap = None
        self._video_frame_surface: pygame.Surface | None = None

    # ── Setters de modo ────────────────────────────────────────────

    def set_background_color(self, color: tuple = COLOR_BG):
        self._mode  = self.MODE_COLOR
        self._color = color
        self._release_video()

    def set_background_image(self, path: str):
        """Carga una imagen estática como fondo."""
        if not path or not os.path.isfile(path):
            print(f"[Renderer] Imagen no encontrada: {path!r}, usando fondo negro.")
            self.set_background_color()
            return
        try:
            img = pygame.image.load(path).convert()
            self._bg_surface = pygame.transform.scale(
                img, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            self._mode = self.MODE_IMAGE
            self._release_video()
            print(f"[Renderer] Imagen cargada: {path}")
        except Exception as e:
            print(f"[Renderer] Error al cargar imagen {path}: {e}")
            self.set_background_color()

    def set_background_gif(self, path: str):
        """Carga un GIF animado como fondo usando Pillow."""
        if not path or not os.path.isfile(path):
            print(f"[Renderer] GIF no encontrado: {path!r}, usando fondo negro.")
            self.set_background_color()
            return
        try:
            from PIL import Image, ImageSequence
            gif = Image.open(path)
            self._gif_frames = []
            self._gif_delays = []
            for frame in ImageSequence.Iterator(gif):
                frame_rgb = frame.convert("RGBA")
                frame_scaled = frame_rgb.resize((SCREEN_WIDTH, SCREEN_HEIGHT))
                raw = frame_scaled.tobytes("raw", "RGBA")
                surface = pygame.image.fromstring(
                    raw, (SCREEN_WIDTH, SCREEN_HEIGHT), "RGBA"
                ).convert_alpha()
                self._gif_frames.append(surface)
                self._gif_delays.append(frame.info.get("duration", 80))
            self._gif_idx = 0
            self._gif_last_tick = pygame.time.get_ticks()
            self._mode = self.MODE_GIF
            self._release_video()
            print(f"[Renderer] GIF cargado: {path} ({len(self._gif_frames)} frames)")
        except Exception as e:
            print(f"[Renderer] Error al cargar GIF {path}: {e}")
            self.set_background_color()

    def set_background_video(self, path: str):
        """Carga un video como fondo usando OpenCV (se reproduce en loop)."""
        if not path or not os.path.isfile(path):
            print(f"[Renderer] Video no encontrado: {path!r}, usando fondo negro.")
            self.set_background_color()
            return
        try:
            import cv2
            self._release_video()
            self._video_cap = cv2.VideoCapture(path)
            if not self._video_cap.isOpened():
                raise ValueError("No se pudo abrir el video")
            self._mode = self.MODE_VIDEO
            print(f"[Renderer] Video cargado: {path}")
        except Exception as e:
            print(f"[Renderer] Error al cargar video {path}: {e}")
            self.set_background_color()

    # ── Carga automática (intenta video > imagen > color) ──────────

    def load_place_background(self, bg_video: str, bg_image: str):
        """
        Carga el fondo de un lugar.
        Intenta video primero, luego imagen, luego fondo negro.
        """
        if bg_video and os.path.isfile(bg_video):
            self.set_background_video(bg_video)
        elif bg_image and os.path.isfile(bg_image):
            self.set_background_image(bg_image)
        else:
            self.set_background_color()

    # ── Dibujado (llamar en cada frame del loop) ───────────────────

    def draw_background(self):
        if self._mode == self.MODE_COLOR:
            self.screen.fill(self._color)

        elif self._mode == self.MODE_IMAGE and self._bg_surface:
            self.screen.blit(self._bg_surface, (0, 0))

        elif self._mode == self.MODE_GIF and self._gif_frames:
            self._advance_gif()
            self.screen.blit(self._gif_frames[self._gif_idx], (0, 0))

        elif self._mode == self.MODE_VIDEO and self._video_cap:
            self._draw_video_frame()

        else:
            self.screen.fill(COLOR_BG)

    # ── Overlay semi-transparente (para legibilidad de texto) ──────

    def draw_overlay(self, alpha: int = 160, color: tuple = (0, 0, 0)):
        """
        Dibuja un overlay oscuro semi-transparente encima del fondo.
        Mejora la legibilidad del texto sobre fondos visuales.
        alpha: 0 (invisible) → 255 (opaco)
        """
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((*color, alpha))
        self.screen.blit(overlay, (0, 0))

    # ── Internos ───────────────────────────────────────────────────

    def _advance_gif(self):
        now = pygame.time.get_ticks()
        delay = self._gif_delays[self._gif_idx] if self._gif_delays else 80
        if now - self._gif_last_tick >= delay:
            self._gif_idx = (self._gif_idx + 1) % len(self._gif_frames)
            self._gif_last_tick = now

    def _draw_video_frame(self):
        import cv2
        ret, frame = self._video_cap.read()
        if not ret:
            # Loop: reiniciar video
            self._video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._video_cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_scaled = cv2.resize(
                frame_rgb, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            surface = pygame.surfarray.make_surface(
                np.transpose(frame_scaled, (1, 0, 2))
            )
            self.screen.blit(surface, (0, 0))

    def _release_video(self):
        if self._video_cap:
            self._video_cap.release()
            self._video_cap = None
