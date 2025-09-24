#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LoginWindow - Sistema SAI
Ventana de login principal del sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from auth.auth_manager import auth_manager, AuthenticationError

class LoginWindow:
    """Ventana principal de login"""

    def __init__(self, on_success_callback=None):
        self.on_success_callback = on_success_callback
        self.login_successful = False
        self.authenticated_user = None

        # Crear ventana principal
        self.root = tk.Tk()
        self.setup_window()
        self.create_ui()

    def setup_window(self):
        """Configurar ventana de login"""
        self.root.title("SAI - Sistema de Nómina Ecuador")
        self.root.geometry("500x600")
        self.root.configure(bg=Config.COLORS['background'])
        self.root.resizable(False, False)

        # Centrar ventana
        self.center_window()

        # Evitar cerrar con Alt+F4 hasta login exitoso
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        """Centrar ventana en pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def create_ui(self):
        """Crear interfaz de usuario"""
        # Header con logo y título
        self.create_header()

        # Formulario de login
        self.create_login_form()

        # Botones
        self.create_buttons()

        # Footer con información
        self.create_footer()

        # Focus inicial en username
        self.username_entry.focus()

    def create_header(self):
        """Crear header con logo y título"""
        header_frame = tk.Frame(self.root, bg=Config.COLORS['primary'], height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Logo simulado
        logo_frame = tk.Frame(header_frame, bg='white', width=80, height=80)
        logo_frame.pack(pady=20)
        logo_frame.pack_propagate(False)

        logo_label = tk.Label(
            logo_frame,
            text="SAI",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg=Config.COLORS['primary']
        )
        logo_label.pack(expand=True)

        # Título
        title_label = tk.Label(
            header_frame,
            text="Sistema Administrativo Integral",
            font=('Arial', 16, 'bold'),
            bg=Config.COLORS['primary'],
            fg='white'
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(
            header_frame,
            text="Nómina Ecuador 2024",
            font=('Arial', 12),
            bg=Config.COLORS['primary'],
            fg='white'
        )
        subtitle_label.pack()

    def create_login_form(self):
        """Crear formulario de login"""
        # Frame principal del formulario
        form_frame = tk.Frame(self.root, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=40)

        # Título del formulario
        form_title = tk.Label(
            form_frame,
            text="Iniciar Sesión",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        )
        form_title.pack(pady=(0, 30))

        # Campo Usuario
        tk.Label(
            form_frame,
            text="Usuario:",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(anchor=tk.W)

        self.username_entry = tk.Entry(
            form_frame,
            font=('Arial', 12),
            width=30,
            relief=tk.SOLID,
            bd=1
        )
        self.username_entry.pack(fill=tk.X, pady=(5, 20))
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())

        # Campo Contraseña
        tk.Label(
            form_frame,
            text="Contraseña:",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(anchor=tk.W)

        self.password_entry = tk.Entry(
            form_frame,
            font=('Arial', 12),
            width=30,
            show="*",
            relief=tk.SOLID,
            bd=1
        )
        self.password_entry.pack(fill=tk.X, pady=(5, 30))
        self.password_entry.bind('<Return>', lambda e: self.login())

        # Mensaje de estado
        self.status_label = tk.Label(
            form_frame,
            text="",
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['danger']
        )
        self.status_label.pack(pady=(0, 20))

        # Información de usuario por defecto
        info_frame = tk.Frame(form_frame, bg='white')
        info_frame.pack(fill=tk.X, pady=(10, 0))

        info_label = tk.Label(
            info_frame,
            text="Usuario por defecto:",
            font=('Arial', 9, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        )
        info_label.pack()

        default_info = tk.Label(
            info_frame,
            text="Usuario: admin | Contraseña: admin123",
            font=('Arial', 9),
            bg='white',
            fg=Config.COLORS['text_light']
        )
        default_info.pack()

    def create_buttons(self):
        """Crear botones de acción"""
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(fill=tk.X, padx=50, pady=(0, 40))

        # Botón Login
        self.login_button = tk.Button(
            button_frame,
            text="INICIAR SESIÓN",
            command=self.login,
            bg=Config.COLORS['primary'],
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.login_button.pack(fill=tk.X, pady=(0, 10))

        # Efectos hover
        self.login_button.bind("<Enter>", lambda e: self.login_button.config(bg=Config.COLORS['primary_dark']))
        self.login_button.bind("<Leave>", lambda e: self.login_button.config(bg=Config.COLORS['primary']))

        # Botón Salir
        exit_button = tk.Button(
            button_frame,
            text="SALIR",
            command=self.exit_app,
            bg=Config.COLORS['text_light'],
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        exit_button.pack(fill=tk.X)

    def create_footer(self):
        """Crear footer con información"""
        footer_frame = tk.Frame(self.root, bg=Config.COLORS['background'], height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        company_label = tk.Label(
            footer_frame,
            text=Config.COMPANY_NAME,
            font=('Arial', 10, 'bold'),
            bg=Config.COLORS['background'],
            fg=Config.COLORS['text']
        )
        company_label.pack(pady=(15, 5))

        version_label = tk.Label(
            footer_frame,
            text=f"Versión {Config.APP_VERSION}",
            font=('Arial', 9),
            bg=Config.COLORS['background'],
            fg=Config.COLORS['text_light']
        )
        version_label.pack()

    def login(self):
        """Procesar login de usuario"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validar campos
        if not username:
            self.show_error("Por favor ingrese el usuario")
            self.username_entry.focus()
            return

        if not password:
            self.show_error("Por favor ingrese la contraseña")
            self.password_entry.focus()
            return

        # Deshabilitar botón durante autenticación
        self.login_button.config(state='disabled', text="Verificando...")
        self.root.update()

        try:
            # Intentar autenticación
            user = auth_manager.authenticate(username, password)

            if user:
                self.show_success("Login exitoso. Bienvenido!")
                self.authenticated_user = user
                self.login_successful = True

                # Esperar un momento antes de cerrar
                self.root.after(1000, self.close_login)

        except AuthenticationError as e:
            self.show_error(str(e))
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

        except Exception as e:
            self.show_error("Error interno del sistema")
            print(f"Error de login: {e}")

        finally:
            # Rehabilitar botón
            self.login_button.config(state='normal', text="INICIAR SESIÓN")

    def show_error(self, message):
        """Mostrar mensaje de error"""
        self.status_label.config(text=message, fg=Config.COLORS['danger'])

    def show_success(self, message):
        """Mostrar mensaje de éxito"""
        self.status_label.config(text=message, fg=Config.COLORS['success'])

    def close_login(self):
        """Cerrar ventana de login"""
        if self.on_success_callback and self.login_successful:
            self.root.destroy()
            self.on_success_callback(self.authenticated_user)
        else:
            self.root.destroy()

    def exit_app(self):
        """Salir de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Está seguro de salir de la aplicación?"):
            self.root.quit()
            self.root.destroy()

    def on_closing(self):
        """Manejar cierre de ventana"""
        if self.login_successful:
            self.root.destroy()
        else:
            self.exit_app()

    def show(self):
        """Mostrar ventana de login"""
        try:
            # Inicializar sistema de autenticación
            auth_manager.initialize_system()

            # Mostrar ventana
            self.root.mainloop()

            return self.login_successful, self.authenticated_user

        except Exception as e:
            messagebox.showerror("Error", f"Error inicializando sistema: {str(e)}")
            return False, None

def show_login_window(on_success_callback=None):
    """Función helper para mostrar ventana de login"""
    login_window = LoginWindow(on_success_callback)
    return login_window.show()