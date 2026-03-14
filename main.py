"""
main.py
Punto de entrada del Kiosko RAMon — Turismo Monterrey 2026
"""
import sys
import os

# Asegura que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    # Crea directorios de assets si no existen
    _ensure_asset_dirs()

    from ui.kiosk_app import KioskApp
    app = KioskApp()
    app.run()


def _ensure_asset_dirs():
    """Crea la estructura de carpetas de assets si no existe."""
    asset_dirs = [
        "ui/assets/backgrounds",
        "ui/assets/mascot",
        "ui/assets/places/barrio_antiguo",
        "ui/assets/places/fashion_drive",
        "ui/assets/places/estadio_bbva",
        "ui/assets/places/santiago_pm",
        "ui/assets/fonts",
        "captured_photos",
        "failed_uploads",
    ]
    for d in asset_dirs:
        os.makedirs(d, exist_ok=True)


if __name__ == "__main__":
    main()
