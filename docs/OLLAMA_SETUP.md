# 🦙 OLLAMA SETUP — Kiosko RAMon 2026

Guía para instalar y configurar Ollama como motor de IA local para las
preguntas de voz en el kiosko.

---

## 1. Instalar Ollama

### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS
```bash
brew install ollama
# ó descarga el installer desde https://ollama.com/download
```

### Windows
Descarga el instalador desde: https://ollama.com/download/windows

---

## 2. Descargar el modelo recomendado

```bash
# Modelo recomendado: llama3.2 (3B parámetros, rápido, multilingüe)
ollama pull llama3.2

# Alternativa más pequeña (para computadoras con menos RAM):
ollama pull llama3.2:1b

# Alternativa con mejor multilingüe:
ollama pull mistral

# Para verificar que se descargó:
ollama list
```

### Requisitos de hardware por modelo

| Modelo          | RAM necesaria | Velocidad estimada |
|-----------------|---------------|--------------------|
| `llama3.2:1b`   | 2 GB          | Muy rápido (~1s)   |
| `llama3.2`      | 4 GB          | Rápido (~2-3s)     |
| `mistral`       | 6 GB          | Moderado (~4s)     |
| `llama3.1:8b`   | 8 GB          | Lento (~8s)        |

---

## 3. Iniciar el servidor de Ollama

```bash
# Inicia Ollama como servidor (escucha en localhost:11434)
ollama serve

# Verificar que está corriendo:
curl http://localhost:11434/api/tags
```

Para que arranque automáticamente al iniciar la computadora:

### Linux (systemd)
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

### macOS (launchd)
Ollama app se arranca automáticamente con el instalador de macOS.

---

## 4. Configurar en el kiosko

En tu archivo `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

## 5. El prompt del sistema (RAMon)

El kiosko usa este prompt para cada conversación:
> _"You are RAMon, the friendly tourism guide mascot for Nuevo León, México,
> during the FIFA World Cup 2026. Answer warmly, briefly (2-4 sentences),
> and in the visitor's language. Focus only on tourism, culture, food,
> and activities in Nuevo León."_

Este prompt se puede personalizar en `config.py` → `OLLAMA_SYSTEM_PROMPT_TEMPLATE`.

---

## 6. Probar manualmente

```bash
# Prueba directa por terminal
ollama run llama3.2

# Luego escribe:
> Tell me about Barrio Antiguo in Monterrey in English
```

O con curl:
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [
    {"role": "user", "content": "What is special about Barrio Antiguo in Monterrey?"}
  ],
  "stream": false
}'
```

---

## 7. Idiomas soportados

Los modelos `llama3.2` y `mistral` tienen buen soporte de:
- ✅ Inglés, Español, Francés
- ✅ Japonés, Coreano
- ⚠️ Polaco, Sueco, Ucraniano (funcional pero menor calidad)

Para mejores resultados con idiomas asiáticos/europeos orientales:
```bash
ollama pull qwen2.5:3b   # Mejor soporte de asiáticos
```

---

## 8. Correr Ollama y el kiosko al mismo tiempo

Terminal 1:
```bash
ollama serve
```

Terminal 2:
```bash
cd /ruta/al/kiosko
python main.py
```

---

## Troubleshooting

| Error                            | Solución                                              |
|----------------------------------|-------------------------------------------------------|
| `Connection refused localhost:11434` | Correr `ollama serve` primero                    |
| Respuesta muy lenta              | Cambiar a `llama3.2:1b` en `.env`                    |
| Modelo no encontrado             | `ollama pull llama3.2`                               |
| GPU no detectada                 | Instalar drivers CUDA / Metal (se usa CPU de fallback)|
| Responde en idioma incorrecto    | El prompt incluye el idioma → verificar `config.py`   |
