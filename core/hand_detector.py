"""
core/hand_detector.py
Detección de manos con MediaPipe.
Provee:
  - count_fingers(hand_landmarks)  → int  (0-5 por mano)
  - is_open_hand(hand_landmarks)   → bool (5 dedos extendidos)
"""
import mediapipe as mp
import cv2
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class HandDetector:
    """
    Wrapper de MediaPipe Hands.

    Uso:
        detector = HandDetector()
        while True:
            ret, frame = cap.read()
            results = detector.process(frame)
            fingers = detector.count_fingers(results)
    """

    # Índices de los 4 dedos (excluyendo pulgar) — tip y pip
    FINGER_TIPS  = [8, 12, 16, 20]        # punta de índice, medio, anular, meñique
    FINGER_PIPS  = [6, 10, 14, 18]        # segunda articulación

    # Pulgar: tip y mcp (en vez de pip porque se dobla lateralmente)
    THUMB_TIP    = 4
    THUMB_IP     = 3
    THUMB_MCP    = 2

    def __init__(self, max_hands: int = 1,
                 min_detection_confidence: float = 0.75,
                 min_tracking_confidence: float = 0.75):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, frame: np.ndarray):
        """
        Procesa un frame BGR de OpenCV.
        Retorna el objeto results de MediaPipe.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True
        return results

    def count_fingers(self, results) -> int:
        """
        Cuenta dedos extendidos de la primera mano detectada.
        Retorna 0 si no hay mano.
        """
        if not results.multi_hand_landmarks:
            return 0

        hand_lm = results.multi_hand_landmarks[0]
        lm = hand_lm.landmark

        # Determinar si la mano está de frente o de espaldas
        # usando la posición del pulgar respecto a la muñeca
        hand_info = results.multi_handedness[0].classification[0]
        is_right_hand = hand_info.label == "Right"

        count = 0

        # ── Pulgar ──────────────────────────────────────────────────
        # Para mano derecha: pulgar extendido si x_tip > x_mcp
        # Para mano izquierda: pulgar extendido si x_tip < x_mcp
        # (la imagen está en espejo por defecto)
        if is_right_hand:
            if lm[self.THUMB_TIP].x > lm[self.THUMB_MCP].x:
                count += 1
        else:
            if lm[self.THUMB_TIP].x < lm[self.THUMB_MCP].x:
                count += 1

        # ── Otros 4 dedos ────────────────────────────────────────────
        for tip, pip_ in zip(self.FINGER_TIPS, self.FINGER_PIPS):
            if lm[tip].y < lm[pip_].y:    # punta arriba respecto a articulación
                count += 1

        return count

    def is_open_hand(self, results) -> bool:
        """True si se detectan 5 dedos extendidos."""
        return self.count_fingers(results) == 5

    def draw_landmarks(self, frame: np.ndarray, results) -> np.ndarray:
        """Dibuja los landmarks de la mano sobre el frame (para debug)."""
        if results.multi_hand_landmarks:
            for hand_lm in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_lm,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )
        return frame

    def release(self):
        self.hands.close()
