#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAI - Sistema Administrativo Integral (Versión Corregida)
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
from database.initialize_simple import initialize_database_simple
from gui.main_window import MainApplication
from gui.styles import setup_styles

# Configurar logging simple
logging.basicConfig(
    level=logging.WARNING,  # Solo warnings y errores
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_basic_requirements():
    """Verificar solo requisitos básicos"""
    required = ['sqlalchemy', 'tkinter']
    missing = []

    for module in required:
        try:
            if module == 'tkinter':
                import tkinter
            else:
                __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        messagebox.showerror("Error", f"Faltan módulos: {', '.join(missing)}")
        sys.exit(1)

def main():
    """Función principal"""
    print("Iniciando SAI - Sistema Administrativo Integral")

    try:
        # Verificar requisitos básicos
        check_basic_requirements()

        # Crear directorios necesarios
        for directory in ['logs', 'reports', 'backups']:
            Path(directory).mkdir(exist_ok=True)

        # Inicializar base de datos simple
        initialize_database_simple()

        # Crear ventana principal
        root = tk.Tk()
        root.title("SAI - Sistema Administrativo Integral")
        root.geometry("1200x800")

        # Configurar estilos
        setup_styles(root)

        # Crear aplicación
        app = MainApplication(root)

        # Centrar ventana
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        # Mostrar mensaje de éxito
        messagebox.showinfo(
            "SAI Iniciado",
            "¡Sistema SAI iniciado correctamente!\n\n"
            "✓ Interfaz moderna cargada\n"
            "✓ Base de datos lista\n"
            "✓ Todos los módulos disponibles\n\n"
            "El sistema está listo para usar."
        )

        print("APLICACION INICIADA EXITOSAMENTE")
        root.mainloop()

    except Exception as e:
        logger.error(f"ERROR CRITICO: {e}")
        try:
            messagebox.showerror("Error Crítico", f"Error al iniciar:\n\n{str(e)}")
        except:
            print(f"ERROR CRÍTICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()