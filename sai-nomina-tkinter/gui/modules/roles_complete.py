#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo de Roles de Pago Completo - Sistema SGN
Visualización de roles actuales e histórico de empleados
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, date, timedelta
import logging
from decimal import Decimal
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, desc, asc

from config import Config
from database.connection import get_session
from database.models import RolPago, Empleado

logger = logging.getLogger(__name__)

class RolesCompleteModule(tk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent, bg='white')
        self.main_app = main_app
        self.session = get_session()
        self.current_role = None

        self.pack(fill="both", expand=True)
        self.setup_ui()
        self.load_roles()

    def setup_ui(self):
        """Configurar interfaz completa del modulo"""
        # Header del modulo
        self.create_module_header()

        # Container principal
        main_container = tk.Frame(self, bg='white')
        main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Panel de busqueda y filtros
        self.create_search_panel(main_container)

        # Container de contenido (lista + detalles)
        content_container = tk.Frame(main_container, bg='white')
        content_container.pack(fill="both", expand=True, pady=(10, 0))

        # Panel izquierdo - Lista de roles
        self.create_roles_list(content_container)

        # Panel derecho - Detalles del rol
        self.create_role_details(content_container)

    def create_module_header(self):
        """Crear header del modulo"""
        header_frame = tk.Frame(self, bg='white')
        header_frame.pack(fill="x", padx=15, pady=15)

        # Titulo y descripcion
        title_label = tk.Label(
            header_frame,
            text="💰 Roles de Pago",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Consulta de roles de pago actuales e histórico por empleado",
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
            text="🔍 Filtros de Búsqueda",
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

        # Buscar por empleado
        tk.Label(row1_frame, text="Empleado:", bg='white', font=('Arial', 10)).pack(side="left")
        self.empleado_var = tk.StringVar()
        self.empleado_entry = tk.Entry(row1_frame, textvariable=self.empleado_var, width=20)
        self.empleado_entry.pack(side="left", padx=(5, 15))

        # Buscar por cédula
        tk.Label(row1_frame, text="Cédula:", bg='white', font=('Arial', 10)).pack(side="left")
        self.cedula_var = tk.StringVar()
        self.cedula_entry = tk.Entry(row1_frame, textvariable=self.cedula_var, width=15)
        self.cedula_entry.pack(side="left", padx=(5, 15))

        # Período
        tk.Label(row1_frame, text="Período:", bg='white', font=('Arial', 10)).pack(side="left")
        self.periodo_var = tk.StringVar()
        self.periodo_combo = ttk.Combobox(row1_frame, textvariable=self.periodo_var, width=10, state="readonly")
        self.periodo_combo.pack(side="left", padx=(5, 15))

        # Row 2 - Filtros adicionales
        row2_frame = tk.Frame(search_frame, bg='white')
        row2_frame.pack(fill="x", pady=(0, 10))

        # Estado
        tk.Label(row2_frame, text="Estado:", bg='white', font=('Arial', 10)).pack(side="left")
        self.estado_var = tk.StringVar()
        self.estado_combo = ttk.Combobox(
            row2_frame,
            textvariable=self.estado_var,
            values=["TODOS", "BORRADOR", "PROCESADO", "PAGADO", "ANULADO"],
            width=12,
            state="readonly"
        )
        self.estado_combo.set("TODOS")
        self.estado_combo.pack(side="left", padx=(5, 15))

        # Tipo nómina
        tk.Label(row2_frame, text="Tipo Nómina:", bg='white', font=('Arial', 10)).pack(side="left")
        self.tipo_nomina_var = tk.StringVar()
        self.tipo_nomina_combo = ttk.Combobox(
            row2_frame,
            textvariable=self.tipo_nomina_var,
            values=["TODOS", "Semanal", "Quincenal", "Mensual"],
            width=12,
            state="readonly"
        )
        self.tipo_nomina_combo.set("TODOS")
        self.tipo_nomina_combo.pack(side="left", padx=(5, 15))

        # Botones de accion
        buttons_frame = tk.Frame(row2_frame, bg='white')
        buttons_frame.pack(side="right")

        search_btn = tk.Button(
            buttons_frame,
            text="🔍 Buscar",
            command=self.search_roles,
            bg=Config.COLORS['primary'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2'
        )
        search_btn.pack(side="left", padx=(0, 5))

        clear_btn = tk.Button(
            buttons_frame,
            text="🗑️ Limpiar",
            command=self.clear_search,
            bg=Config.COLORS['text_light'],
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2'
        )
        clear_btn.pack(side="left", padx=(0, 5))

        export_btn = tk.Button(
            buttons_frame,
            text="📊 Exportar",
            command=self.export_roles,
            bg=Config.COLORS['success'],
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2'
        )
        export_btn.pack(side="left")

    def create_roles_list(self, parent):
        """Crear lista de roles"""
        # Frame izquierdo - Lista
        left_frame = tk.LabelFrame(
            parent,
            text="📋 Lista de Roles de Pago",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=10,
            pady=8
        )
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Lista/Tree de roles
        list_frame = tk.Frame(left_frame, bg='white')
        list_frame.pack(fill="both", expand=True)

        # Treeview
        columns = ("ID", "Período", "Empleado", "Nombre", "Neto", "Estado")
        self.roles_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        # Configurar columnas
        self.roles_tree.heading("ID", text="ID")
        self.roles_tree.heading("Período", text="Período")
        self.roles_tree.heading("Empleado", text="Empleado")
        self.roles_tree.heading("Nombre", text="Nombre Completo")
        self.roles_tree.heading("Neto", text="Neto Pagar")
        self.roles_tree.heading("Estado", text="Estado")

        self.roles_tree.column("ID", width=60, anchor="center")
        self.roles_tree.column("Período", width=80, anchor="center")
        self.roles_tree.column("Empleado", width=80, anchor="center")
        self.roles_tree.column("Nombre", width=200, anchor="w")
        self.roles_tree.column("Neto", width=100, anchor="e")
        self.roles_tree.column("Estado", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.roles_tree.yview)
        self.roles_tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.roles_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Eventos
        self.roles_tree.bind("<ButtonRelease-1>", self.on_role_select)
        self.roles_tree.bind("<Double-1>", self.on_role_double_click)

    def create_role_details(self, parent):
        """Crear panel de detalles del rol"""
        # Frame derecho
        right_frame = tk.LabelFrame(
            parent,
            text="📄 Detalle del Rol de Pago",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=10,
            pady=8
        )
        right_frame.pack(side="right", fill="both", expand=True)

        # Crear notebook para pestañas
        self.details_notebook = ttk.Notebook(right_frame)
        self.details_notebook.pack(fill="both", expand=True)

        # Crear pestañas
        self.create_general_info_tab()
        self.create_ingresos_tab()
        self.create_descuentos_tab()
        self.create_resumen_tab()

    def create_general_info_tab(self):
        """Crear pestaña de información general"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="📋 General")

        # Información del empleado
        employee_frame = tk.LabelFrame(
            tab_frame,
            text="Información del Empleado",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=10,
            pady=8
        )
        employee_frame.pack(fill="x", padx=10, pady=5)

        # Grid de información
        row = 0

        # Código empleado
        tk.Label(employee_frame, text="Código:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_empleado = tk.Label(employee_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_empleado.grid(row=row, column=1, sticky="w", pady=5)

        # Nombres
        tk.Label(employee_frame, text="Nombres:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_nombres = tk.Label(employee_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_nombres.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Período
        tk.Label(employee_frame, text="Período:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_periodo = tk.Label(employee_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_periodo.grid(row=row, column=1, sticky="w", pady=5)

        # Estado
        tk.Label(employee_frame, text="Estado:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_estado = tk.Label(employee_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_estado.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Fechas
        tk.Label(employee_frame, text="Desde:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_fecha_desde = tk.Label(employee_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_fecha_desde.grid(row=row, column=1, sticky="w", pady=5)

        tk.Label(employee_frame, text="Hasta:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_fecha_hasta = tk.Label(employee_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_fecha_hasta.grid(row=row, column=3, sticky="w", pady=5)

        # Información del período
        period_frame = tk.LabelFrame(
            tab_frame,
            text="Información del Período",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=10,
            pady=8
        )
        period_frame.pack(fill="x", padx=10, pady=5)

        row = 0

        # Días trabajados
        tk.Label(period_frame, text="Días Trabajados:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_dias_trabajados = tk.Label(period_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_dias_trabajados.grid(row=row, column=1, sticky="w", pady=5)

        # Tipo nómina
        tk.Label(period_frame, text="Tipo Nómina:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_tipo_nomina = tk.Label(period_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_tipo_nomina.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Horas normales
        tk.Label(period_frame, text="Horas Normales:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_horas_normales = tk.Label(period_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_horas_normales.grid(row=row, column=1, sticky="w", pady=5)

        # Sueldo básico
        tk.Label(period_frame, text="Sueldo Básico:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_sueldo_basico = tk.Label(period_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_sueldo_basico.grid(row=row, column=3, sticky="w", pady=5)

    def create_ingresos_tab(self):
        """Crear pestaña de ingresos"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="💰 Ingresos")

        # Frame para ingresos
        ingresos_frame = tk.LabelFrame(
            tab_frame,
            text="Detalle de Ingresos",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['success'],
            padx=10,
            pady=8
        )
        ingresos_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Grid de ingresos
        row = 0

        # Horas extras
        tk.Label(ingresos_frame, text="Horas Extras 25%:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_horas_25 = tk.Label(ingresos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_horas_25.grid(row=row, column=1, sticky="w", pady=5)

        tk.Label(ingresos_frame, text="Horas Extras 50%:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_horas_50 = tk.Label(ingresos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_horas_50.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        tk.Label(ingresos_frame, text="Horas Extras 100%:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_horas_100 = tk.Label(ingresos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_horas_100.grid(row=row, column=1, sticky="w", pady=5)

        tk.Label(ingresos_frame, text="Total H. Extras:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_total_horas_extras = tk.Label(ingresos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_total_horas_extras.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Otros ingresos
        tk.Label(ingresos_frame, text="Comisiones:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_comisiones = tk.Label(ingresos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_comisiones.grid(row=row, column=1, sticky="w", pady=5)

        tk.Label(ingresos_frame, text="Bonos:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_bonos = tk.Label(ingresos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_bonos.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        tk.Label(ingresos_frame, text="Otros Ingresos:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_otros_ingresos = tk.Label(ingresos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_otros_ingresos.grid(row=row, column=1, sticky="w", pady=5)

        # Separador
        separator = tk.Frame(ingresos_frame, bg=Config.COLORS['success'], height=2)
        separator.grid(row=row+1, column=0, columnspan=4, sticky="ew", pady=10)

        # Total ingresos
        tk.Label(ingresos_frame, text="TOTAL INGRESOS:", bg='white', font=('Arial', 12, 'bold'), fg=Config.COLORS['success']).grid(row=row+2, column=0, columnspan=2, sticky="w", padx=(0, 10), pady=10)
        self.detail_total_ingresos = tk.Label(ingresos_frame, text="$0.00", bg='white', font=('Arial', 12, 'bold'), fg=Config.COLORS['success'])
        self.detail_total_ingresos.grid(row=row+2, column=2, columnspan=2, sticky="e", pady=10)

    def create_descuentos_tab(self):
        """Crear pestaña de descuentos"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="🔻 Descuentos")

        # Frame para descuentos
        descuentos_frame = tk.LabelFrame(
            tab_frame,
            text="Detalle de Descuentos",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['danger'],
            padx=10,
            pady=8
        )
        descuentos_frame.pack(fill="both", expand=True, padx=10, pady=10)

        row = 0

        # Descuentos legales
        tk.Label(descuentos_frame, text="Aporte IESS:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_aporte_iess = tk.Label(descuentos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_aporte_iess.grid(row=row, column=1, sticky="w", pady=5)

        tk.Label(descuentos_frame, text="Impuesto Renta:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_impuesto_renta = tk.Label(descuentos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_impuesto_renta.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        # Otros descuentos
        tk.Label(descuentos_frame, text="Préstamos:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_prestamos = tk.Label(descuentos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_prestamos.grid(row=row, column=1, sticky="w", pady=5)

        tk.Label(descuentos_frame, text="Anticipos:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=2, sticky="w", padx=(30, 10), pady=5)
        self.detail_anticipos = tk.Label(descuentos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_anticipos.grid(row=row, column=3, sticky="w", pady=5)

        row += 1

        tk.Label(descuentos_frame, text="Otros Descuentos:", bg='white', font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.detail_otros_descuentos = tk.Label(descuentos_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_otros_descuentos.grid(row=row, column=1, sticky="w", pady=5)

        # Separador
        separator = tk.Frame(descuentos_frame, bg=Config.COLORS['danger'], height=2)
        separator.grid(row=row+1, column=0, columnspan=4, sticky="ew", pady=10)

        # Total descuentos
        tk.Label(descuentos_frame, text="TOTAL DESCUENTOS:", bg='white', font=('Arial', 12, 'bold'), fg=Config.COLORS['danger']).grid(row=row+2, column=0, columnspan=2, sticky="w", padx=(0, 10), pady=10)
        self.detail_total_descuentos = tk.Label(descuentos_frame, text="$0.00", bg='white', font=('Arial', 12, 'bold'), fg=Config.COLORS['danger'])
        self.detail_total_descuentos.grid(row=row+2, column=2, columnspan=2, sticky="e", pady=10)

    def create_resumen_tab(self):
        """Crear pestaña de resumen"""
        tab_frame = tk.Frame(self.details_notebook, bg='white')
        self.details_notebook.add(tab_frame, text="📊 Resumen")

        # Frame resumen
        resumen_frame = tk.Frame(tab_frame, bg='white')
        resumen_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tarjetas de resumen
        cards_frame = tk.Frame(resumen_frame, bg='white')
        cards_frame.pack(fill="x", pady=20)

        # Tarjeta ingresos
        ingresos_card = tk.Frame(cards_frame, bg=Config.COLORS['success'], relief='raised', bd=2)
        ingresos_card.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(ingresos_card, text="TOTAL INGRESOS", bg=Config.COLORS['success'], fg='white', font=('Arial', 12, 'bold')).pack(pady=10)
        self.resumen_ingresos = tk.Label(ingresos_card, text="$0.00", bg=Config.COLORS['success'], fg='white', font=('Arial', 16, 'bold'))
        self.resumen_ingresos.pack(pady=10)

        # Tarjeta descuentos
        descuentos_card = tk.Frame(cards_frame, bg=Config.COLORS['danger'], relief='raised', bd=2)
        descuentos_card.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(descuentos_card, text="TOTAL DESCUENTOS", bg=Config.COLORS['danger'], fg='white', font=('Arial', 12, 'bold')).pack(pady=10)
        self.resumen_descuentos = tk.Label(descuentos_card, text="$0.00", bg=Config.COLORS['danger'], fg='white', font=('Arial', 16, 'bold'))
        self.resumen_descuentos.pack(pady=10)

        # Tarjeta neto
        neto_card = tk.Frame(cards_frame, bg=Config.COLORS['primary'], relief='raised', bd=2)
        neto_card.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(neto_card, text="NETO A PAGAR", bg=Config.COLORS['primary'], fg='white', font=('Arial', 12, 'bold')).pack(pady=10)
        self.resumen_neto = tk.Label(neto_card, text="$0.00", bg=Config.COLORS['primary'], fg='white', font=('Arial', 16, 'bold'))
        self.resumen_neto.pack(pady=10)

        # Información adicional
        info_frame = tk.LabelFrame(
            resumen_frame,
            text="Información Adicional",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=10,
            pady=8
        )
        info_frame.pack(fill="both", expand=True, pady=20)

        # Fechas de proceso y pago
        dates_frame = tk.Frame(info_frame, bg='white')
        dates_frame.pack(fill="x", pady=10)

        tk.Label(dates_frame, text="Fecha Proceso:", bg='white', font=('Arial', 10, 'bold')).pack(side="left")
        self.detail_fecha_proceso = tk.Label(dates_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_fecha_proceso.pack(side="left", padx=(10, 30))

        tk.Label(dates_frame, text="Fecha Pago:", bg='white', font=('Arial', 10, 'bold')).pack(side="left")
        self.detail_fecha_pago = tk.Label(dates_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_fecha_pago.pack(side="left", padx=10)

        # Procesado por
        procesado_frame = tk.Frame(info_frame, bg='white')
        procesado_frame.pack(fill="x", pady=5)

        tk.Label(procesado_frame, text="Procesado por:", bg='white', font=('Arial', 10, 'bold')).pack(side="left")
        self.detail_procesado_por = tk.Label(procesado_frame, text="-", bg='white', font=('Arial', 10))
        self.detail_procesado_por.pack(side="left", padx=10)

        # Observaciones
        obs_frame = tk.Frame(info_frame, bg='white')
        obs_frame.pack(fill="both", expand=True, pady=10)

        tk.Label(obs_frame, text="Observaciones:", bg='white', font=('Arial', 10, 'bold')).pack(anchor="w")
        self.detail_observaciones = tk.Text(obs_frame, height=4, state='disabled', bg='#f8f9fa')
        self.detail_observaciones.pack(fill="both", expand=True, pady=5)

    def load_periods(self):
        """Cargar períodos disponibles"""
        try:
            periods = self.session.query(RolPago.periodo).distinct().order_by(desc(RolPago.periodo)).all()
            period_values = ["TODOS"] + [p[0] for p in periods]
            self.periodo_combo['values'] = period_values
            if len(period_values) > 1:
                self.periodo_combo.set(period_values[1])  # Seleccionar el más reciente
            else:
                self.periodo_combo.set("TODOS")
        except Exception as e:
            logger.error(f"Error cargando períodos: {str(e)}")
            self.periodo_combo['values'] = ["TODOS"]
            self.periodo_combo.set("TODOS")

    def load_roles(self):
        """Cargar roles de pago"""
        try:
            # Cargar períodos primero
            self.load_periods()

            # Limpiar árbol
            for item in self.roles_tree.get_children():
                self.roles_tree.delete(item)

            # Query base
            query = self.session.query(RolPago, Empleado).join(
                Empleado, RolPago.empleado == Empleado.empleado
            ).order_by(desc(RolPago.fecha_proceso), desc(RolPago.periodo))

            # Aplicar filtros si existen
            roles = query.all()

            # Insertar en tree
            for rol, empleado in roles:
                # Formatear valores
                neto_format = f"${float(rol.neto_pagar or 0):,.2f}"
                nombre_completo = f"{empleado.nombres} {empleado.apellidos}"

                # Determinar color según estado
                tags = ()
                if rol.estado == 'PAGADO':
                    tags = ('pagado',)
                elif rol.estado == 'PROCESADO':
                    tags = ('procesado',)
                elif rol.estado == 'ANULADO':
                    tags = ('anulado',)

                self.roles_tree.insert("", "end", values=(
                    rol.id,
                    rol.periodo,
                    rol.empleado,
                    nombre_completo,
                    neto_format,
                    rol.estado or 'BORRADOR'
                ), tags=tags)

            # Configurar colores
            self.roles_tree.tag_configure('pagado', background='#d4edda')
            self.roles_tree.tag_configure('procesado', background='#cce5ff')
            self.roles_tree.tag_configure('anulado', background='#f8d7da')

            # Limpiar detalles
            self.clear_details()

            logger.info(f"Cargados {len(roles)} roles de pago")

        except Exception as e:
            logger.error(f"Error cargando roles: {str(e)}")
            messagebox.showerror("Error", f"Error cargando roles de pago: {str(e)}")

    def search_roles(self):
        """Buscar roles con filtros"""
        try:
            # Limpiar tree
            for item in self.roles_tree.get_children():
                self.roles_tree.delete(item)

            # Query base con join
            query = self.session.query(RolPago, Empleado).join(
                Empleado, RolPago.empleado == Empleado.empleado
            )

            # Aplicar filtros
            filters = []

            # Filtro por empleado
            if self.empleado_var.get().strip():
                filters.append(RolPago.empleado.like(f"%{self.empleado_var.get().strip()}%"))

            # Filtro por cédula
            if self.cedula_var.get().strip():
                filters.append(Empleado.cedula.like(f"%{self.cedula_var.get().strip()}%"))

            # Filtro por período
            if self.periodo_var.get() and self.periodo_var.get() != "TODOS":
                filters.append(RolPago.periodo == self.periodo_var.get())

            # Filtro por estado
            if self.estado_var.get() and self.estado_var.get() != "TODOS":
                filters.append(RolPago.estado == self.estado_var.get())

            # Filtro por tipo nómina
            if self.tipo_nomina_var.get() and self.tipo_nomina_var.get() != "TODOS":
                tipo_map = {"Semanal": 1, "Quincenal": 2, "Mensual": 3}
                if self.tipo_nomina_var.get() in tipo_map:
                    filters.append(RolPago.tipo_nomina == tipo_map[self.tipo_nomina_var.get()])

            # Aplicar filtros
            if filters:
                query = query.filter(and_(*filters))

            # Ordenar
            query = query.order_by(desc(RolPago.fecha_proceso), desc(RolPago.periodo))

            # Ejecutar query
            roles = query.all()

            # Insertar resultados
            for rol, empleado in roles:
                neto_format = f"${float(rol.neto_pagar or 0):,.2f}"
                nombre_completo = f"{empleado.nombres} {empleado.apellidos}"

                tags = ()
                if rol.estado == 'PAGADO':
                    tags = ('pagado',)
                elif rol.estado == 'PROCESADO':
                    tags = ('procesado',)
                elif rol.estado == 'ANULADO':
                    tags = ('anulado',)

                self.roles_tree.insert("", "end", values=(
                    rol.id,
                    rol.periodo,
                    rol.empleado,
                    nombre_completo,
                    neto_format,
                    rol.estado or 'BORRADOR'
                ), tags=tags)

            # Configurar colores
            self.roles_tree.tag_configure('pagado', background='#d4edda')
            self.roles_tree.tag_configure('procesado', background='#cce5ff')
            self.roles_tree.tag_configure('anulado', background='#f8d7da')

            logger.info(f"Búsqueda completada: {len(roles)} resultados")

        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")

    def clear_search(self):
        """Limpiar filtros de búsqueda"""
        self.empleado_var.set("")
        self.cedula_var.set("")
        self.periodo_var.set("TODOS")
        self.estado_var.set("TODOS")
        self.tipo_nomina_var.set("TODOS")
        self.load_roles()

    def on_role_select(self, event):
        """Manejar selección de rol"""
        selection = self.roles_tree.selection()
        if selection:
            item = self.roles_tree.item(selection[0])
            values = item['values']
            if values:
                rol_id = values[0]
                self.show_role_details(rol_id)

    def on_role_double_click(self, event):
        """Manejar doble clic en rol"""
        # Por ahora solo mostrar detalles, se puede agregar edición si es necesario
        pass

    def show_role_details(self, rol_id):
        """Mostrar detalles del rol seleccionado"""
        try:
            # Buscar rol con empleado
            rol_empleado = self.session.query(RolPago, Empleado).join(
                Empleado, RolPago.empleado == Empleado.empleado
            ).filter(RolPago.id == rol_id).first()

            if not rol_empleado:
                self.clear_details()
                return

            rol, empleado = rol_empleado
            self.current_role = rol

            # Llenar información general
            self.detail_empleado.config(text=rol.empleado or "-")
            nombre_completo = f"{empleado.nombres} {empleado.apellidos}"
            self.detail_nombres.config(text=nombre_completo)
            self.detail_periodo.config(text=rol.periodo or "-")
            self.detail_estado.config(text=rol.estado or "BORRADOR")
            self.detail_fecha_desde.config(text=rol.fecha_desde.strftime("%d/%m/%Y") if rol.fecha_desde else "-")
            self.detail_fecha_hasta.config(text=rol.fecha_hasta.strftime("%d/%m/%Y") if rol.fecha_hasta else "-")

            # Información del período
            self.detail_dias_trabajados.config(text=str(rol.dias_trabajados) if rol.dias_trabajados else "-")
            tipo_nomina_map = {1: "Semanal", 2: "Quincenal", 3: "Mensual"}
            self.detail_tipo_nomina.config(text=tipo_nomina_map.get(rol.tipo_nomina, "-"))
            self.detail_horas_normales.config(text=f"{float(rol.horas_normales or 0):.2f}" if rol.horas_normales else "-")
            self.detail_sueldo_basico.config(text=f"${float(rol.sueldo_basico or 0):,.2f}" if rol.sueldo_basico else "-")

            # Ingresos detallados
            self.detail_horas_25.config(text=f"{float(rol.horas_extras_25 or 0):.2f}" if rol.horas_extras_25 else "-")
            self.detail_horas_50.config(text=f"{float(rol.horas_extras_50 or 0):.2f}" if rol.horas_extras_50 else "-")
            self.detail_horas_100.config(text=f"{float(rol.horas_extras_100 or 0):.2f}" if rol.horas_extras_100 else "-")
            self.detail_total_horas_extras.config(text=f"${float(rol.horas_extras or 0):,.2f}" if rol.horas_extras else "-")
            self.detail_comisiones.config(text=f"${float(rol.comisiones or 0):,.2f}" if rol.comisiones else "-")
            self.detail_bonos.config(text=f"${float(rol.bonos or 0):,.2f}" if rol.bonos else "-")
            self.detail_otros_ingresos.config(text=f"${float(rol.otros_ingresos or 0):,.2f}" if rol.otros_ingresos else "-")
            self.detail_total_ingresos.config(text=f"${float(rol.total_ingresos or 0):,.2f}")

            # Descuentos detallados
            self.detail_aporte_iess.config(text=f"${float(rol.aporte_iess or 0):,.2f}" if rol.aporte_iess else "-")
            self.detail_impuesto_renta.config(text=f"${float(rol.impuesto_renta or 0):,.2f}" if rol.impuesto_renta else "-")
            self.detail_prestamos.config(text=f"${float(rol.prestamos or 0):,.2f}" if rol.prestamos else "-")
            self.detail_anticipos.config(text=f"${float(rol.anticipos or 0):,.2f}" if rol.anticipos else "-")
            self.detail_otros_descuentos.config(text=f"${float(rol.otros_descuentos or 0):,.2f}" if rol.otros_descuentos else "-")
            self.detail_total_descuentos.config(text=f"${float(rol.total_descuentos or 0):,.2f}")

            # Resumen
            self.resumen_ingresos.config(text=f"${float(rol.total_ingresos or 0):,.2f}")
            self.resumen_descuentos.config(text=f"${float(rol.total_descuentos or 0):,.2f}")
            self.resumen_neto.config(text=f"${float(rol.neto_pagar or 0):,.2f}")

            # Información adicional
            self.detail_fecha_proceso.config(text=rol.fecha_proceso.strftime("%d/%m/%Y %H:%M") if rol.fecha_proceso else "-")
            self.detail_fecha_pago.config(text=rol.fecha_pago.strftime("%d/%m/%Y") if rol.fecha_pago else "-")
            self.detail_procesado_por.config(text=rol.procesado_por or "-")

            # Observaciones
            self.detail_observaciones.config(state='normal')
            self.detail_observaciones.delete(1.0, tk.END)
            self.detail_observaciones.insert(1.0, rol.observaciones or "Sin observaciones")
            self.detail_observaciones.config(state='disabled')

        except Exception as e:
            logger.error(f"Error mostrando detalles del rol: {str(e)}")
            self.clear_details()

    def clear_details(self):
        """Limpiar panel de detalles"""
        # Información general
        self.detail_empleado.config(text="-")
        self.detail_nombres.config(text="-")
        self.detail_periodo.config(text="-")
        self.detail_estado.config(text="-")
        self.detail_fecha_desde.config(text="-")
        self.detail_fecha_hasta.config(text="-")

        # Período
        self.detail_dias_trabajados.config(text="-")
        self.detail_tipo_nomina.config(text="-")
        self.detail_horas_normales.config(text="-")
        self.detail_sueldo_basico.config(text="-")

        # Ingresos
        self.detail_horas_25.config(text="-")
        self.detail_horas_50.config(text="-")
        self.detail_horas_100.config(text="-")
        self.detail_total_horas_extras.config(text="-")
        self.detail_comisiones.config(text="-")
        self.detail_bonos.config(text="-")
        self.detail_otros_ingresos.config(text="-")
        self.detail_total_ingresos.config(text="$0.00")

        # Descuentos
        self.detail_aporte_iess.config(text="-")
        self.detail_impuesto_renta.config(text="-")
        self.detail_prestamos.config(text="-")
        self.detail_anticipos.config(text="-")
        self.detail_otros_descuentos.config(text="-")
        self.detail_total_descuentos.config(text="$0.00")

        # Resumen
        self.resumen_ingresos.config(text="$0.00")
        self.resumen_descuentos.config(text="$0.00")
        self.resumen_neto.config(text="$0.00")

        # Información adicional
        self.detail_fecha_proceso.config(text="-")
        self.detail_fecha_pago.config(text="-")
        self.detail_procesado_por.config(text="-")

        # Observaciones
        self.detail_observaciones.config(state='normal')
        self.detail_observaciones.delete(1.0, tk.END)
        self.detail_observaciones.config(state='disabled')

        self.current_role = None

    def export_roles(self):
        """Exportar roles a Excel"""
        try:
            if not self.roles_tree.get_children():
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return

            # Preguntar archivo destino
            filename = filedialog.asksaveasfilename(
                title="Exportar Roles de Pago",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if not filename:
                return

            # Obtener datos actuales de la búsqueda
            data = []
            for item in self.roles_tree.get_children():
                values = self.roles_tree.item(item)['values']
                data.append({
                    'ID': values[0],
                    'Período': values[1],
                    'Empleado': values[2],
                    'Nombre Completo': values[3],
                    'Neto a Pagar': values[4],
                    'Estado': values[5]
                })

            # Crear DataFrame y exportar
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)

            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filename}")

        except Exception as e:
            logger.error(f"Error exportando roles: {str(e)}")
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")