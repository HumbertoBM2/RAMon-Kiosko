"""
ui/screens/qa_screen.py
Pantalla de preguntas al LLM (Ollama local) por voz.
Estados: LISTENING → THINKING → ANSWERING → CHOICE
"""
import pygame
import time
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_ACCENT, COLOR_ACCENT2, COLOR_SUCCESS,
    MAX_RECORD_SECONDS, SAFE_BOTTOM, RAMON_PHOTO_IMAGE
)
from ui.screens.base_screen import BaseScreen
from data.places_content import get_text


class QAScreen(BaseScreen):

    STATE_LISTENING  = "listening"
    STATE_THINKING   = "thinking"
    STATE_ANSWERING  = "answering"
    STATE_CHOICE     = "choice"

    def __init__(self, session_manager, tts, dispatcher, stt, ollama, place_id: str = ""):
        super().__init__(session_manager, tts, dispatcher)
        self.stt     = stt
        self.ollama  = ollama
        self.place_id = place_id

    def set_place(self, place_id: str):
        self.place_id = place_id

    def on_enter(self):
        super().on_enter()
        self._lang         = self.session.current_language()
        self._state        = self.STATE_LISTENING
        self._question      = ""
        self._answer        = ""
        self._answer_shown  = 0
        self._answer_spoken = False
        self._elapsed       = 0.0
        self._pulse         = 0.0
        self._status_msg    = ""
        self._transition_to = None

        # Prompt de voz
        prompt = get_text("qa_prompt", self._lang)
        self.tts.speak(prompt, lang=self._lang, block=False)

        # Cargar foto de RAMon (pequeña para esquina superior)
        import os
        self._ramon_small: pygame.Surface | None = None
        if os.path.isfile(RAMON_PHOTO_IMAGE):
            try:
                img = pygame.image.load(RAMON_PHOTO_IMAGE).convert_alpha()
                self._ramon_small = pygame.transform.scale(img, (80, 80))
            except Exception:
                pass

        # La grabación NO inicia aquí — espera a que TTS termine (ver update)
        self._recording_started = False
        self._listen_start = None

    def update(self, dt, finger_count, gesture_engine):
        self._elapsed += dt
        self._pulse = (self._pulse + dt * 3) % (2 * math.pi)

        # ── LISTENING ──────────────────────────────────────────────
        if self._state == self.STATE_LISTENING:
            # Esperar a que el TTS termine antes de grabar
            if not self._recording_started:
                if not self.tts.is_speaking():
                    self.stt.start_listening(lang=self._lang, timeout=MAX_RECORD_SECONDS)
                    self._listen_start = time.time()
                    self._recording_started = True
                return None   # no checar STT hasta que empiece a grabar

            # Resultado disponible (sin bloquear)
            result = self.stt.stop_and_get_result(wait=False)
            time_up = (time.time() - self._listen_start) > MAX_RECORD_SECONDS + 1

            if result is not None:
                # Google ya respondió
                self._process_stt_result(result)
            elif time_up:
                # Grabación terminó pero Google aún no responde;
                # esperar en hilo para no bloquear la UI
                self._state = self.STATE_THINKING
                self._elapsed = 0.0
                import threading
                threading.Thread(target=self._wait_for_stt_result, daemon=True).start()

        # ── THINKING: esperar respuesta de Ollama ──────────────────
        elif self._state == self.STATE_THINKING:
            # La respuesta se recibe vía callback → ver _on_ollama_answer
            pass

        # ── ANSWERING: mostrar respuesta con typewriter ────────────
        elif self._state == self.STATE_ANSWERING:
            speed = 35
            self._answer_shown = min(
                len(self._answer),
                int(self._elapsed * speed)
            )
            # Avanzar a choice cuando el TTS termina de hablar
            if self._answer_spoken and not self.tts.is_speaking():
                self._state = self.STATE_CHOICE
                self._elapsed = 0.0

        # ── CHOICE: preguntar de nuevo o volver ────────────────────
        elif self._state == self.STATE_CHOICE:
            if finger_count in (1, 2):
                gesture_engine.update(finger_count)
                confirmed = gesture_engine.pop_confirmed()
                if confirmed == 1:
                    self.on_enter()     # preguntar otra vez
                elif confirmed == 2:
                    return "places_menu"
            else:
                gesture_engine.reset()

        if self._transition_to:
            t = self._transition_to
            self._transition_to = None
            return t

        return None

    def _wait_for_stt_result(self):
        """Hilo: espera a que Google devuelva la transcripción y la procesa."""
        result = self.stt.stop_and_get_result(wait=True)
        self._process_stt_result(result)

    def _process_stt_result(self, result):
        """Procesa el texto reconocido: va a Ollama o muestra 'no te escuché'."""
        self._question = result.strip() if result else ""
        if self._question:
            self.session.add_question(self._question)
            self.dispatch.emit_event(
                "question_asked",
                self.session._session.session_id if self.session._session else "",
                {"question": self._question, "place": self.place_id}
            )
            self._state = self.STATE_THINKING
            self._elapsed = 0.0
            self._ask_ollama()
        else:
            self._answer = {
                "en": "I didn't catch that. Try again or go back to the menu.",
                "es": "No te escuché. Intenta de nuevo o vuelve al menú.",
                "fr": "Je n'ai pas entendu. Réessayez ou revenez au menu.",
                "ja": "聴き取れませんでした。もう一度お試しください。",
                "ko": "듣리지 못했습니다. 다시 시도해주세요.",
            }.get(self._lang, "I didn't catch that. Please try again.")
            self._answer_shown = len(self._answer)
            self._answer_spoken = False
            self._state = self.STATE_CHOICE

    def _ask_ollama(self):
        from data.places_content import PLACES_CONTENT
        place_name = (PLACES_CONTENT.get(self.place_id, {})
                      .get("name", {})
                      .get(self._lang, self.place_id))

        self.ollama.ask_async(
            question=self._question,
            place=place_name,
            lang=self._lang,
            callback=self._on_ollama_answer,
        )

    def _on_ollama_answer(self, answer: str):
        self._answer        = answer
        self._answer_shown  = 0
        self._elapsed       = 0.0
        self._answer_spoken = True          # marcamos antes de hablar
        self._state         = self.STATE_ANSWERING
        # Empezar a leer en voz alta de inmediato, en paralelo con el typewriter
        self.tts.speak(self._answer, lang=self._lang, block=False)

    def draw(self, screen, renderer):
        renderer.draw_background()
        renderer.draw_overlay(alpha=150)

        cx = SCREEN_WIDTH // 2
        lang = self._lang

        # Ícono RAMon — foto real o fallback texto
        if getattr(self, "_ramon_small", None):
            screen.blit(self._ramon_small, (cx - 40, 18))
            self.draw_text(screen, "RAMon  Q&A",
                           cx, 108, size=28, bold=True,
                           color=COLOR_ACCENT2, center=True)
        else:
            self.draw_text(screen, "[RAMon]", cx, 30, size=42, center=True)
            self.draw_text(screen, "RAMon  Q&A",
                           cx, 85, size=30, bold=True,
                           color=COLOR_ACCENT2, center=True)

        if self._state == self.STATE_LISTENING:
            # Animación de onda sonora
            pulse = abs(math.sin(self._pulse)) * 40
            r = int(60 + pulse)
            pygame.draw.circle(screen, (*COLOR_ACCENT, 120),
                               (cx, SCREEN_HEIGHT // 2), r + 20)
            pygame.draw.circle(screen, COLOR_ACCENT,
                               (cx, SCREEN_HEIGHT // 2), r, 3)
            self.draw_text(screen, "" + get_text("qa_prompt", lang),
                           cx, SCREEN_HEIGHT // 2 + r + 30,
                           size=24, color=COLOR_WHITE,
                           center=True, max_width=700)
            if self._listen_start is not None:
                bar_prog = min(1.0, (time.time() - self._listen_start) / MAX_RECORD_SECONDS)
            else:
                bar_prog = 0.0
            self.draw_progress_bar(screen, cx - 200, SAFE_BOTTOM - 45,
                                   400, 14, bar_prog, fg_color=(200, 60, 60))

        elif self._state == self.STATE_THINKING:
            dots = "." * (int(self._elapsed * 3) % 4)
            self.draw_text(screen,
                           {
                               "en": f"RAMon is thinking{dots}",
                               "es": f"RAMon está pensando{dots}",
                           }.get(lang, f"Thinking{dots}"),
                           cx, SCREEN_HEIGHT // 2 - 30,
                           size=30, color=COLOR_ACCENT, center=True)
            if self._question:
                self.draw_card(screen, cx - 300, SCREEN_HEIGHT // 2 + 20,
                               600, 60, alpha=150)
                self.draw_text(screen, f'"? {self._question}"',
                               cx, SCREEN_HEIGHT // 2 + 34,
                               size=20, color=(200, 200, 200),
                               center=True, max_width=580)

        elif self._state in (self.STATE_ANSWERING, self.STATE_CHOICE):
            # Pregunta
            if self._question:
                self.draw_card(screen, cx - 350, 135, 700, 58, alpha=150)
                self.draw_text(screen, f'"? {self._question}"',
                               cx, 148, size=20,
                               color=(180, 180, 180), center=True, max_width=680)

            # Respuesta
            self.draw_card(screen, 40, 205, SCREEN_WIDTH - 80, 280,
                           color=(20, 40, 70), alpha=200)
            self.draw_text(screen,
                           self._answer[:self._answer_shown] if self._state == self.STATE_ANSWERING
                           else self._answer,
                           60, 218, size=22, color=COLOR_WHITE,
                           max_width=SCREEN_WIDTH - 120)

            if self._state == self.STATE_CHOICE:
                self.draw_card(screen, cx - 350, SAFE_BOTTOM - 72,
                               700, 52, color=(20, 20, 50), alpha=210)
                self.draw_text(screen, get_text("qa_again", lang),
                               cx, SAFE_BOTTOM - 59,
                               size=20, color=COLOR_WHITE, center=True)
