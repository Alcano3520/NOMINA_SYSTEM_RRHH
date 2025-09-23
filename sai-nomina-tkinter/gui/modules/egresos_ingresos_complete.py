#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Egresos-Ingresos Completo - Sistema SAI
Gestión de ingresos y egresos de empleados
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import sys
import os
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import get_session
from database.models import Empleado, Departamento, Cargo
from gui.components.carga_masiva import CargaMasivaComponent
from gui.components.progress_dialog import show_loading_dialog, ProgressDialog
from gui.components.visual_improvements import show_toast
from gui.components.database_export import show_database_export_dialog
import pandas as pd
import json

class EgresosIngresosCompleteModule(tk.Frame):
    """Módulo completo de egresos e ingresos"""

    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables
        self.selected_employee = None
        self.selected_record = None
        self.tipo_movimiento_var = tk.StringVar(value="ingreso")
        self.categoria_var = tk.StringVar(value="sueldo")

        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Header
        header_frame = tk.Frame(self, bg='#2c5282', height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="GESTIÓN DE EGRESOS E INGRESOS",
            font=('Arial', 16, 'bold'),
            bg='#2c5282',
            fg='white'
        ).pack(side=tk.LEFT, pady=15, padx=20)

        # Toolbar
        self.create_toolbar()

        # Main content
        main_frame = tk.Frame(self, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestañas
        self.create_registro_tab()
        self.create_consultas_tab()
        self.create_resumen_tab()
        self.create_reportes_tab()

    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = tk.Frame(self, bg='#e2e8f0', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=2)
        toolbar.pack_propagate(False)

        # Botones principales
        buttons = [
            ("Nuevo Registro", self.new_record, '#4299e1'),
            ("📊 Carga Masiva", self.carga_masiva_movimientos, '#38a169'),
            ("⚡ Procesamiento Masivo", self.procesamiento_masivo, '#805ad5'),
            ("Consultar", self.query_records, '#48bb78'),
            ("Resumen", self.show_summary, '#9f7aea'),
            ("📥 Descargar BD", self.descargar_bd, '#2d3748'),
            ("Reportes", self.generate_reports, '#e53e3e')
        ]

        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(
                toolbar,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 9, 'bold'),
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5, pady=8)

            # Efectos hover
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self.darken_color(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

    def create_registro_tab(self):
        """Crear pestaña de registro de movimientos"""
        registro_frame = ttk.Frame(self.notebook)
        self.notebook.add(registro_frame, text="Registro de Movimientos")

        # Panel superior - Formulario de registro
        form_frame = tk.LabelFrame(registro_frame, text="Nuevo Movimiento", font=('Arial', 11, 'bold'))
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_movement_form(form_frame)

        # Panel inferior - Lista de movimientos recientes
        recent_frame = tk.LabelFrame(registro_frame, text="Movimientos Recientes", font=('Arial', 11, 'bold'))
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_recent_movements_list(recent_frame)

    def create_movement_form(self, parent):
        """Crear formulario de movimiento"""
        form_grid = tk.Frame(parent)
        form_grid.pack(padx=10, pady=10)

        # Empleado
        tk.Label(form_grid, text="Empleado:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.emp_combo = ttk.Combobox(form_grid, state='readonly', width=35)
        self.emp_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.emp_combo.bind('<<ComboboxSelected>>', self.on_employee_selected)

        # Tipo de movimiento
        tk.Label(form_grid, text="Tipo:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        tipo_frame = tk.Frame(form_grid)
        tipo_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Radiobutton(
            tipo_frame,
            text="💰 Ingreso",
            variable=self.tipo_movimiento_var,
            value="ingreso",
            command=self.update_categories,
            font=('Arial', 9)
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            tipo_frame,
            text="💸 Egreso",
            variable=self.tipo_movimiento_var,
            value="egreso",
            command=self.update_categories,
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=20)

        # Categoría
        tk.Label(form_grid, text="Categoría:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.categoria_combo = ttk.Combobox(form_grid, state='readonly', width=25)
        self.categoria_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Monto
        tk.Label(form_grid, text="Monto:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.monto_entry = tk.Entry(form_grid, width=15, font=('Arial', 10))
        self.monto_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # Fecha
        tk.Label(form_grid, text="Fecha:", font=('Arial', 10, 'bold')).grid(row=3, column=2, sticky=tk.W, padx=10, pady=5)
        self.fecha_entry = tk.Entry(form_grid, width=12)
        self.fecha_entry.grid(row=3, column=3, sticky=tk.W, padx=5, pady=5)
        self.fecha_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Concepto
        tk.Label(form_grid, text="Concepto:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.concepto_entry = tk.Entry(form_grid, width=40, font=('Arial', 10))
        self.concepto_entry.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # Referencia/Comprobante
        tk.Label(form_grid, text="Referencia:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.referencia_entry = tk.Entry(form_grid, width=20)
        self.referencia_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)

        # Método de pago
        tk.Label(form_grid, text="Método Pago:", font=('Arial', 10, 'bold')).grid(row=5, column=2, sticky=tk.W, padx=10, pady=5)
        self.metodo_combo = ttk.Combobox(
            form_grid,
            values=["EFECTIVO", "TRANSFERENCIA", "CHEQUE", "TARJETA", "DESCUENTO"],
            state='readonly',
            width=15
        )
        self.metodo_combo.grid(row=5, column=3, sticky=tk.W, padx=5, pady=5)
        self.metodo_combo.set("TRANSFERENCIA")

        # Observaciones
        tk.Label(form_grid, text="Observaciones:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.obs_text = tk.Text(form_grid, width=50, height=3)
        self.obs_text.grid(row=6, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

        # Botones
        buttons_frame = tk.Frame(form_grid)
        buttons_frame.grid(row=7, column=0, columnspan=4, pady=20)

        tk.Button(
            buttons_frame,
            text="💾 Guardar Movimiento",
            command=self.save_movement,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="🧹 Limpiar",
            command=self.clear_form,
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Inicializar categorías
        self.update_categories()

    def create_recent_movements_list(self, parent):
        """Crear lista de movimientos recientes"""
        # Treeview para movimientos
        columns = ('fecha', 'empleado', 'tipo', 'categoria', 'concepto', 'monto', 'metodo', 'referencia')
        self.recent_tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)

        # Configurar columnas
        headings = ['Fecha', 'Empleado', 'Tipo', 'Categoría', 'Concepto', 'Monto', 'Método', 'Referencia']
        widths = [80, 150, 80, 100, 150, 80, 80, 100]

        for col, heading, width in zip(columns, headings, widths):
            self.recent_tree.heading(col, text=heading)
            self.recent_tree.column(col, width=width)

        # Scrollbars
        recent_scroll_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.recent_tree.yview)
        recent_scroll_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.recent_tree.xview)

        self.recent_tree.configure(yscrollcommand=recent_scroll_y.set, xscrollcommand=recent_scroll_x.set)

        # Pack
        self.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        recent_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        recent_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar datos de ejemplo
        self.load_sample_movements()

        # Bind events
        self.recent_tree.bind('<Double-1>', self.edit_movement)

    def create_consultas_tab(self):
        """Crear pestaña de consultas"""
        consultas_frame = ttk.Frame(self.notebook)
        self.notebook.add(consultas_frame, text="Consultas")

        # Panel de filtros
        filter_frame = tk.LabelFrame(consultas_frame, text="Filtros de Búsqueda", font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_grid = tk.Frame(filter_frame)
        filter_grid.pack(padx=10, pady=5)

        # Filtros
        tk.Label(filter_grid, text="Empleado:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_emp_combo = ttk.Combobox(filter_grid, state='readonly', width=25)
        self.filter_emp_combo.grid(row=0, column=1, padx=5)

        tk.Label(filter_grid, text="Tipo:", font=('Arial', 9)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.filter_tipo_combo = ttk.Combobox(
            filter_grid,
            values=["TODOS", "INGRESO", "EGRESO"],
            state='readonly',
            width=12
        )
        self.filter_tipo_combo.grid(row=0, column=3, padx=5)
        self.filter_tipo_combo.set("TODOS")

        tk.Label(filter_grid, text="Desde:", font=('Arial', 9)).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.filter_desde_entry = tk.Entry(filter_grid, width=12)
        self.filter_desde_entry.grid(row=1, column=1, padx=5)

        tk.Label(filter_grid, text="Hasta:", font=('Arial', 9)).grid(row=1, column=2, sticky=tk.W, padx=5)
        self.filter_hasta_entry = tk.Entry(filter_grid, width=12)
        self.filter_hasta_entry.grid(row=1, column=3, padx=5)

        tk.Button(
            filter_grid,
            text="🔍 Buscar",
            command=self.search_movements,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=15
        ).grid(row=1, column=4, padx=10)

        # Lista de resultados
        self.create_search_results(consultas_frame)

        # Panel de totales
        self.create_totals_panel(consultas_frame)

    def create_search_results(self, parent):
        """Crear lista de resultados de búsqueda"""
        results_frame = tk.LabelFrame(parent, text="Resultados de Búsqueda", font=('Arial', 10, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para resultados
        columns = ('fecha', 'empleado', 'tipo', 'categoria', 'concepto', 'monto', 'metodo', 'referencia', 'observaciones')
        self.search_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        # Configurar columnas
        headings = ['Fecha', 'Empleado', 'Tipo', 'Categoría', 'Concepto', 'Monto', 'Método', 'Referencia', 'Observaciones']
        for col, heading in zip(columns, headings):
            self.search_tree.heading(col, text=heading)
            self.search_tree.column(col, width=100)

        # Scrollbars
        search_scroll_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        search_scroll_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.search_tree.xview)

        self.search_tree.configure(yscrollcommand=search_scroll_y.set, xscrollcommand=search_scroll_x.set)

        # Pack
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        search_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        search_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.search_tree.bind('<Double-1>', self.view_movement_detail)

    def create_totals_panel(self, parent):
        """Crear panel de totales"""
        totals_frame = tk.LabelFrame(parent, text="Resumen de Consulta", font=('Arial', 10, 'bold'))
        totals_frame.pack(fill=tk.X, padx=10, pady=5)

        totals_grid = tk.Frame(totals_frame)
        totals_grid.pack(padx=10, pady=5)

        # Labels de totales
        self.totals_labels = {}
        total_fields = [
            ("Total Ingresos:", "$0.00"),
            ("Total Egresos:", "$0.00"),
            ("Balance:", "$0.00"),
            ("Registros:", "0")
        ]

        for i, (field, value) in enumerate(total_fields):
            tk.Label(totals_grid, text=field, font=('Arial', 10, 'bold')).grid(row=0, column=i*2, sticky=tk.W, padx=10)
            label = tk.Label(totals_grid, text=value, font=('Arial', 10), relief=tk.SUNKEN, width=15)
            label.grid(row=0, column=i*2+1, sticky=tk.W, padx=5)
            self.totals_labels[field] = label

    def create_resumen_tab(self):
        """Crear pestaña de resumen"""
        resumen_frame = ttk.Frame(self.notebook)
        self.notebook.add(resumen_frame, text="Resumen Financiero")

        # Panel de resumen mensual
        monthly_frame = tk.LabelFrame(resumen_frame, text="Resumen Mensual", font=('Arial', 11, 'bold'))
        monthly_frame.pack(fill=tk.X, padx=10, pady=5)

        # Controles de período
        period_frame = tk.Frame(monthly_frame)
        period_frame.pack(padx=10, pady=5)

        tk.Label(period_frame, text="Período:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.month_combo = ttk.Combobox(
            period_frame,
            values=[f"{i:02d}" for i in range(1, 13)],
            state='readonly',
            width=5
        )
        self.month_combo.pack(side=tk.LEFT, padx=5)
        self.month_combo.set(f"{date.today().month:02d}")

        self.year_combo = ttk.Combobox(
            period_frame,
            values=[str(year) for year in range(2020, 2030)],
            state='readonly',
            width=8
        )
        self.year_combo.pack(side=tk.LEFT, padx=5)
        self.year_combo.set(str(date.today().year))

        tk.Button(
            period_frame,
            text="📊 Generar Resumen",
            command=self.generate_monthly_summary,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=15
        ).pack(side=tk.LEFT, padx=10)

        # Panel de estadísticas
        self.create_statistics_panel(resumen_frame)

        # Panel de gráficos (simulado)
        self.create_charts_panel(resumen_frame)

    def create_statistics_panel(self, parent):
        """Crear panel de estadísticas"""
        stats_frame = tk.LabelFrame(parent, text="Estadísticas del Período", font=('Arial', 11, 'bold'))
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        stats_container = tk.Frame(stats_frame)
        stats_container.pack(padx=10, pady=10)

        # Crear tarjetas de estadísticas
        self.stats_cards = {}
        stats_data = [
            ("💰 Total Ingresos", "$0.00", "Ingresos del período"),
            ("💸 Total Egresos", "$0.00", "Egresos del período"),
            ("📊 Balance", "$0.00", "Diferencia neta"),
            ("📈 Promedio Diario", "$0.00", "Promedio por día")
        ]

        for i, (title, value, subtitle) in enumerate(stats_data):
            card_frame = tk.Frame(stats_container, relief=tk.RAISED, bd=1, bg='white')
            card_frame.grid(row=0, column=i, padx=10, pady=5, sticky='ew')

            tk.Label(card_frame, text=title, font=('Arial', 10, 'bold'), bg='white').pack(pady=5)
            value_label = tk.Label(card_frame, text=value, font=('Arial', 14, 'bold'), bg='white', fg='#4299e1')
            value_label.pack()
            tk.Label(card_frame, text=subtitle, font=('Arial', 8), bg='white', fg='gray').pack(pady=5)

            self.stats_cards[title] = value_label

        # Configurar peso de columnas
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1)

    def create_charts_panel(self, parent):
        """Crear panel de gráficos (simulado)"""
        charts_frame = tk.LabelFrame(parent, text="Análisis Visual", font=('Arial', 11, 'bold'))
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Placeholder para gráficos
        chart_placeholder = tk.Frame(charts_frame, bg='#f8f9fa', relief=tk.SUNKEN, bd=2)
        chart_placeholder.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            chart_placeholder,
            text="📊 Área para Gráficos\n\nAquí se mostrarían gráficos de:\n• Tendencia de ingresos vs egresos\n• Distribución por categorías\n• Análisis por empleado\n• Proyecciones",
            font=('Arial', 12),
            bg='#f8f9fa',
            fg='gray'
        ).pack(expand=True)

    def create_reportes_tab(self):
        """Crear pestaña de reportes"""
        reportes_frame = ttk.Frame(self.notebook)
        self.notebook.add(reportes_frame, text="Reportes")

        # Opciones de reporte
        options_frame = tk.LabelFrame(reportes_frame, text="Opciones de Reporte", font=('Arial', 10, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        options_grid = tk.Frame(options_frame)
        options_grid.pack(padx=10, pady=10)

        # Tipo de reporte
        tk.Label(options_grid, text="Tipo de Reporte:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)

        self.report_type_var = tk.StringVar(value="resumen")
        report_types = [
            ("Resumen General", "resumen"),
            ("Por Empleado", "empleado"),
            ("Por Categoría", "categoria"),
            ("Flujo de Caja", "flujo"),
            ("Análisis Comparativo", "comparativo")
        ]

        for i, (text, value) in enumerate(report_types):
            tk.Radiobutton(
                options_grid,
                text=text,
                variable=self.report_type_var,
                value=value,
                font=('Arial', 9)
            ).grid(row=i+1, column=0, sticky=tk.W)

        # Filtros de reporte
        filter_frame = tk.Frame(options_grid)
        filter_frame.grid(row=0, column=1, rowspan=6, sticky=tk.N, padx=30)

        tk.Label(filter_frame, text="Filtros:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        tk.Label(filter_frame, text="Período:", font=('Arial', 9)).pack(anchor=tk.W, pady=(10,0))
        period_frame = tk.Frame(filter_frame)
        period_frame.pack(anchor=tk.W, pady=2)

        tk.Label(period_frame, text="Desde:", font=('Arial', 8)).pack(side=tk.LEFT)
        self.rep_fecha_desde = tk.Entry(period_frame, width=10)
        self.rep_fecha_desde.pack(side=tk.LEFT, padx=2)

        tk.Label(period_frame, text="Hasta:", font=('Arial', 8)).pack(side=tk.LEFT, padx=(10,0))
        self.rep_fecha_hasta = tk.Entry(period_frame, width=10)
        self.rep_fecha_hasta.pack(side=tk.LEFT, padx=2)

        tk.Label(filter_frame, text="Empleado:", font=('Arial', 9)).pack(anchor=tk.W, pady=(10,0))
        self.rep_emp_combo = ttk.Combobox(filter_frame, state='readonly', width=25)
        self.rep_emp_combo.pack(anchor=tk.W, pady=2)

        # Botones de reporte
        buttons_frame = tk.Frame(reportes_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        report_buttons = [
            ("👁️ Vista Previa", self.preview_report, '#4299e1'),
            ("📄 Generar PDF", self.generate_pdf_report, '#e53e3e'),
            ("📊 Exportar Excel", self.export_excel, '#38a169')
        ]

        for text, command, color in report_buttons:
            tk.Button(
                buttons_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 10, 'bold'),
                padx=20,
                pady=8
            ).pack(side=tk.LEFT, padx=5)

    # Métodos de funcionalidad
    def load_employees(self):
        """Cargar empleados en combos"""
        try:
            empleados = self.session.query(Empleado).filter_by(activo=True).all()
            emp_values = [f"{emp.empleado} - {emp.nombres} {emp.apellidos}" for emp in empleados]

            # Actualizar combos
            self.emp_combo['values'] = emp_values
            self.filter_emp_combo['values'] = ["TODOS"] + emp_values
            self.rep_emp_combo['values'] = ["TODOS"] + emp_values

            # Establecer valores por defecto
            self.filter_emp_combo.set("TODOS")
            self.rep_emp_combo.set("TODOS")

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando empleados: {str(e)}")

    def update_categories(self):
        """Actualizar categorías según tipo de movimiento"""
        tipo = self.tipo_movimiento_var.get()

        if tipo == "ingreso":
            categories = [
                "SUELDO", "HORAS_EXTRAS", "COMISIONES", "BONIFICACIONES",
                "SUBSIDIOS", "LIQUIDACION", "PRESTAMOS", "OTROS_INGRESOS"
            ]
        else:  # egreso
            categories = [
                "DESCUENTOS_LEY", "PRESTAMOS", "ANTICIPOS", "MULTAS",
                "UNIFORME", "ALIMENTACION", "TRANSPORTE", "OTROS_EGRESOS"
            ]

        self.categoria_combo['values'] = categories
        if categories:
            self.categoria_combo.set(categories[0])

    def on_employee_selected(self, event):
        """Manejar selección de empleado"""
        selected = self.emp_combo.get()
        if selected:
            codigo = selected.split(' - ')[0]
            # Aquí se podría cargar información adicional del empleado

    def load_sample_movements(self):
        """Cargar movimientos de ejemplo"""
        sample_movements = [
            ("15/01/2024", "001001 - Juan Perez", "INGRESO", "SUELDO", "Sueldo enero 2024", "$1,200.00", "TRANSFERENCIA", "SUE-001"),
            ("15/01/2024", "001001 - Juan Perez", "EGRESO", "DESCUENTOS_LEY", "IESS Personal", "$120.00", "DESCUENTO", "IESS-001"),
            ("20/01/2024", "001002 - Maria Gonzalez", "INGRESO", "HORAS_EXTRAS", "Horas extras", "$150.00", "TRANSFERENCIA", "HE-001"),
            ("25/01/2024", "001003 - Carlos Rodriguez", "EGRESO", "PRESTAMOS", "Cuota préstamo", "$167.50", "DESCUENTO", "PREST-001"),
        ]

        for movement in sample_movements:
            self.recent_tree.insert('', 'end', values=movement)

    # Métodos de eventos
    def new_record(self):
        """Nuevo registro"""
        self.notebook.select(0)  # Ir a pestaña de registro

    def query_records(self):
        """Consultar registros"""
        self.notebook.select(1)  # Ir a pestaña de consultas

    def show_summary(self):
        """Mostrar resumen"""
        self.notebook.select(2)  # Ir a pestaña de resumen

    def generate_reports(self):
        """Generar reportes"""
        self.notebook.select(3)  # Ir a pestaña de reportes

    def save_movement(self):
        """Guardar movimiento"""
        if not self.emp_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un empleado")
            return

        if not self.monto_entry.get():
            messagebox.showwarning("Advertencia", "Ingrese el monto")
            return

        if not self.concepto_entry.get():
            messagebox.showwarning("Advertencia", "Ingrese el concepto")
            return

        # Agregar a la lista de movimientos recientes
        nuevo_movimiento = (
            self.fecha_entry.get(),
            self.emp_combo.get(),
            self.tipo_movimiento_var.get().upper(),
            self.categoria_combo.get(),
            self.concepto_entry.get(),
            f"${float(self.monto_entry.get()):.2f}",
            self.metodo_combo.get(),
            self.referencia_entry.get()
        )

        self.recent_tree.insert('', 0, values=nuevo_movimiento)

        messagebox.showinfo("Éxito", "Movimiento guardado exitosamente")
        self.clear_form()

    def clear_form(self):
        """Limpiar formulario"""
        self.emp_combo.set("")
        self.monto_entry.delete(0, tk.END)
        self.concepto_entry.delete(0, tk.END)
        self.referencia_entry.delete(0, tk.END)
        self.obs_text.delete(1.0, tk.END)
        self.fecha_entry.delete(0, tk.END)
        self.fecha_entry.insert(0, date.today().strftime('%d/%m/%Y'))

    def search_movements(self):
        """Buscar movimientos"""
        # Limpiar resultados anteriores
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        # Simular búsqueda copiando datos de movimientos recientes
        total_ingresos = 0
        total_egresos = 0
        count = 0

        for item in self.recent_tree.get_children():
            values = self.recent_tree.item(item)['values']
            self.search_tree.insert('', 'end', values=values + ("Observación ejemplo",))

            # Calcular totales
            monto_str = values[5].replace('$', '').replace(',', '')
            monto = float(monto_str)

            if values[2] == "INGRESO":
                total_ingresos += monto
            else:
                total_egresos += monto
            count += 1

        # Actualizar totales
        balance = total_ingresos - total_egresos
        self.totals_labels["Total Ingresos:"].config(text=f"${total_ingresos:.2f}")
        self.totals_labels["Total Egresos:"].config(text=f"${total_egresos:.2f}")
        self.totals_labels["Balance:"].config(text=f"${balance:.2f}")
        self.totals_labels["Registros:"].config(text=str(count))

        show_toast(self, f"✅ Búsqueda completada: {count} registros encontrados", "success")

    def generate_monthly_summary(self):
        """Generar resumen mensual"""
        mes = self.month_combo.get()
        año = self.year_combo.get()

        # Simular cálculos
        total_ingresos = 15000.00
        total_egresos = 3500.00
        balance = total_ingresos - total_egresos
        promedio_diario = balance / 30

        # Actualizar tarjetas de estadísticas
        self.stats_cards["💰 Total Ingresos"].config(text=f"${total_ingresos:.2f}")
        self.stats_cards["💸 Total Egresos"].config(text=f"${total_egresos:.2f}")
        self.stats_cards["📊 Balance"].config(text=f"${balance:.2f}")
        self.stats_cards["📈 Promedio Diario"].config(text=f"${promedio_diario:.2f}")

        show_toast(self, f"✅ Resumen generado para {mes}/{año}", "success")

    def edit_movement(self, event):
        """Editar movimiento"""
        selection = self.recent_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Función de edición en desarrollo")

    def view_movement_detail(self, event):
        """Ver detalle de movimiento"""
        selection = self.search_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Vista de detalle en desarrollo")

    def preview_report(self):
        """Vista previa del reporte"""
        messagebox.showinfo("Información", "Vista previa en desarrollo")

    def generate_pdf_report(self):
        """Generar reporte PDF"""
        messagebox.showinfo("Información", "Generación de PDF en desarrollo")

    def export_excel(self):
        """Exportar a Excel"""
        messagebox.showinfo("Información", "Exportación a Excel en desarrollo")

    def carga_masiva_movimientos(self):
        """Carga masiva de movimientos"""
        try:
            columns_mapping = {
                'codigo_empleado': 'empleado',
                'tipo_movimiento': 'tipo',
                'categoria': 'categoria',
                'concepto': 'concepto',
                'monto': 'monto',
                'fecha': 'fecha',
                'metodo_pago': 'metodo',
                'referencia': 'referencia',
                'observaciones': 'observaciones'
            }

            carga_masiva = CargaMasivaComponent(
                parent=self,
                session=self.session,
                entity_type="egresos_ingresos",
                columns_mapping=columns_mapping
            )

            show_toast(self, "Carga masiva de movimientos iniciada", "info")

        except Exception as e:
            messagebox.showerror("Error", f"Error en carga masiva: {str(e)}")

    def procesamiento_masivo(self):
        """Procesamiento masivo de movimientos"""
        try:
            # Crear ventana de procesamiento masivo
            proceso_window = tk.Toplevel(self)
            proceso_window.title("Procesamiento Masivo de Egresos-Ingresos")
            proceso_window.geometry("900x700")
            proceso_window.transient(self)
            proceso_window.grab_set()

            # Header
            header_frame = tk.Frame(proceso_window, bg='#2c5282', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)

            tk.Label(
                header_frame,
                text="⚡ PROCESAMIENTO MASIVO DE EGRESOS-INGRESOS",
                font=('Arial', 16, 'bold'),
                bg='#2c5282',
                fg='white'
            ).pack(pady=15)

            # Notebook para opciones
            notebook = ttk.Notebook(proceso_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Pestaña 1: Procesamiento de nómina
            self.create_nomina_processing_tab(notebook)

            # Pestaña 2: Ajustes masivos
            self.create_ajustes_masivos_tab(notebook)

            # Pestaña 3: Consolidación contable
            self.create_consolidacion_tab(notebook)

        except Exception as e:
            messagebox.showerror("Error", f"Error en procesamiento masivo: {str(e)}")

    def create_nomina_processing_tab(self, parent):
        """Crear pestaña de procesamiento de nómina"""
        nomina_frame = ttk.Frame(parent)
        parent.add(nomina_frame, text="Procesamiento de Nómina")

        # Opciones de procesamiento
        options_frame = tk.LabelFrame(nomina_frame, text="Opciones de Procesamiento", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Período de nómina
        tk.Label(options_frame, text="Período de Nómina:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.nomina_periodo_combo = ttk.Combobox(
            options_frame,
            values=[f"{i:02d}/{date.today().year}" for i in range(1, 13)],
            state='readonly',
            width=10
        )
        self.nomina_periodo_combo.grid(row=0, column=1, padx=5, pady=5)
        self.nomina_periodo_combo.set(f"{date.today().month:02d}/{date.today().year}")

        # Tipo de procesamiento
        tk.Label(options_frame, text="Tipo:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.proc_tipo_combo = ttk.Combobox(
            options_frame,
            values=["SUELDOS", "HORAS_EXTRAS", "COMISIONES", "DESCUENTOS", "TODOS"],
            state='readonly',
            width=15
        )
        self.proc_tipo_combo.grid(row=0, column=3, padx=5, pady=5)
        self.proc_tipo_combo.set("TODOS")

        # Botón procesar
        tk.Button(
            options_frame,
            text="⚡ Procesar Nómina Masivamente",
            command=self.procesar_nomina_masivo,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=1, column=0, columnspan=4, pady=15)

        # Resultados
        results_frame = tk.LabelFrame(nomina_frame, text="Resultados del Procesamiento", font=('Arial', 11, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.nomina_results_text = tk.Text(results_frame, font=('Courier', 9))
        nomina_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.nomina_results_text.yview)
        self.nomina_results_text.configure(yscrollcommand=nomina_scroll.set)

        self.nomina_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        nomina_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_ajustes_masivos_tab(self, parent):
        """Crear pestaña de ajustes masivos"""
        ajustes_frame = ttk.Frame(parent)
        parent.add(ajustes_frame, text="Ajustes Masivos")

        # Opciones de ajuste
        options_frame = tk.LabelFrame(ajustes_frame, text="Parámetros de Ajuste", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Tipo de ajuste
        tk.Label(options_frame, text="Tipo de Ajuste:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.ajuste_tipo_combo = ttk.Combobox(
            options_frame,
            values=["INCREMENTO_SALARIAL", "AJUSTE_BENEFICIOS", "CORRECCION_DESCUENTOS", "RETROACTIVOS"],
            state='readonly',
            width=20
        )
        self.ajuste_tipo_combo.grid(row=0, column=1, padx=5, pady=5)
        self.ajuste_tipo_combo.set("INCREMENTO_SALARIAL")

        # Porcentaje de ajuste
        tk.Label(options_frame, text="Porcentaje (%):", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.ajuste_porcentaje_entry = tk.Entry(options_frame, width=10)
        self.ajuste_porcentaje_entry.grid(row=0, column=3, padx=5, pady=5)
        self.ajuste_porcentaje_entry.insert(0, "3.5")

        # Fecha efectiva
        tk.Label(options_frame, text="Fecha Efectiva:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.ajuste_fecha_entry = tk.Entry(options_frame, width=12)
        self.ajuste_fecha_entry.grid(row=1, column=1, padx=5, pady=5)
        self.ajuste_fecha_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Botón aplicar
        tk.Button(
            options_frame,
            text="🔧 Aplicar Ajustes Masivos",
            command=self.aplicar_ajustes_masivo,
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=2, column=0, columnspan=4, pady=15)

        # Resultados de ajustes
        results_frame = tk.LabelFrame(ajustes_frame, text="Resultados de Ajustes", font=('Arial', 11, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('empleado', 'valor_anterior', 'ajuste', 'valor_nuevo', 'diferencia')
        self.ajustes_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        headings = ['Empleado', 'Valor Anterior', 'Ajuste', 'Valor Nuevo', 'Diferencia']
        for col, heading in zip(columns, headings):
            self.ajustes_tree.heading(col, text=heading)
            self.ajustes_tree.column(col, width=120)

        # Scrollbar
        ajustes_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.ajustes_tree.yview)
        self.ajustes_tree.configure(yscrollcommand=ajustes_scroll.set)

        self.ajustes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ajustes_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_consolidacion_tab(self, parent):
        """Crear pestaña de consolidación contable"""
        consolid_frame = ttk.Frame(parent)
        parent.add(consolid_frame, text="Consolidación Contable")

        # Opciones de consolidación
        options_frame = tk.LabelFrame(consolid_frame, text="Parámetros de Consolidación", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Período de consolidación
        tk.Label(options_frame, text="Período:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.consolid_periodo_combo = ttk.Combobox(
            options_frame,
            values=["MENSUAL", "TRIMESTRAL", "ANUAL"],
            state='readonly',
            width=12
        )
        self.consolid_periodo_combo.grid(row=0, column=1, padx=5, pady=5)
        self.consolid_periodo_combo.set("MENSUAL")

        # Cuenta contable
        tk.Label(options_frame, text="Cuenta Contable:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.cuenta_contable_entry = tk.Entry(options_frame, width=15)
        self.cuenta_contable_entry.grid(row=0, column=3, padx=5, pady=5)
        self.cuenta_contable_entry.insert(0, "5101")

        # Botón consolidar
        tk.Button(
            options_frame,
            text="📊 Generar Consolidación",
            command=self.generar_consolidacion,
            bg='#9f7aea',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=1, column=0, columnspan=4, pady=15)

        # Resultados de consolidación
        results_frame = tk.LabelFrame(consolid_frame, text="Resumen Contable", font=('Arial', 11, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.consolidacion_text = tk.Text(results_frame, font=('Courier', 9))
        consolid_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.consolidacion_text.yview)
        self.consolidacion_text.configure(yscrollcommand=consolid_scroll.set)

        self.consolidacion_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        consolid_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def procesar_nomina_masivo(self):
        """Procesar nómina masivamente"""
        try:
            periodo = self.nomina_periodo_combo.get()
            tipo = self.proc_tipo_combo.get()

            dialog = show_loading_dialog(self, "Procesando", "Calculando nómina masiva...")

            # Simular procesamiento
            resultados = []
            resultados.append("=== PROCESAMIENTO MASIVO DE NÓMINA ===")
            resultados.append(f"Período: {periodo}")
            resultados.append(f"Tipo: {tipo}")
            resultados.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            resultados.append("")

            empleados = self.session.query(Empleado).filter_by(activo=True).all()
            total_ingresos = 0
            total_egresos = 0

            for emp in empleados:
                sueldo = float(emp.sueldo or 0)

                # Ingresos
                if tipo in ["SUELDOS", "TODOS"]:
                    resultados.append(f"[INGRESO] {emp.empleado} - {emp.nombres}: Sueldo ${sueldo:.2f}")
                    total_ingresos += sueldo

                # Egresos (descuentos)
                if tipo in ["DESCUENTOS", "TODOS"]:
                    iess = sueldo * 0.0945
                    impuesto = sueldo * 0.05 if sueldo > 1200 else 0
                    resultados.append(f"[EGRESO] {emp.empleado} - {emp.nombres}: IESS ${iess:.2f}, Imp.Renta ${impuesto:.2f}")
                    total_egresos += (iess + impuesto)

            resultados.append("")
            resultados.append("=== RESUMEN ===")
            resultados.append(f"Total Ingresos Generados: ${total_ingresos:.2f}")
            resultados.append(f"Total Egresos Generados: ${total_egresos:.2f}")
            resultados.append(f"Empleados Procesados: {len(empleados)}")

            # Mostrar resultados
            self.nomina_results_text.delete(1.0, tk.END)
            self.nomina_results_text.insert(tk.END, "\n".join(resultados))

            dialog.close()
            show_toast(self, f"✅ Nómina procesada: {len(empleados)} empleados", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error procesando nómina: {str(e)}")

    def aplicar_ajustes_masivo(self):
        """Aplicar ajustes masivos"""
        try:
            tipo_ajuste = self.ajuste_tipo_combo.get()
            porcentaje = float(self.ajuste_porcentaje_entry.get())
            fecha_efectiva = self.ajuste_fecha_entry.get()

            if not messagebox.askyesno("Confirmar", f"¿Aplicar {tipo_ajuste} del {porcentaje}% a todos los empleados?"):
                return

            dialog = show_loading_dialog(self, "Aplicando", "Procesando ajustes masivos...")

            # Limpiar resultados anteriores
            for item in self.ajustes_tree.get_children():
                self.ajustes_tree.delete(item)

            empleados = self.session.query(Empleado).filter_by(activo=True).all()
            total_diferencia = 0

            for emp in empleados:
                valor_anterior = float(emp.sueldo or 0)
                ajuste = valor_anterior * (porcentaje / 100)
                valor_nuevo = valor_anterior + ajuste
                diferencia = ajuste
                total_diferencia += diferencia

                self.ajustes_tree.insert('', 'end', values=(
                    f"{emp.empleado} - {emp.nombres}",
                    f"${valor_anterior:.2f}",
                    f"{porcentaje}%",
                    f"${valor_nuevo:.2f}",
                    f"${diferencia:.2f}"
                ))

            dialog.close()
            show_toast(self, f"✅ Ajustes aplicados - Incremento total: ${total_diferencia:.2f}", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error aplicando ajustes: {str(e)}")

    def generar_consolidacion(self):
        """Generar consolidación contable"""
        try:
            periodo = self.consolid_periodo_combo.get()
            cuenta = self.cuenta_contable_entry.get()

            dialog = show_loading_dialog(self, "Consolidando", "Generando consolidación contable...")

            # Simular consolidación
            resultados = []
            resultados.append("=== CONSOLIDACIÓN CONTABLE ===")
            resultados.append(f"Período: {periodo}")
            resultados.append(f"Cuenta: {cuenta}")
            resultados.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            resultados.append("")

            resultados.append("RESUMEN POR CATEGORÍAS:")
            resultados.append("-" * 50)

            categorias = {
                "SUELDOS Y SALARIOS": 45000.00,
                "BENEFICIOS SOCIALES": 12000.00,
                "APORTES PATRONALES": 8500.00,
                "DESCUENTOS LEY": -5500.00,
                "OTROS INGRESOS": 2000.00,
                "OTROS EGRESOS": -1500.00
            }

            total_consolidado = 0
            for categoria, monto in categorias.items():
                resultados.append(f"{categoria:<25}: ${monto:>10,.2f}")
                total_consolidado += monto

            resultados.append("-" * 50)
            resultados.append(f"{'TOTAL CONSOLIDADO':<25}: ${total_consolidado:>10,.2f}")
            resultados.append("")

            resultados.append("ASIENTOS CONTABLES SUGERIDOS:")
            resultados.append(f"{cuenta}001 SUELDOS Y SALARIOS     DEBE: ${categorias['SUELDOS Y SALARIOS']:,.2f}")
            resultados.append(f"2101001 CUENTAS POR PAGAR      HABER: ${categorias['SUELDOS Y SALARIOS']:,.2f}")

            # Mostrar resultados
            self.consolidacion_text.delete(1.0, tk.END)
            self.consolidacion_text.insert(tk.END, "\n".join(resultados))

            dialog.close()
            show_toast(self, f"✅ Consolidación generada - Total: ${total_consolidado:,.2f}", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error generando consolidación: {str(e)}")

    def descargar_bd(self):
        """Descargar base de datos completa del sistema"""
        show_database_export_dialog(self)

    def darken_color(self, color):
        """Oscurecer color para efecto hover"""
        color_map = {
            '#4299e1': '#3182ce',
            '#48bb78': '#38a169',
            '#ed8936': '#dd6b20',
            '#9f7aea': '#805ad5',
            '#e53e3e': '#c53030',
            '#38a169': '#2f855a',
            '#805ad5': '#6b46c1',
            '#2d3748': '#1a202c'
        }
        return color_map.get(color, color)

    def __del__(self):
        """Destructor"""
        if hasattr(self, 'session') and hasattr(self.session, 'close'):
            self.session.close()