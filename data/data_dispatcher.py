"""
data/data_dispatcher.py
Distribuye datos de sesión a todos los destinos: Azure + MySQL + API Node.js.
Se llama al finalizar cada sesión.
"""
import json
import requests
import threading
from config import API_BASE_URL, API_ENABLED
from data.azure_client import AzureClient
from data.local_db import LocalDB


class DataDispatcher:
    """
    Singleton que mantiene las conexiones a todos los backends
    y los llama al final de cada sesión.
    """

    def __init__(self):
        self.azure = AzureClient()
        self.db    = LocalDB()
        print("[Dispatcher] Backends inicializados.")
        # Reintentos de sesiones fallidas
        self.azure.retry_failed_uploads()

    # ── Envío de sesión completa ───────────────────────────────────

    def dispatch_session(self, session_dict: dict):
        """
        Envía la sesión a todos los backends de manera no-bloqueante.
        Llamar al finalizar sesión: dispatcher.dispatch_session(session.to_dict())
        """
        t = threading.Thread(
            target=self._send_all, args=(session_dict,), daemon=True
        )
        t.start()

    def _send_all(self, session_dict: dict):
        # 1. Azure Table Storage
        self.azure.send_session(session_dict, async_send=False)

        # 2. MySQL local
        self.db.save_session(session_dict)

        # 3. Node.js API
        if API_ENABLED:
            self._post_to_api(session_dict)

    # ── Telemetría en tiempo real ──────────────────────────────────

    def emit_event(self, event_type: str, session_id: str, extra: dict = None):
        """
        Emite un evento de telemetría puntual.
        Llamar en: idioma seleccionado, lugar visitado, pregunta hecha, etc.
        """
        payload = {"session_id": session_id, **(extra or {})}

        # Azure IoT Hub (tiempo real)
        self.azure.send_event(event_type, payload)

        # MySQL eventos
        self.db.log_event(event_type, payload)

    # ── Node.js API ────────────────────────────────────────────────

    def _post_to_api(self, session_dict: dict):
        try:
            resp = requests.post(
                f"{API_BASE_URL}/api/sessions",
                json=session_dict,
                timeout=10,
            )
            if resp.status_code in (200, 201):
                print(f"[API] Sesión enviada a Node.js: {session_dict['session_id']}")
            else:
                print(f"[API] Respuesta inesperada: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            print("[API] No se pudo conectar a la API de Node.js (¿está corriendo?)")
        except Exception as e:
            print(f"[API] Error: {e}")

    def close(self):
        self.db.close()
        self.azure.disconnect()
