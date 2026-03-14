"""
voice/speech_to_text.py
Voz a texto con Whisper (local) o Google Speech Recognition.
Motor recomendado: Whisper (funciona offline, soporta todos los idiomas del proyecto).
"""
import threading
import queue
import numpy as np
import sounddevice as sd
from config import (
    STT_ENGINE, WHISPER_MODEL, WHISPER_LANGUAGE,
    AUDIO_SAMPLE_RATE, MAX_RECORD_SECONDS
)


# Códigos de idioma ISO 639-1 → BCP-47 para Google Speech API
_GOOGLE_LANG_MAP = {
    "en": "en-US",
    "es": "es-MX",
    "fr": "fr-FR",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "pl": "pl-PL",
    "sv": "sv-SE",
    "uk": "uk-UA",
}


class SpeechToText:
    """
    Graba audio del micrófono y lo convierte a texto.

    Uso:
        stt = SpeechToText()
        text = stt.listen(lang="en", timeout=10)   # bloqueante
        # ó
        stt.start_listening(lang="en")
        # ... hacer otras cosas ...
        text = stt.stop_and_get_result()
    """

    def __init__(self, engine: str = STT_ENGINE):
        self.engine_name = engine
        self._whisper_model = None
        self._recording = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._result_queue: queue.Queue = queue.Queue()
        self._listen_thread: threading.Thread | None = None

        if engine == "whisper":
            self._load_whisper()

    def _load_whisper(self):
        try:
            import whisper
            print(f"[STT] Cargando Whisper ({WHISPER_MODEL})...")
            self._whisper_model = whisper.load_model(WHISPER_MODEL)
            print("[STT] Whisper listo.")
        except ImportError:
            print("[STT] openai-whisper no instalado. Cambiando a Google STT.")
            self.engine_name = "google"
        except Exception as e:
            print(f"[STT] Whisper no disponible ({e}). Cambiando a Google STT.")
            self.engine_name = "google"

    # ── API simple (bloqueante) ────────────────────────────────────

    def listen(self, lang: str = "en", timeout: float = MAX_RECORD_SECONDS) -> str:
        """
        Graba por `timeout` segundos y retorna el texto reconocido.
        """
        audio_data = self._record(timeout)
        if audio_data is None:
            return ""
        return self._transcribe(audio_data, lang)

    # ── API no-bloqueante (para UI) ────────────────────────────────

    def start_listening(self, lang: str = "en",
                        timeout: float = MAX_RECORD_SECONDS):
        """Inicia grabación en hilo separado."""
        if self._recording:
            return
        self._recording = True
        self._listen_thread = threading.Thread(
            target=self._listen_worker,
            args=(lang, timeout),
            daemon=True
        )
        self._listen_thread.start()

    def stop_and_get_result(self, wait: bool = True) -> str | None:
        """
        Detiene la grabación y retorna el resultado.
        Si wait=True, bloquea hasta que haya resultado.
        Retorna None si no hay resultado todavía.
        """
        self._recording = False
        if wait:
            try:
                return self._result_queue.get(timeout=MAX_RECORD_SECONDS + 5)
            except queue.Empty:
                return ""
        else:
            try:
                return self._result_queue.get_nowait()
            except queue.Empty:
                return None

    def is_listening(self) -> bool:
        return self._recording

    # ── Internos ───────────────────────────────────────────────────

    def _listen_worker(self, lang: str, timeout: float):
        audio_data = self._record(timeout)
        result = self._transcribe(audio_data, lang) if audio_data is not None else ""
        self._result_queue.put(result)
        self._recording = False

    def _record(self, duration: float) -> np.ndarray | None:
        """Graba `duration` segundos de audio mono 16kHz."""
        try:
            print(f"[STT] Grabando {duration}s...")
            recording = sd.rec(
                int(duration * AUDIO_SAMPLE_RATE),
                samplerate=AUDIO_SAMPLE_RATE,
                channels=1,
                dtype="float32",
            )
            sd.wait()
            print("[STT] Grabación completa.")
            return recording.flatten()
        except Exception as e:
            print(f"[STT] Error al grabar: {e}")
            return None

    def _transcribe(self, audio: np.ndarray, lang: str) -> str:
        if self.engine_name == "whisper":
            return self._transcribe_whisper(audio, lang)
        else:
            return self._transcribe_google(audio, lang)

    def _transcribe_whisper(self, audio: np.ndarray, lang: str) -> str:
        try:
            if self._whisper_model is None:
                return ""
            result = self._whisper_model.transcribe(
                audio,
                language=WHISPER_LANGUAGE or lang[:2],
                fp16=False,
            )
            text = result.get("text", "").strip()
            print(f"[STT] Whisper → '{text}'")
            return text
        except Exception as e:
            print(f"[STT] Error Whisper: {e}")
            return ""

    def _transcribe_google(self, audio: np.ndarray, lang: str = "en") -> str:
        try:
            import speech_recognition as sr
            import tempfile, os, wave

            # Guardar audio como WAV temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            with wave.open(tmp_path, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(AUDIO_SAMPLE_RATE)
                wf.writeframes((audio * 32767).astype(np.int16).tobytes())

            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_path) as source:
                audio_data = recognizer.record(source)
            os.unlink(tmp_path)

            google_lang = _GOOGLE_LANG_MAP.get(lang, f"{lang}-{lang.upper()}")
            text = recognizer.recognize_google(audio_data, language=google_lang)
            print(f"[STT] Google ({google_lang}) → '{text}'")
            return text
        except Exception as e:
            print(f"[STT] Error Google: {e}")
            return ""
