"""
core/session_manager.py
Gestión y recolección de datos de cada sesión de usuario.
Los datos se envían a Azure + MySQL al finalizar la sesión.
"""
import time
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional
from config import TOTAL_PLACES, DEFAULT_LANGUAGE


@dataclass
class SessionData:
    """Datos completos de una sesión."""
    session_id:       str   = field(default_factory=lambda: str(uuid.uuid4()))
    start_time:       float = field(default_factory=time.time)
    end_time:         Optional[float] = None

    language:         str   = DEFAULT_LANGUAGE
    places_visited:   list  = field(default_factory=list)   # ["barrio_antiguo", ...]
    questions_asked:  list  = field(default_factory=list)   # preguntas de texto
    photo_taken:      bool  = False
    email_provided:   bool  = False
    visitor_email:    str   = ""
    completed_tour:   bool  = False   # visitó todos los lugares

    # Métricas derivadas (se calculan al cerrar sesión)
    duration_seconds: float = 0.0
    most_visited_place: str = ""
    total_questions:  int   = 0

    def to_dict(self) -> dict:
        return {
            "session_id":         self.session_id,
            "start_time":         datetime.fromtimestamp(
                                    self.start_time, tz=timezone.utc
                                  ).isoformat(),
            "end_time":           datetime.fromtimestamp(
                                    self.end_time or time.time(), tz=timezone.utc
                                  ).isoformat(),
            "duration_seconds":   round(self.duration_seconds, 2),
            "language":           self.language,
            "places_visited":     ",".join(self.places_visited),
            "most_visited_place": self.most_visited_place,
            "total_questions":    self.total_questions,
            "photo_taken":        self.photo_taken,
            "email_provided":     self.email_provided,
            "visitor_email":      self.visitor_email,
            "completed_tour":     self.completed_tour,
        }


class SessionManager:
    """
    Maneja el ciclo completo de una sesión.
    """

    def __init__(self):
        self._session: Optional[SessionData] = None

    # ── Ciclo de sesión ────────────────────────────────────────────

    def start(self):
        """Inicia una nueva sesión."""
        self._session = SessionData()
        print(f"[Session] Iniciada → {self._session.session_id}")

    def end(self) -> Optional[SessionData]:
        """
        Cierra la sesión, calcula métricas y retorna los datos.
        """
        if not self._session:
            return None

        s = self._session
        s.end_time = time.time()
        s.duration_seconds = s.end_time - s.start_time
        s.total_questions = len(s.questions_asked)
        s.completed_tour = (
            len(set(s.places_visited)) >= TOTAL_PLACES
        )

        # Lugar más visitado
        if s.places_visited:
            from collections import Counter
            counter = Counter(s.places_visited)
            s.most_visited_place = counter.most_common(1)[0][0]

        print(f"[Session] Cerrada → duración {s.duration_seconds:.1f}s")
        data = self._session
        self._session = None
        return data

    def is_active(self) -> bool:
        return self._session is not None

    # ── Registro de eventos ────────────────────────────────────────

    def set_language(self, lang_code: str):
        if self._session:
            self._session.language = lang_code

    def visit_place(self, place_id: str):
        if self._session:
            self._session.places_visited.append(place_id)
            print(f"[Session] Lugar visitado: {place_id}")

    def add_question(self, question_text: str):
        if self._session:
            self._session.questions_asked.append(question_text)

    def mark_photo_taken(self):
        if self._session:
            self._session.photo_taken = True

    def set_email(self, email: str):
        if self._session:
            self._session.visitor_email = email
            self._session.email_provided = bool(email)

    # ── Consultas de estado ────────────────────────────────────────

    @property
    def visited_place_ids(self) -> list:
        return list(set(self._session.places_visited)) if self._session else []

    def all_places_visited(self) -> bool:
        if not self._session:
            return False
        return len(set(self._session.places_visited)) >= TOTAL_PLACES

    def current_language(self) -> str:
        return self._session.language if self._session else DEFAULT_LANGUAGE
