#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Liquidaciones Completo - Sistema SAI
Gestión de liquidaciones de empleados según normativa ecuatoriana
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import sys
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import get_session
from database.models import Empleado, Departamento, Cargo

class LiquidacionesCompleteModule(tk.Frame):
    """Módulo completo de liquidaciones"""

    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables
        self.selected_employee = None
        self.motivo_liquidacion_var = tk.StringVar(value="renuncia")
        self.tipo_liquidacion_var = tk.StringVar(value="total")

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
            text="GESTIÓN DE LIQUIDACIONES",
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
        self.create_calculo_tab()
        self.create_historial_tab()
        self.create_documentos_tab()
        self.create_reportes_tab()

    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = tk.Frame(self, bg='#e2e8f0', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=2)
        toolbar.pack_propagate(False)

        # Botones principales
        buttons = [
            ("Nueva Liquidación", self.new_liquidation, '#4299e1'),
            ("Calcular", self.calculate_liquidation, '#48bb78'),
            ("Procesar", self.process_liquidation, '#ed8936'),
            ("Documentos", self.generate_documents, '#9f7aea'),
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

    def create_calculo_tab(self):
        """Crear pestaña de cálculo de liquidación"""
        calculo_frame = ttk.Frame(self.notebook)
        self.notebook.add(calculo_frame, text="Cálculo de Liquidación")

        # Panel superior - Datos del empleado
        empleado_frame = tk.LabelFrame(calculo_frame, text="Datos del Empleado", font=('Arial', 11, 'bold'))
        empleado_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_employee_section(empleado_frame)

        # Panel medio - Configuración de liquidación
        config_frame = tk.LabelFrame(calculo_frame, text="Configuración de Liquidación", font=('Arial', 11, 'bold'))
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_config_section(config_frame)

        # Panel inferior - Cálculos
        calculos_frame = tk.LabelFrame(calculo_frame, text="Cálculos de Liquidación", font=('Arial', 11, 'bold'))
        calculos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_calculations_section(calculos_frame)

    def create_employee_section(self, parent):
        """Crear sección de datos del empleado"""
        emp_grid = tk.Frame(parent)
        emp_grid.pack(padx=10, pady=10)

        # Selección de empleado
        tk.Label(emp_grid, text="Empleado:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.emp_combo = ttk.Combobox(emp_grid, state='readonly', width=40)
        self.emp_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.emp_combo.bind('<<ComboboxSelected>>', self.on_employee_selected)

        # Información del empleado (dividida en dos columnas)
        self.emp_info_labels = {}
        info_fields = [
            ("Código:", ""), ("Cédula:", ""),
            ("Cargo:", ""), ("Departamento:", ""),
            ("Fecha Ingreso:", ""), ("Tiempo Trabajado:", ""),
            ("Sueldo Actual:", ""), ("Último Aumento:", ""),
            ("Estado:", ""), ("Tipo Contrato:", "")
        ]

        for i, (field, value) in enumerate(info_fields):
            row = (i // 2) + 1
            col = (i % 2) * 3

            tk.Label(emp_grid, text=field, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=2
            )
            label = tk.Label(emp_grid, text=value, font=('Arial', 9), relief=tk.SUNKEN, width=20)
            label.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
            self.emp_info_labels[field] = label

    def create_config_section(self, parent):
        """Crear sección de configuración"""
        config_grid = tk.Frame(parent)
        config_grid.pack(padx=10, pady=10)

        # Motivo de liquidación
        tk.Label(config_grid, text="Motivo:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        motivo_frame = tk.Frame(config_grid)
        motivo_frame.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        motivos = [
            ("Renuncia Voluntaria", "renuncia"),
            ("Despido Intempestivo", "despido"),
            ("Fin de Contrato", "fin_contrato"),
            ("Jubilación", "jubilacion"),
            ("Muerte", "muerte")
        ]

        for i, (text, value) in enumerate(motivos):
            tk.Radiobutton(
                motivo_frame,
                text=text,
                variable=self.motivo_liquidacion_var,
                value=value,
                command=self.update_liquidation_config,
                font=('Arial', 8)
            ).grid(row=0, column=i, sticky=tk.W, padx=5)

        # Tipo de liquidación
        tk.Label(config_grid, text="Tipo:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        tipo_frame = tk.Frame(config_grid)
        tipo_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Radiobutton(
            tipo_frame,
            text="Liquidación Total",
            variable=self.tipo_liquidacion_var,
            value="total",
            font=('Arial', 9)
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            tipo_frame,
            text="Liquidación Parcial",
            variable=self.tipo_liquidacion_var,
            value="parcial",
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=10)

        # Fechas
        tk.Label(config_grid, text="Fecha Salida:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.fecha_salida_entry = tk.Entry(config_grid, width=12)
        self.fecha_salida_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.fecha_salida_entry.insert(0, date.today().strftime('%d/%m/%Y'))
        self.fecha_salida_entry.bind('<KeyRelease>', self.calculate_time_worked)

        # Días trabajados en el mes actual
        tk.Label(config_grid, text="Días Trabajados (mes actual):", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.dias_trabajados_entry = tk.Entry(config_grid, width=5)
        self.dias_trabajados_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # Observaciones
        tk.Label(config_grid, text="Observaciones:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.obs_text = tk.Text(config_grid, width=60, height=3)
        self.obs_text.grid(row=4, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

    def create_calculations_section(self, parent):
        """Crear sección de cálculos"""
        # Crear notebook para diferentes tipos de cálculos
        calc_notebook = ttk.Notebook(parent)
        calc_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña de beneficios sociales
        self.create_beneficios_tab(calc_notebook)

        # Pestaña de indemnizaciones
        self.create_indemnizaciones_tab(calc_notebook)

        # Pestaña de descuentos
        self.create_descuentos_tab(calc_notebook)

        # Pestaña de resumen
        self.create_resumen_tab(calc_notebook)

    def create_beneficios_tab(self, parent):
        """Crear pestaña de beneficios sociales"""
        beneficios_frame = ttk.Frame(parent)
        parent.add(beneficios_frame, text="Beneficios Sociales")

        # Treeview para beneficios
        columns = ('concepto', 'base', 'tiempo', 'valor')
        self.beneficios_tree = ttk.Treeview(beneficios_frame, columns=columns, show='headings', height=10)

        # Configurar columnas
        headings = ['Concepto', 'Base de Cálculo', 'Tiempo', 'Valor']
        widths = [200, 120, 120, 100]

        for col, heading, width in zip(columns, headings, widths):
            self.beneficios_tree.heading(col, text=heading)
            self.beneficios_tree.column(col, width=width)

        # Scrollbar
        ben_scroll = ttk.Scrollbar(beneficios_frame, orient=tk.VERTICAL, command=self.beneficios_tree.yview)
        self.beneficios_tree.configure(yscrollcommand=ben_scroll.set)

        # Pack
        self.beneficios_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ben_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_indemnizaciones_tab(self, parent):
        """Crear pestaña de indemnizaciones"""
        indemnizaciones_frame = ttk.Frame(parent)
        parent.add(indemnizaciones_frame, text="Indemnizaciones")

        # Treeview para indemnizaciones
        columns = ('concepto', 'base', 'tiempo', 'valor')
        self.indemnizaciones_tree = ttk.Treeview(indemnizaciones_frame, columns=columns, show='headings', height=10)

        # Configurar columnas
        headings = ['Concepto', 'Base de Cálculo', 'Tiempo/Factor', 'Valor']
        widths = [200, 120, 120, 100]

        for col, heading, width in zip(columns, headings, widths):
            self.indemnizaciones_tree.heading(col, text=heading)
            self.indemnizaciones_tree.column(col, width=width)

        # Scrollbar
        ind_scroll = ttk.Scrollbar(indemnizaciones_frame, orient=tk.VERTICAL, command=self.indemnizaciones_tree.yview)
        self.indemnizaciones_tree.configure(yscrollcommand=ind_scroll.set)

        # Pack
        self.indemnizaciones_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ind_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_descuentos_tab(self, parent):
        """Crear pestaña de descuentos"""
        descuentos_frame = ttk.Frame(parent)
        parent.add(descuentos_frame, text="Descuentos")

        # Treeview para descuentos
        columns = ('concepto', 'descripcion', 'valor')
        self.descuentos_tree = ttk.Treeview(descuentos_frame, columns=columns, show='headings', height=10)

        # Configurar columnas
        headings = ['Concepto', 'Descripción', 'Valor']
        widths = [200, 200, 100]

        for col, heading, width in zip(columns, headings, widths):
            self.descuentos_tree.heading(col, text=heading)
            self.descuentos_tree.column(col, width=width)

        # Scrollbar
        desc_scroll = ttk.Scrollbar(descuentos_frame, orient=tk.VERTICAL, command=self.descuentos_tree.yview)
        self.descuentos_tree.configure(yscrollcommand=desc_scroll.set)

        # Pack
        self.descuentos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        desc_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_resumen_tab(self, parent):
        """Crear pestaña de resumen"""
        resumen_frame = ttk.Frame(parent)
        parent.add(resumen_frame, text="Resumen")

        # Panel de totales
        totales_frame = tk.LabelFrame(resumen_frame, text="Totales de Liquidación", font=('Arial', 11, 'bold'))
        totales_frame.pack(fill=tk.X, padx=10, pady=10)

        totales_grid = tk.Frame(totales_frame)
        totales_grid.pack(padx=10, pady=10)

        self.totales_labels = {}
        totales_items = [
            ("Total Beneficios Sociales:", "$0.00"),
            ("Total Indemnizaciones:", "$0.00"),
            ("Total Ingresos:", "$0.00"),
            ("Total Descuentos:", "$0.00"),
            ("Impuesto a la Renta:", "$0.00"),
            ("NETO A PAGAR:", "$0.00")
        ]

        for i, (label, value) in enumerate(totales_items):
            font_style = ('Arial', 10, 'bold') if 'NETO' in label else ('Arial', 10)
            color = 'red' if 'NETO' in label else 'black'

            tk.Label(totales_grid, text=label, font=font_style).grid(
                row=i, column=0, sticky=tk.W, padx=10, pady=5
            )
            value_label = tk.Label(totales_grid, text=value, font=font_style, fg=color, relief=tk.SUNKEN, width=15)
            value_label.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
            self.totales_labels[label] = value_label

        # Botones de acción
        buttons_frame = tk.Frame(resumen_frame)
        buttons_frame.pack(pady=20)

        action_buttons = [
            ("Calcular Liquidación", self.calculate_liquidation, '#48bb78'),
            ("Procesar Liquidación", self.process_liquidation, '#e53e3e'),
            ("Imprimir", self.print_liquidation, '#4299e1'),
            ("Limpiar", self.clear_liquidation_form, '#ed8936')
        ]

        for text, command, color in action_buttons:
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

    def create_historial_tab(self):
        """Crear pestaña de historial"""
        historial_frame = ttk.Frame(self.notebook)
        self.notebook.add(historial_frame, text="Historial")

        # Panel de filtros
        filter_frame = tk.LabelFrame(historial_frame, text="Filtros", font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_grid = tk.Frame(filter_frame)
        filter_grid.pack(padx=10, pady=5)

        # Filtros
        tk.Label(filter_grid, text="Período:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.hist_period_combo = ttk.Combobox(
            filter_grid,
            values=[str(year) for year in range(2020, 2030)],
            state='readonly',
            width=10
        )
        self.hist_period_combo.grid(row=0, column=1, padx=5)
        self.hist_period_combo.set(str(date.today().year))

        tk.Label(filter_grid, text="Motivo:", font=('Arial', 9)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.hist_motivo_combo = ttk.Combobox(
            filter_grid,
            values=["TODOS", "RENUNCIA", "DESPIDO", "FIN CONTRATO", "JUBILACION"],
            state='readonly',
            width=15
        )
        self.hist_motivo_combo.grid(row=0, column=3, padx=5)
        self.hist_motivo_combo.set("TODOS")

        tk.Button(
            filter_grid,
            text="Buscar",
            command=self.search_history,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=15
        ).grid(row=0, column=4, padx=10)

        # Lista de liquidaciones
        self.create_history_list(historial_frame)

    def create_history_list(self, parent):
        """Crear lista de historial"""
        list_frame = tk.LabelFrame(parent, text="Liquidaciones Procesadas", font=('Arial', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para historial
        columns = ('fecha', 'empleado', 'motivo', 'tiempo', 'beneficios', 'indemnizaciones', 'descuentos', 'neto')
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        # Configurar columnas
        headings = ['Fecha', 'Empleado', 'Motivo', 'Tiempo', 'Beneficios', 'Indemnizaciones', 'Descuentos', 'Neto']
        for col, heading in zip(columns, headings):
            self.history_tree.heading(col, text=heading)
            self.history_tree.column(col, width=100)

        # Scrollbars
        hist_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        hist_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)

        self.history_tree.configure(yscrollcommand=hist_scroll_y.set, xscrollcommand=hist_scroll_x.set)

        # Pack
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        hist_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        hist_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar datos de ejemplo
        self.load_sample_history()

        # Bind events
        self.history_tree.bind('<Double-1>', self.view_liquidation_detail)

    def create_documentos_tab(self):
        """Crear pestaña de documentos"""
        documentos_frame = ttk.Frame(self.notebook)
        self.notebook.add(documentos_frame, text="Documentos")

        # Panel de generación de documentos
        doc_frame = tk.LabelFrame(documentos_frame, text="Generación de Documentos", font=('Arial', 10, 'bold'))
        doc_frame.pack(fill=tk.X, padx=10, pady=10)

        doc_grid = tk.Frame(doc_frame)
        doc_grid.pack(padx=10, pady=10)

        # Selección de empleado para documentos
        tk.Label(doc_grid, text="Empleado:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.doc_emp_combo = ttk.Combobox(doc_grid, state='readonly', width=40)
        self.doc_emp_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        # Tipos de documentos
        doc_types_frame = tk.LabelFrame(doc_grid, text="Documentos Disponibles")
        doc_types_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)

        self.doc_vars = {}
        doc_types = [
            ("Acta de Finiquito", "finiquito"),
            ("Comprobante de Liquidación", "comprobante"),
            ("Certificado Laboral", "certificado"),
            ("Paz y Salvo", "paz_salvo"),
            ("Aviso de Salida IESS", "aviso_iess")
        ]

        for i, (text, var_name) in enumerate(doc_types):
            var = tk.BooleanVar(value=True)
            tk.Checkbutton(
                doc_types_frame,
                text=text,
                variable=var,
                font=('Arial', 9)
            ).grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)
            self.doc_vars[var_name] = var

        # Botones de generación
        buttons_frame = tk.Frame(documentos_frame)
        buttons_frame.pack(pady=20)

        doc_buttons = [
            ("Generar PDF", self.generate_pdf_docs, '#e53e3e'),
            ("Vista Previa", self.preview_docs, '#4299e1'),
            ("Enviar por Email", self.send_email, '#48bb78')
        ]

        for text, command, color in doc_buttons:
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

        self.report_type_var = tk.StringVar(value="mensual")
        report_types = [
            ("Liquidaciones Mensuales", "mensual"),
            ("Por Motivo de Salida", "motivo"),
            ("Costos de Liquidación", "costos"),
            ("Estadísticas de Rotación", "estadisticas")
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
        filter_frame.grid(row=0, column=1, rowspan=5, sticky=tk.N, padx=30)

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

        tk.Label(filter_frame, text="Departamento:", font=('Arial', 9)).pack(anchor=tk.W, pady=(10,0))
        self.rep_dept_combo = ttk.Combobox(filter_frame, state='readonly', width=20)
        self.rep_dept_combo.pack(anchor=tk.W, pady=2)

        # Botones de reporte
        buttons_frame = tk.Frame(reportes_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        report_buttons = [
            ("Vista Previa", self.preview_report, '#4299e1'),
            ("Generar PDF", self.generate_pdf_report, '#e53e3e'),
            ("Exportar Excel", self.export_excel, '#38a169')
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
            self.doc_emp_combo['values'] = emp_values

            # Cargar departamentos para reportes
            departamentos = self.session.query(Departamento).filter_by(activo=True).all()
            dept_values = ["TODOS"] + [dept.nombre for dept in departamentos]
            self.rep_dept_combo['values'] = dept_values
            self.rep_dept_combo.set("TODOS")

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando empleados: {str(e)}")

    def on_employee_selected(self, event):
        """Manejar selección de empleado"""
        selected = self.emp_combo.get()
        if selected:
            codigo = selected.split(' - ')[0]
            self.load_employee_data(codigo)

    def load_employee_data(self, codigo_empleado):
        """Cargar datos del empleado seleccionado"""
        try:
            empleado = self.session.query(Empleado).filter_by(empleado=codigo_empleado).first()
            if empleado:
                # Obtener información adicional
                cargo_nombre = "N/A"
                dept_nombre = "N/A"

                if empleado.cargo:
                    cargo = self.session.query(Cargo).filter_by(codigo=empleado.cargo).first()
                    if cargo:
                        cargo_nombre = cargo.nombre

                if empleado.depto:
                    dept = self.session.query(Departamento).filter_by(codigo=empleado.depto).first()
                    if dept:
                        dept_nombre = dept.nombre

                # Actualizar labels
                self.emp_info_labels["Código:"].config(text=empleado.empleado)
                self.emp_info_labels["Cédula:"].config(text=empleado.cedula or "N/A")
                self.emp_info_labels["Cargo:"].config(text=cargo_nombre)
                self.emp_info_labels["Departamento:"].config(text=dept_nombre)
                self.emp_info_labels["Fecha Ingreso:"].config(
                    text=empleado.fecha_ing.strftime('%d/%m/%Y') if empleado.fecha_ing else "N/A"
                )
                self.emp_info_labels["Sueldo Actual:"].config(text=f"${empleado.sueldo:.2f}")
                self.emp_info_labels["Estado:"].config(text=empleado.estado or "N/A")

                # Calcular tiempo trabajado
                if empleado.fecha_ing:
                    self.calculate_time_worked()

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos del empleado: {str(e)}")

    def calculate_time_worked(self, event=None):
        """Calcular tiempo trabajado"""
        try:
            selected = self.emp_combo.get()
            if not selected:
                return

            codigo = selected.split(' - ')[0]
            empleado = self.session.query(Empleado).filter_by(empleado=codigo).first()

            if empleado and empleado.fecha_ing:
                fecha_salida_str = self.fecha_salida_entry.get()
                if fecha_salida_str:
                    fecha_salida = datetime.strptime(fecha_salida_str, '%d/%m/%Y').date()

                    # Calcular diferencia
                    diferencia = fecha_salida - empleado.fecha_ing
                    años = diferencia.days // 365
                    meses = (diferencia.days % 365) // 30
                    dias = (diferencia.days % 365) % 30

                    tiempo_text = f"{años} años, {meses} meses, {dias} días"
                    self.emp_info_labels["Tiempo Trabajado:"].config(text=tiempo_text)

        except Exception as e:
            print(f"Error calculando tiempo: {e}")

    def update_liquidation_config(self):
        """Actualizar configuración según motivo"""
        motivo = self.motivo_liquidacion_var.get()

        # Aquí se puede ajustar la configuración según el motivo
        # Por ejemplo, habilitar/deshabilitar ciertos campos
        pass

    def load_sample_history(self):
        """Cargar historial de ejemplo"""
        sample_data = [
            ("15/12/2023", "001001 - Juan Perez", "RENUNCIA", "3 años", "$1,500.00", "$0.00", "$150.00", "$1,350.00"),
            ("20/11/2023", "001005 - Luis Vargas", "JUBILACION", "15 años", "$8,000.00", "$0.00", "$800.00", "$7,200.00"),
            ("10/10/2023", "001003 - Carlos Rodriguez", "DESPIDO", "2 años", "$1,200.00", "$2,400.00", "$200.00", "$3,400.00"),
        ]

        for data in sample_data:
            self.history_tree.insert('', 'end', values=data)

    # Métodos de cálculo
    def calculate_liquidation(self):
        """Calcular liquidación completa"""
        selected = self.emp_combo.get()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un empleado")
            return

        try:
            # Limpiar tablas
            for tree in [self.beneficios_tree, self.indemnizaciones_tree, self.descuentos_tree]:
                for item in tree.get_children():
                    tree.delete(item)

            codigo = selected.split(' - ')[0]
            empleado = self.session.query(Empleado).filter_by(empleado=codigo).first()

            if not empleado:
                return

            # Calcular beneficios sociales
            self.calculate_beneficios(empleado)

            # Calcular indemnizaciones según motivo
            self.calculate_indemnizaciones(empleado)

            # Calcular descuentos
            self.calculate_descuentos(empleado)

            # Calcular totales
            self.calculate_totales()

            messagebox.showinfo("Éxito", "Cálculo de liquidación completado")

        except Exception as e:
            messagebox.showerror("Error", f"Error en cálculo: {str(e)}")

    def calculate_beneficios(self, empleado):
        """Calcular beneficios sociales"""
        # Décimo tercer sueldo proporcional
        sueldo = empleado.sueldo

        # Simulación de cálculos
        beneficios = [
            ("Décimo Tercer Sueldo", f"${sueldo:.2f}", "Proporcional", f"${sueldo/2:.2f}"),
            ("Décimo Cuarto Sueldo", "$460.00", "Proporcional", "$230.00"),
            ("Vacaciones", f"${sueldo:.2f}", "15 días", f"${sueldo/2:.2f}"),
            ("Fondos de Reserva", f"${sueldo:.2f}", "8.33%", f"${sueldo*0.0833:.2f}")
        ]

        for beneficio in beneficios:
            self.beneficios_tree.insert('', 'end', values=beneficio)

    def calculate_indemnizaciones(self, empleado):
        """Calcular indemnizaciones según motivo"""
        motivo = self.motivo_liquidacion_var.get()
        sueldo = empleado.sueldo

        indemnizaciones = []

        if motivo == "despido":
            # Despido intempestivo
            indemnizaciones = [
                ("Indemnización por Despido", f"${sueldo:.2f}", "3 meses", f"${sueldo*3:.2f}"),
                ("Bonificación por Desahucio", f"${sueldo:.2f}", "25%", f"${sueldo*0.25:.2f}")
            ]
        elif motivo == "renuncia":
            # No hay indemnizaciones por renuncia voluntaria
            indemnizaciones = [
                ("Sin Indemnizaciones", "N/A", "Renuncia Voluntaria", "$0.00")
            ]

        for indemnizacion in indemnizaciones:
            self.indemnizaciones_tree.insert('', 'end', values=indemnizacion)

    def calculate_descuentos(self, empleado):
        """Calcular descuentos"""
        # Simulación de descuentos
        descuentos = [
            ("Impuesto a la Renta", "Según tabla", "$50.00"),
            ("Préstamos Pendientes", "Saldo pendiente", "$0.00"),
            ("Anticipos", "Pendientes de descuento", "$0.00")
        ]

        for descuento in descuentos:
            self.descuentos_tree.insert('', 'end', values=descuento)

    def calculate_totales(self):
        """Calcular totales de liquidación"""
        # Simular totales
        total_beneficios = Decimal('1500.00')
        total_indemnizaciones = Decimal('0.00')
        total_descuentos = Decimal('50.00')

        motivo = self.motivo_liquidacion_var.get()
        if motivo == "despido":
            total_indemnizaciones = Decimal('2400.00')

        total_ingresos = total_beneficios + total_indemnizaciones
        neto_pagar = total_ingresos - total_descuentos

        # Actualizar labels
        self.totales_labels["Total Beneficios Sociales:"].config(text=f"${total_beneficios:.2f}")
        self.totales_labels["Total Indemnizaciones:"].config(text=f"${total_indemnizaciones:.2f}")
        self.totales_labels["Total Ingresos:"].config(text=f"${total_ingresos:.2f}")
        self.totales_labels["Total Descuentos:"].config(text=f"${total_descuentos:.2f}")
        self.totales_labels["NETO A PAGAR:"].config(text=f"${neto_pagar:.2f}")

    # Métodos de eventos
    def new_liquidation(self):
        """Nueva liquidación"""
        self.notebook.select(0)  # Ir a pestaña de cálculo

    def process_liquidation(self):
        """Procesar liquidación"""
        if not self.emp_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un empleado")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de procesar esta liquidación?"):
            messagebox.showinfo("Éxito", "Liquidación procesada exitosamente")

    def generate_documents(self):
        """Generar documentos"""
        self.notebook.select(2)  # Ir a pestaña de documentos

    def generate_reports(self):
        """Generar reportes"""
        self.notebook.select(3)  # Ir a pestaña de reportes

    def print_liquidation(self):
        """Imprimir liquidación"""
        messagebox.showinfo("Información", "Función de impresión en desarrollo")

    def clear_liquidation_form(self):
        """Limpiar formulario"""
        self.emp_combo.set("")
        self.fecha_salida_entry.delete(0, tk.END)
        self.fecha_salida_entry.insert(0, date.today().strftime('%d/%m/%Y'))
        self.dias_trabajados_entry.delete(0, tk.END)
        self.obs_text.delete(1.0, tk.END)

        # Limpiar labels
        for label in self.emp_info_labels.values():
            label.config(text="")
        for label in self.totales_labels.values():
            label.config(text="$0.00")

        # Limpiar tablas
        for tree in [self.beneficios_tree, self.indemnizaciones_tree, self.descuentos_tree]:
            for item in tree.get_children():
                tree.delete(item)

    def search_history(self):
        """Buscar en historial"""
        messagebox.showinfo("Información", "Búsqueda actualizada")

    def view_liquidation_detail(self, event):
        """Ver detalle de liquidación"""
        selection = self.history_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Vista de detalle en desarrollo")

    def generate_pdf_docs(self):
        """Generar documentos PDF"""
        messagebox.showinfo("Información", "Generación de documentos PDF en desarrollo")

    def preview_docs(self):
        """Vista previa de documentos"""
        messagebox.showinfo("Información", "Vista previa en desarrollo")

    def send_email(self):
        """Enviar por email"""
        messagebox.showinfo("Información", "Envío por email en desarrollo")

    def preview_report(self):
        """Vista previa del reporte"""
        messagebox.showinfo("Información", "Vista previa en desarrollo")

    def generate_pdf_report(self):
        """Generar reporte PDF"""
        messagebox.showinfo("Información", "Generación de PDF en desarrollo")

    def export_excel(self):
        """Exportar a Excel"""
        messagebox.showinfo("Información", "Exportación a Excel en desarrollo")

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