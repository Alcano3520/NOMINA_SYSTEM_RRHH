#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Login Window - Sistema de Gestión de Nómina (SGN)
Ventana de login moderna con CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
from pathlib import Path
import threading

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from auth.auth_manager import auth_manager, AuthenticationError

# Configurar tema y apariencia de CustomTkinter
ctk.set_appearance_mode("light")  # Modo claro por defecto
ctk.set_default_color_theme("blue")  # Tema azul

class LoginWindow:
    """Ventana de login moderna con CustomTkinter"""

    def __init__(self, on_success_callback=None):
        self.on_success_callback = on_success_callback
        self.login_successful = False
        self.authenticated_user = None
        self.is_authenticating = False

        # Crear ventana principal con CustomTkinter
        self.root = ctk.CTk()
        self.setup_window()
        self.create_ui()

    def setup_window(self):
        """Configurar ventana de login moderna"""
        # Configuración básica de la ventana
        self.root.title("SGN - Sistema de Gestión de Nómina Ecuador")
        self.root.geometry("600x400")
        self.root.minsize(500, 350)

        # Centrar ventana en pantalla
        self.center_window()

        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configurar grid weights para responsividad
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def center_window(self):
        """Centrar ventana en pantalla"""
        self.root.update_idletasks()
        width = 600
        height = 400
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def create_ui(self):
        """Crear interfaz de usuario moderna"""
        # Frame principal que contiene todo el contenido
        main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header con información del sistema
        self.create_header(main_frame)

        # Contenedor central para el formulario
        self.create_login_form(main_frame)

        # Footer con información de la empresa
        self.create_footer(main_frame)

    def create_header(self, parent):
        """Crear header moderno con información del sistema"""
        # Frame del header
        header_frame = ctk.CTkFrame(parent, height=80, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)

        # Logo/Icono del sistema (simulado con texto)
        logo_frame = ctk.CTkFrame(header_frame, width=60, height=60, corner_radius=10)
        logo_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        logo_frame.grid_propagate(False)

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="SGN",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        logo_label.place(relx=0.5, rely=0.5, anchor="center")

        # Información del sistema
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            info_frame,
            text="Sistema de Gestión de Nómina",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            info_frame,
            text="Nómina Ecuador 2024 • Versión 2.0",
            font=ctk.CTkFont(size=12),
            text_color=("gray90", "gray70")
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

    def create_login_form(self, parent):
        """Crear formulario de login moderno y compacto"""
        # Frame central que contiene el formulario
        center_frame = ctk.CTkFrame(parent, fg_color="transparent")
        center_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        center_frame.grid_rowconfigure(0, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)

        # Frame del formulario de login
        form_frame = ctk.CTkFrame(center_frame, corner_radius=15, width=350, height=280)
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        form_frame.grid_propagate(False)

        # Título del formulario
        form_title = ctk.CTkLabel(
            form_frame,
            text="Iniciar Sesión",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        form_title.pack(pady=(25, 20))

        # Frame para los campos del formulario
        fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        # Campo Usuario
        user_label = ctk.CTkLabel(
            fields_frame,
            text="Usuario:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        user_label.pack(fill="x", pady=(0, 5))

        self.username_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ingrese su usuario",
            font=ctk.CTkFont(size=12),
            height=35,
            corner_radius=8
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Campo Contraseña
        password_label = ctk.CTkLabel(
            fields_frame,
            text="Contraseña:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ingrese su contraseña",
            show="*",
            font=ctk.CTkFont(size=12),
            height=35,
            corner_radius=8
        )
        self.password_entry.pack(fill="x", pady=(0, 15))
        self.password_entry.bind("<Return>", lambda e: self.login())

        # Mensaje de estado
        self.status_label = ctk.CTkLabel(
            fields_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="red"
        )
        self.status_label.pack(fill="x", pady=(0, 15))

        # Botón de login
        self.login_button = ctk.CTkButton(
            fields_frame,
            text="INICIAR SESIÓN",
            command=self.login,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=8
        )
        self.login_button.pack(fill="x", pady=(0, 10))

        # Botón salir
        self.exit_button = ctk.CTkButton(
            fields_frame,
            text="Salir",
            command=self.exit_app,
            font=ctk.CTkFont(size=11),
            height=30,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray20"),
            corner_radius=8
        )
        self.exit_button.pack(fill="x")

        # Información de usuario por defecto
        self.create_default_user_info(form_frame)

        # Focus inicial en el campo de usuario
        self.username_entry.focus()

    def create_default_user_info(self, parent):
        """Crear información de usuario por defecto"""
        info_frame = ctk.CTkFrame(parent, height=60, fg_color=("gray95", "gray15"), corner_radius=8)
        info_frame.pack(fill="x", padx=30, pady=(0, 25))
        info_frame.pack_propagate(False)

        info_title = ctk.CTkLabel(
            info_frame,
            text="👤 Usuario por defecto:",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        info_title.pack(pady=(8, 2))

        info_details = ctk.CTkLabel(
            info_frame,
            text="Usuario: admin | Contraseña: admin123",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        info_details.pack()

    def create_footer(self, parent):
        """Crear footer con información de la empresa"""
        footer_frame = ctk.CTkFrame(parent, height=50, corner_radius=0)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        footer_frame.grid_propagate(False)

        company_label = ctk.CTkLabel(
            footer_frame,
            text=Config.COMPANY_NAME,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        company_label.pack(expand=True)

    def login(self):
        """Procesar login de usuario con threading"""
        if self.is_authenticating:
            return

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

        # Iniciar autenticación en hilo separado para no bloquear la UI
        self.start_authentication(username, password)

    def start_authentication(self, username, password):
        """Iniciar proceso de autenticación en hilo separado"""
        self.is_authenticating = True

        # Deshabilitar controles durante autenticación
        self.login_button.configure(state="disabled", text="Verificando...")
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")

        # Limpiar mensaje de estado
        self.status_label.configure(text="")

        # Crear y ejecutar hilo de autenticación
        auth_thread = threading.Thread(
            target=self.authenticate_user,
            args=(username, password),
            daemon=True
        )
        auth_thread.start()

    def authenticate_user(self, username, password):
        """Autenticar usuario (ejecutado en hilo separado)"""
        try:
            # Intentar autenticación
            user = auth_manager.authenticate(username, password)

            if user:
                # Autenticación exitosa - programar cierre en hilo principal
                self.root.after(0, self.on_authentication_success, user)
            else:
                # Autenticación fallida
                self.root.after(0, self.on_authentication_failure, "Credenciales inválidas")

        except AuthenticationError as e:
            self.root.after(0, self.on_authentication_failure, str(e))
        except Exception as e:
            self.root.after(0, self.on_authentication_failure, "Error interno del sistema")
            print(f"Error de login: {e}")

    def on_authentication_success(self, user):
        """Manejar autenticación exitosa (en hilo principal)"""
        self.authenticated_user = user
        self.login_successful = True

        self.show_success("Login exitoso. ¡Bienvenido!")

        # Esperar un momento antes de cerrar
        self.root.after(1500, self.close_login)

    def on_authentication_failure(self, error_message):
        """Manejar fallo en autenticación (en hilo principal)"""
        self.show_error(error_message)

        # Rehabilitar controles
        self.login_button.configure(state="normal", text="INICIAR SESIÓN")
        self.username_entry.configure(state="normal")
        self.password_entry.configure(state="normal")

        # Limpiar contraseña y enfocar
        self.password_entry.delete(0, "end")
        self.password_entry.focus()

        self.is_authenticating = False

    def show_error(self, message):
        """Mostrar mensaje de error"""
        self.status_label.configure(text=message, text_color="red")

    def show_success(self, message):
        """Mostrar mensaje de éxito"""
        self.status_label.configure(text=message, text_color="green")

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
    """Función helper para mostrar ventana de login moderna"""
    login_window = LoginWindow(on_success_callback)
    return login_window.show()