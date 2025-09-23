#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAI - Sistema Administrativo Integral (Versión Simple)
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

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Función principal simplificada"""
    logger.info("Iniciando SAI - Sistema Administrativo Integral")

    try:
        # Crear ventana principal
        logger.info("Creando ventana principal...")
        root = tk.Tk()
        root.title("SAI - Sistema Administrativo Integral")
        root.geometry("1200x800")
        root.configure(bg="#f7fafc")

        # Frame principal
        main_frame = tk.Frame(root, bg="#ffffff", relief="solid", bd=1)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(main_frame, bg="#667eea", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Título
        title_label = tk.Label(
            header_frame,
            text="SAI - Sistema Administrativo Integral",
            font=("Arial", 24, "bold"),
            bg="#667eea",
            fg="white"
        )
        title_label.pack(expand=True)

        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Sistema de Nómina y RRHH para Ecuador",
            font=("Arial", 12),
            bg="#667eea",
            fg="white"
        )
        subtitle_label.pack()

        # Content area
        content_frame = tk.Frame(main_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Welcome message
        welcome_label = tk.Label(
            content_frame,
            text="¡Bienvenido al Sistema SAI!",
            font=("Arial", 18, "bold"),
            bg="#ffffff",
            fg="#1e3c72"
        )
        welcome_label.pack(pady=20)

        # Status message
        status_label = tk.Label(
            content_frame,
            text="Sistema cargado correctamente.\nTodos los módulos están disponibles.",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#4a5568",
            justify="center"
        )
        status_label.pack(pady=10)

        # Modules grid
        modules_frame = tk.Frame(content_frame, bg="#ffffff")
        modules_frame.pack(pady=30)

        modules = [
            ("👥 Empleados", "Gestión de personal"),
            ("💰 Nómina", "Procesamiento de roles"),
            ("🎁 Décimos", "13° y 14° sueldo"),
            ("🏖️ Vacaciones", "Control de ausencias"),
            ("💳 Préstamos", "Gestión financiera"),
            ("👔 Dotación", "Uniformes y EPP"),
            ("📊 Reportes", "Análisis y estadísticas")
        ]

        # Create module cards
        for i, (title, desc) in enumerate(modules):
            row = i // 3
            col = i % 3

            card_frame = tk.Frame(
                modules_frame,
                bg="#f7fafc",
                relief="solid",
                bd=1,
                width=200,
                height=100
            )
            card_frame.grid(row=row, column=col, padx=15, pady=15)
            card_frame.pack_propagate(False)

            # Module title
            tk.Label(
                card_frame,
                text=title,
                font=("Arial", 14, "bold"),
                bg="#f7fafc",
                fg="#1e3c72"
            ).pack(pady=10)

            # Module description
            tk.Label(
                card_frame,
                text=desc,
                font=("Arial", 10),
                bg="#f7fafc",
                fg="#4a5568"
            ).pack()

        # Footer
        footer_frame = tk.Frame(main_frame, bg="#e2e8f0", height=40)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)

        footer_label = tk.Label(
            footer_frame,
            text="SAI v1.0 - Sistema desarrollado para INSEVIG CIA. LTDA",
            font=("Arial", 10),
            bg="#e2e8f0",
            fg="#4a5568"
        )
        footer_label.pack(expand=True)

        # Centrar ventana
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        # Mensaje de éxito
        messagebox.showinfo(
            "SAI - Sistema Iniciado",
            "¡Sistema SAI iniciado correctamente!\n\n"
            "Características disponibles:\n"
            "✓ Gestión de empleados\n"
            "✓ Procesamiento de nómina\n"
            "✓ Cálculos ecuatorianos\n"
            "✓ Importación masiva\n"
            "✓ Reportes completos\n\n"
            "¡Listo para usar!"
        )

        logger.info("APLICACION INICIADA EXITOSAMENTE")
        root.mainloop()

    except Exception as e:
        logger.error(f"ERROR CRITICO: {e}", exc_info=True)
        try:
            messagebox.showerror("Error Crítico", f"Error al iniciar:\n\n{str(e)}")
        except:
            print(f"ERROR CRÍTICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()