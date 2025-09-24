#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Vacaciones Completo - Sistema SGN
Gestión de vacaciones según normativa ecuatoriana
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta
from decimal import Decimal
import calendar
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

class VacacionesCompleteModule(tk.Frame):
    """Módulo completo de vacaciones"""

    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables
        self.selected_employee = None
        self.selected_period = None
        self.solicitud_tipo_var = tk.StringVar(value="programada")

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
            text="GESTIÓN DE VACACIONES",
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
        self.create_solicitudes_tab()
        self.create_calendario_tab()
        self.create_liquidacion_tab()
        self.create_reportes_tab()

    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = tk.Frame(self, bg='#e2e8f0', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=2)
        toolbar.pack_propagate(False)

        # Botones principales
        buttons = [
            ("Nueva Solicitud", self.new_request, '#4299e1'),
            ("📊 Carga Masiva", self.carga_masiva_vacaciones, '#38a169'),
            ("⚡ Proceso Masivo", self.proceso_masivo_vacaciones, '#805ad5'),
            ("Aprobar", self.approve_request, '#48bb78'),
            ("Liquidar", self.liquidate_vacation, '#ed8936'),
            ("Calendario", self.show_calendar, '#9f7aea'),
            ("📥 Descargar BD", self.descargar_bd, '#e53e3e'),
            ("Reportes", self.generate_reports, '#ed8936')
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

    def create_solicitudes_tab(self):
        """Crear pestaña de solicitudes de vacaciones"""
        solicitudes_frame = ttk.Frame(self.notebook)
        self.notebook.add(solicitudes_frame, text="Solicitudes")

        # Panel superior - Formulario de solicitud
        form_frame = tk.LabelFrame(solicitudes_frame, text="Nueva Solicitud de Vacaciones", font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        # Grid del formulario
        form_grid = tk.Frame(form_frame)
        form_grid.pack(padx=10, pady=10)

        # Empleado
        tk.Label(form_grid, text="Empleado:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.emp_combo = ttk.Combobox(form_grid, state='readonly', width=30)
        self.emp_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.emp_combo.bind('<<ComboboxSelected>>', self.on_employee_selected)

        # Período vacacional
        tk.Label(form_grid, text="Período:", font=('Arial', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=2)
        self.period_combo = ttk.Combobox(form_grid, state='readonly', width=15)
        self.period_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        # Tipo de solicitud
        tk.Label(form_grid, text="Tipo:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        tipo_frame = tk.Frame(form_grid)
        tipo_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Radiobutton(
            tipo_frame,
            text="Programada",
            variable=self.solicitud_tipo_var,
            value="programada",
            font=('Arial', 8)
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            tipo_frame,
            text="Emergencia",
            variable=self.solicitud_tipo_var,
            value="emergencia",
            font=('Arial', 8)
        ).pack(side=tk.LEFT, padx=10)

        # Fechas
        tk.Label(form_grid, text="Fecha Inicio:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.fecha_inicio_entry = tk.Entry(form_grid, width=12)
        self.fecha_inicio_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.fecha_inicio_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        tk.Label(form_grid, text="Días:", font=('Arial', 9, 'bold')).grid(row=2, column=2, sticky=tk.W, padx=10, pady=2)
        self.dias_entry = tk.Entry(form_grid, width=5)
        self.dias_entry.grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)
        self.dias_entry.bind('<KeyRelease>', self.calculate_end_date)

        tk.Label(form_grid, text="Fecha Fin:", font=('Arial', 9, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.fecha_fin_label = tk.Label(form_grid, text="", font=('Arial', 9), relief=tk.SUNKEN, width=12)
        self.fecha_fin_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        # Observaciones
        tk.Label(form_grid, text="Observaciones:", font=('Arial', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=2)
        self.obs_text = tk.Text(form_grid, width=50, height=3)
        self.obs_text.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)

        # Botones del formulario
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Guardar Solicitud",
            command=self.save_request,
            bg='#48bb78',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Limpiar",
            command=self.clear_form,
            bg='#ed8936',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        # Panel inferior - Lista de solicitudes
        self.create_requests_list(solicitudes_frame)

    def create_requests_list(self, parent):
        """Crear lista de solicitudes"""
        list_frame = tk.LabelFrame(parent, text="Solicitudes Registradas", font=('Arial', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para solicitudes
        columns = ('codigo', 'empleado', 'periodo', 'tipo', 'fecha_inicio', 'dias', 'fecha_fin', 'estado')
        self.requests_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        # Configurar columnas
        headings = ['Código', 'Empleado', 'Período', 'Tipo', 'F. Inicio', 'Días', 'F. Fin', 'Estado']
        widths = [80, 180, 80, 80, 80, 50, 80, 80]

        for col, heading, width in zip(columns, headings, widths):
            self.requests_tree.heading(col, text=heading)
            self.requests_tree.column(col, width=width)

        # Scrollbars
        req_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.requests_tree.yview)
        req_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.requests_tree.xview)

        self.requests_tree.configure(yscrollcommand=req_scroll_y.set, xscrollcommand=req_scroll_x.set)

        # Pack
        self.requests_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        req_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        req_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar solicitudes de ejemplo
        self.load_sample_requests()

        # Bind events
        self.requests_tree.bind('<Double-1>', self.edit_request)

    def create_calendario_tab(self):
        """Crear pestaña de calendario"""
        calendario_frame = ttk.Frame(self.notebook)
        self.notebook.add(calendario_frame, text="Calendario")

        # Controles del calendario
        controls_frame = tk.Frame(calendario_frame, bg='white')
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(controls_frame, text="Mes/Año:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT, padx=5)

        self.cal_month_var = tk.StringVar(value=str(date.today().month))
        month_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.cal_month_var,
            values=[str(i) for i in range(1, 13)],
            state='readonly',
            width=5
        )
        month_combo.pack(side=tk.LEFT, padx=5)

        self.cal_year_var = tk.StringVar(value=str(date.today().year))
        year_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.cal_year_var,
            values=[str(year) for year in range(2020, 2030)],
            state='readonly',
            width=8
        )
        year_combo.pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls_frame,
            text="Actualizar",
            command=self.update_calendar,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=10)

        # Calendario visual
        self.create_calendar_view(calendario_frame)

    def create_calendar_view(self, parent):
        """Crear vista de calendario"""
        cal_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        cal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Header del calendario
        header_frame = tk.Frame(cal_frame, bg='#2c5282', height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for i, day in enumerate(days):
            tk.Label(
                header_frame,
                text=day,
                bg='#2c5282',
                fg='white',
                font=('Arial', 10, 'bold')
            ).grid(row=0, column=i, sticky='nsew')
            header_frame.grid_columnconfigure(i, weight=1)

        # Grid del calendario
        self.calendar_grid = tk.Frame(cal_frame, bg='white')
        self.calendar_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_calendar()

    def create_liquidacion_tab(self):
        """Crear pestaña de liquidación de vacaciones"""
        liquidacion_frame = ttk.Frame(self.notebook)
        self.notebook.add(liquidacion_frame, text="Liquidación")

        # Panel de información del empleado
        emp_info_frame = tk.LabelFrame(liquidacion_frame, text="Información del Empleado", font=('Arial', 10, 'bold'))
        emp_info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_grid = tk.Frame(emp_info_frame)
        info_grid.pack(padx=10, pady=10)

        # Selección de empleado para liquidación
        tk.Label(info_grid, text="Empleado:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.liq_emp_combo = ttk.Combobox(info_grid, state='readonly', width=30)
        self.liq_emp_combo.grid(row=0, column=1, padx=5)
        self.liq_emp_combo.bind('<<ComboboxSelected>>', self.load_employee_vacation_info)

        # Información de vacaciones
        info_labels = [
            "Fecha Ingreso:",
            "Tiempo Trabajado:",
            "Días Acumulados:",
            "Días Tomados:",
            "Días Pendientes:",
            "Valor por Día:",
            "Total a Liquidar:"
        ]

        self.liq_info_labels = {}
        for i, label in enumerate(info_labels, start=1):
            tk.Label(info_grid, text=label, font=('Arial', 9)).grid(row=i, column=0, sticky=tk.W, pady=2)
            value_label = tk.Label(info_grid, text="", font=('Arial', 9), relief=tk.SUNKEN, width=20)
            value_label.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self.liq_info_labels[label] = value_label

        # Panel de cálculo
        calc_frame = tk.LabelFrame(liquidacion_frame, text="Cálculo de Liquidación", font=('Arial', 10, 'bold'))
        calc_frame.pack(fill=tk.X, padx=10, pady=5)

        calc_grid = tk.Frame(calc_frame)
        calc_grid.pack(padx=10, pady=10)

        tk.Label(calc_grid, text="Días a Liquidar:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.dias_liquidar_entry = tk.Entry(calc_grid, width=10)
        self.dias_liquidar_entry.grid(row=0, column=1, padx=5)
        self.dias_liquidar_entry.bind('<KeyRelease>', self.calculate_liquidation)

        tk.Label(calc_grid, text="Motivo:", font=('Arial', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10)
        self.motivo_combo = ttk.Combobox(
            calc_grid,
            values=["Renuncia", "Despido", "Fin de Contrato", "Jubilación"],
            state='readonly',
            width=15
        )
        self.motivo_combo.grid(row=0, column=3, padx=5)

        # Botón de liquidación
        tk.Button(
            calc_frame,
            text="Procesar Liquidación",
            command=self.process_liquidation,
            bg='#e53e3e',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        ).pack(pady=10)

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

        self.report_type_var = tk.StringVar(value="pendientes")
        report_types = [
            ("Vacaciones Pendientes", "pendientes"),
            ("Solicitudes por Período", "periodo"),
            ("Calendario de Vacaciones", "calendario"),
            ("Liquidaciones", "liquidaciones")
        ]

        for i, (text, value) in enumerate(report_types):
            tk.Radiobutton(
                options_grid,
                text=text,
                variable=self.report_type_var,
                value=value,
                font=('Arial', 9)
            ).grid(row=i+1, column=0, sticky=tk.W)

        # Filtros
        filter_frame = tk.Frame(options_grid)
        filter_frame.grid(row=0, column=1, rowspan=5, sticky=tk.N, padx=20)

        tk.Label(filter_frame, text="Filtros:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        tk.Label(filter_frame, text="Departamento:", font=('Arial', 9)).pack(anchor=tk.W)
        self.rep_dept_combo = ttk.Combobox(filter_frame, state='readonly', width=20)
        self.rep_dept_combo.pack(anchor=tk.W, pady=2)

        tk.Label(filter_frame, text="Período:", font=('Arial', 9)).pack(anchor=tk.W, pady=(10,0))
        self.rep_period_combo = ttk.Combobox(filter_frame, state='readonly', width=20)
        self.rep_period_combo.pack(anchor=tk.W, pady=2)

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

    def load_employees(self):
        """Cargar empleados en combos"""
        try:
            empleados = self.session.query(Empleado).filter_by(activo=True).all()
            emp_values = [f"{emp.empleado} - {emp.nombres} {emp.apellidos}" for emp in empleados]

            # Actualizar combos
            self.emp_combo['values'] = emp_values
            self.liq_emp_combo['values'] = emp_values

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando empleados: {str(e)}")

    def on_employee_selected(self, event):
        """Manejar selección de empleado"""
        selected = self.emp_combo.get()
        if selected:
            codigo = selected.split(' - ')[0]
            self.load_employee_periods(codigo)

    def load_employee_periods(self, codigo_empleado):
        """Cargar períodos vacacionales del empleado"""
        try:
            empleado = self.session.query(Empleado).filter_by(empleado=codigo_empleado).first()
            if empleado and empleado.fecha_ing:
                # Calcular períodos desde fecha de ingreso
                fecha_ing = empleado.fecha_ing
                current_date = date.today()

                periods = []
                year = fecha_ing.year
                while year <= current_date.year:
                    if year == fecha_ing.year:
                        period_start = fecha_ing
                    else:
                        period_start = date(year, fecha_ing.month, fecha_ing.day)

                    if year < current_date.year:
                        period_end = date(year + 1, fecha_ing.month, fecha_ing.day) - timedelta(days=1)
                    else:
                        period_end = current_date

                    periods.append(f"{period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}")
                    year += 1

                self.period_combo['values'] = periods

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando períodos: {str(e)}")

    def calculate_end_date(self, event):
        """Calcular fecha fin basada en días"""
        try:
            dias = int(self.dias_entry.get() or 0)
            fecha_inicio_str = self.fecha_inicio_entry.get()

            if dias > 0 and fecha_inicio_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%d/%m/%Y').date()
                fecha_fin = fecha_inicio + timedelta(days=dias - 1)
                self.fecha_fin_label.config(text=fecha_fin.strftime('%d/%m/%Y'))
            else:
                self.fecha_fin_label.config(text="")
        except:
            self.fecha_fin_label.config(text="")

    def update_calendar(self):
        """Actualizar vista de calendario"""
        try:
            # Limpiar grid
            for widget in self.calendar_grid.winfo_children():
                widget.destroy()

            month = int(self.cal_month_var.get())
            year = int(self.cal_year_var.get())

            # Obtener calendario del mes
            cal = calendar.monthcalendar(year, month)

            # Crear grid de días
            for week_num, week in enumerate(cal):
                for day_num, day in enumerate(week):
                    if day == 0:
                        # Día vacío
                        cell = tk.Frame(self.calendar_grid, bg='#f5f5f5', relief=tk.RAISED, bd=1)
                    else:
                        # Día con número
                        cell = tk.Frame(self.calendar_grid, bg='white', relief=tk.RAISED, bd=1)
                        day_label = tk.Label(cell, text=str(day), font=('Arial', 10))
                        day_label.pack(anchor=tk.NW, padx=2, pady=2)

                        # Verificar si hay vacaciones este día
                        if self.has_vacation_on_date(year, month, day):
                            status_label = tk.Label(cell, text="V", fg='red', font=('Arial', 8, 'bold'))
                            status_label.pack(anchor=tk.SE, padx=2, pady=2)

                    cell.grid(row=week_num, column=day_num, sticky='nsew', padx=1, pady=1)
                    self.calendar_grid.grid_columnconfigure(day_num, weight=1)

                self.calendar_grid.grid_rowconfigure(week_num, weight=1)

        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando calendario: {str(e)}")

    def has_vacation_on_date(self, year, month, day):
        """Verificar si hay vacaciones en una fecha específica"""
        # Placeholder - aquí iría la lógica para verificar vacaciones
        return False

    def load_sample_requests(self):
        """Cargar solicitudes de ejemplo"""
        sample_requests = [
            ("VAC001", "001001 - Juan Perez", "2024-2025", "Programada", "15/01/2024", "15", "29/01/2024", "Aprobada"),
            ("VAC002", "001002 - Maria Gonzalez", "2024-2025", "Emergencia", "10/02/2024", "5", "14/02/2024", "Pendiente"),
            ("VAC003", "001003 - Carlos Rodriguez", "2023-2024", "Programada", "20/12/2023", "10", "29/12/2023", "Liquidada"),
        ]

        for request in sample_requests:
            self.requests_tree.insert('', 'end', values=request)

    def load_employee_vacation_info(self, event):
        """Cargar información de vacaciones del empleado"""
        selected = self.liq_emp_combo.get()
        if selected:
            codigo = selected.split(' - ')[0]

            # Placeholder - aquí iría la lógica real
            self.liq_info_labels["Fecha Ingreso:"].config(text="15/01/2020")
            self.liq_info_labels["Tiempo Trabajado:"].config(text="4 años, 2 meses")
            self.liq_info_labels["Días Acumulados:"].config(text="60 días")
            self.liq_info_labels["Días Tomados:"].config(text="30 días")
            self.liq_info_labels["Días Pendientes:"].config(text="30 días")
            self.liq_info_labels["Valor por Día:"].config(text="$16.67")
            self.liq_info_labels["Total a Liquidar:"].config(text="$500.00")

    def calculate_liquidation(self, event):
        """Calcular liquidación"""
        try:
            dias = int(self.dias_liquidar_entry.get() or 0)
            valor_dia = 16.67  # Placeholder
            total = dias * valor_dia
            self.liq_info_labels["Total a Liquidar:"].config(text=f"${total:.2f}")
        except:
            pass

    # Métodos de eventos
    def new_request(self):
        """Nueva solicitud"""
        self.notebook.select(0)  # Ir a pestaña de solicitudes

    def approve_request(self):
        """Aprobar solicitud"""
        selection = self.requests_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Solicitud aprobada exitosamente")
        else:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")

    def liquidate_vacation(self):
        """Liquidar vacaciones"""
        self.notebook.select(2)  # Ir a pestaña de liquidación

    def show_calendar(self):
        """Mostrar calendario"""
        self.notebook.select(1)  # Ir a pestaña de calendario

    def generate_reports(self):
        """Generar reportes"""
        self.notebook.select(3)  # Ir a pestaña de reportes

    def save_request(self):
        """Guardar solicitud"""
        if not self.emp_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un empleado")
            return

        if not self.dias_entry.get():
            messagebox.showwarning("Advertencia", "Ingrese el número de días")
            return

        messagebox.showinfo("Éxito", "Solicitud guardada exitosamente")
        self.clear_form()

    def clear_form(self):
        """Limpiar formulario"""
        self.emp_combo.set("")
        self.period_combo.set("")
        self.fecha_inicio_entry.delete(0, tk.END)
        self.fecha_inicio_entry.insert(0, date.today().strftime('%d/%m/%Y'))
        self.dias_entry.delete(0, tk.END)
        self.fecha_fin_label.config(text="")
        self.obs_text.delete(1.0, tk.END)

    def edit_request(self, event):
        """Editar solicitud"""
        selection = self.requests_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Función de edición en desarrollo")

    def process_liquidation(self):
        """Procesar liquidación"""
        if not self.liq_emp_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un empleado")
            return

        if not self.dias_liquidar_entry.get():
            messagebox.showwarning("Advertencia", "Ingrese los días a liquidar")
            return

        messagebox.showinfo("Éxito", "Liquidación procesada exitosamente")

    def preview_report(self):
        """Vista previa del reporte"""
        messagebox.showinfo("Información", "Vista previa en desarrollo")

    def generate_pdf(self):
        """Generar PDF"""
        messagebox.showinfo("Información", "Generación de PDF en desarrollo")

    def export_excel(self):
        """Exportar a Excel"""
        messagebox.showinfo("Información", "Exportación a Excel en desarrollo")

    def carga_masiva_vacaciones(self):
        """Carga masiva de solicitudes de vacaciones"""
        try:
            columns_mapping = {
                'codigo_empleado': 'empleado',
                'periodo': 'periodo',
                'tipo_solicitud': 'tipo',
                'fecha_inicio': 'fecha_inicio',
                'dias_solicitados': 'dias',
                'fecha_fin': 'fecha_fin',
                'observaciones': 'observaciones',
                'estado': 'estado'
            }

            carga_masiva = CargaMasivaComponent(
                parent=self,
                session=self.session,
                entity_type="vacaciones",
                columns_mapping=columns_mapping
            )

            show_toast(self, "Carga masiva de vacaciones iniciada", "info")

        except Exception as e:
            messagebox.showerror("Error", f"Error en carga masiva: {str(e)}")

    def proceso_masivo_vacaciones(self):
        """Procesamiento masivo de vacaciones"""
        try:
            # Crear ventana de proceso masivo
            proceso_window = tk.Toplevel(self)
            proceso_window.title("Procesamiento Masivo de Vacaciones")
            proceso_window.geometry("800x600")
            proceso_window.transient(self)
            proceso_window.grab_set()

            # Header
            header_frame = tk.Frame(proceso_window, bg='#2c5282', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)

            tk.Label(
                header_frame,
                text="⚡ PROCESAMIENTO MASIVO DE VACACIONES",
                font=('Arial', 16, 'bold'),
                bg='#2c5282',
                fg='white'
            ).pack(pady=15)

            # Notebook para opciones
            notebook = ttk.Notebook(proceso_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Pestaña 1: Cálculo masivo de saldos
            self.create_calculo_saldos_tab(notebook)

            # Pestaña 2: Aprobación masiva
            self.create_aprobacion_masiva_tab(notebook)

            # Pestaña 3: Liquidación masiva
            self.create_liquidacion_masiva_tab(notebook)

        except Exception as e:
            messagebox.showerror("Error", f"Error en procesamiento masivo: {str(e)}")

    def create_calculo_saldos_tab(self, parent):
        """Crear pestaña de cálculo masivo de saldos"""
        saldos_frame = ttk.Frame(parent)
        parent.add(saldos_frame, text="Cálculo de Saldos")

        # Opciones de cálculo
        options_frame = tk.LabelFrame(saldos_frame, text="Opciones de Cálculo", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Período
        tk.Label(options_frame, text="Período:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.periodo_saldos_combo = ttk.Combobox(
            options_frame,
            values=[str(year) for year in range(2020, 2030)],
            state='readonly',
            width=10
        )
        self.periodo_saldos_combo.grid(row=0, column=1, padx=5, pady=5)
        self.periodo_saldos_combo.set(str(date.today().year))

        # Departamento
        tk.Label(options_frame, text="Departamento:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.dept_saldos_combo = ttk.Combobox(options_frame, state='readonly', width=20)
        self.dept_saldos_combo.grid(row=0, column=3, padx=5, pady=5)

        # Cargar departamentos
        departamentos = self.session.query(Departamento).filter_by(activo=True).all()
        dept_values = ["TODOS"] + [dept.nombre_codigo for dept in departamentos]
        self.dept_saldos_combo['values'] = dept_values
        self.dept_saldos_combo.set("TODOS")

        # Botón calcular
        tk.Button(
            options_frame,
            text="🔄 Calcular Saldos Masivamente",
            command=self.calcular_saldos_masivo,
            bg='#4299e1',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=1, column=0, columnspan=4, pady=15)

        # Resultados
        results_frame = tk.LabelFrame(saldos_frame, text="Resultados", font=('Arial', 11, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para resultados
        columns = ('empleado', 'periodo_ant', 'dias_acum', 'dias_tomados', 'saldo_actual', 'estado')
        self.saldos_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        headings = ['Empleado', 'Período Anterior', 'Días Acumulados', 'Días Tomados', 'Saldo Actual', 'Estado']
        for col, heading in zip(columns, headings):
            self.saldos_tree.heading(col, text=heading)
            self.saldos_tree.column(col, width=120)

        # Scrollbar
        saldos_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.saldos_tree.yview)
        self.saldos_tree.configure(yscrollcommand=saldos_scroll.set)

        self.saldos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        saldos_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_aprobacion_masiva_tab(self, parent):
        """Crear pestaña de aprobación masiva"""
        aprobacion_frame = ttk.Frame(parent)
        parent.add(aprobacion_frame, text="Aprobación Masiva")

        # Filtros
        filter_frame = tk.LabelFrame(aprobacion_frame, text="Filtros para Aprobación", font=('Arial', 11, 'bold'))
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # Estado actual
        tk.Label(filter_frame, text="Estado Actual:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.estado_actual_combo = ttk.Combobox(
            filter_frame,
            values=["PENDIENTE", "REVISION", "OBSERVADA"],
            state='readonly',
            width=15
        )
        self.estado_actual_combo.grid(row=0, column=1, padx=5, pady=5)
        self.estado_actual_combo.set("PENDIENTE")

        # Nuevo estado
        tk.Label(filter_frame, text="Nuevo Estado:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.nuevo_estado_combo = ttk.Combobox(
            filter_frame,
            values=["APROBADA", "RECHAZADA", "OBSERVADA"],
            state='readonly',
            width=15
        )
        self.nuevo_estado_combo.grid(row=0, column=3, padx=5, pady=5)
        self.nuevo_estado_combo.set("APROBADA")

        # Botón procesar
        tk.Button(
            filter_frame,
            text="✅ Procesar Aprobaciones Masivas",
            command=self.procesar_aprobacion_masiva,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=1, column=0, columnspan=4, pady=15)

        # Lista de solicitudes
        solicitudes_frame = tk.LabelFrame(aprobacion_frame, text="Solicitudes a Procesar", font=('Arial', 11, 'bold'))
        solicitudes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview
        columns = ('seleccionar', 'empleado', 'tipo', 'fecha_inicio', 'dias', 'estado_actual')
        self.aprobacion_tree = ttk.Treeview(solicitudes_frame, columns=columns, show='headings')

        headings = ['☑', 'Empleado', 'Tipo', 'Fecha Inicio', 'Días', 'Estado']
        for col, heading in zip(columns, headings):
            self.aprobacion_tree.heading(col, text=heading)
            self.aprobacion_tree.column(col, width=100)

        # Scrollbar
        aprob_scroll = ttk.Scrollbar(solicitudes_frame, orient=tk.VERTICAL, command=self.aprobacion_tree.yview)
        self.aprobacion_tree.configure(yscrollcommand=aprob_scroll.set)

        self.aprobacion_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        aprob_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_liquidacion_masiva_tab(self, parent):
        """Crear pestaña de liquidación masiva"""
        liquidacion_frame = ttk.Frame(parent)
        parent.add(liquidacion_frame, text="Liquidación Masiva")

        # Opciones
        options_frame = tk.LabelFrame(liquidacion_frame, text="Opciones de Liquidación", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Motivo de liquidación
        tk.Label(options_frame, text="Motivo:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.motivo_liq_combo = ttk.Combobox(
            options_frame,
            values=["RENUNCIA", "DESPIDO", "FIN_CONTRATO", "JUBILACION"],
            state='readonly',
            width=15
        )
        self.motivo_liq_combo.grid(row=0, column=1, padx=5, pady=5)
        self.motivo_liq_combo.set("RENUNCIA")

        # Fecha de liquidación
        tk.Label(options_frame, text="Fecha Liquidación:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.fecha_liq_entry = tk.Entry(options_frame, width=12)
        self.fecha_liq_entry.grid(row=0, column=3, padx=5, pady=5)
        self.fecha_liq_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Botón procesar
        tk.Button(
            options_frame,
            text="💰 Procesar Liquidaciones Masivas",
            command=self.procesar_liquidacion_masiva,
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=1, column=0, columnspan=4, pady=15)

        # Resultados de liquidación
        resultados_frame = tk.LabelFrame(liquidacion_frame, text="Resultados de Liquidación", font=('Arial', 11, 'bold'))
        resultados_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.liquidacion_text = tk.Text(resultados_frame, font=('Courier', 9))
        liq_scroll = ttk.Scrollbar(resultados_frame, orient=tk.VERTICAL, command=self.liquidacion_text.yview)
        self.liquidacion_text.configure(yscrollcommand=liq_scroll.set)

        self.liquidacion_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        liq_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def calcular_saldos_masivo(self):
        """Calcular saldos de vacaciones masivamente"""
        try:
            dialog = show_loading_dialog(self, "Calculando Saldos", "Procesando saldos de vacaciones...")

            # Limpiar resultados anteriores
            for item in self.saldos_tree.get_children():
                self.saldos_tree.delete(item)

            # Obtener empleados según filtros
            empleados = self.session.query(Empleado).filter_by(activo=True).all()

            count = 0
            for emp in empleados:
                # Simular cálculo de saldos
                dias_acum = 30  # 30 días por año
                dias_tomados = 15  # Simulado
                saldo = dias_acum - dias_tomados

                self.saldos_tree.insert('', 'end', values=(
                    f"{emp.empleado} - {emp.nombres} {emp.apellidos}",
                    f"{date.today().year-1}",
                    dias_acum,
                    dias_tomados,
                    saldo,
                    "ACTUALIZADO"
                ))
                count += 1

            dialog.close()
            show_toast(self, f"✅ {count} saldos calculados exitosamente", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error calculando saldos: {str(e)}")

    def procesar_aprobacion_masiva(self):
        """Procesar aprobaciones masivas"""
        try:
            estado_actual = self.estado_actual_combo.get()
            nuevo_estado = self.nuevo_estado_combo.get()

            if not estado_actual or not nuevo_estado:
                messagebox.showwarning("Advertencia", "Seleccione estados válidos")
                return

            # Confirmación
            if not messagebox.askyesno("Confirmar", f"¿Cambiar todas las solicitudes de {estado_actual} a {nuevo_estado}?"):
                return

            dialog = show_loading_dialog(self, "Procesando", "Actualizando solicitudes...")

            # Simular procesamiento
            import time
            time.sleep(2)

            dialog.close()
            show_toast(self, "✅ Aprobaciones procesadas exitosamente", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error procesando aprobaciones: {str(e)}")

    def procesar_liquidacion_masiva(self):
        """Procesar liquidaciones masivas"""
        try:
            motivo = self.motivo_liq_combo.get()
            fecha_liq = self.fecha_liq_entry.get()

            if not motivo or not fecha_liq:
                messagebox.showwarning("Advertencia", "Complete todos los campos")
                return

            # Confirmación
            if not messagebox.askyesno("Confirmar", f"¿Procesar liquidaciones masivas por {motivo}?"):
                return

            dialog = show_loading_dialog(self, "Procesando", "Calculando liquidaciones...")

            # Simular cálculo
            resultados = []
            resultados.append("=== LIQUIDACIÓN MASIVA DE VACACIONES ===")
            resultados.append(f"Motivo: {motivo}")
            resultados.append(f"Fecha: {fecha_liq}")
            resultados.append("")

            empleados = self.session.query(Empleado).filter_by(activo=True).limit(10).all()
            total_liquidado = 0

            for emp in empleados:
                saldo_dias = 15  # Simulado
                valor_dia = float(emp.sueldo or 0) / 30
                total_emp = saldo_dias * valor_dia
                total_liquidado += total_emp

                resultados.append(f"{emp.empleado} - {emp.nombres}: {saldo_dias} días x ${valor_dia:.2f} = ${total_emp:.2f}")

            resultados.append("")
            resultados.append(f"TOTAL LIQUIDADO: ${total_liquidado:.2f}")

            # Mostrar resultados
            self.liquidacion_text.delete(1.0, tk.END)
            self.liquidacion_text.insert(tk.END, "\n".join(resultados))

            dialog.close()
            show_toast(self, f"✅ Liquidaciones procesadas: ${total_liquidado:.2f}", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error procesando liquidaciones: {str(e)}")

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
            '#805ad5': '#6b46c1'
        }
        return color_map.get(color, color)

    def __del__(self):
        """Destructor"""
        if hasattr(self, 'session') and hasattr(self.session, 'close'):
            self.session.close()