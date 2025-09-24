#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo de Empleados Completo - Sistema SAI
Basado en SISTEMA GESTION EMPLEADO.py e interfaz HTML
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, date
import logging
from decimal import Decimal

from config import Config
from database.connection import get_session
from database.models import Empleado, Departamento, Cargo
from gui.components.carga_masiva import show_carga_masiva_empleados

logger = logging.getLogger(__name__)

class EmpleadosCompleteModule(tk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent, bg='white')
        self.main_app = main_app
        self.session = get_session()
        self.current_employee = None
        self.data_modified = False

        self.pack(fill="both", expand=True)
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        """Configurar interfaz completa del modulo"""
        # Header del modulo
        self.create_module_header()

        # Container principal
        main_container = tk.Frame(self, bg='white')
        main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Panel de busqueda
        self.create_search_panel(main_container)

        # Container de contenido (lista + detalles)
        content_container = tk.Frame(main_container, bg='white')
        content_container.pack(fill="both", expand=True, pady=(10, 0))

        # Panel izquierdo - Lista de empleados
        self.create_employee_list(content_container)

        # Panel derecho - Detalles con pestañas
        self.create_employee_details(content_container)

    def create_module_header(self):
        """Crear header del modulo"""
        header_frame = tk.Frame(self, bg='white')
        header_frame.pack(fill="x", padx=15, pady=15)

        # Titulo y descripcion
        title_label = tk.Label(
            header_frame,
            text="👥 Gestión de Empleados",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Gestión completa del personal - Datos generales, ingresos, descuentos y más",
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text']
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Separador
        separator = tk.Frame(header_frame, bg=Config.COLORS['border'], height=2)
        separator.pack(fill="x", pady=(15, 0))

    def create_search_panel(self, parent):
        """Crear panel de busqueda"""
        search_frame = tk.LabelFrame(
            parent,
            text="🔍 Búsqueda y Filtros",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=10,
            pady=8
        )
        search_frame.pack(fill="x", pady=(0, 10))

        # Row 1 - Busquedas principales
        row1_frame = tk.Frame(search_frame, bg='white')
        row1_frame.pack(fill="x", pady=(0, 10))

        tk.Label(row1_frame, text="Empleado:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.search_employee_var = tk.StringVar()
        self.search_employee_entry = tk.Entry(row1_frame, textvariable=self.search_employee_var, width=15)
        self.search_employee_entry.grid(row=0, column=1, padx=(0, 15))

        tk.Label(row1_frame, text="Cédula:", bg='white', font=('Arial', 10)).grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.search_cedula_var = tk.StringVar()
        self.search_cedula_entry = tk.Entry(row1_frame, textvariable=self.search_cedula_var, width=15)
        self.search_cedula_entry.grid(row=0, column=3, padx=(0, 15))

        tk.Label(row1_frame, text="Nombres:", bg='white', font=('Arial', 10)).grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.search_name_var = tk.StringVar()
        self.search_name_entry = tk.Entry(row1_frame, textvariable=self.search_name_var, width=20)
        self.search_name_entry.grid(row=0, column=5, padx=(0, 15))

        # Row 2 - Filtros adicionales
        row2_frame = tk.Frame(search_frame, bg='white')
        row2_frame.pack(fill="x", pady=(0, 10))

        tk.Label(row2_frame, text="Departamento:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.search_dept_var = tk.StringVar()
        self.search_dept_combo = ttk.Combobox(row2_frame, textvariable=self.search_dept_var, width=15, state="readonly")
        self.search_dept_combo.grid(row=0, column=1, padx=(0, 15))

        tk.Label(row2_frame, text="Estado:", bg='white', font=('Arial', 10)).grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.search_status_var = tk.StringVar()
        self.search_status_combo = ttk.Combobox(
            row2_frame,
            textvariable=self.search_status_var,
            values=["Todos", "Activos", "Inactivos"],
            width=12,
            state="readonly"
        )
        self.search_status_combo.set("Activos")
        self.search_status_combo.grid(row=0, column=3, padx=(0, 15))

        # Botones de accion
        buttons_frame = tk.Frame(row2_frame, bg='white')
        buttons_frame.grid(row=0, column=4, padx=(20, 0))

        search_btn = tk.Button(
            buttons_frame,
            text="🔍 Buscar",
            command=self.search_employees,
            bg=Config.COLORS['primary'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        search_btn.pack(side="left", padx=(0, 5))

        clear_btn = tk.Button(
            buttons_frame,
            text="🗑️ Limpiar",
            command=self.clear_search,
            bg=Config.COLORS['secondary'],
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        clear_btn.pack(side="left")

        # Cargar departamentos en combo
        self.load_departments()

    def create_employee_list(self, parent):
        """Crear lista de empleados"""
        # Frame izquierdo
        left_frame = tk.Frame(parent, bg='white', width=400)
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Header de lista
        list_header = tk.Frame(left_frame, bg='white')
        list_header.pack(fill="x", pady=(0, 10))

        list_title = tk.Label(
            list_header,
            text="Lista de Empleados",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        list_title.pack(side="left")

        # Botones de accion
        buttons_frame = tk.Frame(list_header, bg='white')
        buttons_frame.pack(side="right")

        new_btn = tk.Button(
            buttons_frame,
            text="➕ Nuevo",
            command=self.new_employee,
            bg=Config.COLORS['success'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2'
        )
        new_btn.pack(side="left", padx=(0, 5))

        import_btn = tk.Button(
            buttons_frame,
            text="📊 Carga Masiva",
            command=self.carga_masiva_empleados,
            bg=Config.COLORS['info'],
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2'
        )
        import_btn.pack(side="left")

        # Lista/Tree de empleados
        list_frame = tk.Frame(left_frame, bg='white')
        list_frame.pack(fill="both", expand=True)

        # Treeview
        columns = ("Código", "Cédula", "Empleado", "Estado")
        self.employee_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        # Configurar columnas
        self.employee_tree.heading("Código", text="Código")
        self.employee_tree.heading("Cédula", text="Cédula")
        self.employee_tree.heading("Empleado", text="Empleado")
        self.employee_tree.heading("Estado", text="Estado")

        self.employee_tree.column("Código", width=70, anchor="center")
        self.employee_tree.column("Cédula", width=90, anchor="center")
        self.employee_tree.column("Empleado", width=160, anchor="w")
        self.employee_tree.column("Estado", width=70, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.employee_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Eventos
        self.employee_tree.bind("<ButtonRelease-1>", self.on_employee_select)
        self.employee_tree.bind("<Double-1>", self.on_employee_double_click)

    def create_employee_details(self, parent):
        """Crear panel de detalles con pestañas"""
        # Frame derecho
        right_frame = tk.Frame(parent, bg='white')
        right_frame.pack(side="left", fill="both", expand=True)

        # Header de detalles
        details_header = tk.Frame(right_frame, bg='white')
        details_header.pack(fill="x", pady=(0, 10))

        self.details_title = tk.Label(
            details_header,
            text="Detalles del Empleado",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        self.details_title.pack(side="left")

        # Botones de accion
        action_buttons = tk.Frame(details_header, bg='white')
        action_buttons.pack(side="right")

        self.edit_btn = tk.Button(
            action_buttons,
            text="✏️ Editar",
            command=self.edit_employee,
            bg=Config.COLORS['warning'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2',
            state='disabled'
        )
        self.edit_btn.pack(side="left", padx=(0, 5))

        self.save_btn = tk.Button(
            action_buttons,
            text="💾 Guardar",
            command=self.save_employee,
            bg=Config.COLORS['success'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2',
            state='disabled'
        )
        self.save_btn.pack(side="left", padx=(0, 5))

        self.delete_btn = tk.Button(
            action_buttons,
            text="🗑️ Eliminar",
            command=self.delete_employee,
            bg=Config.COLORS['danger'],
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2',
            state='disabled'
        )
        self.delete_btn.pack(side="left")

        # Notebook para pestañas
        self.details_notebook = ttk.Notebook(right_frame)
        self.details_notebook.pack(fill="both", expand=True)

        # Crear todas las pestañas
        self.create_general_tab()
        self.create_personal_tab()
        self.create_job_tab()
        self.create_financial_tab()
        self.create_ingresos_descuentos_tab()
        self.create_observaciones_tab()
        self.create_documents_tab()

    def create_general_tab(self):
        """Crear pestaña de datos generales"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="📋 General")

        # Scroll frame para el contenido
        canvas = tk.Canvas(tab_frame, bg='white')
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Seccion informacion basica
        basic_frame = tk.LabelFrame(
            scrollable_frame,
            text="Información Básica",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=10,
            pady=8
        )
        basic_frame.pack(fill="x", padx=8, pady=4)

        # Grid para campos
        row = 0

        # Codigo empleado
        tk.Label(basic_frame, text="Código Empleado:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.codigo_var = tk.StringVar()
        self.codigo_entry = tk.Entry(basic_frame, textvariable=self.codigo_var, width=15, state='readonly')
        self.codigo_entry.grid(row=row, column=1, sticky="w", pady=5)

        # Cedula
        tk.Label(basic_frame, text="Cédula:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.cedula_var = tk.StringVar()
        self.cedula_entry = tk.Entry(basic_frame, textvariable=self.cedula_var, width=15)
        self.cedula_entry.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Nombres
        tk.Label(basic_frame, text="Nombres:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.nombres_var = tk.StringVar()
        self.nombres_entry = tk.Entry(basic_frame, textvariable=self.nombres_var, width=25)
        self.nombres_entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)

        row += 1

        # Apellidos
        tk.Label(basic_frame, text="Apellidos:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.apellidos_var = tk.StringVar()
        self.apellidos_entry = tk.Entry(basic_frame, textvariable=self.apellidos_var, width=25)
        self.apellidos_entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)

        # Seccion fechas
        dates_frame = tk.LabelFrame(
            scrollable_frame,
            text="Fechas Importantes",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=10,
            pady=8
        )
        dates_frame.pack(fill="x", padx=8, pady=4)

        row = 0

        # Fecha nacimiento
        tk.Label(dates_frame, text="Fecha Nacimiento:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.fecha_nac_var = tk.StringVar()
        self.fecha_nac_entry = tk.Entry(dates_frame, textvariable=self.fecha_nac_var, width=15)
        self.fecha_nac_entry.grid(row=row, column=1, sticky="w", pady=5)

        # Fecha ingreso
        tk.Label(dates_frame, text="Fecha Ingreso:", bg='white', font=('Arial', 10)).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.fecha_ing_var = tk.StringVar()
        self.fecha_ing_entry = tk.Entry(dates_frame, textvariable=self.fecha_ing_var, width=15)
        self.fecha_ing_entry.grid(row=row, column=3, sticky="w", pady=5)

        # Pack canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_personal_tab(self):
        """Crear pestaña datos personales"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="👤 Personal")

        # Contenido personal
        content_frame = tk.Frame(tab_frame, bg='white')
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Datos personales
        personal_frame = tk.LabelFrame(
            content_frame,
            text="Datos Personales",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=10
        )
        personal_frame.pack(fill="x", pady=(0, 10))

        row = 0

        # Sexo
        tk.Label(personal_frame, text="Sexo:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.sexo_var = tk.StringVar()
        self.sexo_combo = ttk.Combobox(personal_frame, textvariable=self.sexo_var, values=["M", "F"], width=10, state="readonly")
        self.sexo_combo.grid(row=row, column=1, sticky="w", pady=5)

        # Estado civil
        tk.Label(personal_frame, text="Estado Civil:", bg='white', font=('Arial', 10)).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.estado_civil_var = tk.StringVar()
        self.estado_civil_combo = ttk.Combobox(
            personal_frame,
            textvariable=self.estado_civil_var,
            values=["S", "C", "D", "V", "U"],
            width=10,
            state="readonly"
        )
        self.estado_civil_combo.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Direccion
        tk.Label(personal_frame, text="Dirección:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.direccion_var = tk.StringVar()
        self.direccion_entry = tk.Entry(personal_frame, textvariable=self.direccion_var, width=50)
        self.direccion_entry.grid(row=row, column=1, columnspan=3, sticky="ew", pady=5)

        row += 1

        # Telefonos
        tk.Label(personal_frame, text="Teléfono:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.telefono_var = tk.StringVar()
        self.telefono_entry = tk.Entry(personal_frame, textvariable=self.telefono_var, width=15)
        self.telefono_entry.grid(row=row, column=1, sticky="w", pady=5)

        tk.Label(personal_frame, text="Celular:", bg='white', font=('Arial', 10)).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.celular_var = tk.StringVar()
        self.celular_entry = tk.Entry(personal_frame, textvariable=self.celular_var, width=15)
        self.celular_entry.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Email
        tk.Label(personal_frame, text="Email:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(personal_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)

    def create_job_tab(self):
        """Crear pestaña datos laborales"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="💼 Laboral")

        content_frame = tk.Frame(tab_frame, bg='white')
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Datos laborales
        job_frame = tk.LabelFrame(
            content_frame,
            text="Información Laboral",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=10
        )
        job_frame.pack(fill="x", pady=(0, 10))

        row = 0

        # Departamento
        tk.Label(job_frame, text="Departamento:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.depto_var = tk.StringVar()
        self.depto_combo = ttk.Combobox(job_frame, textvariable=self.depto_var, width=20, state="readonly")
        self.depto_combo.grid(row=row, column=1, sticky="w", pady=5)

        # Cargo
        tk.Label(job_frame, text="Cargo:", bg='white', font=('Arial', 10)).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.cargo_var = tk.StringVar()
        self.cargo_combo = ttk.Combobox(job_frame, textvariable=self.cargo_var, width=20, state="readonly")
        self.cargo_combo.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Sueldo
        tk.Label(job_frame, text="Sueldo:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.sueldo_var = tk.StringVar()
        self.sueldo_entry = tk.Entry(job_frame, textvariable=self.sueldo_var, width=15)
        self.sueldo_entry.grid(row=row, column=1, sticky="w", pady=5)

        # Estado
        tk.Label(job_frame, text="Estado:", bg='white', font=('Arial', 10)).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.estado_var = tk.StringVar()
        self.estado_combo = ttk.Combobox(
            job_frame,
            textvariable=self.estado_var,
            values=list(Config.ESTADOS_EMPLEADO.keys()),
            width=10,
            state="readonly"
        )
        self.estado_combo.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Tipo trabajador
        tk.Label(job_frame, text="Tipo Trabajador:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.tipo_tra_var = tk.StringVar()
        self.tipo_tra_combo = ttk.Combobox(
            job_frame,
            textvariable=self.tipo_tra_var,
            values=["1 - Operativo", "2 - Administrativo", "3 - Ejecutivo"],
            width=20,
            state="readonly"
        )
        self.tipo_tra_combo.grid(row=row, column=1, sticky="w", pady=5)

        # Tipo pago
        tk.Label(job_frame, text="Tipo Pago:", bg='white', font=('Arial', 10)).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.tipo_pgo_var = tk.StringVar()
        self.tipo_pgo_combo = ttk.Combobox(
            job_frame,
            textvariable=self.tipo_pgo_var,
            values=["1 - Semanal", "2 - Quincenal", "3 - Mensual"],
            width=15,
            state="readonly"
        )
        self.tipo_pgo_combo.grid(row=row, column=3, sticky="w", pady=5)

    def create_financial_tab(self):
        """Crear pestaña datos financieros"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="💰 Financiero")

        content_frame = tk.Frame(tab_frame, bg='white')
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Datos bancarios
        bank_frame = tk.LabelFrame(
            content_frame,
            text="Datos Bancarios",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=10
        )
        bank_frame.pack(fill="x", pady=(0, 10))

        row = 0

        # Banco
        tk.Label(bank_frame, text="Banco:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.banco_var = tk.StringVar()
        self.banco_combo = ttk.Combobox(
            bank_frame,
            textvariable=self.banco_var,
            values=[f"{k} - {v}" for k, v in Config.BANCOS.items()],
            width=30,
            state="readonly"
        )
        self.banco_combo.grid(row=row, column=1, columnspan=2, sticky="w", pady=5)

        row += 1

        # Cuenta banco
        tk.Label(bank_frame, text="Cuenta Bancaria:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.cuenta_banco_var = tk.StringVar()
        self.cuenta_banco_entry = tk.Entry(bank_frame, textvariable=self.cuenta_banco_var, width=25)
        self.cuenta_banco_entry.grid(row=row, column=1, sticky="w", pady=5)

        # Datos adicionales
        extras_frame = tk.LabelFrame(
            content_frame,
            text="Datos Adicionales",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=10
        )
        extras_frame.pack(fill="x", pady=(0, 10))

        row = 0

        # Anticipo
        tk.Label(extras_frame, text="Anticipo:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.anticipo_var = tk.StringVar(value="0.00")
        self.anticipo_entry = tk.Entry(extras_frame, textvariable=self.anticipo_var, width=15)
        self.anticipo_entry.grid(row=row, column=1, sticky="w", pady=5)

        # Descuento extra
        tk.Label(extras_frame, text="Desc. Extra:", bg='white', font=('Arial', 10)).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.dct_extra_var = tk.StringVar(value="0.00")
        self.dct_extra_entry = tk.Entry(extras_frame, textvariable=self.dct_extra_var, width=15)
        self.dct_extra_entry.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Ingreso extra
        tk.Label(extras_frame, text="Ing. Extra:", bg='white', font=('Arial', 10)).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.ing_extra_var = tk.StringVar(value="0.00")
        self.ing_extra_entry = tk.Entry(extras_frame, textvariable=self.ing_extra_var, width=15)
        self.ing_extra_entry.grid(row=row, column=1, sticky="w", pady=5)

    def create_ingresos_descuentos_tab(self):
        """Crear pestaña ingresos y descuentos"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="💳 Ing/Desc")

        # Placeholder por ahora
        placeholder_label = tk.Label(
            tab_frame,
            text="🚧 Módulo de Ingresos/Descuentos\\nEn desarrollo",
            font=('Arial', 14),
            bg='white',
            fg=Config.COLORS['text_light']
        )
        placeholder_label.pack(expand=True)

    def create_observaciones_tab(self):
        """Crear pestaña observaciones"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="📝 Observaciones")

        content_frame = tk.Frame(tab_frame, bg='white')
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Text area para observaciones
        obs_frame = tk.LabelFrame(
            content_frame,
            text="Observaciones y Notas",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=10
        )
        obs_frame.pack(fill="both", expand=True)

        self.observaciones_text = tk.Text(
            obs_frame,
            wrap=tk.WORD,
            width=60,
            height=15,
            font=('Arial', 10)
        )

        obs_scroll = ttk.Scrollbar(obs_frame, orient="vertical", command=self.observaciones_text.yview)
        self.observaciones_text.configure(yscrollcommand=obs_scroll.set)

        self.observaciones_text.pack(side="left", fill="both", expand=True)
        obs_scroll.pack(side="right", fill="y")

    def create_documents_tab(self):
        """Crear pestaña documentos"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="📄 Documentos")

        # Placeholder por ahora
        placeholder_label = tk.Label(
            tab_frame,
            text="📄 Módulo de Documentos\\nEn desarrollo",
            font=('Arial', 14),
            bg='white',
            fg=Config.COLORS['text_light']
        )
        placeholder_label.pack(expand=True)

    def load_departments(self):
        """Cargar departamentos en combos"""
        try:
            departamentos = self.session.query(Departamento).filter(Departamento.activo == True).all()
            dept_list = ["Todos"] + [f"{d.codigo} - {d.nombre_codigo}" for d in departamentos]

            self.search_dept_combo['values'] = dept_list
            self.search_dept_combo.set("Todos")

            dept_values = [f"{d.codigo} - {d.nombre_codigo}" for d in departamentos]
            self.depto_combo['values'] = dept_values

        except Exception as e:
            logger.error(f"Error cargando departamentos: {e}")

    def load_employees(self):
        """Cargar lista de empleados"""
        try:
            # Limpiar tree
            for item in self.employee_tree.get_children():
                self.employee_tree.delete(item)

            # Query base
            query = self.session.query(Empleado)

            # Aplicar filtros de busqueda si existen
            if hasattr(self, 'search_employee_var') and self.search_employee_var.get():
                query = query.filter(Empleado.empleado.like(f"%{self.search_employee_var.get()}%"))

            if hasattr(self, 'search_cedula_var') and self.search_cedula_var.get():
                query = query.filter(Empleado.cedula.like(f"%{self.search_cedula_var.get()}%"))

            if hasattr(self, 'search_name_var') and self.search_name_var.get():
                search_text = self.search_name_var.get().upper()
                query = query.filter(
                    (Empleado.nombres.like(f"%{search_text}%")) |
                    (Empleado.apellidos.like(f"%{search_text}%"))
                )

            # Filtro de estado
            if hasattr(self, 'search_status_var'):
                status = self.search_status_var.get()
                if status == "Activos":
                    query = query.filter(Empleado.activo == True)
                elif status == "Inactivos":
                    query = query.filter(Empleado.activo == False)

            # Ejecutar query
            empleados = query.order_by(Empleado.nombres, Empleado.apellidos).all()

            # Poblar tree
            for emp in empleados:
                estado = "Activo" if emp.activo else "Inactivo"
                nombre_completo = f"{emp.nombres} {emp.apellidos}"

                self.employee_tree.insert("", "end", values=(
                    emp.empleado,
                    emp.cedula,
                    nombre_completo,
                    estado
                ))

        except Exception as e:
            logger.error(f"Error cargando empleados: {e}")
            messagebox.showerror("Error", f"Error al cargar empleados: {str(e)}")

    def search_employees(self):
        """Buscar empleados con filtros"""
        self.load_employees()

    def clear_search(self):
        """Limpiar filtros de busqueda"""
        self.search_employee_var.set("")
        self.search_cedula_var.set("")
        self.search_name_var.set("")
        self.search_dept_combo.set("Todos")
        self.search_status_combo.set("Activos")
        self.load_employees()

    def on_employee_select(self, event):
        """Manejar seleccion de empleado"""
        selection = self.employee_tree.selection()
        if selection:
            item = self.employee_tree.item(selection[0])
            employee_code = item['values'][0]
            self.load_employee_details(employee_code)

            # Habilitar botones
            self.edit_btn.config(state='normal')
            self.delete_btn.config(state='normal')

    def on_employee_double_click(self, event):
        """Manejar doble clic en empleado"""
        self.edit_employee()

    def load_employee_details(self, employee_code):
        """Cargar detalles del empleado seleccionado"""
        try:
            employee = self.session.query(Empleado).filter(Empleado.empleado == employee_code).first()
            if not employee:
                return

            self.current_employee = employee

            # Actualizar titulo
            self.details_title.config(text=f"Detalles: {employee.nombres} {employee.apellidos}")

            # Llenar campos generales
            self.codigo_var.set(employee.empleado or "")
            self.cedula_var.set(employee.cedula or "")
            self.nombres_var.set(employee.nombres or "")
            self.apellidos_var.set(employee.apellidos or "")
            self.fecha_nac_var.set(employee.fecha_nac.strftime("%d/%m/%Y") if employee.fecha_nac else "")
            self.fecha_ing_var.set(employee.fecha_ing.strftime("%d/%m/%Y") if employee.fecha_ing else "")

            # Campos personales
            self.sexo_var.set(employee.sexo or "")
            self.estado_civil_var.set(employee.estado_civil or "")
            self.direccion_var.set(employee.direccion or "")
            self.telefono_var.set(employee.telefono or "")
            self.celular_var.set(employee.celular or "")
            self.email_var.set(employee.email or "")

            # Campos laborales
            self.depto_var.set(employee.depto or "")
            self.cargo_var.set(employee.cargo or "")
            self.sueldo_var.set(str(employee.sueldo) if employee.sueldo else "0.00")
            self.estado_var.set(employee.estado or "ACT")
            self.tipo_tra_var.set(f"{employee.tipo_tra} - {Config.TIPOS_TRABAJADOR.get(employee.tipo_tra, 'Operativo')}" if employee.tipo_tra else "")
            self.tipo_pgo_var.set(f"{employee.tipo_pgo} - {Config.TIPOS_PAGO.get(employee.tipo_pgo, 'Mensual')}" if employee.tipo_pgo else "")

            # Campos financieros
            self.banco_var.set(employee.banco or "")
            self.cuenta_banco_var.set(employee.cuenta_banco or "")
            self.anticipo_var.set(str(employee.anticipo) if employee.anticipo else "0.00")
            self.dct_extra_var.set(str(employee.dct_extra) if employee.dct_extra else "0.00")
            self.ing_extra_var.set(str(employee.ing_extra) if employee.ing_extra else "0.00")

            # Observaciones
            # self.observaciones_text.delete(1.0, tk.END)
            # self.observaciones_text.insert(1.0, employee.observaciones or "")

        except Exception as e:
            logger.error(f"Error cargando detalles del empleado: {e}")
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")

    def new_employee(self):
        """Crear nuevo empleado"""
        # Limpiar campos
        self.clear_employee_fields()

        # Generar nuevo codigo
        new_code = self.generate_employee_code()
        self.codigo_var.set(new_code)

        # Habilitar edicion
        self.edit_btn.config(state='disabled')
        self.save_btn.config(state='normal')
        self.delete_btn.config(state='disabled')

        # Enfocar primer campo
        self.cedula_entry.focus()

        self.current_employee = None
        self.details_title.config(text="Nuevo Empleado")

    def generate_employee_code(self):
        """Generar nuevo codigo de empleado"""
        try:
            # Obtener ultimo codigo
            last_employee = self.session.query(Empleado).order_by(Empleado.empleado.desc()).first()
            if last_employee:
                last_code = int(last_employee.empleado)
                new_code = str(last_code + 1).zfill(6)
            else:
                new_code = "001001"

            return new_code
        except:
            return "001001"

    def clear_employee_fields(self):
        """Limpiar todos los campos"""
        # Campos generales
        self.codigo_var.set("")
        self.cedula_var.set("")
        self.nombres_var.set("")
        self.apellidos_var.set("")
        self.fecha_nac_var.set("")
        self.fecha_ing_var.set(datetime.now().strftime("%d/%m/%Y"))

        # Campos personales
        self.sexo_var.set("")
        self.estado_civil_var.set("")
        self.direccion_var.set("")
        self.telefono_var.set("")
        self.celular_var.set("")
        self.email_var.set("")

        # Campos laborales
        self.depto_var.set("")
        self.cargo_var.set("")
        self.sueldo_var.set(str(Config.SBU))
        self.estado_var.set("ACT")
        self.tipo_tra_var.set("")
        self.tipo_pgo_var.set("")

        # Campos financieros
        self.banco_var.set("")
        self.cuenta_banco_var.set("")
        self.anticipo_var.set("0.00")
        self.dct_extra_var.set("0.00")
        self.ing_extra_var.set("0.00")

    def edit_employee(self):
        """Habilitar edicion del empleado actual"""
        if not self.current_employee:
            return

        self.edit_btn.config(state='disabled')
        self.save_btn.config(state='normal')

    def save_employee(self):
        """Guardar empleado (nuevo o editado)"""
        try:
            # Validaciones basicas
            if not self.cedula_var.get():
                messagebox.showerror("Error", "La cédula es obligatoria")
                return

            if not self.nombres_var.get():
                messagebox.showerror("Error", "Los nombres son obligatorios")
                return

            if not self.apellidos_var.get():
                messagebox.showerror("Error", "Los apellidos son obligatorios")
                return

            # Si es nuevo empleado
            if not self.current_employee:
                employee = Empleado()
                employee.empleado = self.codigo_var.get()
            else:
                employee = self.current_employee

            # Asignar valores
            employee.cedula = self.cedula_var.get()
            employee.nombres = self.nombres_var.get().upper()
            employee.apellidos = self.apellidos_var.get().upper()

            # Fechas
            if self.fecha_nac_var.get():
                employee.fecha_nac = datetime.strptime(self.fecha_nac_var.get(), "%d/%m/%Y").date()
            if self.fecha_ing_var.get():
                employee.fecha_ing = datetime.strptime(self.fecha_ing_var.get(), "%d/%m/%Y").date()

            # Datos personales
            employee.sexo = self.sexo_var.get()
            employee.estado_civil = self.estado_civil_var.get()
            employee.direccion = self.direccion_var.get().upper()
            employee.telefono = self.telefono_var.get()
            employee.celular = self.celular_var.get()
            employee.email = self.email_var.get().lower()

            # Datos laborales
            employee.depto = self.depto_var.get().split(' - ')[0] if ' - ' in self.depto_var.get() else self.depto_var.get()
            employee.cargo = self.cargo_var.get().split(' - ')[0] if ' - ' in self.cargo_var.get() else self.cargo_var.get()
            employee.sueldo = Decimal(self.sueldo_var.get() or '0')
            employee.estado = self.estado_var.get()

            # Tipos
            if self.tipo_tra_var.get():
                employee.tipo_tra = int(self.tipo_tra_var.get()[0])
            if self.tipo_pgo_var.get():
                employee.tipo_pgo = int(self.tipo_pgo_var.get()[0])

            # Datos financieros
            employee.banco = self.banco_var.get().split(' - ')[0] if ' - ' in self.banco_var.get() else self.banco_var.get()
            employee.cuenta_banco = self.cuenta_banco_var.get()
            employee.anticipo = Decimal(self.anticipo_var.get() or '0')
            employee.dct_extra = Decimal(self.dct_extra_var.get() or '0')
            employee.ing_extra = Decimal(self.ing_extra_var.get() or '0')

            # Estado activo
            employee.activo = employee.estado == 'ACT'

            # Guardar en BD
            if not self.current_employee:
                self.session.add(employee)

            self.session.commit()

            # Actualizar lista
            self.load_employees()

            # Actualizar botones
            self.edit_btn.config(state='normal')
            self.save_btn.config(state='disabled')

            messagebox.showinfo("Éxito", "Empleado guardado correctamente")

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error guardando empleado: {e}")
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def delete_employee(self):
        """Eliminar empleado actual"""
        if not self.current_employee:
            return

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al empleado {self.current_employee.nombres} {self.current_employee.apellidos}?"):
            try:
                self.session.delete(self.current_employee)
                self.session.commit()

                # Limpiar campos y actualizar lista
                self.clear_employee_fields()
                self.load_employees()

                # Deshabilitar botones
                self.edit_btn.config(state='disabled')
                self.save_btn.config(state='disabled')
                self.delete_btn.config(state='disabled')

                self.current_employee = None
                self.details_title.config(text="Detalles del Empleado")

                messagebox.showinfo("Éxito", "Empleado eliminado correctamente")

            except Exception as e:
                self.session.rollback()
                logger.error(f"Error eliminando empleado: {e}")
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def carga_masiva_empleados(self):
        """Abrir ventana de carga masiva de empleados"""
        try:
            show_carga_masiva_empleados(self, self.session)
            # Recargar empleados después de la carga masiva
            self.load_employees()
        except Exception as e:
            logger.error(f"Error en carga masiva: {e}")
            messagebox.showerror("Error", f"Error abriendo carga masiva: {str(e)}")

    def import_employees(self):
        """Método legacy - usar carga_masiva_empleados en su lugar"""
        self.carga_masiva_empleados()