# Kiosko RAMon — Instrucciones de Desinstalación

Sigue los pasos según lo que quieras eliminar.

---

## 1. Detener la aplicación

Si el kiosko está corriendo, ciérralo con `Ctrl+C` en la terminal donde fue lanzado.

---

## 2. Desinstalar Ollama (LLM local)

```bash
# Detener y deshabilitar el servicio
sudo systemctl stop ollama
sudo systemctl disable ollama

# Borrar el binario
sudo rm -f /usr/local/bin/ollama

# Borrar todos los modelos descargados (~2 GB por modelo)
rm -rf ~/.ollama

# (Opcional) Borrar el archivo de servicio systemd
sudo rm -f /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
```

---

## 3. Borrar la base de datos MySQL

```bash
mysql -u root -p
```

Dentro del prompt de MySQL:

```sql
DROP DATABASE IF EXISTS kiosko_ramon;
EXIT;
```

---

## 4. Borrar el entorno virtual de Python

Si existe un `venv/` dentro del proyecto:

```bash
rm -rf /home/humberto/Downloads/kiosko/venv
```

---

## 5. Desinstalar paquetes Python del sistema (opcional)

Solo si los instalaste a nivel de sistema y no te sirven para otras cosas:

```bash
pip3 uninstall -y pygame speechrecognition pyttsx3 requests \
    python-dotenv qrcode pillow opencv-python
```

---

## 6. Detener y borrar la API de Node.js

```bash
# Si usas PM2
pm2 delete kiosko-api
pm2 save

# Borrar dependencias de Node
rm -rf /home/humberto/Downloads/kiosko/IoT-Medicine-Container-Optimization/API_codes/node_modules
```

---

## 7. Borrar la carpeta completa del proyecto

```bash
rm -rf /home/humberto/Downloads/kiosko
```

> **Advertencia:** Esto borra el código fuente, assets (`aesthetic/`), el `.env` y todo lo demás. Haz un respaldo antes si es necesario.

---

## Resumen rápido (todo de un jalón)

```bash
sudo systemctl stop ollama && sudo systemctl disable ollama
sudo rm -f /usr/local/bin/ollama
rm -rf ~/.ollama
mysql -u root -p -e "DROP DATABASE IF EXISTS kiosko_ramon;"
rm -rf /home/humberto/Downloads/kiosko
```
