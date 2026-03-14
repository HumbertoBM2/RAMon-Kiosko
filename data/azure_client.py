"""
data/azure_client.py
Envío de datos de sesión a Azure.
Soporta:
  - Azure Table Storage (sesiones completas al finalizar)
  - Azure IoT Hub (telemetría en tiempo real, opcional)

Documentación de setup: docs/AZURE_SETUP.md
"""
import json
import threading
from datetime import datetime, timezone
from config import (
    AZURE_CONNECTION_STRING, AZURE_TABLE_NAME,
    AZURE_PARTITION_KEY, AZURE_ENABLED,
    AZURE_IOT_HUB_CONN_STR, AZURE_IOT_HUB_ENABLED,
)


class AzureClient:
    """
    Cliente Azure para kiosko RAMon.

    Métodos principales:
        send_session(session_data: dict)     → envía sesión completa
        send_event(event_type, payload)      → telemetría en tiempo real
    """

    def __init__(self):
        self._table_client = None
        self._iot_client   = None

        if AZURE_ENABLED:
            self._init_table_storage()
        if AZURE_IOT_HUB_ENABLED:
            self._init_iot_hub()

    # ── Inicialización ─────────────────────────────────────────────

    def _init_table_storage(self):
        try:
            from azure.data.tables import TableServiceClient
            service = TableServiceClient.from_connection_string(
                conn_str=AZURE_CONNECTION_STRING
            )
            # Crea la tabla si no existe
            service.create_table_if_not_exists(table_name=AZURE_TABLE_NAME)
            self._table_client = service.get_table_client(
                table_name=AZURE_TABLE_NAME
            )
            print("[Azure] Table Storage inicializado correctamente.")
        except ImportError:
            print("[Azure] 'azure-data-tables' no instalado. pip install azure-data-tables")
        except Exception as e:
            print(f"[Azure] Error al inicializar Table Storage: {e}")

    def _init_iot_hub(self):
        try:
            from azure.iot.device import IoTHubDeviceClient
            self._iot_client = IoTHubDeviceClient.create_from_connection_string(
                AZURE_IOT_HUB_CONN_STR
            )
            self._iot_client.connect()
            print("[Azure IoT] Conectado al IoT Hub.")
        except ImportError:
            print("[Azure IoT] 'azure-iot-device' no instalado. pip install azure-iot-device")
        except Exception as e:
            print(f"[Azure IoT] Error al conectar: {e}")

    # ── API pública ────────────────────────────────────────────────

    def send_session(self, session_dict: dict, async_send: bool = True):
        """
        Envía los datos completos de una sesión a Azure Table Storage.
        session_dict: resultado de SessionData.to_dict()
        async_send: si True, no bloquea el hilo principal.
        """
        if not AZURE_ENABLED or self._table_client is None:
            print("[Azure] Envío desactivado / no configurado.")
            return

        if async_send:
            t = threading.Thread(
                target=self._upload_session, args=(session_dict,), daemon=True
            )
            t.start()
        else:
            self._upload_session(session_dict)

    def send_event(self, event_type: str, payload: dict,
                   async_send: bool = True):
        """
        Envía un evento de telemetría puntual a Azure IoT Hub.
        Útil para: language_selected, place_entered, question_asked, etc.
        """
        if not AZURE_IOT_HUB_ENABLED or self._iot_client is None:
            return

        message_body = json.dumps({
            "event":     event_type,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            **payload,
        })

        if async_send:
            t = threading.Thread(
                target=self._send_iot_message, args=(message_body,), daemon=True
            )
            t.start()
        else:
            self._send_iot_message(message_body)

    def is_connected(self) -> dict:
        return {
            "table_storage": self._table_client is not None,
            "iot_hub":       self._iot_client is not None,
        }

    def disconnect(self):
        if self._iot_client:
            try:
                self._iot_client.disconnect()
            except Exception:
                pass

    # ── Internos ───────────────────────────────────────────────────

    def _upload_session(self, session_dict: dict):
        try:
            entity = {
                "PartitionKey": AZURE_PARTITION_KEY,
                "RowKey":       session_dict["session_id"],
                **self._sanitize_for_table(session_dict),
            }
            self._table_client.upsert_entity(entity=entity)
            print(f"[Azure] Sesión enviada: {session_dict['session_id']}")
        except Exception as e:
            print(f"[Azure] Error al subir sesión: {e}")
            self._save_locally(session_dict)   # Fallback local

    def _send_iot_message(self, message_body: str):
        try:
            from azure.iot.device import Message
            msg = Message(message_body)
            msg.content_encoding = "utf-8"
            msg.content_type = "application/json"
            self._iot_client.send_message(msg)
        except Exception as e:
            print(f"[Azure IoT] Error al enviar mensaje: {e}")

    def _sanitize_for_table(self, d: dict) -> dict:
        """
        Azure Table Storage solo acepta str, int, float, bool, datetime.
        Convierte listas a strings JSON.
        """
        clean = {}
        for k, v in d.items():
            if isinstance(v, (str, int, float, bool)):
                clean[k] = v
            elif v is None:
                clean[k] = ""
            else:
                clean[k] = str(v)
        return clean

    def _save_locally(self, session_dict: dict):
        """Guarda la sesión en JSON local si Azure falla."""
        import os
        folder = "failed_uploads"
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{session_dict['session_id']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session_dict, f, ensure_ascii=False, indent=2)
        print(f"[Azure] Sesión guardada localmente → {path}")

    def retry_failed_uploads(self):
        """
        Intenta reenviar las sesiones que fallaron previamente.
        Llamar al inicio de la aplicación si hay conexión.
        """
        import os, glob
        if not AZURE_ENABLED or self._table_client is None:
            return
        for path in glob.glob("failed_uploads/*.json"):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            try:
                self._upload_session(data)
                os.remove(path)
                print(f"[Azure] Reenvío exitoso: {path}")
            except Exception:
                pass
