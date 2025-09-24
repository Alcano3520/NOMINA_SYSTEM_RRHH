#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGN - Sistema de Gestión de Nómina
Sistema de Nómina y RRHH para Ecuador
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

# Importaciones locales
from config import Config
from database.initialize import initialize_database
from gui.main_window import MainApplication
from gui.styles import setup_styles

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/sgn_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_requirements():
    """Verificar que todos los requisitos estén instalados"""
    # Módulos requeridos (críticos)
    required_modules = [
        'sqlalchemy', 'pandas', 'openpyxl'
    ]

    # Módulos opcionales (deseables pero no críticos)
    optional_modules = [
        'reportlab', 'matplotlib', 'PIL', 'tkcalendar'
    ]

    missing_required = []
    missing_optional = []

    # Verificar módulos requeridos
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"[OK] Módulo {module} disponible")
        except ImportError:
            missing_required.append(module)
            logger.warning(f"[FALTA] Módulo {module} faltante")

    # Verificar módulos opcionales
    for module in optional_modules:
        try:
            __import__(module)
            logger.info(f"[OK] Módulo opcional {module} disponible")
        except ImportError:
            missing_optional.append(module)
            logger.warning(f"[OPCIONAL] Módulo opcional {module} faltante")

    # Solo fallar si faltan módulos críticos
    if missing_required:
        error_msg = f"Módulos críticos faltantes:\n{', '.join(missing_required)}\n\n"
        error_msg += f"Instale con: pip install {' '.join(missing_required)}"

        # Crear ventana temporal para mostrar error
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Dependencias Faltantes", error_msg)
        temp_root.destroy()
        sys.exit(1)

    # Advertir sobre módulos opcionales faltantes
    if missing_optional:
        logger.warning(f"Módulos opcionales faltantes: {', '.join(missing_optional)}")
        logger.warning("Algunas funciones pueden estar limitadas")

def main():
    """Función principal"""
    logger.info("Iniciando SGN - Sistema de Gestión de Nómina")

    try:
        # Verificar requisitos
        logger.info("Verificando requisitos...")
        check_requirements()
        logger.info("[OK] Verificación de requisitos completada")

        # Crear directorios necesarios
        logger.info("Creando directorios necesarios...")
        for directory in ['logs', 'reports', 'backups']:
            Path(directory).mkdir(exist_ok=True)
        logger.info("[OK] Directorios creados")

        # Inicializar base de datos
        logger.info("Inicializando base de datos...")
        initialize_database()
        logger.info("[OK] Base de datos inicializada correctamente")

        # Crear ventana principal
        logger.info("Creando ventana principal...")
        root = tk.Tk()
        root.title("SGN - Sistema de Gestión de Nómina")
        root.geometry("1200x800")
        logger.info("[OK] Ventana principal creada")

        # Configurar estilos
        logger.info("Configurando estilos...")
        setup_styles(root)
        logger.info("[OK] Estilos configurados")

        # Crear aplicación
        logger.info("Creando aplicación principal...")
        app = MainApplication(root)
        logger.info("[OK] Aplicación creada")

        # Centrar ventana
        logger.info("Centrando ventana...")
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        logger.info("[OK] Ventana centrada")

        # Iniciar aplicación
        logger.info("APLICACION INICIADA EXITOSAMENTE - Mostrando ventana")
        root.mainloop()

    except Exception as e:
        logger.error(f"ERROR CRITICO en main(): {e}", exc_info=True)

        # Crear ventana temporal para mostrar error
        try:
            temp_root = tk.Tk()
            temp_root.withdraw()
            messagebox.showerror("Error Crítico", f"Error al iniciar la aplicación:\n\n{str(e)}")
            temp_root.destroy()
        except:
            print(f"ERROR CRÍTICO: {e}")

        sys.exit(1)

if __name__ == "__main__":
    main()