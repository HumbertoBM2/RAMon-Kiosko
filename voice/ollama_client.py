"""
voice/ollama_client.py
Cliente para el LLM local (Ollama).
Construye el prompt de sistema con contexto del lugar y el idioma,
y retorna la respuesta de RAMon de manera sincrónica o en streaming.
"""
import requests
import json
import threading
from config import (
    OLLAMA_BASE_URL, OLLAMA_MODEL,
    OLLAMA_TIMEOUT, OLLAMA_SYSTEM_PROMPT_TEMPLATE
)

# Mapa código ISO → nombre de idioma en inglés (para el prompt)
_LANG_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French",
    "ja": "Japanese", "ko": "Korean", "pl": "Polish",
    "sv": "Swedish", "uk": "Ukrainian",
}


class OllamaClient:
    """
    Wrapper simplificado para la API de Ollama.

    Uso:
        client = OllamaClient()
        response = client.ask(
            question="What is special about Barrio Antiguo?",
            place="Barrio Antiguo",
            lang="en"
        )
        print(response)
    """

    def __init__(self,
                 base_url: str = OLLAMA_BASE_URL,
                 model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._chat_url = f"{self.base_url}/api/chat"
        self._generate_url = f"{self.base_url}/api/generate"

    # ── API principal ──────────────────────────────────────────────

    def ask(self, question: str, place: str = "", lang: str = "en") -> str:
        """
        Envía una pregunta a Ollama y retorna la respuesta completa como string.
        Bloqueante. Usar ask_async para uso en hilos.
        """
        system_prompt = self._build_system_prompt(place, lang)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": question},
        ]
        payload = {
            "model":    self.model,
            "messages": messages,
            "stream":   False,
        }
        try:
            resp = requests.post(
                self._chat_url,
                json=payload,
                timeout=OLLAMA_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "").strip()
        except requests.exceptions.ConnectionError:
            return self._offline_fallback(lang)
        except Exception as e:
            print(f"[Ollama] Error: {e}")
            return self._offline_fallback(lang)

    def ask_async(self, question: str, place: str = "", lang: str = "en",
                  callback=None):
        """
        Versión no-bloqueante. callback(response: str) se llama al completar.
        """
        def worker():
            result = self.ask(question, place, lang)
            if callback:
                callback(result)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return t

    def ask_stream(self, question: str, place: str = "", lang: str = "en",
                   on_token=None, on_done=None):
        """
        Streaming: on_token(token: str) se llama por cada token,
        on_done(full_text: str) al finalizar.
        """
        system_prompt = self._build_system_prompt(place, lang)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": question},
        ]
        payload = {
            "model":    self.model,
            "messages": messages,
            "stream":   True,
        }

        def worker():
            full_text = ""
            try:
                with requests.post(
                    self._chat_url, json=payload,
                    timeout=OLLAMA_TIMEOUT, stream=True
                ) as resp:
                    resp.raise_for_status()
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("message", {}).get("content", "")
                        full_text += token
                        if on_token and token:
                            on_token(token)
                        if chunk.get("done"):
                            break
            except Exception as e:
                print(f"[Ollama] Stream error: {e}")
                full_text = self._offline_fallback(lang)
            if on_done:
                on_done(full_text)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return t

    def is_available(self) -> bool:
        """Verifica si Ollama está corriendo."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Lista los modelos disponibles en Ollama."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    # ── Internos ───────────────────────────────────────────────────

    def _build_system_prompt(self, place: str, lang: str) -> str:
        lang_name = _LANG_NAMES.get(lang, "English")
        return OLLAMA_SYSTEM_PROMPT_TEMPLATE.format(
            lang=lang_name,
            place=place or "Monterrey, Nuevo León"
        )

    def _offline_fallback(self, lang: str) -> str:
        _fallbacks = {
            "en": "I'm sorry, I can't answer right now. Please try again.",
            "es": "Lo siento, no puedo responder ahora. Por favor intenta de nuevo.",
            "fr": "Désolé, je ne peux pas répondre maintenant. Veuillez réessayer.",
            "ja": "申し訳ありませんが、今は答えられません。後でお試しください。",
            "ko": "죄송합니다, 지금은 답변할 수 없습니다. 다시 시도해 주세요.",
            "pl": "Przepraszam, nie mogę teraz odpowiedzieć. Proszę spróbować ponownie.",
            "sv": "Förlåt, jag kan inte svara nu. Försök igen.",
            "uk": "Вибачте, я не можу відповісти зараз. Спробуйте ще раз.",
        }
        return _fallbacks.get(lang, _fallbacks["en"])
