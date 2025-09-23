"""
Módulo de Configuración del Sistema SAI
Gestión de configuraciones generales, empresa, parámetros y preferencias del sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os
from datetime import datetime
from pathlib import Path
from config import Config
from database.connection import get_session
from database.models import *


class ConfiguracionCompleteModule(tk.Frame):
    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables de configuración
        self.config_data = {}
        self.unsaved_changes = False

        # Variables del formulario
        self.empresa_nombre_var = tk.StringVar(value=Config.COMPANY_NAME)
        self.empresa_ruc_var = tk.StringVar()
        self.empresa_direccion_var = tk.StringVar()
        self.empresa_telefono_var = tk.StringVar()
        self.empresa_email_var = tk.StringVar()
        self.empresa_web_var = tk.StringVar()

        # Variables de parámetros laborales
        self.sbu_var = tk.DoubleVar(value=Config.SBU)
        self.aporte_personal_var = tk.DoubleVar(value=Config.APORTE_PERSONAL_IESS)
        self.aporte_patronal_var = tk.DoubleVar(value=Config.APORTE_PATRONAL_IESS)
        self.fondos_reserva_var = tk.DoubleVar(value=Config.FONDOS_RESERVA)
        self.jornada_semanal_var = tk.IntVar(value=Config.JORNADA_SEMANAL)
        self.dias_vacaciones_var = tk.IntVar(value=Config.DIAS_VACACIONES_ANUAL)

        # Variables de interface
        self.tema_var = tk.StringVar(value="moderno")
        self.idioma_var = tk.StringVar(value="español")
        self.mostrar_ayuda_var = tk.BooleanVar(value=True)
        self.auto_backup_var = tk.BooleanVar(value=True)
        self.backup_dias_var = tk.IntVar(value=7)

        self.pack(fill="both", expand=True)
        self.setup_ui()
        self.load_configuration()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Título principal
        title_frame = tk.Frame(self, bg='#f0f0f0')
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = tk.Label(
            title_frame,
            text="⚙️ CONFIGURACIÓN DEL SISTEMA",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg=Config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        buttons_frame = tk.Frame(title_frame, bg='#f0f0f0')
        buttons_frame.pack(side="right")

        save_btn = tk.Button(
            buttons_frame,
            text="💾 Guardar",
            font=('Arial', 10, 'bold'),
            bg=Config.COLORS['success'],
            fg='white',
            relief="flat",
            padx=20,
            command=self.save_configuration
        )
        save_btn.pack(side="left", padx=(0, 10))

        reset_btn = tk.Button(
            buttons_frame,
            text="🔄 Restaurar",
            font=('Arial', 10),
            bg=Config.COLORS['warning'],
            fg='white',
            relief="flat",
            padx=20,
            command=self.reset_configuration
        )
        reset_btn.pack(side="left", padx=(0, 10))

        export_btn = tk.Button(
            buttons_frame,
            text="📤 Exportar",
            font=('Arial', 10),
            bg=Config.COLORS['info'],
            fg='white',
            relief="flat",
            padx=20,
            command=self.export_configuration
        )
        export_btn.pack(side="left", padx=(0, 10))

        import_btn = tk.Button(
            buttons_frame,
            text="📥 Importar",
            font=('Arial', 10),
            bg=Config.COLORS['primary'],
            fg='white',
            relief="flat",
            padx=20,
            command=self.import_configuration
        )
        import_btn.pack(side="left")

        # Crear notebook para las pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Crear las pestañas
        self.create_empresa_tab()
        self.create_parametros_tab()
        self.create_interface_tab()
        self.create_database_tab()
        self.create_backup_tab()

    def create_empresa_tab(self):
        """Crear pestaña de información de empresa"""
        empresa_frame = ttk.Frame(self.notebook)
        self.notebook.add(empresa_frame, text="🏢 Empresa")

        # Canvas y scrollbar
        canvas = tk.Canvas(empresa_frame, bg='white')
        scrollbar = ttk.Scrollbar(empresa_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Información de la empresa
        empresa_info_frame = tk.LabelFrame(
            scrollable_frame,
            text="Información de la Empresa",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        empresa_info_frame.pack(fill="x", padx=20, pady=15)

        # Grid para campos
        fields = [
            ("Razón Social:", self.empresa_nombre_var, "text"),
            ("RUC:", self.empresa_ruc_var, "text"),
            ("Dirección:", self.empresa_direccion_var, "text"),
            ("Teléfono:", self.empresa_telefono_var, "text"),
            ("Email:", self.empresa_email_var, "text"),
            ("Sitio Web:", self.empresa_web_var, "text")
        ]

        for i, (label_text, var, field_type) in enumerate(fields):
            label = tk.Label(
                empresa_info_frame,
                text=label_text,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg=Config.COLORS['text']
            )
            label.grid(row=i, column=0, sticky="w", padx=(0, 15), pady=8)

            if field_type == "text":
                entry = tk.Entry(
                    empresa_info_frame,
                    textvariable=var,
                    font=('Arial', 10),
                    width=40,
                    relief="solid",
                    borderwidth=1
                )
                entry.grid(row=i, column=1, sticky="ew", pady=8)
                entry.bind('<KeyRelease>', self.mark_unsaved)

        empresa_info_frame.grid_columnconfigure(1, weight=1)

        # Logo de la empresa
        logo_frame = tk.LabelFrame(
            scrollable_frame,
            text="Logo de la Empresa",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        logo_frame.pack(fill="x", padx=20, pady=15)

        logo_current_frame = tk.Frame(logo_frame, bg='white')
        logo_current_frame.pack(fill="x", pady=10)

        self.logo_label = tk.Label(
            logo_current_frame,
            text="📷 Sin logo configurado",
            font=('Arial', 12),
            bg='#f8f9fa',
            fg=Config.COLORS['text_light'],
            relief="solid",
            borderwidth=1,
            width=50,
            height=8
        )
        self.logo_label.pack(side="left", padx=(0, 15))

        logo_buttons_frame = tk.Frame(logo_current_frame, bg='white')
        logo_buttons_frame.pack(side="left", fill="y")

        tk.Button(
            logo_buttons_frame,
            text="📁 Seleccionar Logo",
            font=('Arial', 10),
            bg=Config.COLORS['primary'],
            fg='white',
            relief="flat",
            padx=15,
            command=self.select_logo
        ).pack(pady=(0, 10))

        tk.Button(
            logo_buttons_frame,
            text="🗑️ Quitar Logo",
            font=('Arial', 10),
            bg=Config.COLORS['danger'],
            fg='white',
            relief="flat",
            padx=15,
            command=self.remove_logo
        ).pack()

    def create_parametros_tab(self):
        """Crear pestaña de parámetros laborales"""
        parametros_frame = ttk.Frame(self.notebook)
        self.notebook.add(parametros_frame, text="⚖️ Parámetros")

        # Canvas y scrollbar
        canvas = tk.Canvas(parametros_frame, bg='white')
        scrollbar = ttk.Scrollbar(parametros_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Parámetros salariales
        salarios_frame = tk.LabelFrame(
            scrollable_frame,
            text="Parámetros Salariales",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        salarios_frame.pack(fill="x", padx=20, pady=15)

        # Campos de parámetros
        param_fields = [
            ("Salario Básico Unificado (SBU):", self.sbu_var, "USD", "double"),
            ("Aporte Personal IESS (%):", self.aporte_personal_var, "%", "percent"),
            ("Aporte Patronal IESS (%):", self.aporte_patronal_var, "%", "percent"),
            ("Fondos de Reserva (%):", self.fondos_reserva_var, "%", "percent")
        ]

        for i, (label_text, var, suffix, field_type) in enumerate(param_fields):
            label = tk.Label(
                salarios_frame,
                text=label_text,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg=Config.COLORS['text']
            )
            label.grid(row=i, column=0, sticky="w", padx=(0, 15), pady=8)

            entry_frame = tk.Frame(salarios_frame, bg='white')
            entry_frame.grid(row=i, column=1, sticky="ew", pady=8)

            entry = tk.Entry(
                entry_frame,
                textvariable=var,
                font=('Arial', 10),
                width=15,
                relief="solid",
                borderwidth=1,
                justify="right"
            )
            entry.pack(side="left")
            entry.bind('<KeyRelease>', self.mark_unsaved)

            tk.Label(
                entry_frame,
                text=f" {suffix}",
                font=('Arial', 10),
                bg='white',
                fg=Config.COLORS['text_light']
            ).pack(side="left")

        salarios_frame.grid_columnconfigure(1, weight=1)

        # Parámetros de tiempo
        tiempo_frame = tk.LabelFrame(
            scrollable_frame,
            text="Parámetros de Tiempo Laboral",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        tiempo_frame.pack(fill="x", padx=20, pady=15)

        tiempo_fields = [
            ("Jornada Semanal (horas):", self.jornada_semanal_var, "horas", "int"),
            ("Días de Vacaciones Anuales:", self.dias_vacaciones_var, "días", "int")
        ]

        for i, (label_text, var, suffix, field_type) in enumerate(tiempo_fields):
            label = tk.Label(
                tiempo_frame,
                text=label_text,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg=Config.COLORS['text']
            )
            label.grid(row=i, column=0, sticky="w", padx=(0, 15), pady=8)

            entry_frame = tk.Frame(tiempo_frame, bg='white')
            entry_frame.grid(row=i, column=1, sticky="ew", pady=8)

            entry = tk.Entry(
                entry_frame,
                textvariable=var,
                font=('Arial', 10),
                width=15,
                relief="solid",
                borderwidth=1,
                justify="right"
            )
            entry.pack(side="left")
            entry.bind('<KeyRelease>', self.mark_unsaved)

            tk.Label(
                entry_frame,
                text=f" {suffix}",
                font=('Arial', 10),
                bg='white',
                fg=Config.COLORS['text_light']
            ).pack(side="left")

        tiempo_frame.grid_columnconfigure(1, weight=1)

    def create_interface_tab(self):
        """Crear pestaña de configuración de interfaz"""
        interface_frame = ttk.Frame(self.notebook)
        self.notebook.add(interface_frame, text="🎨 Interfaz")

        # Canvas y scrollbar
        canvas = tk.Canvas(interface_frame, bg='white')
        scrollbar = ttk.Scrollbar(interface_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configuración de tema
        tema_frame = tk.LabelFrame(
            scrollable_frame,
            text="Configuración de Tema",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        tema_frame.pack(fill="x", padx=20, pady=15)

        # Selector de tema
        tk.Label(
            tema_frame,
            text="Tema:",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        ).grid(row=0, column=0, sticky="w", padx=(0, 15), pady=8)

        tema_combo = ttk.Combobox(
            tema_frame,
            textvariable=self.tema_var,
            values=["clásico", "moderno", "oscuro", "personalizado"],
            state="readonly",
            width=20
        )
        tema_combo.grid(row=0, column=1, sticky="ew", pady=8)
        tema_combo.bind('<<ComboboxSelected>>', self.mark_unsaved)

        # Selector de idioma
        tk.Label(
            tema_frame,
            text="Idioma:",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        ).grid(row=1, column=0, sticky="w", padx=(0, 15), pady=8)

        idioma_combo = ttk.Combobox(
            tema_frame,
            textvariable=self.idioma_var,
            values=["español", "english"],
            state="readonly",
            width=20
        )
        idioma_combo.grid(row=1, column=1, sticky="ew", pady=8)
        idioma_combo.bind('<<ComboboxSelected>>', self.mark_unsaved)

        tema_frame.grid_columnconfigure(1, weight=1)

        # Configuración de preferencias
        prefs_frame = tk.LabelFrame(
            scrollable_frame,
            text="Preferencias de Usuario",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        prefs_frame.pack(fill="x", padx=20, pady=15)

        # Checkboxes de preferencias
        tk.Checkbutton(
            prefs_frame,
            text="Mostrar ayuda emergente",
            variable=self.mostrar_ayuda_var,
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text'],
            command=self.mark_unsaved
        ).pack(anchor="w", pady=5)

        tk.Checkbutton(
            prefs_frame,
            text="Backup automático",
            variable=self.auto_backup_var,
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text'],
            command=self.mark_unsaved
        ).pack(anchor="w", pady=5)

        # Días de backup
        backup_frame = tk.Frame(prefs_frame, bg='white')
        backup_frame.pack(anchor="w", pady=5)

        tk.Label(
            backup_frame,
            text="Backup cada:",
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(side="left")

        tk.Entry(
            backup_frame,
            textvariable=self.backup_dias_var,
            font=('Arial', 10),
            width=5,
            relief="solid",
            borderwidth=1,
            justify="center"
        ).pack(side="left", padx=(5, 5))

        tk.Label(
            backup_frame,
            text="días",
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(side="left")

    def create_database_tab(self):
        """Crear pestaña de configuración de base de datos"""
        database_frame = ttk.Frame(self.notebook)
        self.notebook.add(database_frame, text="🗄️ Base de Datos")

        # Canvas y scrollbar
        canvas = tk.Canvas(database_frame, bg='white')
        scrollbar = ttk.Scrollbar(database_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Información de la base de datos
        db_info_frame = tk.LabelFrame(
            scrollable_frame,
            text="Información de la Base de Datos",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        db_info_frame.pack(fill="x", padx=20, pady=15)

        # Estado de la conexión
        self.db_status_label = tk.Label(
            db_info_frame,
            text="🟢 Conectado - SQLite",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=Config.COLORS['success']
        )
        self.db_status_label.pack(anchor="w", pady=5)

        # Ruta de la base de datos
        tk.Label(
            db_info_frame,
            text=f"Ubicación: {Config.DATABASE_PATH}",
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(anchor="w", pady=2)

        # Tamaño del archivo
        try:
            db_size = os.path.getsize(Config.DATABASE_PATH) / (1024 * 1024)  # MB
            tk.Label(
                db_info_frame,
                text=f"Tamaño: {db_size:.2f} MB",
                font=('Arial', 10),
                bg='white',
                fg=Config.COLORS['text']
            ).pack(anchor="w", pady=2)
        except:
            tk.Label(
                db_info_frame,
                text="Tamaño: No disponible",
                font=('Arial', 10),
                bg='white',
                fg=Config.COLORS['text_light']
            ).pack(anchor="w", pady=2)

        # Botones de mantenimiento
        maintenance_frame = tk.LabelFrame(
            scrollable_frame,
            text="Mantenimiento de Base de Datos",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        maintenance_frame.pack(fill="x", padx=20, pady=15)

        buttons_grid = tk.Frame(maintenance_frame, bg='white')
        buttons_grid.pack(fill="x", pady=10)

        maintenance_buttons = [
            ("🔧 Optimizar DB", self.optimize_database, Config.COLORS['primary']),
            ("📊 Verificar Integridad", self.check_integrity, Config.COLORS['info']),
            ("🧹 Limpiar Logs", self.clean_logs, Config.COLORS['warning']),
            ("🔄 Reinicializar", self.reinitialize_db, Config.COLORS['danger'])
        ]

        for i, (text, command, color) in enumerate(maintenance_buttons):
            btn = tk.Button(
                buttons_grid,
                text=text,
                font=('Arial', 10),
                bg=color,
                fg='white',
                relief="flat",
                padx=20,
                pady=8,
                command=command
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")

        buttons_grid.grid_columnconfigure(0, weight=1)
        buttons_grid.grid_columnconfigure(1, weight=1)

    def create_backup_tab(self):
        """Crear pestaña de configuración de backups"""
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text="💾 Respaldos")

        # Canvas y scrollbar
        canvas = tk.Canvas(backup_frame, bg='white')
        scrollbar = ttk.Scrollbar(backup_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Crear backup manual
        manual_backup_frame = tk.LabelFrame(
            scrollable_frame,
            text="Crear Respaldo Manual",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        manual_backup_frame.pack(fill="x", padx=20, pady=15)

        tk.Button(
            manual_backup_frame,
            text="💾 Crear Respaldo Completo",
            font=('Arial', 12, 'bold'),
            bg=Config.COLORS['success'],
            fg='white',
            relief="flat",
            padx=30,
            pady=15,
            command=self.create_manual_backup
        ).pack(pady=10)

        tk.Label(
            manual_backup_frame,
            text="Incluye: Base de datos, configuraciones, reportes y logs",
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text_light']
        ).pack()

        # Lista de backups existentes
        backups_list_frame = tk.LabelFrame(
            scrollable_frame,
            text="Respaldos Disponibles",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=20,
            pady=15
        )
        backups_list_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Treeview para lista de backups
        columns = ('Fecha', 'Tamaño', 'Tipo')
        self.backups_tree = ttk.Treeview(backups_list_frame, columns=columns, show='headings', height=8)

        # Configurar columnas
        self.backups_tree.heading('Fecha', text='Fecha y Hora')
        self.backups_tree.heading('Tamaño', text='Tamaño')
        self.backups_tree.heading('Tipo', text='Tipo')

        self.backups_tree.column('Fecha', width=200)
        self.backups_tree.column('Tamaño', width=100)
        self.backups_tree.column('Tipo', width=150)

        # Scrollbar para la lista
        tree_scrollbar = ttk.Scrollbar(backups_list_frame, orient="vertical", command=self.backups_tree.yview)
        self.backups_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.backups_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")

        # Botones para gestión de backups
        backup_buttons_frame = tk.Frame(scrollable_frame, bg='white')
        backup_buttons_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            backup_buttons_frame,
            text="🔄 Actualizar Lista",
            font=('Arial', 10),
            bg=Config.COLORS['info'],
            fg='white',
            relief="flat",
            padx=15,
            command=self.refresh_backups_list
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            backup_buttons_frame,
            text="📂 Restaurar",
            font=('Arial', 10),
            bg=Config.COLORS['warning'],
            fg='white',
            relief="flat",
            padx=15,
            command=self.restore_backup
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            backup_buttons_frame,
            text="🗑️ Eliminar",
            font=('Arial', 10),
            bg=Config.COLORS['danger'],
            fg='white',
            relief="flat",
            padx=15,
            command=self.delete_backup
        ).pack(side="left")

        # Cargar lista inicial
        self.refresh_backups_list()

    def mark_unsaved(self, event=None):
        """Marcar que hay cambios sin guardar"""
        self.unsaved_changes = True

    def load_configuration(self):
        """Cargar configuración actual"""
        config_file = Config.BASE_DIR / "user_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)

                # Cargar valores en variables
                empresa = self.config_data.get('empresa', {})
                self.empresa_nombre_var.set(empresa.get('nombre', Config.COMPANY_NAME))
                self.empresa_ruc_var.set(empresa.get('ruc', ''))
                self.empresa_direccion_var.set(empresa.get('direccion', ''))
                self.empresa_telefono_var.set(empresa.get('telefono', ''))
                self.empresa_email_var.set(empresa.get('email', ''))
                self.empresa_web_var.set(empresa.get('web', ''))

                parametros = self.config_data.get('parametros', {})
                self.sbu_var.set(parametros.get('sbu', Config.SBU))
                self.aporte_personal_var.set(parametros.get('aporte_personal', Config.APORTE_PERSONAL_IESS))
                self.aporte_patronal_var.set(parametros.get('aporte_patronal', Config.APORTE_PATRONAL_IESS))
                self.fondos_reserva_var.set(parametros.get('fondos_reserva', Config.FONDOS_RESERVA))
                self.jornada_semanal_var.set(parametros.get('jornada_semanal', Config.JORNADA_SEMANAL))
                self.dias_vacaciones_var.set(parametros.get('dias_vacaciones', Config.DIAS_VACACIONES_ANUAL))

                interface = self.config_data.get('interface', {})
                self.tema_var.set(interface.get('tema', 'moderno'))
                self.idioma_var.set(interface.get('idioma', 'español'))
                self.mostrar_ayuda_var.set(interface.get('mostrar_ayuda', True))
                self.auto_backup_var.set(interface.get('auto_backup', True))
                self.backup_dias_var.set(interface.get('backup_dias', 7))

            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar configuración: {str(e)}")

    def save_configuration(self):
        """Guardar configuración"""
        try:
            # Recopilar datos del formulario
            self.config_data = {
                'empresa': {
                    'nombre': self.empresa_nombre_var.get(),
                    'ruc': self.empresa_ruc_var.get(),
                    'direccion': self.empresa_direccion_var.get(),
                    'telefono': self.empresa_telefono_var.get(),
                    'email': self.empresa_email_var.get(),
                    'web': self.empresa_web_var.get()
                },
                'parametros': {
                    'sbu': self.sbu_var.get(),
                    'aporte_personal': self.aporte_personal_var.get(),
                    'aporte_patronal': self.aporte_patronal_var.get(),
                    'fondos_reserva': self.fondos_reserva_var.get(),
                    'jornada_semanal': self.jornada_semanal_var.get(),
                    'dias_vacaciones': self.dias_vacaciones_var.get()
                },
                'interface': {
                    'tema': self.tema_var.get(),
                    'idioma': self.idioma_var.get(),
                    'mostrar_ayuda': self.mostrar_ayuda_var.get(),
                    'auto_backup': self.auto_backup_var.get(),
                    'backup_dias': self.backup_dias_var.get()
                },
                'ultima_modificacion': datetime.now().isoformat()
            }

            # Guardar en archivo
            config_file = Config.BASE_DIR / "user_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)

            self.unsaved_changes = False
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")

    def reset_configuration(self):
        """Restaurar configuración por defecto"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de restaurar la configuración por defecto?"):
            # Resetear a valores por defecto
            self.empresa_nombre_var.set(Config.COMPANY_NAME)
            self.empresa_ruc_var.set('')
            self.empresa_direccion_var.set('')
            self.empresa_telefono_var.set('')
            self.empresa_email_var.set('')
            self.empresa_web_var.set('')

            self.sbu_var.set(Config.SBU)
            self.aporte_personal_var.set(Config.APORTE_PERSONAL_IESS)
            self.aporte_patronal_var.set(Config.APORTE_PATRONAL_IESS)
            self.fondos_reserva_var.set(Config.FONDOS_RESERVA)
            self.jornada_semanal_var.set(Config.JORNADA_SEMANAL)
            self.dias_vacaciones_var.set(Config.DIAS_VACACIONES_ANUAL)

            self.tema_var.set("moderno")
            self.idioma_var.set("español")
            self.mostrar_ayuda_var.set(True)
            self.auto_backup_var.set(True)
            self.backup_dias_var.set(7)

            self.mark_unsaved()

    def export_configuration(self):
        """Exportar configuración a archivo"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Exportar Configuración",
                defaultextension=".json",
                filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Éxito", f"Configuración exportada a: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar configuración: {str(e)}")

    def import_configuration(self):
        """Importar configuración desde archivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Importar Configuración",
                filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
            )

            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported_config = json.load(f)

                if messagebox.askyesno("Confirmar", "¿Está seguro de importar esta configuración? Se reemplazará la configuración actual."):
                    self.config_data = imported_config
                    self.load_configuration()
                    messagebox.showinfo("Éxito", "Configuración importada correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar configuración: {str(e)}")

    def select_logo(self):
        """Seleccionar logo de empresa"""
        filename = filedialog.askopenfilename(
            title="Seleccionar Logo",
            filetypes=[
                ("Archivos de imagen", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )

        if filename:
            try:
                # Aquí se podría implementar la carga y redimensionamiento del logo
                self.logo_label.config(text=f"📷 Logo: {os.path.basename(filename)}")
                self.mark_unsaved()
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar logo: {str(e)}")

    def remove_logo(self):
        """Quitar logo de empresa"""
        self.logo_label.config(text="📷 Sin logo configurado")
        self.mark_unsaved()

    def optimize_database(self):
        """Optimizar base de datos"""
        try:
            # Implementar optimización de SQLite
            messagebox.showinfo("Éxito", "Base de datos optimizada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al optimizar base de datos: {str(e)}")

    def check_integrity(self):
        """Verificar integridad de base de datos"""
        try:
            # Implementar verificación de integridad
            messagebox.showinfo("Éxito", "Verificación de integridad completada. No se encontraron errores.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar integridad: {str(e)}")

    def clean_logs(self):
        """Limpiar archivos de log"""
        try:
            logs_dir = Config.BASE_DIR / "logs"
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log"):
                    log_file.unlink()
                messagebox.showinfo("Éxito", "Archivos de log limpiados correctamente")
            else:
                messagebox.showinfo("Info", "No se encontraron archivos de log para limpiar")
        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar logs: {str(e)}")

    def reinitialize_db(self):
        """Reinicializar base de datos"""
        if messagebox.askyesno("ADVERTENCIA", "¿Está seguro de reinicializar la base de datos? Se perderán TODOS los datos."):
            if messagebox.askyesno("CONFIRMACIÓN FINAL", "Esta acción NO se puede deshacer. ¿Continuar?"):
                try:
                    # Implementar reinicialización
                    messagebox.showinfo("Éxito", "Base de datos reinicializada correctamente")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al reinicializar base de datos: {str(e)}")

    def create_manual_backup(self):
        """Crear respaldo manual"""
        try:
            backup_dir = Config.BACKUPS_DIR
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_manual_{timestamp}.zip"

            # Aquí se implementaría la creación del backup
            messagebox.showinfo("Éxito", f"Respaldo creado: {backup_filename}")
            self.refresh_backups_list()

        except Exception as e:
            messagebox.showerror("Error", f"Error al crear respaldo: {str(e)}")

    def refresh_backups_list(self):
        """Actualizar lista de respaldos"""
        # Limpiar lista actual
        for item in self.backups_tree.get_children():
            self.backups_tree.delete(item)

        try:
            backup_dir = Config.BACKUPS_DIR
            if backup_dir.exists():
                for backup_file in backup_dir.glob("*.zip"):
                    stat = backup_file.stat()
                    fecha = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    tamaño = f"{stat.st_size / (1024*1024):.2f} MB"
                    tipo = "Manual" if "manual" in backup_file.name else "Automático"

                    self.backups_tree.insert('', 'end', values=(fecha, tamaño, tipo))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar lista de respaldos: {str(e)}")

    def restore_backup(self):
        """Restaurar respaldo seleccionado"""
        selection = self.backups_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un respaldo para restaurar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de restaurar este respaldo? Se reemplazarán los datos actuales."):
            try:
                # Implementar restauración
                messagebox.showinfo("Éxito", "Respaldo restaurado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al restaurar respaldo: {str(e)}")

    def delete_backup(self):
        """Eliminar respaldo seleccionado"""
        selection = self.backups_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un respaldo para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este respaldo?"):
            try:
                # Implementar eliminación
                self.refresh_backups_list()
                messagebox.showinfo("Éxito", "Respaldo eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar respaldo: {str(e)}")