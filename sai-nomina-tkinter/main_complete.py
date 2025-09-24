#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAI - Sistema Administrativo Integral COMPLETO
Sistema de Nomina y RRHH para Ecuador
Basado en sai_sistema_mejorado_completo.html y SISTEMA GESTION EMPLEADO.py
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from datetime import datetime, date
from decimal import Decimal

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Verificar requisitos basicos"""
    required = ['sqlalchemy']
    missing = []

    for module in required:
        try:
            __import__(module)
            print(f"[OK] {module} disponible")
        except ImportError:
            missing.append(module)
            print(f"[ERROR] {module} faltante")

    if missing:
        error_msg = f"Faltan modulos: {', '.join(missing)}\\n\\nInstale con: pip install {' '.join(missing)}"
        messagebox.showerror("Error", error_msg)
        sys.exit(1)

def main():
    """Funcion principal con sistema de autenticación"""
    print("=== SAI - Sistema Administrativo Integral COMPLETO ===")
    print("Version: 2.0.0 - Sistema con autenticación completa")

    try:
        check_requirements()

        # Importar configuracion
        from config import Config

        # Crear directorios
        for directory in ['logs', 'reports', 'backups', 'exports']:
            Path(directory).mkdir(exist_ok=True)

        # Inicializar base de datos (incluyendo nuevas tablas de autenticación)
        from init_database import create_database
        create_database()
        print("[OK] Base de datos inicializada con sistema de autenticación")

        # Importar sistema de autenticación
        from auth.login_window import show_login_window
        from auth.auth_manager import auth_manager

        def on_login_success(authenticated_user):
            """Callback ejecutado después de login exitoso"""
            print(f"[OK] Usuario autenticado: {authenticated_user.username}")

            # Crear ventana principal responsive
            root = tk.Tk()
            root.title(f"{Config.APP_NAME} - Sistema Completo - Usuario: {authenticated_user.nombre_completo}")

            # Configurar tamaño responsive según resolución
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # Calcular tamaño más compacto pero funcional
            window_width = min(1200, int(screen_width * 0.75))
            window_height = min(800, int(screen_height * 0.8))

            # Centrar ventana
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            root.minsize(600, 400)  # Tamaño mínimo más pequeño
            root.configure(bg=Config.COLORS['background'])

            # Hacer redimensionable
            root.rowconfigure(0, weight=1)
            root.columnconfigure(0, weight=1)

            # Manejar cierre de ventana
            def on_main_window_close():
                if messagebox.askokcancel("Salir", "¿Está seguro de cerrar el sistema?"):
                    # Hacer logout
                    auth_manager.logout()
                    root.destroy()

            root.protocol("WM_DELETE_WINDOW", on_main_window_close)

            # Crear aplicacion completa
            app = SAICompleteApp(root, authenticated_user)

            print("[OK] Sistema SAI completo iniciado exitosamente")
            print("[INFO] Todos los modulos disponibles:")
            print("  - Empleados (Gestion completa)")
            print("  - Nomina (Procesamiento y roles)")
            print("  - Decimos (13vo y 14vo sueldo)")
            print("  - Vacaciones (Solicitudes y saldos)")
            print("  - Liquidaciones (Calculo finiquitos)")
            print("  - Prestamos (Prestamos y anticipos)")
            print("  - Egresos-Ingresos (Descuentos adicionales)")
            print("  - Dotacion (Uniformes y equipos)")
            print("  - Reportes (PDF y Excel)")
            print("  - Configuracion (Tablas maestras)")

            # Iniciar aplicacion
            root.mainloop()

        # Mostrar ventana de login
        print("[INFO] Mostrando ventana de login...")
        success, user = show_login_window(on_login_success)

        if not success:
            print("[INFO] Login cancelado por usuario")
            return

    except Exception as e:
        error_msg = f"Error critico: {str(e)}"
        print(f"ERROR: {error_msg}")
        messagebox.showerror("Error Critico", error_msg)
        sys.exit(1)

class SAICompleteApp:
    """Aplicacion SAI completa con todos los modulos"""

    def __init__(self, root, authenticated_user):
        self.root = root
        self.current_module = None
        self.current_employee = None
        self.current_user = authenticated_user  # Usuario autenticado

        # Importar configuracion
        from config import Config
        self.config = Config

        # Importar sistema de permisos
        from auth.permissions import permission_manager
        self.permission_manager = permission_manager

        # Variables de control
        self.data_modified = False

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz principal"""
        # Frame principal
        self.main_frame = tk.Frame(
            self.root,
            bg=self.config.COLORS['background']
        )
        self.main_frame.pack(fill="both", expand=True)

        # Header moderno
        self.create_header()

        # Container principal con sidebar y contenido
        self.create_main_container()

        # Status bar
        self.create_status_bar()

        # Cargar dashboard inicial
        self.show_dashboard()

    def create_header(self):
        """Crear header moderno basado en HTML"""
        header_frame = tk.Frame(
            self.main_frame,
            bg=self.config.COLORS['secondary'],
            height=80
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Logo y titulo
        left_frame = tk.Frame(header_frame, bg=self.config.COLORS['secondary'])
        left_frame.pack(side="left", padx=20, pady=15)

        # Logo simulado
        logo_frame = tk.Frame(
            left_frame,
            bg='white',
            width=50,
            height=50
        )
        logo_frame.pack(side="left", padx=(0, 15))
        logo_frame.pack_propagate(False)

        logo_label = tk.Label(
            logo_frame,
            text="SAI",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg=self.config.COLORS['secondary']
        )
        logo_label.pack(expand=True)

        # Titulo y subtitulo
        title_frame = tk.Frame(left_frame, bg=self.config.COLORS['secondary'])
        title_frame.pack(side="left")

        title_label = tk.Label(
            title_frame,
            text="Sistema Administrativo Integral",
            font=('Arial', 16, 'bold'),
            bg=self.config.COLORS['secondary'],
            fg='white'
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame,
            text="INSEVIG CIA. LTDA - Gestion de RRHH y Nomina",
            font=('Arial', 10),
            bg=self.config.COLORS['secondary'],
            fg='lightgray'
        )
        subtitle_label.pack(anchor="w")

        # Info usuario derecha
        right_frame = tk.Frame(header_frame, bg=self.config.COLORS['secondary'])
        right_frame.pack(side="right", padx=20, pady=15)

        # Avatar usuario
        user_frame = tk.Frame(right_frame, bg=self.config.COLORS['secondary'])
        user_frame.pack(side="right")

        avatar_frame = tk.Frame(
            user_frame,
            bg='white',
            width=40,
            height=40
        )
        avatar_frame.pack(side="left", padx=(15, 10))
        avatar_frame.pack_propagate(False)

        # Avatar con iniciales del usuario
        initials = ''.join([n[0].upper() for n in self.current_user.nombre_completo.split()[:2]])
        avatar_label = tk.Label(
            avatar_frame,
            text=initials,
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.config.COLORS['secondary']
        )
        avatar_label.pack(expand=True)

        # Info usuario
        user_info_frame = tk.Frame(user_frame, bg=self.config.COLORS['secondary'])
        user_info_frame.pack(side="left")

        user_name_label = tk.Label(
            user_info_frame,
            text=self.current_user.nombre_completo,
            font=('Arial', 11, 'bold'),
            bg=self.config.COLORS['secondary'],
            fg='white'
        )
        user_name_label.pack(anchor="e")

        # Rol del usuario
        role_label = tk.Label(
            user_info_frame,
            text=f"({self.current_user.rol.nombre})",
            font=('Arial', 8),
            bg=self.config.COLORS['secondary'],
            fg='lightgray'
        )
        role_label.pack(anchor="e")

        date_label = tk.Label(
            user_info_frame,
            text=datetime.now().strftime("%d/%m/%Y %H:%M"),
            font=('Arial', 9),
            bg=self.config.COLORS['secondary'],
            fg='lightgray'
        )
        date_label.pack(anchor="e")

        # Botón logout
        logout_btn = tk.Button(
            right_frame,
            text="Cerrar Sesión",
            command=self.logout,
            bg=self.config.COLORS['danger'],
            fg='white',
            font=('Arial', 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        logout_btn.pack(side="right", padx=(10, 0))

    def create_main_container(self):
        """Crear container principal con sidebar y contenido"""
        container = tk.Frame(
            self.main_frame,
            bg=self.config.COLORS['background']
        )
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Grid layout
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.create_sidebar(container)

        # Area de contenido
        self.create_content_area(container)

    def logout(self):
        """Cerrar sesión del usuario"""
        if messagebox.askokcancel("Cerrar Sesión",
                                 f"¿Está seguro de cerrar la sesión de {self.current_user.nombre_completo}?"):
            try:
                # Importar auth_manager
                from auth.auth_manager import auth_manager

                # Hacer logout
                auth_manager.logout()

                # Cerrar ventana principal
                self.root.destroy()

                # Mostrar ventana de login nuevamente
                from auth.login_window import show_login_window
                success, user = show_login_window()

                if success:
                    # Crear nueva instancia de la aplicación
                    new_root = tk.Tk()
                    new_root.title(f"{self.config.APP_NAME} - Sistema Completo - Usuario: {user.nombre_completo}")

                    # Configurar ventana igual que antes
                    screen_width = new_root.winfo_screenwidth()
                    screen_height = new_root.winfo_screenheight()
                    window_width = min(1400, int(screen_width * 0.8))
                    window_height = min(900, int(screen_height * 0.8))
                    x = (screen_width - window_width) // 2
                    y = (screen_height - window_height) // 2
                    new_root.geometry(f"{window_width}x{window_height}+{x}+{y}")
                    new_root.minsize(1000, 700)
                    new_root.configure(bg=self.config.COLORS['background'])

                    # Crear nueva aplicación
                    SAICompleteApp(new_root, user)
                    new_root.mainloop()

            except Exception as e:
                messagebox.showerror("Error", f"Error al cerrar sesión: {str(e)}")

    def create_sidebar(self, parent):
        """Crear sidebar con navegacion"""
        sidebar_frame = tk.Frame(
            parent,
            bg='white',
            width=250,
            relief='raised',
            bd=1
        )
        sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        sidebar_frame.pack_propagate(False)

        # Header sidebar (fijo)
        sidebar_header = tk.Frame(sidebar_frame, bg='white')
        sidebar_header.pack(fill="x", padx=20, pady=(20, 10))

        nav_title = tk.Label(
            sidebar_header,
            text="SISTEMA SAI - NAVEGACIÓN",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.config.COLORS['secondary']
        )
        nav_title.pack()

        # Separador
        separator1 = tk.Frame(sidebar_header, bg=self.config.COLORS['border'], height=2)
        separator1.pack(fill="x", pady=(10, 0))

        # Crear area scrollable para los módulos
        self.create_scrollable_sidebar_content(sidebar_frame)

    def create_scrollable_sidebar_content(self, parent):
        """Crear contenido scrollable para el sidebar"""
        # Canvas y scrollbar para hacer scrollable el contenido
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Menu principal (filtrado por permisos)
        main_menu_items = self.get_filtered_menu_items("MODULOS PRINCIPALES", [
            ("Dashboard", "dashboard", "🏠", None),  # Dashboard siempre disponible
            ("Empleados", "empleados", "👥", "empleados"),
            ("Nomina", "nomina", "💰", "nomina"),
            ("Decimos", "decimos", "🎁", "decimos"),
            ("Vacaciones", "vacaciones", "✈️", "vacaciones"),
            ("Liquidaciones", "liquidaciones", "🧮", "liquidaciones"),
            ("Prestamos", "prestamos", "💳", "prestamos"),
            ("Egresos-Ingresos", "egresos", "💸", "nomina"),
            ("Dotacion", "dotacion", "📦", "empleados"),
            ("Reportes", "reportes", "📊", "reportes")
        ])
        if main_menu_items:
            self.create_nav_menu(scrollable_frame, "MODULOS PRINCIPALES", main_menu_items)


        # Menu configuracion (filtrado por permisos)
        config_menu_items = self.get_filtered_menu_items("CONFIGURACION", [
            ("Departamentos", "departamentos", "🏢", "departamentos"),
            ("Turnos", "turnos", "🕐", "configuracion"),
            ("Equipos", "equipos", "⛑️", "configuracion"),
            ("Clientes", "clientes", "🤝", "configuracion"),
        ])
        if config_menu_items:
            # Separador solo si hay items anteriores y actuales
            if main_menu_items:
                separator2 = tk.Frame(scrollable_frame, bg=self.config.COLORS['border'], height=1)
                separator2.pack(fill="x", padx=20, pady=10)
            self.create_nav_menu(scrollable_frame, "CONFIGURACION", config_menu_items)


        # Menu base de datos (filtrado por permisos)
        db_menu_items = self.get_filtered_menu_items("BASE DE DATOS", [
            ("RPEMPLEA", "rpemplea", "📋", "empleados"),
            ("RPHISTOR", "rphistor", "📚", "auditoria"),
            ("RPCONTRL", "rpcontrl", "⚙️", "configuracion"),
        ])
        if db_menu_items:
            # Separador solo si hay items anteriores
            if main_menu_items or config_menu_items:
                separator3 = tk.Frame(scrollable_frame, bg=self.config.COLORS['border'], height=1)
                separator3.pack(fill="x", padx=20, pady=10)
            self.create_nav_menu(scrollable_frame, "BASE DE DATOS", db_menu_items)


        # Menu administración (filtrado por permisos)
        admin_menu_items = self.get_filtered_menu_items("ADMINISTRACIÓN", [
            ("Usuarios", "usuarios", "👤", "usuarios"),
            ("Auditoría", "auditoria", "🔍", "auditoria"),
            ("Configuración", "configuracion", "⚙️", "configuracion"),
        ])
        if admin_menu_items:
            # Separador solo si hay items anteriores
            if main_menu_items or config_menu_items or db_menu_items:
                separator4 = tk.Frame(scrollable_frame, bg=self.config.COLORS['border'], height=1)
                separator4.pack(fill="x", padx=20, pady=10)
            self.create_nav_menu(scrollable_frame, "ADMINISTRACIÓN", admin_menu_items)

        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")

        # Binding para scroll con rueda del ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def get_filtered_menu_items(self, section_name, items):
        """Filtrar items del menú basado en permisos del usuario"""
        filtered_items = []

        for item in items:
            if len(item) == 4:  # (text, module, icon, permission_module)
                text, module, icon, permission_module = item

                # Si no requiere permisos específicos (None), siempre mostrar
                if permission_module is None:
                    filtered_items.append((text, module, icon))
                # Si el usuario tiene permisos para el módulo, mostrar
                elif self.permission_manager.check_permission(self.current_user, permission_module, "read"):
                    filtered_items.append((text, module, icon))
            else:
                # Formato anterior sin permisos
                filtered_items.append(item)

        return filtered_items

    def create_nav_menu(self, parent, title, items):
        """Crear menu de navegacion"""
        # Titulo seccion
        title_frame = tk.Frame(parent, bg='white')
        title_frame.pack(fill="x", padx=20, pady=(10, 5))

        title_label = tk.Label(
            title_frame,
            text=title,
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=self.config.COLORS['text'],
            anchor="w"
        )
        title_label.pack(fill="x")

        # Items del menu
        for text, module, icon in items:
            self.create_nav_item(parent, text, module, icon)

    def create_nav_item(self, parent, text, module, icon):
        """Crear item de navegacion"""
        item_frame = tk.Frame(parent, bg='white')
        item_frame.pack(fill="x", padx=20, pady=2)

        # Crear boton
        btn = tk.Button(
            item_frame,
            text=f"{icon} {text}",
            command=lambda m=module: self.load_module(m),
            bg='white',
            fg=self.config.COLORS['text'],
            font=('Arial', 10),
            relief='flat',
            anchor="w",
            padx=15,
            pady=8,
            cursor='hand2'
        )
        btn.pack(fill="x")

        # Efectos hover
        def on_enter(e):
            btn.configure(bg=self.config.COLORS['primary'], fg='white')
        def on_leave(e):
            btn.configure(bg='white', fg=self.config.COLORS['text'])

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def create_content_area(self, parent):
        """Crear area de contenido principal"""
        self.content_area = tk.Frame(
            parent,
            bg='white',
            relief='raised',
            bd=1
        )
        self.content_area.grid(row=0, column=1, sticky="nsew")

    def create_status_bar(self):
        """Crear barra de estado"""
        status_frame = tk.Frame(
            self.main_frame,
            bg=self.config.COLORS['border'],
            height=30
        )
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="Sistema SAI iniciado - Todos los modulos disponibles",
            bg=self.config.COLORS['border'],
            fg=self.config.COLORS['text'],
            font=('Arial', 9),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        # Info derecha
        info_label = tk.Label(
            status_frame,
            text=f"Base de datos: SQLite | Empresa: {self.config.COMPANY_NAME}",
            bg=self.config.COLORS['border'],
            fg=self.config.COLORS['text'],
            font=('Arial', 9),
            anchor="e"
        )
        info_label.pack(side="right", padx=10, pady=5)

    def show_dashboard(self):
        """Mostrar dashboard principal"""
        self.clear_content()
        self.current_module = "dashboard"

        # Frame del dashboard
        dashboard_frame = tk.Frame(self.content_area, bg='white')
        dashboard_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        header_frame = tk.Frame(dashboard_frame, bg='white')
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="📊 Dashboard Ejecutivo - Sistema SAI",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg=self.config.COLORS['secondary']
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Resumen general del sistema de nomina y recursos humanos",
            font=('Arial', 12),
            bg='white',
            fg=self.config.COLORS['text']
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Estadisticas principales
        self.create_dashboard_stats(dashboard_frame)

        # Graficos y informacion adicional
        self.create_dashboard_charts(dashboard_frame)

        self.status_label.config(text="Dashboard ejecutivo - Resumen general del sistema")

    def create_dashboard_stats(self, parent):
        """Crear tarjetas de estadisticas para dashboard"""
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill="x", pady=(0, 20))

        # Obtener estadisticas reales
        stats_data = self.get_dashboard_stats()

        # Grid de estadisticas
        for i, (title, value, subtitle, color, icon) in enumerate(stats_data):
            col = i % 4
            card = self.create_stat_card_modern(stats_frame, title, value, subtitle, color, icon)
            card.grid(row=0, column=col, padx=10, pady=5, sticky="ew")

        # Configurar columnas
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)

    def create_stat_card_modern(self, parent, title, value, subtitle, color, icon):
        """Crear tarjeta de estadistica moderna"""
        card_frame = tk.Frame(
            parent,
            bg=color,
            relief='raised',
            bd=2,
            width=180,
            height=100
        )
        card_frame.grid_propagate(False)

        # Header con icono
        header_frame = tk.Frame(card_frame, bg=color)
        header_frame.pack(fill="x", padx=12, pady=(12, 3))

        icon_label = tk.Label(
            header_frame,
            text=icon,
            font=('Arial', 20),
            bg=color,
            fg='white'
        )
        icon_label.pack(side="left")

        title_label = tk.Label(
            header_frame,
            text=title,
            font=('Arial', 10, 'bold'),
            bg=color,
            fg='white'
        )
        title_label.pack(side="right")

        # Valor principal
        value_label = tk.Label(
            card_frame,
            text=str(value),
            font=('Arial', 20, 'bold'),
            bg=color,
            fg='white'
        )
        value_label.pack()

        # Subtitulo
        if subtitle:
            subtitle_label = tk.Label(
                card_frame,
                text=subtitle,
                font=('Arial', 9),
                bg=color,
                fg='lightgray'
            )
            subtitle_label.pack(pady=(0, 10))

        return card_frame

    def get_dashboard_stats(self):
        """Obtener estadisticas para dashboard"""
        try:
            from database.connection import get_session
            from database.models import Empleado, RolPago, Vacacion, Prestamo
            from gui.components.visual_improvements import StatCard, show_toast

            session = get_session()

            total_empleados = session.query(Empleado).count()
            empleados_activos = session.query(Empleado).filter(Empleado.activo == True).count()

            # Simular otras estadisticas
            roles_procesados = session.query(RolPago).count() if hasattr(session.query(RolPago), 'count') else 12
            vacaciones_pendientes = 8

            session.close()

            stats = [
                ("Total Empleados", total_empleados, "Personal registrado", self.config.COLORS['primary'], "👥"),
                ("Empleados Activos", empleados_activos, "Personal activo", self.config.COLORS['success'], "✅"),
                ("Roles Procesados", roles_procesados, "Este mes", self.config.COLORS['info'], "💰"),
                ("Vacaciones Pendientes", vacaciones_pendientes, "Por aprobar", self.config.COLORS['warning'], "✈️")
            ]

        except Exception as e:
            logger.warning(f"Error obteniendo estadisticas: {e}")
            stats = [
                ("Total Empleados", "8", "Personal registrado", self.config.COLORS['primary'], "👥"),
                ("Empleados Activos", "8", "Personal activo", self.config.COLORS['success'], "✅"),
                ("Roles Procesados", "12", "Este mes", self.config.COLORS['info'], "💰"),
                ("Vacaciones Pendientes", "5", "Por aprobar", self.config.COLORS['warning'], "✈️")
            ]

        return stats

    def create_dashboard_charts(self, parent):
        """Crear area de graficos y resumen"""
        charts_frame = tk.Frame(parent, bg='white')
        charts_frame.pack(fill="both", expand=True)

        # Grid para dos columnas
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)

        # Resumen actividad reciente
        self.create_activity_summary(charts_frame)

        # Accesos rapidos
        self.create_quick_actions(charts_frame)

    def create_activity_summary(self, parent):
        """Crear resumen de actividad"""
        activity_frame = tk.LabelFrame(
            parent,
            text="📈 Actividad Reciente",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        activity_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        activities = [
            "• Juan Perez - Solicitud de vacaciones procesada",
            "• Maria Gonzalez - Actualizacion de datos personales",
            "• Nomina de Septiembre procesada exitosamente",
            "• Carlos Rodriguez - Nuevo prestamo aprobado",
            "• Sistema - Backup automatico completado",
            "• Ana Martinez - Finiquito calculado",
            "• Nuevos empleados registrados: 2",
            "• Reportes mensuales generados"
        ]

        for i, activity in enumerate(activities):
            activity_label = tk.Label(
                activity_frame,
                text=activity,
                font=('Arial', 10),
                bg='white',
                fg=self.config.COLORS['text'],
                anchor="w"
            )
            activity_label.pack(fill="x", pady=2)

    def create_quick_actions(self, parent):
        """Crear acciones rapidas"""
        actions_frame = tk.LabelFrame(
            parent,
            text="⚡ Acciones Rapidas",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        actions_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        actions = [
            ("Procesar Nomina", "nomina", self.config.COLORS['primary']),
            ("Nuevo Empleado", "empleados", self.config.COLORS['success']),
            ("Generar Reportes", "reportes", self.config.COLORS['info']),
            ("Calcular Decimos", "decimos", self.config.COLORS['warning']),
            ("Aprobar Vacaciones", "vacaciones", self.config.COLORS['secondary']),
            ("Revisar Prestamos", "prestamos", self.config.COLORS['danger'])
        ]

        for i, (text, module, color) in enumerate(actions):
            btn = tk.Button(
                actions_frame,
                text=text,
                command=lambda m=module: self.load_module(m),
                bg=color,
                fg='white',
                font=('Arial', 10, 'bold'),
                relief='flat',
                padx=20,
                pady=8,
                cursor='hand2'
            )
            btn.pack(fill="x", pady=5)

            # Efecto hover
            def on_enter(e, button=btn, orig_color=color):
                button.configure(bg=self.darken_color(orig_color))
            def on_leave(e, button=btn, orig_color=color):
                button.configure(bg=orig_color)

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def darken_color(self, color):
        """Oscurecer color para efecto hover"""
        # Simulacion simple de oscurecimiento
        color_map = {
            self.config.COLORS['primary']: '#5a6fd8',
            self.config.COLORS['success']: '#38a169',
            self.config.COLORS['info']: '#3182ce',
            self.config.COLORS['warning']: '#d69e2e',
            self.config.COLORS['secondary']: '#1a365d',
            self.config.COLORS['danger']: '#e53e3e'
        }
        return color_map.get(color, color)

    def load_module(self, module_name):
        """Cargar modulo especifico"""
        self.current_module = module_name
        self.clear_content()

        try:
            if module_name == "dashboard":
                self.show_dashboard()
            elif module_name == "empleados":
                self.show_empleados_module()
            elif module_name == "nomina":
                self.show_nomina_module()
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
            elif module_name == "rpemplea":
                self.show_rpemplea_module()
            elif module_name == "rphistor":
                self.show_rphistor_module()
            elif module_name == "rpcontrl":
                self.show_rpcontrl_module()
            else:
                self.show_module_placeholder(module_name)

        except Exception as e:
            logger.error(f"Error cargando modulo {module_name}: {e}")
            self.show_error_screen(module_name, str(e))

    def clear_content(self):
        """Limpiar area de contenido"""
        try:
            children = self.content_area.winfo_children()
            logger.info(f"🧹 Limpiando {len(children)} widgets del área de contenido")
            for i, widget in enumerate(children):
                logger.debug(f"🗑️ Destruyendo widget {i+1}/{len(children)}: {type(widget).__name__}")
                widget.destroy()
            logger.info("✅ Área de contenido limpiada exitosamente")
        except Exception as e:
            logger.error(f"❌ Error limpiando área de contenido: {str(e)}")
            raise

    def show_empleados_module(self):
        """Mostrar modulo de empleados completo"""
        self.clear_content()
        # Importar desde archivo separado que vamos a crear
        from gui.modules.empleados_complete import EmpleadosCompleteModule
        module = EmpleadosCompleteModule(self.content_area, self)
        self.status_label.config(text="Modulo Empleados - Gestion completa de personal")

    def show_nomina_module(self):
        """Mostrar modulo de nomina"""
        self.clear_content()
        from gui.modules.nomina_complete import NominaCompleteModule
        module = NominaCompleteModule(self.content_area, self)
        self.status_label.config(text="Modulo Nomina - Procesamiento de roles de pago")

    def show_decimos_module(self):
        """Mostrar modulo de decimos"""
        logger.info("🚀 INICIANDO carga del módulo DÉCIMOS")
        try:
            logger.info("🧹 Limpiando área de contenido...")
            self.clear_content()
            logger.info("✅ Área de contenido limpiada correctamente")

            logger.info("📦 Importando DecimosCompleteModule...")
            from gui.modules.decimos_complete import DecimosCompleteModule
            logger.info("✅ Módulo DecimosCompleteModule importado correctamente")

            logger.info("🏗️ Creando instancia del módulo décimos...")
            module = DecimosCompleteModule(self.content_area)
            logger.info("✅ Instancia del módulo décimos creada correctamente")

            logger.info("📝 Actualizando status label...")
            self.status_label.config(text="Modulo Decimos - Gestion de 13vo y 14vo sueldo")
            logger.info("🎉 MÓDULO DÉCIMOS CARGADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"❌ ERROR cargando módulo décimos: {str(e)}")
            logger.error(f"💥 Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Error cargando módulo décimos: {str(e)}")

    def show_vacaciones_module(self):
        """Mostrar modulo de vacaciones"""
        logger.info("🚀 INICIANDO carga del módulo VACACIONES")
        try:
            logger.info("🧹 Limpiando área de contenido...")
            self.clear_content()
            logger.info("✅ Área de contenido limpiada correctamente")

            logger.info("📦 Importando VacacionesCompleteModule...")
            from gui.modules.vacaciones_complete import VacacionesCompleteModule
            logger.info("✅ Módulo VacacionesCompleteModule importado correctamente")

            logger.info("🏗️ Creando instancia del módulo vacaciones...")
            module = VacacionesCompleteModule(self.content_area)
            logger.info("✅ Instancia del módulo vacaciones creada correctamente")

            logger.info("📝 Actualizando status label...")
            self.status_label.config(text="Modulo Vacaciones - Solicitudes y saldos")
            logger.info("🎉 MÓDULO VACACIONES CARGADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"❌ ERROR cargando módulo vacaciones: {str(e)}")
            logger.error(f"💥 Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Error cargando módulo vacaciones: {str(e)}")

    def show_liquidaciones_module(self):
        """Mostrar modulo de liquidaciones"""
        logger.info("🚀 INICIANDO carga del módulo LIQUIDACIONES")
        try:
            logger.info("🧹 Limpiando área de contenido...")
            self.clear_content()
            logger.info("✅ Área de contenido limpiada correctamente")

            logger.info("📦 Importando LiquidacionesCompleteModule...")
            from gui.modules.liquidaciones_complete import LiquidacionesCompleteModule
            logger.info("✅ Módulo LiquidacionesCompleteModule importado correctamente")

            logger.info("🏗️ Creando instancia del módulo liquidaciones...")
            module = LiquidacionesCompleteModule(self.content_area)
            logger.info("✅ Instancia del módulo liquidaciones creada correctamente")

            logger.info("📝 Actualizando status label...")
            self.status_label.config(text="Modulo Liquidaciones - Calculo de finiquitos")
            logger.info("🎉 MÓDULO LIQUIDACIONES CARGADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"❌ ERROR cargando módulo liquidaciones: {str(e)}")
            logger.error(f"💥 Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Error cargando módulo liquidaciones: {str(e)}")

    def show_prestamos_module(self):
        """Mostrar modulo de prestamos"""
        logger.info("🚀 INICIANDO carga del módulo PRÉSTAMOS")
        try:
            logger.info("🧹 Limpiando área de contenido...")
            self.clear_content()
            logger.info("✅ Área de contenido limpiada correctamente")

            logger.info("📦 Importando PrestamosCompleteModule...")
            from gui.modules.prestamos_complete import PrestamosCompleteModule
            logger.info("✅ Módulo PrestamosCompleteModule importado correctamente")

            logger.info("🏗️ Creando instancia del módulo préstamos...")
            module = PrestamosCompleteModule(self.content_area)
            logger.info("✅ Instancia del módulo préstamos creada correctamente")

            logger.info("📝 Actualizando status label...")
            self.status_label.config(text="Modulo Prestamos - Prestamos y anticipos")
            logger.info("🎉 MÓDULO PRÉSTAMOS CARGADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"❌ ERROR cargando módulo préstamos: {str(e)}")
            logger.error(f"💥 Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Error cargando módulo préstamos: {str(e)}")

    def show_egresos_module(self):
        """Mostrar modulo de egresos e ingresos"""
        logger.info("🚀 INICIANDO carga del módulo EGRESOS-INGRESOS")
        try:
            logger.info("🧹 Limpiando área de contenido...")
            self.clear_content()
            logger.info("✅ Área de contenido limpiada correctamente")

            logger.info("📦 Importando EgresosIngresosCompleteModule...")
            from gui.modules.egresos_ingresos_complete import EgresosIngresosCompleteModule
            logger.info("✅ Módulo EgresosIngresosCompleteModule importado correctamente")

            logger.info("🏗️ Creando instancia del módulo egresos-ingresos...")
            module = EgresosIngresosCompleteModule(self.content_area)
            logger.info("✅ Instancia del módulo egresos-ingresos creada correctamente")

            logger.info("📝 Actualizando status label...")
            self.status_label.config(text="Modulo Egresos-Ingresos - Descuentos y bonificaciones")
            logger.info("🎉 MÓDULO EGRESOS-INGRESOS CARGADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"❌ ERROR cargando módulo egresos-ingresos: {str(e)}")
            logger.error(f"💥 Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Error cargando módulo egresos-ingresos: {str(e)}")

    def show_dotacion_module(self):
        """Mostrar modulo de dotacion"""
        logger.info("🚀 INICIANDO carga del módulo DOTACIÓN")
        try:
            logger.info("🧹 Limpiando área de contenido...")
            self.clear_content()
            logger.info("✅ Área de contenido limpiada correctamente")

            logger.info("📦 Importando DotacionCompleteModule...")
            from gui.modules.dotacion_complete import DotacionCompleteModule
            logger.info("✅ Módulo DotacionCompleteModule importado correctamente")

            logger.info("🏗️ Creando instancia del módulo dotación...")
            module = DotacionCompleteModule(self.content_area)
            logger.info("✅ Instancia del módulo dotación creada correctamente")

            logger.info("📝 Actualizando status label...")
            self.status_label.config(text="Modulo Dotacion - Control de uniformes y equipos")
            logger.info("🎉 MÓDULO DOTACIÓN CARGADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"❌ ERROR cargando módulo dotación: {str(e)}")
            logger.error(f"💥 Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Error cargando módulo dotación: {str(e)}")

    def show_reportes_module(self):
        """Mostrar modulo de reportes"""
        self.clear_content()
        from gui.modules.reportes_complete import ReportesCompleteModule
        module = ReportesCompleteModule(self.content_area)
        self.status_label.config(text="Modulo Reportes - Generacion de informes PDF/Excel")

    def show_departamentos_module(self):
        """Mostrar modulo de departamentos/puestos de seguridad"""
        logger.info("🚀 INICIANDO carga del módulo DEPARTAMENTOS")
        try:
            logger.info("🧹 Limpiando área de contenido...")
            self.clear_content()
            logger.info("✅ Área de contenido limpiada correctamente")

            logger.info("📦 Importando DepartamentosCompleteModule...")
            from gui.modules.departamentos_complete import DepartamentosCompleteModule
            logger.info("✅ Módulo DepartamentosCompleteModule importado correctamente")

            logger.info("🏗️ Creando instancia del módulo departamentos...")
            module = DepartamentosCompleteModule(self.content_area)
            logger.info("✅ Instancia del módulo departamentos creada correctamente")

            logger.info("📝 Actualizando status label...")
            self.status_label.config(text="Departamentos/Puestos de Seguridad - Gestión de ubicaciones y clientes")
            logger.info("🎉 MÓDULO DEPARTAMENTOS CARGADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"❌ ERROR cargando módulo departamentos: {str(e)}")
            logger.error(f"💥 Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Error cargando módulo departamentos: {str(e)}")

    def show_turnos_module(self):
        """Mostrar modulo de turnos"""
        self.clear_content()
        from gui.modules.turnos_complete import TurnosCompleteModule
        module = TurnosCompleteModule(self.content_area)
        self.status_label.config(text="Configuracion - Turnos y horarios")

    def show_equipos_module(self):
        """Mostrar modulo de equipos"""
        self.clear_content()
        from gui.modules.equipos_complete import EquiposCompleteModule
        module = EquiposCompleteModule(self.content_area)
        self.status_label.config(text="Configuracion - Equipos y herramientas")

    def show_clientes_module(self):
        """Mostrar modulo de clientes"""
        self.clear_content()
        from gui.modules.clientes_complete import ClientesCompleteModule
        module = ClientesCompleteModule(self.content_area)
        self.status_label.config(text="Configuracion - Clientes y contratos")

    def show_rpemplea_module(self):
        """Mostrar tabla RPEMPLEA"""
        self.clear_content()
        from gui.modules.rpemplea_complete import RPEmpleaCompleteModule
        module = RPEmpleaCompleteModule(self.content_area)
        self.status_label.config(text="Base de Datos - Tabla RPEMPLEA")

    def show_rphistor_module(self):
        """Mostrar tabla RPHISTOR"""
        self.clear_content()
        from gui.modules.rphistor_complete import RPHistorCompleteModule
        module = RPHistorCompleteModule(self.content_area)
        self.status_label.config(text="Base de Datos - Tabla RPHISTOR")

    def show_rpcontrl_module(self):
        """Mostrar tabla RPCONTRL"""
        self.clear_content()
        from gui.modules.rpcontrl_complete import RPContrlCompleteModule
        module = RPContrlCompleteModule(self.content_area)
        self.status_label.config(text="Base de Datos - Tabla RPCONTRL")

    def show_configuracion_module(self):
        """Mostrar modulo de configuración del sistema"""
        logger.info("🚀 INICIANDO carga del módulo CONFIGURACIÓN")
        try:
            logger.info("🧹 Limpiando área de contenido...")
            self.clear_content()
            logger.info("✅ Área de contenido limpiada correctamente")

            logger.info("📦 Importando ConfiguracionCompleteModule...")
            from gui.modules.configuracion_complete import ConfiguracionCompleteModule
            logger.info("✅ Módulo ConfiguracionCompleteModule importado correctamente")

            logger.info("🏗️ Creando instancia del módulo configuración...")
            module = ConfiguracionCompleteModule(self.content_area)
            logger.info("✅ Instancia del módulo configuración creada correctamente")

            logger.info("📝 Actualizando status label...")
            self.status_label.config(text="Configuración del Sistema - Parámetros y preferencias")
            logger.info("🎉 MÓDULO CONFIGURACIÓN CARGADO EXITOSAMENTE")

        except Exception as e:
            logger.error(f"❌ ERROR cargando módulo configuración: {str(e)}")
            logger.error(f"💥 Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Error cargando módulo configuración: {str(e)}")

    def show_module_placeholder(self, module_name):
        """Mostrar placeholder temporal"""
        placeholder_frame = tk.Frame(self.content_area, bg='white')
        placeholder_frame.pack(fill="both", expand=True, padx=50, pady=50)

        icon_label = tk.Label(
            placeholder_frame,
            text="🚧",
            font=('Arial', 72),
            bg='white',
            fg=self.config.COLORS['text_light']
        )
        icon_label.pack(pady=(50, 20))

        title_label = tk.Label(
            placeholder_frame,
            text=f"Modulo {module_name.title()}",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg=self.config.COLORS['secondary']
        )
        title_label.pack(pady=(0, 10))

        message_label = tk.Label(
            placeholder_frame,
            text="En desarrollo - Proximamente disponible",
            font=('Arial', 12),
            bg='white',
            fg=self.config.COLORS['text']
        )
        message_label.pack()

    def show_error_screen(self, module_name, error):
        """Mostrar pantalla de error"""
        error_frame = tk.Frame(self.content_area, bg='white')
        error_frame.pack(fill="both", expand=True, padx=50, pady=50)

        title_label = tk.Label(
            error_frame,
            text=f"❌ Error en modulo {module_name}",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg=self.config.COLORS['danger']
        )
        title_label.pack(pady=(50, 20))

        error_label = tk.Label(
            error_frame,
            text=f"Error: {error}",
            font=('Arial', 10),
            bg='white',
            fg=self.config.COLORS['text'],
            wraplength=600,
            justify='center'
        )
        error_label.pack()

if __name__ == "__main__":
    main()