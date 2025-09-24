#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Reportes Completo - Sistema SAI
Generación de reportes del sistema de nómina y RRHH
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
from decimal import Decimal
import sys
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import get_session
from database.models import Empleado, Departamento, Cargo

class ReportesCompleteModule(tk.Frame):
    """Módulo completo de reportes"""

    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables
        self.report_type_var = tk.StringVar(value="nomina")
        self.format_var = tk.StringVar(value="pdf")
        self.period_type_var = tk.StringVar(value="mensual")

        self.pack(fill="both", expand=True)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Header
        header_frame = tk.Frame(self, bg='#2c5282', height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="CENTRO DE REPORTES",
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
        self.create_nomina_reports_tab()
        self.create_rrhh_reports_tab()
        self.create_financiero_reports_tab()
        self.create_custom_reports_tab()

    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = tk.Frame(self, bg='#e2e8f0', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=2)
        toolbar.pack_propagate(False)

        # Botones principales
        buttons = [
            ("Generar Reporte", self.generate_report, '#4299e1'),
            ("Vista Previa", self.preview_report, '#48bb78'),
            ("Programar", self.schedule_report, '#ed8936'),
            ("Historial", self.view_history, '#9f7aea'),
            ("Configuración", self.report_settings, '#e53e3e')
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

    def create_nomina_reports_tab(self):
        """Crear pestaña de reportes de nómina"""
        nomina_frame = ttk.Frame(self.notebook)
        self.notebook.add(nomina_frame, text="Reportes de Nómina")

        # Panel de selección de reportes
        selection_frame = tk.LabelFrame(nomina_frame, text="Reportes Disponibles", font=('Arial', 11, 'bold'))
        selection_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_nomina_selection(selection_frame)

        # Panel de configuración
        config_frame = tk.LabelFrame(nomina_frame, text="Configuración del Reporte", font=('Arial', 11, 'bold'))
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_report_config(config_frame)

    def create_nomina_selection(self, parent):
        """Crear selección de reportes de nómina"""
        selection_grid = tk.Frame(parent)
        selection_grid.pack(padx=10, pady=10)

        # Lista de reportes de nómina
        nomina_reports = [
            ("Rol de Pagos", "rol_pagos", "Rol de pagos mensual con todos los empleados"),
            ("Resumen por Departamento", "resumen_dept", "Resumen de pagos agrupado por departamento"),
            ("Detalle de Descuentos", "detalle_descuentos", "Detalle de todos los descuentos aplicados"),
            ("Provisiones Sociales", "provisiones", "Cálculo de décimos y fondos de reserva"),
            ("Comparativo Mensual", "comparativo", "Comparación de nóminas entre períodos"),
            ("Empleados por Rango Salarial", "rango_salarial", "Empleados agrupados por rangos de sueldo")
        ]

        self.nomina_report_var = tk.StringVar(value="rol_pagos")

        for i, (nombre, valor, descripcion) in enumerate(nomina_reports):
            # Radio button
            tk.Radiobutton(
                selection_grid,
                text=nombre,
                variable=self.nomina_report_var,
                value=valor,
                font=('Arial', 10, 'bold'),
                command=self.update_report_description
            ).grid(row=i, column=0, sticky=tk.W, pady=2)

            # Descripción
            tk.Label(
                selection_grid,
                text=descripcion,
                font=('Arial', 9),
                fg='gray'
            ).grid(row=i, column=1, sticky=tk.W, padx=20, pady=2)

    def create_rrhh_reports_tab(self):
        """Crear pestaña de reportes de RRHH"""
        rrhh_frame = ttk.Frame(self.notebook)
        self.notebook.add(rrhh_frame, text="Reportes de RRHH")

        # Panel de selección
        selection_frame = tk.LabelFrame(rrhh_frame, text="Reportes de Recursos Humanos", font=('Arial', 11, 'bold'))
        selection_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_rrhh_selection(selection_frame)

        # Panel de vista previa
        preview_frame = tk.LabelFrame(rrhh_frame, text="Vista Previa", font=('Arial', 11, 'bold'))
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_preview_area(preview_frame)

    def create_rrhh_selection(self, parent):
        """Crear selección de reportes de RRHH"""
        selection_grid = tk.Frame(parent)
        selection_grid.pack(padx=10, pady=10)

        # Lista de reportes de RRHH
        rrhh_reports = [
            ("Listado de Empleados", "listado_empleados", "Listado completo de empleados activos"),
            ("Vacaciones Pendientes", "vacaciones_pendientes", "Empleados con vacaciones pendientes"),
            ("Cumpleaños del Mes", "cumpleanos", "Empleados que cumplen años en el período"),
            ("Ingresos y Salidas", "ingresos_salidas", "Movimientos de personal en el período"),
            ("Estructura Organizacional", "estructura_org", "Organigrama por departamentos"),
            ("Liquidaciones", "liquidaciones", "Liquidaciones procesadas en el período"),
            ("Préstamos Activos", "prestamos_activos", "Estado de préstamos de empleados"),
            ("Dotación Entregada", "dotacion", "Control de elementos de dotación")
        ]

        self.rrhh_report_var = tk.StringVar(value="listado_empleados")

        for i, (nombre, valor, descripcion) in enumerate(rrhh_reports):
            # Radio button
            tk.Radiobutton(
                selection_grid,
                text=nombre,
                variable=self.rrhh_report_var,
                value=valor,
                font=('Arial', 10, 'bold')
            ).grid(row=i//2, column=(i%2)*2, sticky=tk.W, pady=2, padx=5)

            # Descripción
            tk.Label(
                selection_grid,
                text=descripcion,
                font=('Arial', 8),
                fg='gray',
                wraplength=200
            ).grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=5, pady=2)

    def create_financiero_reports_tab(self):
        """Crear pestaña de reportes financieros"""
        financiero_frame = ttk.Frame(self.notebook)
        self.notebook.add(financiero_frame, text="Reportes Financieros")

        # Panel de reportes financieros
        financial_frame = tk.LabelFrame(financiero_frame, text="Reportes Financieros", font=('Arial', 11, 'bold'))
        financial_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_financial_selection(financial_frame)

        # Panel de gráficos
        charts_frame = tk.LabelFrame(financiero_frame, text="Gráficos y Estadísticas", font=('Arial', 11, 'bold'))
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_charts_area(charts_frame)

    def create_financial_selection(self, parent):
        """Crear selección de reportes financieros"""
        selection_grid = tk.Frame(parent)
        selection_grid.pack(padx=10, pady=10)

        # Lista de reportes financieros
        financial_reports = [
            ("Costos de Nómina", "costos_nomina", "Análisis de costos de nómina por período"),
            ("Presupuesto vs Real", "presupuesto_real", "Comparación presupuesto vs gastos reales"),
            ("Provisiones Contables", "provisiones_contables", "Cálculo de provisiones para estados financieros"),
            ("Costos por Centro", "costos_centro", "Distribución de costos por centro de costos"),
            ("IESS y Contribuciones", "iess_contribuciones", "Reporte de aportes al IESS"),
            ("Retenciones Fiscales", "retenciones", "Retenciones de impuesto a la renta"),
            ("Flujo de Efectivo", "flujo_efectivo", "Proyección de flujo de efectivo de nómina")
        ]

        self.financial_report_var = tk.StringVar(value="costos_nomina")

        for i, (nombre, valor, descripcion) in enumerate(financial_reports):
            tk.Radiobutton(
                selection_grid,
                text=nombre,
                variable=self.financial_report_var,
                value=valor,
                font=('Arial', 10, 'bold')
            ).grid(row=i, column=0, sticky=tk.W, pady=2)

            tk.Label(
                selection_grid,
                text=descripcion,
                font=('Arial', 9),
                fg='gray'
            ).grid(row=i, column=1, sticky=tk.W, padx=20, pady=2)

    def create_custom_reports_tab(self):
        """Crear pestaña de reportes personalizados"""
        custom_frame = ttk.Frame(self.notebook)
        self.notebook.add(custom_frame, text="Reportes Personalizados")

        # Panel de creación de reportes
        creator_frame = tk.LabelFrame(custom_frame, text="Crear Reporte Personalizado", font=('Arial', 11, 'bold'))
        creator_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_custom_creator(creator_frame)

        # Panel de reportes guardados
        saved_frame = tk.LabelFrame(custom_frame, text="Reportes Guardados", font=('Arial', 11, 'bold'))
        saved_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_saved_reports_list(saved_frame)

    def create_report_config(self, parent):
        """Crear configuración del reporte"""
        config_notebook = ttk.Notebook(parent)
        config_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña de parámetros
        params_frame = ttk.Frame(config_notebook)
        config_notebook.add(params_frame, text="Parámetros")

        self.create_parameters_section(params_frame)

        # Pestaña de filtros
        filters_frame = ttk.Frame(config_notebook)
        config_notebook.add(filters_frame, text="Filtros")

        self.create_filters_section(filters_frame)

        # Pestaña de formato
        format_frame = ttk.Frame(config_notebook)
        config_notebook.add(format_frame, text="Formato")

        self.create_format_section(format_frame)

    def create_parameters_section(self, parent):
        """Crear sección de parámetros"""
        params_grid = tk.Frame(parent)
        params_grid.pack(padx=10, pady=10)

        # Período
        tk.Label(params_grid, text="Tipo de Período:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        period_frame = tk.Frame(params_grid)
        period_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        period_types = [("Mensual", "mensual"), ("Trimestral", "trimestral"), ("Anual", "anual"), ("Personalizado", "personalizado")]
        for i, (text, value) in enumerate(period_types):
            tk.Radiobutton(
                period_frame,
                text=text,
                variable=self.period_type_var,
                value=value,
                font=('Arial', 9)
            ).pack(side=tk.LEFT, padx=5)

        # Fechas
        tk.Label(params_grid, text="Fecha Desde:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fecha_desde_entry = tk.Entry(params_grid, width=12)
        self.fecha_desde_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(params_grid, text="Fecha Hasta:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.fecha_hasta_entry = tk.Entry(params_grid, width=12)
        self.fecha_hasta_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Establecer fechas por defecto
        today = date.today()
        first_day = today.replace(day=1)
        self.fecha_desde_entry.insert(0, first_day.strftime('%d/%m/%Y'))
        self.fecha_hasta_entry.insert(0, today.strftime('%d/%m/%Y'))

        # Agrupación
        tk.Label(params_grid, text="Agrupar por:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.agrupar_combo = ttk.Combobox(
            params_grid,
            values=["Ninguno", "Departamento", "Cargo", "Tipo de Empleado"],
            state='readonly',
            width=15
        )
        self.agrupar_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.agrupar_combo.set("Ninguno")

        # Ordenamiento
        tk.Label(params_grid, text="Ordenar por:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.ordenar_combo = ttk.Combobox(
            params_grid,
            values=["Código Empleado", "Nombre", "Departamento", "Sueldo"],
            state='readonly',
            width=15
        )
        self.ordenar_combo.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.ordenar_combo.set("Código Empleado")

    def create_filters_section(self, parent):
        """Crear sección de filtros"""
        filters_grid = tk.Frame(parent)
        filters_grid.pack(padx=10, pady=10)

        # Filtro por departamento
        tk.Label(filters_grid, text="Departamento:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.filter_dept_combo = ttk.Combobox(filters_grid, state='readonly', width=20)
        self.filter_dept_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Filtro por cargo
        tk.Label(filters_grid, text="Cargo:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.filter_cargo_combo = ttk.Combobox(filters_grid, state='readonly', width=20)
        self.filter_cargo_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Filtro por empleados específicos
        tk.Label(filters_grid, text="Empleados:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        emp_filter_frame = tk.Frame(filters_grid)
        emp_filter_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.emp_filter_var = tk.StringVar(value="todos")
        tk.Radiobutton(
            emp_filter_frame,
            text="Todos",
            variable=self.emp_filter_var,
            value="todos",
            font=('Arial', 9)
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            emp_filter_frame,
            text="Seleccionar",
            variable=self.emp_filter_var,
            value="seleccionar",
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            emp_filter_frame,
            text="Seleccionar Empleados",
            command=self.select_employees,
            bg='#4299e1',
            fg='white',
            font=('Arial', 8),
            padx=10
        ).pack(side=tk.LEFT, padx=5)

        # Filtro por rango salarial
        tk.Label(filters_grid, text="Rango Salarial:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        salary_frame = tk.Frame(filters_grid)
        salary_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(salary_frame, text="Desde $", font=('Arial', 9)).pack(side=tk.LEFT)
        self.salary_from_entry = tk.Entry(salary_frame, width=8)
        self.salary_from_entry.pack(side=tk.LEFT, padx=2)

        tk.Label(salary_frame, text="Hasta $", font=('Arial', 9)).pack(side=tk.LEFT, padx=(10,0))
        self.salary_to_entry = tk.Entry(salary_frame, width=8)
        self.salary_to_entry.pack(side=tk.LEFT, padx=2)

    def create_format_section(self, parent):
        """Crear sección de formato"""
        format_grid = tk.Frame(parent)
        format_grid.pack(padx=10, pady=10)

        # Formato de salida
        tk.Label(format_grid, text="Formato de Salida:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        format_frame = tk.Frame(format_grid)
        format_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        formats = [("PDF", "pdf"), ("Excel", "excel"), ("CSV", "csv"), ("Pantalla", "screen")]
        for i, (text, value) in enumerate(formats):
            tk.Radiobutton(
                format_frame,
                text=text,
                variable=self.format_var,
                value=value,
                font=('Arial', 9)
            ).pack(side=tk.LEFT, padx=5)

        # Orientación
        tk.Label(format_grid, text="Orientación:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.orientation_var = tk.StringVar(value="vertical")
        orientation_frame = tk.Frame(format_grid)
        orientation_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Radiobutton(
            orientation_frame,
            text="Vertical",
            variable=self.orientation_var,
            value="vertical",
            font=('Arial', 9)
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            orientation_frame,
            text="Horizontal",
            variable=self.orientation_var,
            value="horizontal",
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=10)

        # Incluir totales
        self.include_totals_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            format_grid,
            text="Incluir Totales",
            variable=self.include_totals_var,
            font=('Arial', 10)
        ).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Incluir gráficos
        self.include_charts_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            format_grid,
            text="Incluir Gráficos",
            variable=self.include_charts_var,
            font=('Arial', 10)
        ).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # Logo de la empresa
        self.include_logo_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            format_grid,
            text="Incluir Logo de la Empresa",
            variable=self.include_logo_var,
            font=('Arial', 10)
        ).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

    def create_preview_area(self, parent):
        """Crear área de vista previa"""
        # Área de texto para vista previa
        self.preview_text = tk.Text(parent, height=15, font=('Courier', 9))

        # Scrollbar
        preview_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)

        # Pack
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar vista previa de ejemplo
        self.load_sample_preview()

    def create_charts_area(self, parent):
        """Crear área de gráficos"""
        charts_grid = tk.Frame(parent)
        charts_grid.pack(padx=10, pady=10)

        # Simulación de gráficos con labels
        chart_types = [
            ("Distribución Salarial", "Gráfico de barras mostrando distribución de sueldos"),
            ("Costos por Departamento", "Gráfico circular con costos por departamento"),
            ("Tendencia Mensual", "Gráfico de líneas con evolución de costos"),
            ("Comparativo Anual", "Gráfico comparativo año anterior vs actual")
        ]

        for i, (title, description) in enumerate(chart_types):
            chart_frame = tk.LabelFrame(charts_grid, text=title, font=('Arial', 10, 'bold'))
            chart_frame.grid(row=i//2, column=i%2, sticky='nsew', padx=5, pady=5)

            # Simulación de gráfico
            chart_area = tk.Frame(chart_frame, bg='lightgray', width=200, height=150)
            chart_area.pack(padx=10, pady=5)
            chart_area.pack_propagate(False)

            tk.Label(chart_area, text="[GRÁFICO]", bg='lightgray', font=('Arial', 12, 'bold')).pack(expand=True)
            tk.Label(chart_frame, text=description, font=('Arial', 8), wraplength=180).pack(pady=2)

    def create_custom_creator(self, parent):
        """Crear creador de reportes personalizados"""
        creator_grid = tk.Frame(parent)
        creator_grid.pack(padx=10, pady=10)

        # Nombre del reporte
        tk.Label(creator_grid, text="Nombre del Reporte:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.custom_name_entry = tk.Entry(creator_grid, width=30)
        self.custom_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Descripción
        tk.Label(creator_grid, text="Descripción:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.custom_desc_entry = tk.Entry(creator_grid, width=50)
        self.custom_desc_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # Campos disponibles
        tk.Label(creator_grid, text="Campos Disponibles:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)

        fields_frame = tk.Frame(creator_grid)
        fields_frame.grid(row=2, column=1, columnspan=2, sticky='ew', padx=5, pady=5)

        # Lista de campos
        self.available_fields = tk.Listbox(fields_frame, height=8, width=30)
        self.available_fields.pack(side=tk.LEFT, padx=5)

        # Botones de acción
        buttons_frame = tk.Frame(fields_frame)
        buttons_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(buttons_frame, text=">>", command=self.add_field, width=5).pack(pady=2)
        tk.Button(buttons_frame, text="<<", command=self.remove_field, width=5).pack(pady=2)

        # Campos seleccionados
        self.selected_fields = tk.Listbox(fields_frame, height=8, width=30)
        self.selected_fields.pack(side=tk.LEFT, padx=5)

        # Cargar campos disponibles
        self.load_available_fields()

        # Botones de guardado
        save_frame = tk.Frame(creator_grid)
        save_frame.grid(row=3, column=0, columnspan=3, pady=15)

        tk.Button(
            save_frame,
            text="Guardar Reporte",
            command=self.save_custom_report,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            save_frame,
            text="Limpiar",
            command=self.clear_custom_report,
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20
        ).pack(side=tk.LEFT, padx=5)

    def create_saved_reports_list(self, parent):
        """Crear lista de reportes guardados"""
        # Treeview para reportes guardados
        columns = ('nombre', 'descripcion', 'fecha_creacion', 'usado')
        self.saved_reports_tree = ttk.Treeview(parent, columns=columns, show='headings')

        # Configurar columnas
        headings = ['Nombre', 'Descripción', 'Fecha Creación', 'Último Uso']
        for col, heading in zip(columns, headings):
            self.saved_reports_tree.heading(col, text=heading)
            self.saved_reports_tree.column(col, width=150)

        # Scrollbar
        saved_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.saved_reports_tree.yview)
        self.saved_reports_tree.configure(yscrollcommand=saved_scroll.set)

        # Pack
        self.saved_reports_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        saved_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar reportes de ejemplo
        self.load_sample_saved_reports()

        # Bind events
        self.saved_reports_tree.bind('<Double-1>', self.load_saved_report)

    # Métodos de funcionalidad
    def load_data(self):
        """Cargar datos iniciales"""
        try:
            # Cargar departamentos
            departamentos = self.session.query(Departamento).filter_by(activo=True).all()
            dept_values = ["TODOS"] + [dept.nombre_codigo for dept in departamentos]
            self.filter_dept_combo['values'] = dept_values
            self.filter_dept_combo.set("TODOS")

            # Cargar cargos
            cargos = self.session.query(Cargo).filter_by(activo=True).all()
            cargo_values = ["TODOS"] + [cargo.nombre for cargo in cargos]
            self.filter_cargo_combo['values'] = cargo_values
            self.filter_cargo_combo.set("TODOS")

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos: {str(e)}")

    def load_available_fields(self):
        """Cargar campos disponibles"""
        fields = [
            "Código Empleado", "Nombres", "Apellidos", "Cédula",
            "Departamento", "Cargo", "Fecha Ingreso", "Sueldo Base",
            "Horas Extras", "Comisiones", "Bonificaciones",
            "Total Ingresos", "IESS Personal", "IESS Patronal",
            "Impuesto Renta", "Préstamos", "Total Descuentos",
            "Neto a Pagar", "Décimo Tercer Sueldo", "Décimo Cuarto Sueldo",
            "Fondos de Reserva", "Vacaciones"
        ]

        for field in fields:
            self.available_fields.insert(tk.END, field)

    def load_sample_preview(self):
        """Cargar vista previa de ejemplo"""
        sample_preview = """
SISTEMA SAI - REPORTE DE NÓMINA
INSEVIG CIA. LTDA.
Período: Enero 2024

CÓDIGO    EMPLEADO                DEPARTAMENTO       SUELDO    NETO
001001    PEREZ GONZALEZ JUAN     OPERACIONES        500.00    432.75
001002    GONZALEZ LOPEZ MARIA    SUPERVISION        800.00    692.40
001003    RODRIGUEZ SILVA CARLOS  OPERACIONES       1200.00   1038.60
001004    MARTINEZ TORRES ANA     RRHH               900.00    779.10
001005    VARGAS MORENO LUIS      ADMINISTRACION    2000.00   1732.00

TOTALES:                                            5400.00   4674.85

Generado: {fecha}
Usuario: Sistema SAI
        """.format(fecha=datetime.now().strftime('%d/%m/%Y %H:%M'))

        self.preview_text.insert(tk.END, sample_preview)

    def load_sample_saved_reports(self):
        """Cargar reportes guardados de ejemplo"""
        sample_reports = [
            ("Nómina Ejecutivos", "Reporte personalizado para ejecutivos", "15/01/2024", "20/01/2024"),
            ("Costos Operativos", "Costos por departamentos operativos", "10/01/2024", "18/01/2024"),
            ("Análisis Vacaciones", "Empleados con vacaciones vencidas", "05/01/2024", "15/01/2024"),
        ]

        for report in sample_reports:
            self.saved_reports_tree.insert('', 'end', values=report)

    # Métodos de eventos
    def update_report_description(self):
        """Actualizar descripción del reporte"""
        # Aquí se podría mostrar información adicional del reporte seleccionado
        pass

    def select_employees(self):
        """Seleccionar empleados específicos"""
        messagebox.showinfo("Información", "Selector de empleados en desarrollo")

    def add_field(self):
        """Agregar campo al reporte"""
        selection = self.available_fields.curselection()
        if selection:
            field = self.available_fields.get(selection[0])
            self.selected_fields.insert(tk.END, field)

    def remove_field(self):
        """Quitar campo del reporte"""
        selection = self.selected_fields.curselection()
        if selection:
            self.selected_fields.delete(selection[0])

    def save_custom_report(self):
        """Guardar reporte personalizado"""
        if not self.custom_name_entry.get():
            messagebox.showwarning("Advertencia", "Ingrese un nombre para el reporte")
            return

        messagebox.showinfo("Éxito", "Reporte personalizado guardado")
        self.clear_custom_report()

    def clear_custom_report(self):
        """Limpiar formulario de reporte personalizado"""
        self.custom_name_entry.delete(0, tk.END)
        self.custom_desc_entry.delete(0, tk.END)
        self.selected_fields.delete(0, tk.END)

    def load_saved_report(self, event):
        """Cargar reporte guardado"""
        selection = self.saved_reports_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Carga de reporte guardado en desarrollo")

    # Métodos principales
    def generate_report(self):
        """Generar reporte"""
        try:
            # Validar parámetros
            if not self.fecha_desde_entry.get() or not self.fecha_hasta_entry.get():
                messagebox.showwarning("Advertencia", "Ingrese las fechas del período")
                return

            # Mostrar progreso
            progress_window = tk.Toplevel(self)
            progress_window.title("Generando Reporte")
            progress_window.geometry("400x120")
            progress_window.transient(self)
            progress_window.grab_set()

            tk.Label(progress_window, text="Generando reporte...", font=('Arial', 12)).pack(pady=20)
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()

            # Simular generación
            self.after(3000, lambda: self.finish_report_generation(progress_window))

        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")

    def finish_report_generation(self, progress_window):
        """Finalizar generación de reporte"""
        progress_window.destroy()
        messagebox.showinfo("Éxito", "Reporte generado exitosamente")

    def preview_report(self):
        """Vista previa del reporte"""
        self.notebook.select(1)  # Ir a pestaña de RRHH que tiene vista previa
        messagebox.showinfo("Información", "Vista previa actualizada")

    def schedule_report(self):
        """Programar reporte"""
        messagebox.showinfo("Información", "Programación de reportes en desarrollo")

    def view_history(self):
        """Ver historial de reportes"""
        messagebox.showinfo("Información", "Historial de reportes en desarrollo")

    def report_settings(self):
        """Configuración de reportes"""
        messagebox.showinfo("Información", "Configuración de reportes en desarrollo")

    def darken_color(self, color):
        """Oscurecer color para efecto hover"""
        color_map = {
            '#4299e1': '#3182ce',
            '#48bb78': '#38a169',
            '#ed8936': '#dd6b20',
            '#9f7aea': '#805ad5',
            '#e53e3e': '#c53030'
        }
        return color_map.get(color, color)

    def __del__(self):
        """Destructor"""
        if hasattr(self, 'session'):
            self.session.close()