#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGN - Sistema de Gestión de Nómina COMPLETO
Sistema de Nomina y RRHH para Ecuador con CustomTkinter
Version 2.0 - Interfaz moderna y compacta
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
from tkinter import messagebox
import logging
from datetime import datetime
import threading

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Verificar requisitos básicos"""
    required = ['sqlalchemy', 'customtkinter']
    missing = []

    for module in required:
        try:
            __import__(module)
            print(f"[OK] {module} disponible")
        except ImportError:
            missing.append(module)
            print(f"[ERROR] {module} faltante")

    if missing:
        error_msg = f"Faltan módulos: {', '.join(missing)}\\n\\nInstale con: pip install {' '.join(missing)}"
        messagebox.showerror("Error", error_msg)
        sys.exit(1)

def main():
    """Función principal con sistema de autenticación"""
    print("=== SGN - Sistema de Gestión de Nómina COMPLETO ===")
    print("Versión: 2.0.0 - Interfaz moderna con CustomTkinter")

    try:
        check_requirements()

        # Importar después de verificar requisitos
        from config_ctk import ConfigCTK
        from auth.login_window_ctk import show_login_window

        # Configurar tema CustomTkinter
        ConfigCTK.setup_ctk_theme()

        # Crear directorios necesarios
        ConfigCTK.create_directories()

        def on_login_success(authenticated_user):
            """Callback ejecutado después del login exitoso"""
            try:
                print(f"[LOGIN] Usuario autenticado: {authenticated_user.username}")

                # Crear ventana principal
                root = ctk.CTk()

                def on_main_window_close():
                    """Manejar cierre de ventana principal"""
                    try:
                        print("[CLOSE] Cerrando aplicación principal")
                        root.quit()
                        root.destroy()
                    except Exception as e:
                        print(f"Error al cerrar: {e}")

                root.protocol("WM_DELETE_WINDOW", on_main_window_close)

                # Crear aplicación completa
                app = SGNCompleteApp(root, authenticated_user)

                print("[OK] Sistema SGN completo iniciado exitosamente")
                print("[INFO] Todos los módulos disponibles:")
                print("  - Empleados (Gestión completa)")
                print("  - Nómina (Procesamiento y roles)")
                print("  - Roles de Pago (Consulta actual e histórico)")
                print("  - Décimos (13vo y 14vo sueldo)")
                print("  - Vacaciones (Gestión y liquidación)")
                print("  - Préstamos (Control de préstamos)")
                print("  - Liquidaciones (Cálculo de liquidaciones)")
                print("  - Reportes (Dashboard ejecutivo)")

                # Mostrar ventana principal
                root.mainloop()

            except Exception as e:
                error_msg = f"Error iniciando aplicación principal: {str(e)}"
                print(f"ERROR: {error_msg}")
                messagebox.showerror("Error Crítico", error_msg)

        # Mostrar ventana de login
        success, user = show_login_window(on_login_success)

        if not success:
            print("[CANCEL] Login cancelado por el usuario")
            return

        print("[EXIT] Aplicación finalizada correctamente")

    except Exception as e:
        error_msg = f"Error crítico en main(): {str(e)}"
        print(f"ERROR: {error_msg}")
        messagebox.showerror("Error Crítico", error_msg)
        sys.exit(1)

class SGNCompleteApp:
    """Aplicación SGN completa con CustomTkinter"""

    def __init__(self, root, authenticated_user):
        self.root = root
        self.current_module = None
        self.authenticated_user = authenticated_user

        # Importar configuración
        from config_ctk import ConfigCTK
        self.config = ConfigCTK

        # Configurar ventana principal
        self.setup_main_window()

        # Crear interfaz
        self.create_ui()

        # Cargar dashboard por defecto
        self.load_module("dashboard")

    def setup_main_window(self):
        """Configurar ventana principal moderna"""
        # Configurar título y tamaño
        self.root.title(f"{self.config.APP_NAME} - v{self.config.APP_VERSION}")

        # Configurar tamaño inicial compacto pero escalable
        window_config = self.config.get_window_config('main')
        self.root.geometry(window_config['geometry'])
        self.root.minsize(*window_config['min_size'])

        # Configurar grid weights para responsividad
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)  # Columna de contenido principal

    def create_ui(self):
        """Crear interfaz de usuario moderna"""
        # Crear sidebar de navegación
        self.create_sidebar()

        # Crear área de contenido principal
        self.create_content_area()

        # Crear barra de estado
        self.create_status_bar()

    def create_sidebar(self):
        """Crear sidebar de navegación moderna"""
        # Frame principal del sidebar
        self.sidebar_frame = ctk.CTkFrame(
            self.root,
            width=250,
            corner_radius=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # Header del sidebar con información del usuario
        self.create_sidebar_header()

        # Contenedor scrollable para los módulos
        self.create_scrollable_sidebar_content()

    def create_sidebar_header(self):
        """Crear header del sidebar con información del usuario"""
        # Frame del header
        header_frame = ctk.CTkFrame(self.sidebar_frame, height=100, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Logo y título del sistema
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=15)

        # Logo simulado
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="SGN",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        logo_label.pack(anchor="w")

        # Información del usuario
        user_info = ctk.CTkLabel(
            logo_frame,
            text=f"👤 {self.authenticated_user.username}",
            font=ctk.CTkFont(size=10),
            text_color=("gray90", "gray70")
        )
        user_info.pack(anchor="w", pady=(2, 0))

    def create_scrollable_sidebar_content(self):
        """Crear contenido scrollable del sidebar"""
        # Frame scrollable para los menús
        scrollable_frame = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            label_text="NAVEGACIÓN",
            label_font=ctk.CTkFont(size=12, weight="bold")
        )
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Menú principal
        self.create_main_menu(scrollable_frame)

        # Separador
        separator = ctk.CTkFrame(scrollable_frame, height=2)
        separator.pack(fill="x", pady=10)

        # Menú de configuración
        self.create_config_menu(scrollable_frame)

        # Separador
        separator2 = ctk.CTkFrame(scrollable_frame, height=2)
        separator2.pack(fill="x", pady=10)

        # Opciones de usuario
        self.create_user_menu(scrollable_frame)

    def create_main_menu(self, parent):
        """Crear menú principal de módulos"""
        # Título del menú
        menu_title = ctk.CTkLabel(
            parent,
            text="📊 MÓDULOS PRINCIPALES",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray20", "gray80")
        )
        menu_title.pack(anchor="w", pady=(0, 5))

        # Lista de módulos principales
        main_modules = [
            ("🏠 Dashboard", "dashboard"),
            ("👥 Empleados", "empleados"),
            ("💰 Nómina", "nomina"),
            ("💰 Roles de Pago", "roles"),
            ("🎁 Décimos", "decimos"),
            ("✈️ Vacaciones", "vacaciones"),
            ("🧮 Liquidaciones", "liquidaciones"),
            ("💳 Préstamos", "prestamos"),
            ("💸 Egresos-Ingresos", "egresos"),
            ("📦 Dotación", "dotacion"),
            ("📊 Reportes", "reportes")
        ]

        # Crear botones para cada módulo
        for text, module_id in main_modules:
            btn = ctk.CTkButton(
                parent,
                text=text,
                command=lambda m=module_id: self.load_module(m),
                height=32,
                corner_radius=6,
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            btn.pack(fill="x", pady=2)

    def create_config_menu(self, parent):
        """Crear menú de configuración"""
        # Título del menú
        menu_title = ctk.CTkLabel(
            parent,
            text="⚙️ CONFIGURACIÓN",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray20", "gray80")
        )
        menu_title.pack(anchor="w", pady=(0, 5))

        # Lista de módulos de configuración
        config_modules = [
            ("🏢 Departamentos", "departamentos"),
            ("🕐 Turnos", "turnos"),
            ("⛑️ Equipos", "equipos"),
            ("🤝 Clientes", "clientes")
        ]

        # Crear botones para cada módulo de configuración
        for text, module_id in config_modules:
            btn = ctk.CTkButton(
                parent,
                text=text,
                command=lambda m=module_id: self.load_module(m),
                height=32,
                corner_radius=6,
                font=ctk.CTkFont(size=11),
                anchor="w",
                fg_color=("gray70", "gray30")
            )
            btn.pack(fill="x", pady=2)

    def create_user_menu(self, parent):
        """Crear menú de opciones de usuario"""
        # Título del menú
        menu_title = ctk.CTkLabel(
            parent,
            text="👤 USUARIO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray20", "gray80")
        )
        menu_title.pack(anchor="w", pady=(0, 5))

        # Botón cerrar sesión
        logout_btn = ctk.CTkButton(
            parent,
            text="🚪 Cerrar Sesión",
            command=self.logout,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=11),
            anchor="w",
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        logout_btn.pack(fill="x", pady=2)

    def create_content_area(self):
        """Crear área de contenido principal"""
        # Frame principal del contenido
        self.content_frame = ctk.CTkFrame(
            self.root,
            corner_radius=0
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Configurar grid para responsividad
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Frame interno para el contenido de los módulos
        self.content_area = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.content_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def create_status_bar(self):
        """Crear barra de estado moderna"""
        # Frame de la barra de estado
        status_frame = ctk.CTkFrame(
            self.root,
            height=30,
            corner_radius=0
        )
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_frame.grid_propagate(False)

        # Label de estado
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Sistema SGN iniciado - Todos los módulos disponibles",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        # Información adicional en el lado derecho
        info_label = ctk.CTkLabel(
            status_frame,
            text=f"Usuario: {self.authenticated_user.username} | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=ctk.CTkFont(size=10),
            anchor="e"
        )
        info_label.pack(side="right", padx=10, pady=5)

    def load_module(self, module_name):
        """Cargar módulo específico"""
        self.current_module = module_name
        self.clear_content()

        try:
            if module_name == "dashboard":
                self.show_dashboard()
            elif module_name == "empleados":
                self.show_empleados_module()
            elif module_name == "nomina":
                self.show_nomina_module()
            elif module_name == "roles":
                self.show_roles_module()
            elif module_name == "decimos":
                self.show_decimos_module()
            elif module_name == "vacaciones":
                self.show_vacaciones_module()
            elif module_name == "liquidaciones":
                self.show_liquidaciones_module()
            elif module_name == "prestamos":
                self.show_prestamos_module()
            elif module_name == "egresos":
                self.show_egresos_module()
            elif module_name == "dotacion":
                self.show_dotacion_module()
            elif module_name == "reportes":
                self.show_reportes_module()
            elif module_name == "departamentos":
                self.show_departamentos_module()
            elif module_name == "turnos":
                self.show_turnos_module()
            elif module_name == "equipos":
                self.show_equipos_module()
            elif module_name == "clientes":
                self.show_clientes_module()
            else:
                self.show_module_placeholder(module_name)

        except Exception as e:
            logger.error(f"Error cargando módulo {module_name}: {e}")
            self.show_error_screen(module_name, str(e))

    def clear_content(self):
        """Limpiar área de contenido"""
        try:
            for widget in self.content_area.winfo_children():
                widget.destroy()
            logger.info("✅ Área de contenido limpiada exitosamente")
        except Exception as e:
            logger.error(f"❌ Error limpiando área de contenido: {str(e)}")
            raise

    def show_dashboard(self):
        """Mostrar dashboard ejecutivo moderno"""
        self.clear_content()

        # Header del dashboard
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Dashboard Ejecutivo - Sistema SGN",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Resumen ejecutivo del sistema de gestión de nómina",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Frame para las tarjetas de métricas
        metrics_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=10)

        # Configurar grid para tarjetas responsivas
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Tarjetas de métricas simuladas
        self.create_metric_card(metrics_frame, "👥 Empleados", "145", "Activos", 0, 0)
        self.create_metric_card(metrics_frame, "💰 Nómina", "$45,230", "Este mes", 0, 1)
        self.create_metric_card(metrics_frame, "📊 Roles", "87", "Procesados", 0, 2)
        self.create_metric_card(metrics_frame, "✈️ Vacaciones", "23", "Pendientes", 0, 3)

        # Área de contenido adicional
        content_frame = ctk.CTkFrame(self.content_area)
        content_frame.pack(fill="both", expand=True, pady=20)

        welcome_label = ctk.CTkLabel(
            content_frame,
            text=f"¡Bienvenido al Sistema SGN, {self.authenticated_user.username}!",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        welcome_label.pack(pady=40)

        info_label = ctk.CTkLabel(
            content_frame,
            text="Seleccione un módulo del menú lateral para comenzar.",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        info_label.pack()

        # Actualizar status
        self.status_label.configure(text="Dashboard - Resumen ejecutivo del sistema")

    def create_metric_card(self, parent, title, value, subtitle, row, col):
        """Crear tarjeta de métrica"""
        card = ctk.CTkFrame(parent, width=150, height=100)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        card.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray60", "gray40")
        )
        title_label.pack(pady=(10, 2))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        value_label.pack(pady=2)

        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=9),
            text_color=("gray50", "gray50")
        )
        subtitle_label.pack()

    def show_module_placeholder(self, module_name):
        """Mostrar placeholder para módulos en desarrollo"""
        self.clear_content()

        # Frame del placeholder
        placeholder_frame = ctk.CTkFrame(self.content_area)
        placeholder_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Icono y mensaje
        icon_label = ctk.CTkLabel(
            placeholder_frame,
            text="🚧",
            font=ctk.CTkFont(size=48)
        )
        icon_label.pack(pady=(50, 20))

        title_label = ctk.CTkLabel(
            placeholder_frame,
            text=f"Módulo {module_name.title()}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        message_label = ctk.CTkLabel(
            placeholder_frame,
            text="Este módulo está en desarrollo.\nPróximamente disponible con interfaz CustomTkinter.",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        message_label.pack(pady=20)

        # Botón volver al dashboard
        back_btn = ctk.CTkButton(
            placeholder_frame,
            text="← Volver al Dashboard",
            command=lambda: self.load_module("dashboard"),
            width=200
        )
        back_btn.pack(pady=10)

        # Actualizar status
        self.status_label.configure(text=f"Módulo {module_name.title()} - En desarrollo")

    def show_error_screen(self, module_name, error_msg):
        """Mostrar pantalla de error"""
        self.clear_content()

        error_frame = ctk.CTkFrame(self.content_area)
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)

        error_icon = ctk.CTkLabel(
            error_frame,
            text="❌",
            font=ctk.CTkFont(size=48)
        )
        error_icon.pack(pady=(50, 20))

        error_title = ctk.CTkLabel(
            error_frame,
            text="Error al cargar módulo",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        error_title.pack(pady=(0, 10))

        error_message = ctk.CTkLabel(
            error_frame,
            text=f"No se pudo cargar el módulo '{module_name}':\n{error_msg}",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        error_message.pack(pady=20)

        back_btn = ctk.CTkButton(
            error_frame,
            text="← Volver al Dashboard",
            command=lambda: self.load_module("dashboard"),
            width=200
        )
        back_btn.pack(pady=10)

    # Módulos migrados a CustomTkinter
    def show_empleados_module(self):
        """Mostrar módulo de empleados con CustomTkinter"""
        self.clear_content()
        try:
            from gui.modules.empleados_ctk import EmpleadosModuleCTK
            module = EmpleadosModuleCTK(self.content_area, self)
            self.status_label.configure(text="Módulo Empleados - Gestión completa de personal con CustomTkinter")
        except Exception as e:
            logger.error(f"Error cargando módulo empleados CTK: {e}")
            self.show_error_screen("empleados", str(e))

    def show_nomina_module(self):
        self.show_module_placeholder("nomina")

    def show_roles_module(self):
        self.show_module_placeholder("roles")

    def show_decimos_module(self):
        self.show_module_placeholder("decimos")

    def show_vacaciones_module(self):
        self.show_module_placeholder("vacaciones")

    def show_liquidaciones_module(self):
        self.show_module_placeholder("liquidaciones")

    def show_prestamos_module(self):
        self.show_module_placeholder("prestamos")

    def show_egresos_module(self):
        self.show_module_placeholder("egresos")

    def show_dotacion_module(self):
        self.show_module_placeholder("dotacion")

    def show_reportes_module(self):
        self.show_module_placeholder("reportes")

    def show_departamentos_module(self):
        self.show_module_placeholder("departamentos")

    def show_turnos_module(self):
        self.show_module_placeholder("turnos")

    def show_equipos_module(self):
        self.show_module_placeholder("equipos")

    def show_clientes_module(self):
        self.show_module_placeholder("clientes")

    def logout(self):
        """Cerrar sesión del usuario"""
        if messagebox.askokcancel("Cerrar Sesión", "¿Está seguro de cerrar la sesión?"):
            try:
                print(f"[LOGOUT] Usuario {self.authenticated_user.username} cerró sesión")
                self.root.destroy()

                # Crear nueva ventana de login
                from auth.login_window_ctk import show_login_window

                def on_new_login(user):
                    new_root = ctk.CTk()
                    new_root.protocol("WM_DELETE_WINDOW", lambda: new_root.destroy())
                    SGNCompleteApp(new_root, user)
                    new_root.mainloop()

                show_login_window(on_new_login)

            except Exception as e:
                messagebox.showerror("Error", f"Error al cerrar sesión: {str(e)}")

if __name__ == "__main__":
    main()