"""Componente Sidebar - Barra lateral de navegación"""

import tkinter as tk
from tkinter import ttk
from config import Config

class Sidebar(tk.Frame):
    def __init__(self, parent, on_module_select=None):
        super().__init__(
            parent,
            bg=Config.COLORS['secondary'],
            width=Config.UI_CONFIG['sidebar_width'],
            relief='flat'
        )

        self.on_module_select = on_module_select
        self.active_button = None
        self.pack_propagate(False)

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del sidebar"""
        # Logo/Título
        self.create_header()

        # Sección de módulos principales
        self.create_main_modules()

        # Sección de configuración
        self.create_config_section()

        # Footer
        self.create_footer()

    def create_header(self):
        """Crear encabezado del sidebar"""
        header_frame = tk.Frame(self, bg=Config.COLORS['secondary'])
        header_frame.pack(fill="x", padx=20, pady=20)

        # Logo (emoji como placeholder)
        logo_label = tk.Label(
            header_frame,
            text="⚡",
            font=('Segoe UI', 24),
            bg=Config.COLORS['secondary'],
            fg='white'
        )
        logo_label.pack()

        # Título
        title_label = tk.Label(
            header_frame,
            text="SAI System",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['secondary'],
            fg='white'
        )
        title_label.pack(pady=(5, 0))

        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="INSEVIG CIA. LTDA.",
            font=Config.FONTS['small'],
            bg=Config.COLORS['secondary'],
            fg=Config.COLORS['text_light']
        )
        subtitle_label.pack()

        # Separador
        separator = tk.Frame(
            self,
            height=1,
            bg=Config.COLORS['secondary_dark']
        )
        separator.pack(fill="x", padx=20, pady=10)

    def create_main_modules(self):
        """Crear sección de módulos principales"""
        # Título de sección
        section_label = tk.Label(
            self,
            text="MÓDULOS PRINCIPALES",
            font=Config.FONTS['small'],
            bg=Config.COLORS['secondary'],
            fg=Config.COLORS['text_light']
        )
        section_label.pack(anchor="w", padx=20, pady=(10, 5))

        # Módulos
        modules = [
            {
                "id": "empleados",
                "text": "👥 Empleados",
                "description": "Gestión de personal"
            },
            {
                "id": "nomina",
                "text": "💰 Nómina",
                "description": "Procesar roles de pago"
            },
            {
                "id": "decimos",
                "text": "🎁 Décimos",
                "description": "13°, 14° y Fondos"
            },
            {
                "id": "vacaciones",
                "text": "🏖️ Vacaciones",
                "description": "Control de ausencias"
            },
            {
                "id": "prestamos",
                "text": "💳 Préstamos",
                "description": "Anticipos y créditos"
            },
            {
                "id": "egresos",
                "text": "📉 Egresos",
                "description": "Descuentos varios"
            }
        ]

        for module in modules:
            self.create_module_button(module)

    def create_config_section(self):
        """Crear sección de configuración"""
        # Separador
        separator = tk.Frame(
            self,
            height=1,
            bg=Config.COLORS['secondary_dark']
        )
        separator.pack(fill="x", padx=20, pady=20)

        # Título de sección
        section_label = tk.Label(
            self,
            text="CONFIGURACIÓN",
            font=Config.FONTS['small'],
            bg=Config.COLORS['secondary'],
            fg=Config.COLORS['text_light']
        )
        section_label.pack(anchor="w", padx=20, pady=(0, 5))

        # Módulos de configuración
        config_modules = [
            {
                "id": "dotacion",
                "text": "🎽 Dotación",
                "description": "Uniformes y equipos"
            },
            {
                "id": "reportes",
                "text": "📊 Reportes",
                "description": "Informes y análisis"
            }
        ]

        for module in config_modules:
            self.create_module_button(module)

    def create_module_button(self, module):
        """Crear botón de módulo"""
        # Frame contenedor
        btn_frame = tk.Frame(self, bg=Config.COLORS['secondary'])
        btn_frame.pack(fill="x", padx=10, pady=2)

        # Botón principal
        btn = tk.Button(
            btn_frame,
            text=module["text"],
            font=Config.FONTS['default'],
            bg=Config.COLORS['secondary'],
            fg='white',
            relief='flat',
            bd=0,
            anchor='w',
            padx=15,
            pady=12,
            cursor='hand2',
            command=lambda: self.select_module(module["id"], btn_frame)
        )
        btn.pack(fill="x")

        # Descripción
        desc_label = tk.Label(
            btn_frame,
            text=module["description"],
            font=Config.FONTS['small'],
            bg=Config.COLORS['secondary'],
            fg=Config.COLORS['text_light'],
            anchor='w'
        )
        desc_label.pack(fill="x", padx=30)

        # Efectos hover
        self.apply_button_hover(btn, btn_frame)

        # Guardar referencia para activación
        btn_frame.module_id = module["id"]

    def apply_button_hover(self, button, frame):
        """Aplicar efectos hover a botón"""
        def on_enter(event):
            if frame != self.active_button:
                button.configure(bg=Config.COLORS['secondary_dark'])
                frame.configure(bg=Config.COLORS['secondary_dark'])
                for child in frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=Config.COLORS['secondary_dark'])

        def on_leave(event):
            if frame != self.active_button:
                button.configure(bg=Config.COLORS['secondary'])
                frame.configure(bg=Config.COLORS['secondary'])
                for child in frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=Config.COLORS['secondary'])

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)

    def select_module(self, module_id, button_frame):
        """Seleccionar módulo"""
        # Desactivar botón anterior
        if self.active_button:
            self.active_button.configure(bg=Config.COLORS['secondary'])
            for child in self.active_button.winfo_children():
                child.configure(bg=Config.COLORS['secondary'])

        # Activar nuevo botón
        self.active_button = button_frame
        button_frame.configure(bg=Config.COLORS['primary'])
        for child in button_frame.winfo_children():
            child.configure(bg=Config.COLORS['primary'])

        # Notificar selección
        if self.on_module_select:
            self.on_module_select(module_id)

    def set_active(self, module_id):
        """Establecer módulo activo externamente"""
        # Buscar frame del módulo
        for child in self.winfo_children():
            if hasattr(child, 'module_id') and child.module_id == module_id:
                self.select_module(module_id, child)
                break

    def create_footer(self):
        """Crear pie del sidebar"""
        # Spacer para empujar footer al final
        spacer = tk.Frame(self, bg=Config.COLORS['secondary'])
        spacer.pack(fill="both", expand=True)

        # Footer frame
        footer_frame = tk.Frame(self, bg=Config.COLORS['secondary_dark'])
        footer_frame.pack(fill="x", padx=0, pady=0)

        # Información del sistema
        version_label = tk.Label(
            footer_frame,
            text=f"v{Config.APP_VERSION}",
            font=Config.FONTS['small'],
            bg=Config.COLORS['secondary_dark'],
            fg=Config.COLORS['text_light']
        )
        version_label.pack(pady=10)

        # Usuario actual (placeholder)
        user_frame = tk.Frame(footer_frame, bg=Config.COLORS['secondary_dark'])
        user_frame.pack(fill="x", padx=15, pady=(0, 15))

        user_icon = tk.Label(
            user_frame,
            text="👤",
            font=Config.FONTS['default'],
            bg=Config.COLORS['secondary_dark'],
            fg='white'
        )
        user_icon.pack(side="left")

        user_label = tk.Label(
            user_frame,
            text="Admin",
            font=Config.FONTS['small'],
            bg=Config.COLORS['secondary_dark'],
            fg='white'
        )
        user_label.pack(side="left", padx=(5, 0))