#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componente de Dialogo de Progreso - Sistema SGN
Dialogo reutilizable para mostrar progreso de operaciones
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

class ProgressDialog:
    """Dialogo de progreso reutilizable"""

    def __init__(self, parent, title="Procesando...", message="Por favor espere..."):
        self.parent = parent
        self.title = title
        self.message = message
        self.cancelled = False
        self.window = None
        self.progress_var = None
        self.message_var = None
        self.progress_bar = None

    def show(self, max_value=100, show_cancel=True):
        """Mostrar dialogo de progreso"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(self.title)
        self.window.geometry("400x150")
        self.window.transient(self.parent)
        self.window.grab_set()

        # Centrar ventana
        self.window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))

        # No permitir redimensionar
        self.window.resizable(False, False)

        # Frame principal
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Icono y mensaje
        message_frame = tk.Frame(main_frame, bg='white')
        message_frame.pack(fill=tk.X, pady=(0, 20))

        # Icono de procesamiento
        icon_label = tk.Label(
            message_frame,
            text="⏳",
            font=('Arial', 20),
            bg='white'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # Mensaje
        self.message_var = tk.StringVar(value=self.message)
        message_label = tk.Label(
            message_frame,
            textvariable=self.message_var,
            font=('Arial', 11),
            bg='white',
            wraplength=300
        )
        message_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Barra de progreso
        progress_frame = tk.Frame(main_frame, bg='white')
        progress_frame.pack(fill=tk.X, pady=(0, 20))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=max_value,
            length=360
        )
        self.progress_bar.pack(fill=tk.X)

        # Porcentaje
        self.percentage_var = tk.StringVar(value="0%")
        percentage_label = tk.Label(
            progress_frame,
            textvariable=self.percentage_var,
            font=('Arial', 9),
            bg='white',
            fg='#666'
        )
        percentage_label.pack(pady=(5, 0))

        # Botón cancelar (opcional)
        if show_cancel:
            cancel_button = tk.Button(
                main_frame,
                text="Cancelar",
                command=self.cancel,
                bg='#e53e3e',
                fg='white',
                font=('Arial', 10, 'bold'),
                relief=tk.FLAT,
                padx=20,
                pady=8
            )
            cancel_button.pack()

        # Protocolo para cerrar ventana
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)

        return self

    def update_progress(self, value, message=None):
        """Actualizar progreso"""
        if self.window and not self.cancelled:
            self.progress_var.set(value)

            # Calcular porcentaje
            max_val = self.progress_bar['maximum']
            percentage = (value / max_val) * 100 if max_val > 0 else 0
            self.percentage_var.set(f"{percentage:.1f}%")

            if message:
                self.message_var.set(message)

            self.window.update()

    def set_indeterminate(self):
        """Configurar barra como indeterminada"""
        if self.progress_bar:
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start()
            self.percentage_var.set("Procesando...")

    def cancel(self):
        """Cancelar operación"""
        self.cancelled = True
        if self.window:
            self.window.destroy()

    def close(self):
        """Cerrar dialogo"""
        if self.window:
            self.window.destroy()

    def is_cancelled(self):
        """Verificar si fue cancelado"""
        return self.cancelled


class ProcessingManager:
    """Gestor de procesos con dialogo de progreso"""

    def __init__(self, parent):
        self.parent = parent
        self.progress_dialog = None

    def execute_with_progress(self, task_func, title="Procesando...", message="Por favor espere...",
                            show_cancel=True, args=None, kwargs=None):
        """
        Ejecutar tarea con dialogo de progreso

        Args:
            task_func: Función a ejecutar
            title: Título del dialogo
            message: Mensaje inicial
            show_cancel: Mostrar botón cancelar
            args: Argumentos para la función
            kwargs: Argumentos con nombre para la función
        """
        args = args or []
        kwargs = kwargs or {}

        # Crear dialogo
        self.progress_dialog = ProgressDialog(self.parent, title, message)
        self.progress_dialog.show(show_cancel=show_cancel)

        # Función wrapper para pasar el dialogo a la tarea
        def task_wrapper():
            try:
                result = task_func(self.progress_dialog, *args, **kwargs)
                return result
            except Exception as e:
                self.progress_dialog.close()
                raise e

        # Ejecutar en thread separado
        thread = threading.Thread(target=task_wrapper)
        thread.daemon = True
        thread.start()

        return self.progress_dialog

    def simulate_long_process(self, progress_dialog, steps=10, delay=0.5):
        """Simular proceso largo para pruebas"""
        for i in range(steps + 1):
            if progress_dialog.is_cancelled():
                break

            progress_dialog.update_progress(
                i * (100 / steps),
                f"Procesando paso {i} de {steps}..."
            )
            time.sleep(delay)

        if not progress_dialog.is_cancelled():
            progress_dialog.update_progress(100, "¡Proceso completado!")
            time.sleep(0.5)
            progress_dialog.close()


# Funciones utilitarias para usar en módulos
def show_loading_dialog(parent, title="Cargando...", message="Por favor espere..."):
    """Mostrar dialogo de carga simple"""
    dialog = ProgressDialog(parent, title, message)
    dialog.show(show_cancel=False)
    dialog.set_indeterminate()
    return dialog

def show_progress_dialog(parent, title="Procesando...", message="Por favor espere...", max_value=100):
    """Mostrar dialogo de progreso"""
    dialog = ProgressDialog(parent, title, message)
    dialog.show(max_value=max_value)
    return dialog

def execute_with_loading(parent, task_func, title="Procesando...", message="Por favor espere..."):
    """Ejecutar tarea con indicador de carga"""
    manager = ProcessingManager(parent)
    return manager.execute_with_progress(
        task_func, title, message, show_cancel=False
    )