"""
voice/text_to_speech.py
Texto a voz con soporte para múltiples idiomas.
Motores disponibles:
  - gTTS (Google TTS, requiere internet, mejor calidad de idiomas)
  - pyttsx3 (offline, limitado en idiomas no latinos)
"""
import os
import sys
import io
import threading
import tempfile
from config import TTS_ENGINE, TTS_SPEED_GTTS


class TextToSpeech:
    """
    Interfaz unificada de TTS.

    Uso:
        tts = TextToSpeech()
        tts.speak("Hello, welcome to Monterrey!", lang="en")
        tts.speak("こんにちは", lang="ja")
    """

    def __init__(self, engine: str = TTS_ENGINE):
        self.engine_name = engine
        self._engine = None
        self._is_speaking = False   # True desde que arranca el hilo hasta que termina
        self._init_engine()

    def _init_engine(self):
        if self.engine_name == "pyttsx3":
            try:
                import pyttsx3
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", 160)
            except ImportError:
                print("[TTS] pyttsx3 no instalado, usando gTTS como fallback")
                self.engine_name = "gtts"
        # gTTS no requiere inicialización previa

    # ─────────────────────────────────────────────────────────────────

    def speak(self, text: str, lang: str = "en", block: bool = True):
        """
        Convierte texto a voz y lo reproduce.
        block=True → espera a que termine antes de retornar.
        block=False → reproduce en hilo separado (no bloqueante).
        """
        if not text:
            return

        if not block:
            self._is_speaking = True
            def _run():
                try:
                    self._speak_internal(text, lang)
                finally:
                    self._is_speaking = False
            t = threading.Thread(target=_run, daemon=True)
            t.start()
        else:
            self._speak_internal(text, lang)

    def _speak_internal(self, text: str, lang: str):
        if self.engine_name == "gtts":
            self._speak_gtts(text, lang)
        else:
            self._speak_pyttsx3(text)

    def _speak_gtts(self, text: str, lang: str):
        try:
            from gtts import gTTS
            import pygame

            tts = gTTS(text=text, lang=lang, slow=False)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_path = f.name
            tts.save(tmp_path)

            # Reproducir con pygame.mixer (ya inicializado por la app)
            if pygame.mixer.get_init():
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            else:
                # Fallback: reproducir con playsound si pygame no está listo
                try:
                    import playsound
                    playsound.playsound(tmp_path)
                except Exception:
                    pass

            os.unlink(tmp_path)
        except Exception as e:
            print(f"[TTS] Error gTTS: {e}")

    def _speak_pyttsx3(self, text: str):
        try:
            if self._engine:
                self._engine.say(text)
                self._engine.runAndWait()
        except Exception as e:
            print(f"[TTS] Error pyttsx3: {e}")

    def is_speaking(self) -> bool:
        """True si el TTS está reproduciendo audio en este momento."""
        if self._is_speaking:
            return True
        try:
            import pygame
            if pygame.mixer.get_init():
                return bool(pygame.mixer.music.get_busy())
        except Exception:
            pass
        return False

    def stop(self):
        """Detiene la reproducción actual."""
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass
