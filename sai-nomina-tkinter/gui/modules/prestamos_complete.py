#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Préstamos Completo - Sistema SAI
Gestión de préstamos a empleados con cálculo de cuotas e intereses
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

class PrestamosCompleteModule(tk.Frame):
    """Módulo completo de préstamos"""

    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables
        self.selected_employee = None
        self.selected_loan = None
        self.tipo_prestamo_var = tk.StringVar(value="quirografario")
        self.tipo_interes_var = tk.StringVar(value="fijo")

        self.pack(fill="both", expand=True)
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
            text="GESTIÓN DE PRÉSTAMOS",
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
        self.create_nuevo_prestamo_tab()
        self.create_administracion_tab()
        self.create_pagos_tab()
        self.create_reportes_tab()

    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = tk.Frame(self, bg='#e2e8f0', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=2)
        toolbar.pack_propagate(False)

        # Botones principales
        buttons = [
            ("Nuevo Préstamo", self.new_loan, '#4299e1'),
            ("📄 Carga Masiva", self.carga_masiva_prestamos, '#38a169'),
            ("⚡ Cálculos Masivos", self.calculos_masivos_prestamos, '#805ad5'),
            ("Calcular Cuotas", self.calculate_installments, '#48bb78'),
            ("Registrar Pago", self.register_payment, '#ed8936'),
            ("Consultar", self.query_loans, '#9f7aea'),
            ("📅 Descargar BD", self.descargar_bd, '#2d3748'),
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

    def create_nuevo_prestamo_tab(self):
        """Crear pestaña de nuevo préstamo"""
        nuevo_frame = ttk.Frame(self.notebook)
        self.notebook.add(nuevo_frame, text="Nuevo Préstamo")

        # Panel principal dividido en dos columnas
        main_panel = tk.Frame(nuevo_frame, bg='#f0f0f0')
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Columna izquierda - Datos del préstamo
        left_panel = tk.LabelFrame(main_panel, text="Datos del Préstamo", font=('Arial', 11, 'bold'))
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.create_loan_form(left_panel)

        # Columna derecha - Cálculos y tabla de amortización
        right_panel = tk.LabelFrame(main_panel, text="Simulación de Cuotas", font=('Arial', 11, 'bold'))
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.create_amortization_table(right_panel)

    def create_loan_form(self, parent):
        """Crear formulario de préstamo"""
        form_frame = tk.Frame(parent)
        form_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Empleado
        tk.Label(form_frame, text="Empleado:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.emp_combo = ttk.Combobox(form_frame, state='readonly', width=30)
        self.emp_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.emp_combo.bind('<<ComboboxSelected>>', self.on_employee_selected)

        # Información del empleado
        emp_info_frame = tk.LabelFrame(form_frame, text="Información del Empleado")
        emp_info_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)

        self.emp_info_labels = {}
        info_fields = ["Sueldo:", "Cargo:", "Fecha Ingreso:", "Capacidad de Pago:"]
        for i, field in enumerate(info_fields):
            tk.Label(emp_info_frame, text=field, font=('Arial', 9)).grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=5, pady=2)
            label = tk.Label(emp_info_frame, text="", font=('Arial', 9), relief=tk.SUNKEN, width=15)
            label.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=5, pady=2)
            self.emp_info_labels[field] = label

        # Tipo de préstamo
        tk.Label(form_frame, text="Tipo de Préstamo:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        tipo_frame = tk.Frame(form_frame)
        tipo_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        tk.Radiobutton(
            tipo_frame,
            text="Quirografario",
            variable=self.tipo_prestamo_var,
            value="quirografario",
            command=self.update_loan_params
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            tipo_frame,
            text="Hipotecario",
            variable=self.tipo_prestamo_var,
            value="hipotecario",
            command=self.update_loan_params
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            tipo_frame,
            text="Emergencia",
            variable=self.tipo_prestamo_var,
            value="emergencia",
            command=self.update_loan_params
        ).pack(side=tk.LEFT)

        # Monto
        tk.Label(form_frame, text="Monto:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.monto_entry = tk.Entry(form_frame, width=15)
        self.monto_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.monto_entry.bind('<KeyRelease>', self.calculate_preview)

        # Plazo
        tk.Label(form_frame, text="Plazo (meses):", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.plazo_entry = tk.Entry(form_frame, width=10)
        self.plazo_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.plazo_entry.bind('<KeyRelease>', self.calculate_preview)

        # Tasa de interés
        tk.Label(form_frame, text="Tasa Interés (%):", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.tasa_entry = tk.Entry(form_frame, width=10)
        self.tasa_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.tasa_entry.bind('<KeyRelease>', self.calculate_preview)

        # Tipo de interés
        tipo_int_frame = tk.Frame(form_frame)
        tipo_int_frame.grid(row=5, column=2, sticky=tk.W, padx=5)

        tk.Radiobutton(
            tipo_int_frame,
            text="Fijo",
            variable=self.tipo_interes_var,
            value="fijo",
            font=('Arial', 8)
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            tipo_int_frame,
            text="Variable",
            variable=self.tipo_interes_var,
            value="variable",
            font=('Arial', 8)
        ).pack(side=tk.LEFT)

        # Fecha de inicio
        tk.Label(form_frame, text="Fecha Inicio:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.fecha_inicio_entry = tk.Entry(form_frame, width=12)
        self.fecha_inicio_entry.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        self.fecha_inicio_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Observaciones
        tk.Label(form_frame, text="Observaciones:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=5)
        self.obs_text = tk.Text(form_frame, width=40, height=4)
        self.obs_text.grid(row=7, column=1, columnspan=2, sticky='ew', padx=5, pady=5)

        # Resumen del préstamo
        resumen_frame = tk.LabelFrame(form_frame, text="Resumen del Préstamo")
        resumen_frame.grid(row=8, column=0, columnspan=3, sticky='ew', pady=10)

        self.resumen_labels = {}
        resumen_fields = ["Cuota Mensual:", "Total a Pagar:", "Total Intereses:", "% del Sueldo:"]
        for i, field in enumerate(resumen_fields):
            tk.Label(resumen_frame, text=field, font=('Arial', 9, 'bold')).grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=5, pady=2)
            label = tk.Label(resumen_frame, text="$0.00", font=('Arial', 9), fg='blue', relief=tk.SUNKEN, width=12)
            label.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=5, pady=2)
            self.resumen_labels[field] = label

        # Botones
        buttons_frame = tk.Frame(form_frame)
        buttons_frame.grid(row=9, column=0, columnspan=3, pady=20)

        tk.Button(
            buttons_frame,
            text="Guardar Préstamo",
            command=self.save_loan,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="Limpiar",
            command=self.clear_loan_form,
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    def create_amortization_table(self, parent):
        """Crear tabla de amortización"""
        table_frame = tk.Frame(parent)
        table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Título
        tk.Label(table_frame, text="Tabla de Amortización", font=('Arial', 12, 'bold')).pack(pady=5)

        # Treeview para tabla de amortización
        columns = ('cuota', 'fecha', 'capital', 'interes', 'cuota_total', 'saldo')
        self.amort_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)

        # Configurar columnas
        headings = ['#', 'Fecha', 'Capital', 'Interés', 'Cuota', 'Saldo']
        widths = [40, 80, 80, 80, 80, 80]

        for col, heading, width in zip(columns, headings, widths):
            self.amort_tree.heading(col, text=heading)
            self.amort_tree.column(col, width=width, anchor=tk.CENTER)

        # Scrollbar
        amort_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.amort_tree.yview)
        self.amort_tree.configure(yscrollcommand=amort_scroll.set)

        # Pack
        self.amort_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        amort_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_administracion_tab(self):
        """Crear pestaña de administración de préstamos"""
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="Administración")

        # Panel de filtros
        filter_frame = tk.LabelFrame(admin_frame, text="Filtros de Búsqueda", font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_grid = tk.Frame(filter_frame)
        filter_grid.pack(padx=10, pady=5)

        # Filtros
        tk.Label(filter_grid, text="Empleado:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_emp_combo = ttk.Combobox(filter_grid, state='readonly', width=25)
        self.filter_emp_combo.grid(row=0, column=1, padx=5)

        tk.Label(filter_grid, text="Estado:", font=('Arial', 9)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.filter_estado_combo = ttk.Combobox(
            filter_grid,
            values=["TODOS", "ACTIVO", "CANCELADO", "VENCIDO"],
            state='readonly',
            width=12
        )
        self.filter_estado_combo.grid(row=0, column=3, padx=5)
        self.filter_estado_combo.set("TODOS")

        tk.Button(
            filter_grid,
            text="Buscar",
            command=self.search_loans,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=15
        ).grid(row=0, column=4, padx=10)

        # Lista de préstamos
        self.create_loans_list(admin_frame)

        # Panel de detalles
        self.create_loan_details_panel(admin_frame)

    def create_loans_list(self, parent):
        """Crear lista de préstamos"""
        list_frame = tk.LabelFrame(parent, text="Préstamos Registrados", font=('Arial', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para préstamos
        columns = ('codigo', 'empleado', 'tipo', 'monto', 'plazo', 'cuota', 'saldo', 'estado')
        self.loans_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        # Configurar columnas
        headings = ['Código', 'Empleado', 'Tipo', 'Monto', 'Plazo', 'Cuota', 'Saldo', 'Estado']
        widths = [80, 150, 100, 80, 60, 80, 80, 80]

        for col, heading, width in zip(columns, headings, widths):
            self.loans_tree.heading(col, text=heading)
            self.loans_tree.column(col, width=width)

        # Scrollbars
        loans_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.loans_tree.yview)
        loans_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.loans_tree.xview)

        self.loans_tree.configure(yscrollcommand=loans_scroll_y.set, xscrollcommand=loans_scroll_x.set)

        # Pack
        self.loans_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        loans_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        loans_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.loans_tree.bind('<<TreeviewSelect>>', self.on_loan_select)

        # Cargar préstamos de ejemplo
        self.load_sample_loans()

    def create_loan_details_panel(self, parent):
        """Crear panel de detalles del préstamo"""
        details_frame = tk.LabelFrame(parent, text="Detalles del Préstamo", font=('Arial', 10, 'bold'))
        details_frame.pack(fill=tk.X, padx=10, pady=5)

        details_grid = tk.Frame(details_frame)
        details_grid.pack(padx=10, pady=5)

        # Información del préstamo
        self.detail_labels = {}
        detail_fields = [
            "Empleado:", "Tipo:", "Monto Original:", "Fecha Inicio:",
            "Plazo:", "Tasa:", "Cuota Mensual:", "Total Pagado:",
            "Saldo Pendiente:", "Próximo Pago:", "Estado:", "Observaciones:"
        ]

        for i, field in enumerate(detail_fields):
            row = i // 4
            col = (i % 4) * 2
            tk.Label(details_grid, text=field, font=('Arial', 9, 'bold')).grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            label = tk.Label(details_grid, text="", font=('Arial', 9), relief=tk.SUNKEN, width=15)
            label.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
            self.detail_labels[field] = label

        # Botones de acciones
        actions_frame = tk.Frame(details_frame)
        actions_frame.pack(pady=10)

        action_buttons = [
            ("Ver Tabla", self.view_amortization, '#4299e1'),
            ("Registrar Pago", self.register_payment, '#48bb78'),
            ("Modificar", self.modify_loan, '#ed8936'),
            ("Cancelar", self.cancel_loan, '#e53e3e')
        ]

        for text, command, color in action_buttons:
            tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 9, 'bold'),
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=5)

    def create_pagos_tab(self):
        """Crear pestaña de pagos"""
        pagos_frame = ttk.Frame(self.notebook)
        self.notebook.add(pagos_frame, text="Registro de Pagos")

        # Panel de registro de pago
        pago_frame = tk.LabelFrame(pagos_frame, text="Registrar Pago", font=('Arial', 10, 'bold'))
        pago_frame.pack(fill=tk.X, padx=10, pady=5)

        pago_grid = tk.Frame(pago_frame)
        pago_grid.pack(padx=10, pady=10)

        # Préstamo
        tk.Label(pago_grid, text="Préstamo:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pago_prestamo_combo = ttk.Combobox(pago_grid, state='readonly', width=40)
        self.pago_prestamo_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        # Fecha de pago
        tk.Label(pago_grid, text="Fecha Pago:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fecha_pago_entry = tk.Entry(pago_grid, width=12)
        self.fecha_pago_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.fecha_pago_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Monto
        tk.Label(pago_grid, text="Monto:", font=('Arial', 9, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)
        self.monto_pago_entry = tk.Entry(pago_grid, width=12)
        self.monto_pago_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        # Tipo de pago
        tk.Label(pago_grid, text="Tipo Pago:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.tipo_pago_combo = ttk.Combobox(
            pago_grid,
            values=["CUOTA NORMAL", "PAGO PARCIAL", "PAGO TOTAL", "PAGO ANTICIPADO"],
            state='readonly',
            width=15
        )
        self.tipo_pago_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Observaciones del pago
        tk.Label(pago_grid, text="Observaciones:", font=('Arial', 9, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.obs_pago_text = tk.Text(pago_grid, width=50, height=3)
        self.obs_pago_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

        # Botón de guardar pago
        tk.Button(
            pago_frame,
            text="Registrar Pago",
            command=self.save_payment,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(pady=10)

        # Historial de pagos
        self.create_payments_history(pagos_frame)

    def create_payments_history(self, parent):
        """Crear historial de pagos"""
        history_frame = tk.LabelFrame(parent, text="Historial de Pagos", font=('Arial', 10, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para historial
        columns = ('fecha', 'prestamo', 'empleado', 'cuota', 'capital', 'interes', 'total', 'tipo')
        self.payments_tree = ttk.Treeview(history_frame, columns=columns, show='headings')

        # Configurar columnas
        headings = ['Fecha', 'Préstamo', 'Empleado', 'Cuota #', 'Capital', 'Interés', 'Total', 'Tipo']
        for col, heading in zip(columns, headings):
            self.payments_tree.heading(col, text=heading)
            self.payments_tree.column(col, width=90)

        # Scrollbars
        pay_scroll_y = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.payments_tree.yview)
        pay_scroll_x = ttk.Scrollbar(history_frame, orient=tk.HORIZONTAL, command=self.payments_tree.xview)

        self.payments_tree.configure(yscrollcommand=pay_scroll_y.set, xscrollcommand=pay_scroll_x.set)

        # Pack
        self.payments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        pay_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        pay_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar historial de ejemplo
        self.load_sample_payments()

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

        self.report_type_var = tk.StringVar(value="cartera")
        report_types = [
            ("Estado de Cartera", "cartera"),
            ("Vencimientos", "vencimientos"),
            ("Pagos por Período", "pagos"),
            ("Tabla de Amortización", "amortizacion")
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

        tk.Label(filter_frame, text="Empleado:", font=('Arial', 9)).pack(anchor=tk.W, pady=(10,0))
        self.rep_emp_combo = ttk.Combobox(filter_frame, state='readonly', width=25)
        self.rep_emp_combo.pack(anchor=tk.W, pady=2)

        tk.Label(filter_frame, text="Período:", font=('Arial', 9)).pack(anchor=tk.W, pady=(10,0))
        period_frame = tk.Frame(filter_frame)
        period_frame.pack(anchor=tk.W, pady=2)

        tk.Label(period_frame, text="Desde:", font=('Arial', 8)).pack(side=tk.LEFT)
        self.rep_fecha_desde = tk.Entry(period_frame, width=10)
        self.rep_fecha_desde.pack(side=tk.LEFT, padx=2)

        tk.Label(period_frame, text="Hasta:", font=('Arial', 8)).pack(side=tk.LEFT, padx=(10,0))
        self.rep_fecha_hasta = tk.Entry(period_frame, width=10)
        self.rep_fecha_hasta.pack(side=tk.LEFT, padx=2)

        # Botones de reporte
        buttons_frame = tk.Frame(reportes_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        report_buttons = [
            ("Vista Previa", self.preview_report, '#4299e1'),
            ("Generar PDF", self.generate_pdf, '#e53e3e'),
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
            self.filter_emp_combo['values'] = ["TODOS"] + emp_values
            self.rep_emp_combo['values'] = ["TODOS"] + emp_values

            # Establecer valores por defecto
            self.filter_emp_combo.set("TODOS")
            self.rep_emp_combo.set("TODOS")

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando empleados: {str(e)}")

    def on_employee_selected(self, event):
        """Manejar selección de empleado"""
        selected = self.emp_combo.get()
        if selected:
            codigo = selected.split(' - ')[0]
            self.load_employee_info(codigo)

    def load_employee_info(self, codigo_empleado):
        """Cargar información del empleado"""
        try:
            empleado = self.session.query(Empleado).filter_by(empleado=codigo_empleado).first()
            if empleado:
                # Obtener información del cargo
                cargo_nombre = "N/A"
                if empleado.cargo:
                    cargo = self.session.query(Cargo).filter_by(codigo=empleado.cargo).first()
                    if cargo:
                        cargo_nombre = cargo.nombre

                # Actualizar labels
                self.emp_info_labels["Sueldo:"].config(text=f"${empleado.sueldo:.2f}")
                self.emp_info_labels["Cargo:"].config(text=cargo_nombre)
                self.emp_info_labels["Fecha Ingreso:"].config(
                    text=empleado.fecha_ing.strftime('%d/%m/%Y') if empleado.fecha_ing else "N/A"
                )

                # Calcular capacidad de pago (máximo 40% del sueldo)
                capacidad = empleado.sueldo * Decimal('0.40')
                self.emp_info_labels["Capacidad de Pago:"].config(text=f"${capacidad:.2f}")

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando información del empleado: {str(e)}")

    def update_loan_params(self):
        """Actualizar parámetros según tipo de préstamo"""
        tipo = self.tipo_prestamo_var.get()

        if tipo == "quirografario":
            self.tasa_entry.delete(0, tk.END)
            self.tasa_entry.insert(0, "15.30")  # Tasa típica IESS
            self.plazo_entry.delete(0, tk.END)
            self.plazo_entry.insert(0, "36")  # Máximo 36 meses
        elif tipo == "hipotecario":
            self.tasa_entry.delete(0, tk.END)
            self.tasa_entry.insert(0, "10.64")  # Tasa típica hipotecaria
            self.plazo_entry.delete(0, tk.END)
            self.plazo_entry.insert(0, "240")  # Máximo 20 años
        elif tipo == "emergencia":
            self.tasa_entry.delete(0, tk.END)
            self.tasa_entry.insert(0, "0.00")  # Sin interés
            self.plazo_entry.delete(0, tk.END)
            self.plazo_entry.insert(0, "12")  # Máximo 12 meses

        self.calculate_preview()

    def calculate_preview(self, event=None):
        """Calcular vista previa del préstamo"""
        try:
            monto = Decimal(self.monto_entry.get() or '0')
            plazo = int(self.plazo_entry.get() or '0')
            tasa_anual = Decimal(self.tasa_entry.get() or '0')

            if monto > 0 and plazo > 0:
                # Calcular cuota mensual
                if tasa_anual > 0:
                    tasa_mensual = tasa_anual / 100 / 12
                    cuota = monto * (tasa_mensual * (1 + tasa_mensual) ** plazo) / ((1 + tasa_mensual) ** plazo - 1)
                else:
                    cuota = monto / plazo

                total_pagar = cuota * plazo
                total_intereses = total_pagar - monto

                # Actualizar labels de resumen
                self.resumen_labels["Cuota Mensual:"].config(text=f"${cuota:.2f}")
                self.resumen_labels["Total a Pagar:"].config(text=f"${total_pagar:.2f}")
                self.resumen_labels["Total Intereses:"].config(text=f"${total_intereses:.2f}")

                # Calcular porcentaje del sueldo
                selected_emp = self.emp_combo.get()
                if selected_emp:
                    codigo = selected_emp.split(' - ')[0]
                    empleado = self.session.query(Empleado).filter_by(empleado=codigo).first()
                    if empleado:
                        porcentaje = (cuota / empleado.sueldo) * 100
                        self.resumen_labels["% del Sueldo:"].config(text=f"{porcentaje:.1f}%")

                # Generar tabla de amortización
                self.generate_amortization_table(monto, plazo, tasa_anual / 100 / 12 if tasa_anual > 0 else 0)

        except ValueError:
            # Limpiar labels si hay error en los datos
            for label in self.resumen_labels.values():
                label.config(text="$0.00")

    def generate_amortization_table(self, monto, plazo, tasa_mensual):
        """Generar tabla de amortización"""
        # Limpiar tabla
        for item in self.amort_tree.get_children():
            self.amort_tree.delete(item)

        if monto <= 0 or plazo <= 0:
            return

        # Calcular cuota
        if tasa_mensual > 0:
            cuota = monto * (tasa_mensual * (1 + tasa_mensual) ** plazo) / ((1 + tasa_mensual) ** plazo - 1)
        else:
            cuota = monto / plazo

        saldo = monto
        fecha_actual = datetime.strptime(self.fecha_inicio_entry.get(), '%d/%m/%Y').date()

        for i in range(1, min(plazo + 1, 13)):  # Mostrar máximo 12 cuotas
            interes = saldo * tasa_mensual
            capital = cuota - interes
            saldo = saldo - capital

            if saldo < 0:
                saldo = 0

            self.amort_tree.insert('', 'end', values=(
                i,
                fecha_actual.strftime('%d/%m/%Y'),
                f"${capital:.2f}",
                f"${interes:.2f}",
                f"${cuota:.2f}",
                f"${saldo:.2f}"
            ))

            # Siguiente mes
            if fecha_actual.month == 12:
                fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1)
            else:
                fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1)

    def load_sample_loans(self):
        """Cargar préstamos de ejemplo"""
        sample_loans = [
            ("PREST001", "001001 - Juan Perez", "Quirografario", "$5,000.00", "36", "$167.50", "$3,200.00", "ACTIVO"),
            ("PREST002", "001002 - Maria Gonzalez", "Emergencia", "$1,000.00", "12", "$83.33", "$500.00", "ACTIVO"),
            ("PREST003", "001003 - Carlos Rodriguez", "Hipotecario", "$25,000.00", "180", "$275.00", "$22,000.00", "ACTIVO"),
        ]

        for loan in sample_loans:
            self.loans_tree.insert('', 'end', values=loan)

    def load_sample_payments(self):
        """Cargar historial de pagos de ejemplo"""
        sample_payments = [
            ("15/01/2024", "PREST001", "Juan Perez", "1", "$132.50", "$35.00", "$167.50", "CUOTA NORMAL"),
            ("15/02/2024", "PREST001", "Juan Perez", "2", "$134.20", "$33.30", "$167.50", "CUOTA NORMAL"),
            ("15/01/2024", "PREST002", "Maria Gonzalez", "1", "$83.33", "$0.00", "$83.33", "CUOTA NORMAL"),
        ]

        for payment in sample_payments:
            self.payments_tree.insert('', 'end', values=payment)

    def on_loan_select(self, event):
        """Manejar selección de préstamo"""
        selection = self.loans_tree.selection()
        if selection:
            item = self.loans_tree.item(selection[0])
            values = item['values']

            # Actualizar panel de detalles
            self.detail_labels["Empleado:"].config(text=values[1])
            self.detail_labels["Tipo:"].config(text=values[2])
            self.detail_labels["Monto Original:"].config(text=values[3])
            self.detail_labels["Plazo:"].config(text=f"{values[4]} meses")
            self.detail_labels["Cuota Mensual:"].config(text=values[5])
            self.detail_labels["Saldo Pendiente:"].config(text=values[6])
            self.detail_labels["Estado:"].config(text=values[7])

    # Métodos de eventos
    def new_loan(self):
        """Nuevo préstamo"""
        self.notebook.select(0)  # Ir a pestaña de nuevo préstamo

    def calculate_installments(self):
        """Calcular cuotas"""
        self.calculate_preview()

    def register_payment(self):
        """Registrar pago"""
        self.notebook.select(2)  # Ir a pestaña de pagos

    def query_loans(self):
        """Consultar préstamos"""
        self.notebook.select(1)  # Ir a pestaña de administración

    def generate_reports(self):
        """Generar reportes"""
        self.notebook.select(3)  # Ir a pestaña de reportes

    def save_loan(self):
        """Guardar préstamo"""
        if not self.emp_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un empleado")
            return

        if not self.monto_entry.get():
            messagebox.showwarning("Advertencia", "Ingrese el monto del préstamo")
            return

        messagebox.showinfo("Éxito", "Préstamo guardado exitosamente")
        self.clear_loan_form()

    def clear_loan_form(self):
        """Limpiar formulario de préstamo"""
        self.emp_combo.set("")
        self.monto_entry.delete(0, tk.END)
        self.plazo_entry.delete(0, tk.END)
        self.tasa_entry.delete(0, tk.END)
        self.obs_text.delete(1.0, tk.END)

        # Limpiar labels
        for label in self.emp_info_labels.values():
            label.config(text="")
        for label in self.resumen_labels.values():
            label.config(text="$0.00")

        # Limpiar tabla
        for item in self.amort_tree.get_children():
            self.amort_tree.delete(item)

    def search_loans(self):
        """Buscar préstamos"""
        messagebox.showinfo("Información", "Búsqueda actualizada")

    def view_amortization(self):
        """Ver tabla de amortización"""
        messagebox.showinfo("Información", "Vista de tabla de amortización en desarrollo")

    def modify_loan(self):
        """Modificar préstamo"""
        messagebox.showinfo("Información", "Modificación de préstamo en desarrollo")

    def cancel_loan(self):
        """Cancelar préstamo"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de cancelar el préstamo?"):
            messagebox.showinfo("Información", "Préstamo cancelado")

    def save_payment(self):
        """Guardar pago"""
        if not self.pago_prestamo_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un préstamo")
            return

        messagebox.showinfo("Éxito", "Pago registrado exitosamente")

    def preview_report(self):
        """Vista previa del reporte"""
        messagebox.showinfo("Información", "Vista previa en desarrollo")

    def generate_pdf(self):
        """Generar PDF"""
        messagebox.showinfo("Información", "Generación de PDF en desarrollo")

    def export_excel(self):
        """Exportar a Excel"""
        messagebox.showinfo("Información", "Exportación a Excel en desarrollo")

    def carga_masiva_prestamos(self):
        """Carga masiva de préstamos"""
        try:
            columns_mapping = {
                'codigo_empleado': 'empleado',
                'tipo_prestamo': 'tipo',
                'monto_prestamo': 'monto',
                'plazo_meses': 'plazo',
                'tasa_interes': 'tasa',
                'fecha_inicio': 'fecha_inicio',
                'cuota_mensual': 'cuota',
                'observaciones': 'observaciones',
                'estado': 'estado'
            }

            carga_masiva = CargaMasivaComponent(
                parent=self,
                session=self.session,
                entity_type="prestamos",
                columns_mapping=columns_mapping
            )

            show_toast(self, "Carga masiva de préstamos iniciada", "info")

        except Exception as e:
            messagebox.showerror("Error", f"Error en carga masiva: {str(e)}")

    def calculos_masivos_prestamos(self):
        """Cálculos masivos de préstamos"""
        try:
            # Crear ventana de cálculos masivos
            calculo_window = tk.Toplevel(self)
            calculo_window.title("Cálculos Masivos de Préstamos")
            calculo_window.geometry("1000x800")
            calculo_window.transient(self)
            calculo_window.grab_set()

            # Header
            header_frame = tk.Frame(calculo_window, bg='#2c5282', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)

            tk.Label(
                header_frame,
                text="⚡ CÁLCULOS MASIVOS DE PRÉSTAMOS",
                font=('Arial', 16, 'bold'),
                bg='#2c5282',
                fg='white'
            ).pack(pady=15)

            # Notebook para opciones
            notebook = ttk.Notebook(calculo_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Pestaña 1: Cálculo de cuotas masivo
            self.create_calculo_cuotas_tab(notebook)

            # Pestaña 2: Proyección de pagos
            self.create_proyeccion_pagos_tab(notebook)

            # Pestaña 3: Reestructuración masiva
            self.create_reestructuracion_tab(notebook)

        except Exception as e:
            messagebox.showerror("Error", f"Error en cálculos masivos: {str(e)}")

    def create_calculo_cuotas_tab(self, parent):
        """Crear pestaña de cálculo de cuotas masivo"""
        cuotas_frame = ttk.Frame(parent)
        parent.add(cuotas_frame, text="Cálculo de Cuotas")

        # Opciones de cálculo
        options_frame = tk.LabelFrame(cuotas_frame, text="Opciones de Cálculo Masivo", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Parámetros globales
        tk.Label(options_frame, text="Tipo de Préstamo:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.tipo_masivo_combo = ttk.Combobox(
            options_frame,
            values=["QUIROGRAFARIO", "HIPOTECARIO", "EMERGENCIA", "TODOS"],
            state='readonly',
            width=15
        )
        self.tipo_masivo_combo.grid(row=0, column=1, padx=5, pady=5)
        self.tipo_masivo_combo.set("TODOS")

        # Nueva tasa de interés
        tk.Label(options_frame, text="Nueva Tasa (%):", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.nueva_tasa_entry = tk.Entry(options_frame, width=10)
        self.nueva_tasa_entry.grid(row=0, column=3, padx=5, pady=5)
        self.nueva_tasa_entry.insert(0, "15.30")

        # Fecha de aplicación
        tk.Label(options_frame, text="Fecha Aplicación:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.fecha_aplicacion_entry = tk.Entry(options_frame, width=12)
        self.fecha_aplicacion_entry.grid(row=1, column=1, padx=5, pady=5)
        self.fecha_aplicacion_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Botón calcular
        tk.Button(
            options_frame,
            text="🔄 Recalcular Cuotas Masivamente",
            command=self.recalcular_cuotas_masivo,
            bg='#4299e1',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=2, column=0, columnspan=4, pady=15)

        # Resultados
        results_frame = tk.LabelFrame(cuotas_frame, text="Resultados del Recálculo", font=('Arial', 11, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para resultados
        columns = ('empleado', 'tipo', 'monto', 'plazo', 'tasa_anterior', 'cuota_anterior', 'tasa_nueva', 'cuota_nueva', 'diferencia')
        self.cuotas_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        headings = ['Empleado', 'Tipo', 'Monto', 'Plazo', 'Tasa Ant.', 'Cuota Ant.', 'Tasa Nueva', 'Cuota Nueva', 'Diferencia']
        for col, heading in zip(columns, headings):
            self.cuotas_tree.heading(col, text=heading)
            self.cuotas_tree.column(col, width=100)

        # Scrollbar
        cuotas_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.cuotas_tree.yview)
        self.cuotas_tree.configure(yscrollcommand=cuotas_scroll.set)

        self.cuotas_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        cuotas_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_proyeccion_pagos_tab(self, parent):
        """Crear pestaña de proyección de pagos"""
        proyeccion_frame = ttk.Frame(parent)
        parent.add(proyeccion_frame, text="Proyección de Pagos")

        # Opciones de proyección
        options_frame = tk.LabelFrame(proyeccion_frame, text="Parámetros de Proyección", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Período de proyección
        tk.Label(options_frame, text="Proyectar hasta:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.proyeccion_meses_combo = ttk.Combobox(
            options_frame,
            values=["6 meses", "12 meses", "24 meses", "36 meses"],
            state='readonly',
            width=10
        )
        self.proyeccion_meses_combo.grid(row=0, column=1, padx=5, pady=5)
        self.proyeccion_meses_combo.set("12 meses")

        # Estado de préstamos
        tk.Label(options_frame, text="Estado:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.estado_proyeccion_combo = ttk.Combobox(
            options_frame,
            values=["ACTIVO", "TODOS"],
            state='readonly',
            width=10
        )
        self.estado_proyeccion_combo.grid(row=0, column=3, padx=5, pady=5)
        self.estado_proyeccion_combo.set("ACTIVO")

        # Botón proyectar
        tk.Button(
            options_frame,
            text="📈 Generar Proyección de Pagos",
            command=self.generar_proyeccion_pagos,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=1, column=0, columnspan=4, pady=15)

        # Resultados de proyección
        results_frame = tk.LabelFrame(proyeccion_frame, text="Proyección de Flujo de Pagos", font=('Arial', 11, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para proyección
        columns = ('mes_ano', 'total_cuotas', 'total_capital', 'total_interes', 'total_recaudacion', 'prestamos_activos')
        self.proyeccion_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        headings = ['Mes/Año', 'Total Cuotas', 'Capital', 'Interés', 'Recaudación', 'Préstamos Activos']
        for col, heading in zip(columns, headings):
            self.proyeccion_tree.heading(col, text=heading)
            self.proyeccion_tree.column(col, width=120)

        # Scrollbar
        proy_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.proyeccion_tree.yview)
        self.proyeccion_tree.configure(yscrollcommand=proy_scroll.set)

        self.proyeccion_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        proy_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_reestructuracion_tab(self, parent):
        """Crear pestaña de reestructuración masiva"""
        reestructura_frame = ttk.Frame(parent)
        parent.add(reestructura_frame, text="Reestructuración Masiva")

        # Opciones de reestructuración
        options_frame = tk.LabelFrame(reestructura_frame, text="Parámetros de Reestructuración", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Criterios de selección
        tk.Label(options_frame, text="Reestructurar préstamos:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.criterio_reestructura_combo = ttk.Combobox(
            options_frame,
            values=["CON MORA > 30 DÍAS", "CON MORA > 60 DÍAS", "CUOTA > 40% SUELDO", "TODOS ACTIVOS"],
            state='readonly',
            width=20
        )
        self.criterio_reestructura_combo.grid(row=0, column=1, padx=5, pady=5)
        self.criterio_reestructura_combo.set("CUOTA > 40% SUELDO")

        # Nuevo plazo
        tk.Label(options_frame, text="Nuevo Plazo (meses):", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.nuevo_plazo_entry = tk.Entry(options_frame, width=10)
        self.nuevo_plazo_entry.grid(row=1, column=1, padx=5, pady=5)
        self.nuevo_plazo_entry.insert(0, "60")

        # Nueva tasa
        tk.Label(options_frame, text="Nueva Tasa (%):", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)
        self.nueva_tasa_reestr_entry = tk.Entry(options_frame, width=10)
        self.nueva_tasa_reestr_entry.grid(row=1, column=3, padx=5, pady=5)
        self.nueva_tasa_reestr_entry.insert(0, "12.50")

        # Botón reestructurar
        tk.Button(
            options_frame,
            text="🔄 Reestructurar Préstamos Masivamente",
            command=self.reestructurar_prestamos_masivo,
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=2, column=0, columnspan=4, pady=15)

        # Resultados de reestructuración
        results_frame = tk.LabelFrame(reestructura_frame, text="Resultados de Reestructuración", font=('Arial', 11, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.reestructura_text = tk.Text(results_frame, font=('Courier', 9))
        reestr_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.reestructura_text.yview)
        self.reestructura_text.configure(yscrollcommand=reestr_scroll.set)

        self.reestructura_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        reestr_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def recalcular_cuotas_masivo(self):
        """Recalcular cuotas masivamente"""
        try:
            dialog = show_loading_dialog(self, "Calculando", "Recalculando cuotas de préstamos...")

            # Limpiar resultados anteriores
            for item in self.cuotas_tree.get_children():
                self.cuotas_tree.delete(item)

            # Obtener parámetros
            tipo_prestamo = self.tipo_masivo_combo.get()
            nueva_tasa = float(self.nueva_tasa_entry.get())
            fecha_aplicacion = self.fecha_aplicacion_entry.get()

            # Obtener empleados (simular préstamos)
            empleados = self.session.query(Empleado).filter_by(activo=True).all()

            count = 0
            total_diferencia = 0

            for emp in empleados:
                # Simular datos de préstamo existente
                monto = float(emp.sueldo or 0) * 5  # 5 veces el sueldo
                plazo = 36
                tasa_anterior = 15.30
                tipo = "QUIROGRAFARIO"

                # Calcular cuota anterior
                tasa_mensual_ant = tasa_anterior / 100 / 12
                cuota_anterior = monto * (tasa_mensual_ant * (1 + tasa_mensual_ant) ** plazo) / ((1 + tasa_mensual_ant) ** plazo - 1)

                # Calcular nueva cuota
                tasa_mensual_nueva = nueva_tasa / 100 / 12
                cuota_nueva = monto * (tasa_mensual_nueva * (1 + tasa_mensual_nueva) ** plazo) / ((1 + tasa_mensual_nueva) ** plazo - 1)

                diferencia = cuota_nueva - cuota_anterior
                total_diferencia += diferencia

                self.cuotas_tree.insert('', 'end', values=(
                    f"{emp.empleado} - {emp.nombres}",
                    tipo,
                    f"${monto:.2f}",
                    f"{plazo} meses",
                    f"{tasa_anterior:.2f}%",
                    f"${cuota_anterior:.2f}",
                    f"{nueva_tasa:.2f}%",
                    f"${cuota_nueva:.2f}",
                    f"${diferencia:.2f}"
                ))
                count += 1

            dialog.close()
            show_toast(self, f"✅ {count} cuotas recalculadas - Diferencia total: ${total_diferencia:.2f}", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error recalculando cuotas: {str(e)}")

    def generar_proyeccion_pagos(self):
        """Generar proyección de pagos"""
        try:
            dialog = show_loading_dialog(self, "Generando", "Creando proyección de pagos...")

            # Limpiar resultados anteriores
            for item in self.proyeccion_tree.get_children():
                self.proyeccion_tree.delete(item)

            # Obtener parámetros
            meses_proyeccion = int(self.proyeccion_meses_combo.get().split()[0])
            estado = self.estado_proyeccion_combo.get()

            # Generar proyección mes a mes
            fecha_actual = date.today()
            empleados_activos = self.session.query(Empleado).filter_by(activo=True).count()

            for i in range(meses_proyeccion):
                # Calcular fecha del mes
                if fecha_actual.month + i <= 12:
                    mes = fecha_actual.month + i
                    ano = fecha_actual.year
                else:
                    mes = (fecha_actual.month + i) % 12
                    if mes == 0:
                        mes = 12
                    ano = fecha_actual.year + ((fecha_actual.month + i - 1) // 12)

                mes_ano = f"{mes:02d}/{ano}"

                # Simular cálculos
                total_cuotas = empleados_activos * 0.7  # 70% tiene préstamos
                promedio_cuota = 250  # Promedio por cuota
                total_recaudacion = total_cuotas * promedio_cuota
                total_capital = total_recaudacion * 0.75  # 75% capital
                total_interes = total_recaudacion * 0.25  # 25% interés
                prestamos_activos = int(total_cuotas)

                self.proyeccion_tree.insert('', 'end', values=(
                    mes_ano,
                    int(total_cuotas),
                    f"${total_capital:.2f}",
                    f"${total_interes:.2f}",
                    f"${total_recaudacion:.2f}",
                    prestamos_activos
                ))

            dialog.close()
            show_toast(self, f"✅ Proyección generada para {meses_proyeccion} meses", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error generando proyección: {str(e)}")

    def reestructurar_prestamos_masivo(self):
        """Reestructurar préstamos masivamente"""
        try:
            criterio = self.criterio_reestructura_combo.get()
            nuevo_plazo = int(self.nuevo_plazo_entry.get())
            nueva_tasa = float(self.nueva_tasa_reestr_entry.get())

            # Confirmación
            if not messagebox.askyesno("Confirmar", f"¿Reestructurar préstamos según criterio: {criterio}?"):
                return

            dialog = show_loading_dialog(self, "Reestructurando", "Procesando reestructuración...")

            # Simular reestructuración
            resultados = []
            resultados.append("=== REESTRUCTURACIÓN MASIVA DE PRÉSTAMOS ===")
            resultados.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            resultados.append(f"Criterio: {criterio}")
            resultados.append(f"Nuevo Plazo: {nuevo_plazo} meses")
            resultados.append(f"Nueva Tasa: {nueva_tasa}%")
            resultados.append("")

            empleados = self.session.query(Empleado).filter_by(activo=True).limit(10).all()
            total_reestructurados = 0
            total_reduccion = 0

            for emp in empleados:
                # Simular cálculo de reestructuración
                monto_actual = float(emp.sueldo or 0) * 5
                plazo_actual = 36
                tasa_actual = 15.30

                # Cuota actual
                tasa_mes_actual = tasa_actual / 100 / 12
                cuota_actual = monto_actual * (tasa_mes_actual * (1 + tasa_mes_actual) ** plazo_actual) / ((1 + tasa_mes_actual) ** plazo_actual - 1)

                # Nueva cuota
                tasa_mes_nueva = nueva_tasa / 100 / 12
                cuota_nueva = monto_actual * (tasa_mes_nueva * (1 + tasa_mes_nueva) ** nuevo_plazo) / ((1 + tasa_mes_nueva) ** nuevo_plazo - 1)

                reduccion = cuota_actual - cuota_nueva
                total_reduccion += reduccion

                resultados.append(f"{emp.empleado} - {emp.nombres}:")
                resultados.append(f"  Cuota actual: ${cuota_actual:.2f} -> Nueva cuota: ${cuota_nueva:.2f}")
                resultados.append(f"  Reducción: ${reduccion:.2f} ({(reduccion/cuota_actual*100):.1f}%)")
                resultados.append("")

                total_reestructurados += 1

            resultados.append("=== RESUMEN ===")
            resultados.append(f"Préstamos reestructurados: {total_reestructurados}")
            resultados.append(f"Reducción total mensual: ${total_reduccion:.2f}")
            resultados.append(f"Reducción promedio: ${total_reduccion/total_reestructurados:.2f}")

            # Mostrar resultados
            self.reestructura_text.delete(1.0, tk.END)
            self.reestructura_text.insert(tk.END, "\n".join(resultados))

            dialog.close()
            show_toast(self, f"✅ {total_reestructurados} préstamos reestructurados", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error en reestructuración: {str(e)}")

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