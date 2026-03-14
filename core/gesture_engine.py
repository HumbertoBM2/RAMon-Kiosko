"""
core/gesture_engine.py
Motor de gestos con lógica de temporización.
Convierte lecturas instantáneas de dedos en gestos confirmados
(el usuario debe mantener N dedos por X segundos para confirmar).
"""
import time
from config import (
    WAVE_FINGERS_REQUIRED, WAVE_HOLD_SECONDS,
    GESTURE_HOLD_SECONDS, GESTURE_COOLDOWN
)


class GestureEngine:
    """
    Rastrea cuántos dedos se han mostrado de forma continua y
    emite un evento 'confirmed' cuando se cumple el tiempo requerido.

    Uso básico:
        engine = GestureEngine()
        engine.update(finger_count)
        if engine.confirmed_gesture is not None:
            handle(engine.confirmed_gesture)
            engine.reset()
    """

    def __init__(self):
        self._current_fingers: int = 0
        self._hold_start: float = 0.0
        self._last_confirmed_at: float = 0.0
        self.confirmed_gesture: int | None = None   # se llena al confirmar
        self.hold_progress: float = 0.0             # 0.0 → 1.0 (para progress bar)

    # ── API pública ────────────────────────────────────────────────

    def update(self, finger_count: int,
               required: int | None = None,
               hold_secs: float | None = None) -> None:
        """
        Llamar en cada frame con la cantidad de dedos detectados.

        required  → fuerza un número específico de dedos (None = cualquiera > 0)
        hold_secs → tiempo de espera personalizado (None = usa GESTURE_HOLD_SECONDS)
        """
        now = time.time()
        hold_needed = hold_secs if hold_secs is not None else GESTURE_HOLD_SECONDS

        # Cooldown: evitar doble disparo
        if now - self._last_confirmed_at < GESTURE_COOLDOWN:
            self.hold_progress = 0.0
            return

        # ¿Es el gesto que esperamos?
        is_valid = (
            (required is None and finger_count > 0) or
            (required is not None and finger_count == required)
        )

        if not is_valid:
            self._reset_hold()
            return

        # ¿Cambió el número de dedos?
        if finger_count != self._current_fingers:
            self._current_fingers = finger_count
            self._hold_start = now
            self.hold_progress = 0.0
            return

        # Mismo gesto: calcular progreso
        elapsed = now - self._hold_start
        self.hold_progress = min(elapsed / hold_needed, 1.0)

        if elapsed >= hold_needed:
            self.confirmed_gesture = finger_count
            self._last_confirmed_at = now
            self.hold_progress = 1.0

    def update_wave(self, finger_count: int) -> bool:
        """
        Método específico para detectar saludo (WAVE_FINGERS_REQUIRED dedos
        mantenidos por WAVE_HOLD_SECONDS).
        Acepta 4 ó 5 dedos para evitar resets por fluctuaciones del pulgar.
        Retorna True cuando el saludo es confirmado.
        """
        # Normalizar: 4 o 5 dedos = mano abierta
        normalized = WAVE_FINGERS_REQUIRED if finger_count >= WAVE_FINGERS_REQUIRED - 1 else finger_count
        self.update(normalized,
                    required=WAVE_FINGERS_REQUIRED,
                    hold_secs=WAVE_HOLD_SECONDS)
        if self.confirmed_gesture == WAVE_FINGERS_REQUIRED:
            self.reset()
            return True
        return False

    def pop_confirmed(self) -> int | None:
        """
        Retorna el gesto confirmado y lo limpia.
        Usar en lugar de acceder directamente a `confirmed_gesture`.
        """
        gesture = self.confirmed_gesture
        if gesture is not None:
            self.confirmed_gesture = None
        return gesture

    def reset(self):
        """Resetea el estado del engine (llamar tras procesar un gesto)."""
        self._reset_hold()
        self.confirmed_gesture = None

    # ── Internos ───────────────────────────────────────────────────

    def _reset_hold(self):
        self._current_fingers = 0
        self._hold_start = 0.0
        self.hold_progress = 0.0
