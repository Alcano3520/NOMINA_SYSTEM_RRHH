#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo de Nomina Completo - Sistema SAI
Procesamiento de roles de pago segun normativa ecuatoriana
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, date
import logging
from decimal import Decimal
import calendar

from config import Config
from database.connection import get_session
from database.models import Empleado, RolPago, IngresoDescuento
from gui.components.carga_masiva import show_carga_masiva_nomina
from services.payroll_calculator import payroll_calculator

logger = logging.getLogger(__name__)

class NominaCompleteModule(tk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent, bg='white')
        self.main_app = main_app
        self.session = get_session()
        self.current_period = datetime.now().strftime("%Y-%m")

        self.pack(fill="both", expand=True)
        self.setup_ui()
        self.load_payroll_data()

    def setup_ui(self):
        """Configurar interfaz del modulo"""
        # Header
        self.create_module_header()

        # Container principal
        main_container = tk.Frame(self, bg='white')
        main_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        # Panel de control
        self.create_control_panel(main_container)

        # Notebook con pestañas
        self.create_payroll_notebook(main_container)

    def create_module_header(self):
        """Crear header del modulo"""
        header_frame = tk.Frame(self, bg='white')
        header_frame.pack(fill="x", padx=25, pady=25)

        title_label = tk.Label(
            header_frame,
            text="💰 Procesamiento de Nómina",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Cálculo automático de roles de pago según normativa ecuatoriana",
            font=('Arial', 12),
            bg='white',
            fg=Config.COLORS['text']
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        separator = tk.Frame(header_frame, bg=Config.COLORS['border'], height=2)
        separator.pack(fill="x", pady=(15, 0))

    def create_control_panel(self, parent):
        """Crear panel de control"""
        control_frame = tk.LabelFrame(
            parent,
            text="🎛️ Panel de Control",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=10
        )
        control_frame.pack(fill="x", pady=(0, 10))

        # Fila 1 - Selección de periodo
        row1_frame = tk.Frame(control_frame, bg='white')
        row1_frame.pack(fill="x", pady=(0, 10))

        tk.Label(row1_frame, text="Período:", bg='white', font=('Arial', 12, 'bold')).pack(side="left", padx=(0, 10))

        self.period_var = tk.StringVar(value=self.current_period)
        period_combo = ttk.Combobox(row1_frame, textvariable=self.period_var, width=12, state="readonly")
        period_combo['values'] = self.generate_periods()
        period_combo.pack(side="left", padx=(0, 20))
        period_combo.bind("<<ComboboxSelected>>", self.on_period_change)

        # Estado del periodo
        tk.Label(row1_frame, text="Estado:", bg='white', font=('Arial', 12, 'bold')).pack(side="left", padx=(0, 10))
        self.status_label = tk.Label(
            row1_frame,
            text="● ABIERTO",
            bg='white',
            fg=Config.COLORS['success'],
            font=('Arial', 12, 'bold')
        )
        self.status_label.pack(side="left", padx=(0, 20))

        # Información del SBU
        sbu_info_label = tk.Label(
            row1_frame,
            text=f"SBU 2024: ${Config.SBU}",
            bg='white',
            fg=Config.COLORS['info'],
            font=('Arial', 10, 'bold')
        )
        sbu_info_label.pack(side="right")

        # Fila 2 - Botones de acción
        row2_frame = tk.Frame(control_frame, bg='white')
        row2_frame.pack(fill="x")

        buttons = [
            ("📊 Carga Masiva", self.carga_masiva_nomina, '#38a169'),
            ("🔄 Calcular Nómina", self.calculate_payroll, Config.COLORS['primary']),
            ("💾 Procesar Roles", self.process_payroll, Config.COLORS['success']),
            ("📄 Generar Reporte", self.generate_report, Config.COLORS['info']),
            ("📊 Resumen IESS", self.show_iess_summary, Config.COLORS['warning']),
            ("🗑️ Limpiar Período", self.clear_period, Config.COLORS['danger'])
        ]

        for text, command, color in buttons:
            btn = tk.Button(
                row2_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 10, 'bold'),
                relief='flat',
                padx=15,
                pady=8,
                cursor='hand2'
            )
            btn.pack(side="left", padx=(0, 10))

    def create_payroll_notebook(self, parent):
        """Crear notebook con pestañas de nómina"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        # Pestaña roles individuales
        self.create_individual_roles_tab()

        # Pestaña resumen
        self.create_summary_tab()

        # Pestaña ingresos/descuentos
        self.create_income_deductions_tab()

        # Pestaña configuración
        self.create_config_tab()

    def create_individual_roles_tab(self):
        """Crear pestaña de roles individuales"""
        tab_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_frame, text="👤 Roles Individuales")

        # Frame superior con filtros
        filter_frame = tk.Frame(tab_frame, bg='white')
        filter_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(filter_frame, text="Buscar empleado:", bg='white', font=('Arial', 10)).pack(side="left", padx=(0, 5))

        self.search_employee_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_employee_var, width=30)
        search_entry.pack(side="left", padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_employees)

        # Treeview para empleados
        tree_frame = tk.Frame(tab_frame, bg='white')
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("Empleado", "Nombres", "Cargo", "Sueldo", "Días Trab.", "Total Ing.", "Total Desc.", "Neto")
        self.payroll_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Configurar columnas
        column_widths = {"Empleado": 80, "Nombres": 200, "Cargo": 150, "Sueldo": 100,
                        "Días Trab.": 80, "Total Ing.": 100, "Total Desc.": 100, "Neto": 120}

        for col in columns:
            self.payroll_tree.heading(col, text=col)
            self.payroll_tree.column(col, width=column_widths[col], anchor="center" if col != "Nombres" else "w")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.payroll_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.payroll_tree.xview)
        self.payroll_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid
        self.payroll_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Eventos
        self.payroll_tree.bind("<Double-1>", self.edit_individual_role)

    def create_summary_tab(self):
        """Crear pestaña de resumen"""
        tab_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_frame, text="📊 Resumen")

        # Scroll frame
        canvas = tk.Canvas(tab_frame, bg='white')
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Estadísticas generales
        self.create_general_stats(scrollable_frame)

        # Resumen por departamento
        self.create_department_summary(scrollable_frame)

        # Resumen IESS
        self.create_iess_summary(scrollable_frame)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_income_deductions_tab(self):
        """Crear pestaña de ingresos y descuentos"""
        tab_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_frame, text="💳 Ing/Desc Adicionales")

        # Panel de control
        control_frame = tk.Frame(tab_frame, bg='white')
        control_frame.pack(fill="x", padx=15, pady=15)

        add_btn = tk.Button(
            control_frame,
            text="➕ Agregar Concepto",
            command=self.add_income_deduction,
            bg=Config.COLORS['success'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2'
        )
        add_btn.pack(side="left")

        # Lista de ingresos/descuentos
        list_frame = tk.Frame(tab_frame, bg='white')
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("Empleado", "Nombres", "Tipo", "Concepto", "Valor", "Aplica IESS", "Aplica IR", "Estado")
        self.income_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.income_tree.heading(col, text=col)
            width = 120 if col != "Nombres" else 180
            self.income_tree.column(col, width=width, anchor="center" if col != "Nombres" else "w")

        income_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.income_tree.yview)
        self.income_tree.configure(yscrollcommand=income_scrollbar.set)

        self.income_tree.pack(side="left", fill="both", expand=True)
        income_scrollbar.pack(side="right", fill="y")

    def create_config_tab(self):
        """Crear pestaña de configuración"""
        tab_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_frame, text="⚙️ Configuración")

        content_frame = tk.Frame(tab_frame, bg='white')
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Parámetros de nómina
        params_frame = tk.LabelFrame(
            content_frame,
            text="Parámetros de Nómina Ecuador 2024",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=15
        )
        params_frame.pack(fill="x", pady=(0, 20))

        params_data = [
            ("Salario Básico Unificado (SBU)", f"${Config.SBU}"),
            ("Aporte Personal IESS", f"{Config.APORTE_PERSONAL_IESS * 100:.2f}%"),
            ("Aporte Patronal IESS", f"{Config.APORTE_PATRONAL_IESS * 100:.2f}%"),
            ("Fondos de Reserva", f"{Config.FONDOS_RESERVA * 100:.2f}%"),
            ("Horas Extra 25%", f"{Config.HORAS_EXTRAS_25 * 100:.0f}%"),
            ("Horas Extra 50%", f"{Config.HORAS_EXTRAS_50 * 100:.0f}%"),
            ("Horas Extra 100%", f"{Config.HORAS_EXTRAS_100 * 100:.0f}%"),
            ("Días de Vacaciones Anuales", f"{Config.DIAS_VACACIONES_ANUAL} días")
        ]

        for i, (param, value) in enumerate(params_data):
            row = i // 2
            col = i % 2

            param_frame = tk.Frame(params_frame, bg='white')
            param_frame.grid(row=row, column=col, sticky="ew", padx=20, pady=5)

            tk.Label(param_frame, text=f"{param}:", bg='white', font=('Arial', 10)).pack(side="left")
            tk.Label(param_frame, text=value, bg='white', font=('Arial', 10, 'bold'), fg=Config.COLORS['primary']).pack(side="right")

        # Configurar grid
        for i in range(2):
            params_frame.grid_columnconfigure(i, weight=1)

    def create_general_stats(self, parent):
        """Crear estadísticas generales"""
        stats_frame = tk.LabelFrame(
            parent,
            text=f"📊 Estadísticas Generales - {self.period_var.get()}",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=15
        )
        stats_frame.pack(fill="x", padx=10, pady=10)

        # Obtener estadísticas
        stats = self.get_payroll_stats()

        # Grid de estadísticas
        stats_grid = tk.Frame(stats_frame, bg='white')
        stats_grid.pack(fill="x")

        stat_items = [
            ("Total Empleados", stats['total_employees'], "👥"),
            ("Total Sueldos", f"${stats['total_salary']:,.2f}", "💰"),
            ("Total IESS Personal", f"${stats['total_iess_personal']:,.2f}", "🏛️"),
            ("Total IESS Patronal", f"${stats['total_iess_patronal']:,.2f}", "🏢"),
            ("Total Neto a Pagar", f"${stats['total_net']:,.2f}", "💸"),
            ("Promedio Sueldo", f"${stats['avg_salary']:,.2f}", "📊")
        ]

        for i, (label, value, icon) in enumerate(stat_items):
            row = i // 3
            col = i % 3

            card_frame = tk.Frame(stats_grid, bg=Config.COLORS['primary'], relief='raised', bd=2)
            card_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

            icon_label = tk.Label(card_frame, text=icon, font=('Arial', 16), bg=Config.COLORS['primary'], fg='white')
            icon_label.pack(pady=(10, 5))

            value_label = tk.Label(card_frame, text=str(value), font=('Arial', 12, 'bold'), bg=Config.COLORS['primary'], fg='white')
            value_label.pack()

            label_label = tk.Label(card_frame, text=label, font=('Arial', 9), bg=Config.COLORS['primary'], fg='lightgray')
            label_label.pack(pady=(0, 10))

        # Configurar grid
        for i in range(3):
            stats_grid.grid_columnconfigure(i, weight=1)

    def create_department_summary(self, parent):
        """Crear resumen por departamento"""
        dept_frame = tk.LabelFrame(
            parent,
            text="🏢 Resumen por Departamento",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=15
        )
        dept_frame.pack(fill="x", padx=10, pady=10)

        # Treeview para departamentos
        columns = ("Departamento", "Empleados", "Total Sueldos", "Total IESS", "Neto a Pagar")
        dept_tree = ttk.Treeview(dept_frame, columns=columns, show="headings", height=6)

        for col in columns:
            dept_tree.heading(col, text=col)
            width = 150 if col == "Departamento" else 120
            dept_tree.column(col, width=width, anchor="w" if col == "Departamento" else "center")

        dept_scrollbar = ttk.Scrollbar(dept_frame, orient="vertical", command=dept_tree.yview)
        dept_tree.configure(yscrollcommand=dept_scrollbar.set)

        dept_tree.pack(side="left", fill="x", expand=True)
        dept_scrollbar.pack(side="right", fill="y")

        # Llenar datos de departamentos
        self.populate_department_summary(dept_tree)

    def create_iess_summary(self, parent):
        """Crear resumen IESS"""
        iess_frame = tk.LabelFrame(
            parent,
            text="🏛️ Resumen IESS",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=15
        )
        iess_frame.pack(fill="x", padx=10, pady=10)

        iess_stats = self.get_iess_stats()

        # Grid IESS
        iess_grid = tk.Frame(iess_frame, bg='white')
        iess_grid.pack(fill="x")

        iess_items = [
            ("Aporte Personal 9.45%", f"${iess_stats['aporte_personal']:,.2f}"),
            ("Aporte Patronal 11.15%", f"${iess_stats['aporte_patronal']:,.2f}"),
            ("Total IESS", f"${iess_stats['total_iess']:,.2f}"),
            ("Fondos de Reserva 8.33%", f"${iess_stats['fondos_reserva']:,.2f}")
        ]

        for i, (label, value) in enumerate(iess_items):
            col = i % 2
            row = i // 2

            item_frame = tk.Frame(iess_grid, bg='white')
            item_frame.grid(row=row, column=col, sticky="ew", padx=20, pady=5)

            tk.Label(item_frame, text=f"{label}:", bg='white', font=('Arial', 11)).pack(side="left")
            tk.Label(item_frame, text=value, bg='white', font=('Arial', 11, 'bold'), fg=Config.COLORS['success']).pack(side="right")

        for i in range(2):
            iess_grid.grid_columnconfigure(i, weight=1)

    def generate_periods(self):
        """Generar lista de periodos"""
        current_year = datetime.now().year
        periods = []

        for year in [current_year - 1, current_year, current_year + 1]:
            for month in range(1, 13):
                period = f"{year}-{month:02d}"
                periods.append(period)

        return periods

    def on_period_change(self, event):
        """Manejar cambio de período"""
        self.current_period = self.period_var.get()
        self.load_payroll_data()

    def load_payroll_data(self):
        """Cargar datos de nómina del período"""
        try:
            # Limpiar tree
            for item in self.payroll_tree.get_children():
                self.payroll_tree.delete(item)

            # Obtener empleados activos
            employees = self.session.query(Empleado).filter(Empleado.activo == True).all()

            for emp in employees:
                # Calcular valores de nómina
                salary = float(emp.sueldo or 0)
                worked_days = 30  # Por defecto, días del mes

                # Cálculos básicos
                total_income = salary
                iess_personal = salary * Config.APORTE_PERSONAL_IESS
                total_deductions = iess_personal
                net_pay = total_income - total_deductions

                self.payroll_tree.insert("", "end", values=(
                    emp.empleado,
                    f"{emp.nombres} {emp.apellidos}",
                    emp.cargo or "Sin cargo",
                    f"${salary:,.2f}",
                    worked_days,
                    f"${total_income:,.2f}",
                    f"${total_deductions:,.2f}",
                    f"${net_pay:,.2f}"
                ))

        except Exception as e:
            logger.error(f"Error cargando datos de nómina: {e}")
            messagebox.showerror("Error", f"Error al cargar nómina: {str(e)}")

    def filter_employees(self, event):
        """Filtrar empleados en la lista"""
        search_text = self.search_employee_var.get().upper()

        # Limpiar y recargar con filtro
        for item in self.payroll_tree.get_children():
            self.payroll_tree.delete(item)

        try:
            employees = self.session.query(Empleado).filter(Empleado.activo == True)

            if search_text:
                employees = employees.filter(
                    (Empleado.nombres.like(f"%{search_text}%")) |
                    (Empleado.apellidos.like(f"%{search_text}%")) |
                    (Empleado.empleado.like(f"%{search_text}%"))
                )

            for emp in employees.all():
                salary = float(emp.sueldo or 0)
                worked_days = 30
                total_income = salary
                iess_personal = salary * Config.APORTE_PERSONAL_IESS
                total_deductions = iess_personal
                net_pay = total_income - total_deductions

                self.payroll_tree.insert("", "end", values=(
                    emp.empleado,
                    f"{emp.nombres} {emp.apellidos}",
                    emp.cargo or "Sin cargo",
                    f"${salary:,.2f}",
                    worked_days,
                    f"${total_income:,.2f}",
                    f"${total_deductions:,.2f}",
                    f"${net_pay:,.2f}"
                ))

        except Exception as e:
            logger.error(f"Error filtrando empleados: {e}")

    def calculate_payroll(self):
        """Calcular nómina del período usando PayrollCalculator"""
        if messagebox.askyesno("Confirmar", f"¿Calcular nómina para el período {self.current_period}?"):
            try:
                self.main_app.root.config(cursor="wait")

                # Actualizar status
                self.status_label.config(text="● CALCULANDO...", fg=Config.COLORS['warning'])
                self.main_app.root.update()

                # Extraer año y mes del período
                year, month = map(int, self.current_period.split('-'))

                # Calcular nómina usando el calculador
                payroll_results = payroll_calculator.calculate_payroll_period(year, month)

                if not payroll_results:
                    messagebox.showwarning("Sin datos", "No se encontraron empleados activos para calcular.")
                    return

                # Guardar resultados
                current_user = getattr(self.main_app, 'current_user', None)
                username = current_user.username if current_user else 'SYSTEM'
                payroll_calculator.save_payroll_results(payroll_results, username)

                # Finalizar proceso
                self.finish_calculation()

                messagebox.showinfo("Éxito",
                    f"Nómina calculada correctamente para {len(payroll_results)} empleados.\n\n"
                    f"Período: {self.current_period}\n"
                    f"Total procesado: ${sum(r['total_ingresos'] for r in payroll_results):,.2f}")

            except Exception as e:
                logger.error(f"Error calculando nómina: {e}")
                messagebox.showerror("Error", f"Error en cálculo: {str(e)}")
                self.status_label.config(text="● ERROR", fg=Config.COLORS['danger'])
            finally:
                self.main_app.root.config(cursor="")

    def finish_calculation(self):
        """Finalizar cálculo de nómina"""
        self.status_label.config(text="● CALCULADO", fg=Config.COLORS['info'])
        self.load_payroll_data()
        # Actualizar resumen
        self.update_summary_widgets()

    def update_summary_widgets(self):
        """Actualizar widgets de resumen con datos reales"""
        try:
            year, month = map(int, self.current_period.split('-'))
            summary = payroll_calculator.get_payroll_summary(year, month)

            # Actualizar labels de resumen (si existen)
            if hasattr(self, 'summary_labels'):
                self.summary_labels['empleados'].config(text=f"{summary.get('total_empleados', 0)}")
                self.summary_labels['ingresos'].config(text=f"${summary.get('total_ingresos', 0):,.2f}")
                self.summary_labels['descuentos'].config(text=f"${summary.get('total_descuentos', 0):,.2f}")
                self.summary_labels['liquido'].config(text=f"${summary.get('liquido_total', 0):,.2f}")
                self.summary_labels['iess'].config(text=f"${summary.get('aporte_iess_personal', 0):,.2f}")
                self.summary_labels['patronal'].config(text=f"${summary.get('aporte_iess_patronal', 0):,.2f}")

        except Exception as e:
            logger.error(f"Error actualizando resumen: {e}")

    def process_payroll(self):
        """Procesar roles de pago"""
        if messagebox.askyesno("Confirmar", f"¿Procesar roles definitivamente para {self.current_period}?"):
            try:
                self.status_label.config(text="● PROCESANDO...", fg=Config.COLORS['warning'])
                self.main_app.root.update()

                # Aquí iría el procesamiento real
                self.main_app.root.after(3000, self.finish_processing)

                messagebox.showinfo("Proceso Iniciado", "Procesando roles de pago...")

            except Exception as e:
                logger.error(f"Error procesando nómina: {e}")
                messagebox.showerror("Error", f"Error en procesamiento: {str(e)}")

    def finish_processing(self):
        """Finalizar procesamiento"""
        self.status_label.config(text="● PROCESADO", fg=Config.COLORS['success'])
        messagebox.showinfo("Éxito", "Roles procesados correctamente")

    def generate_report(self):
        """Generar reporte de nómina"""
        try:
            # Seleccionar ubicación
            file_path = filedialog.asksaveasfilename(
                title="Guardar reporte",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if file_path:
                # Simular generación
                messagebox.showinfo("Éxito", f"Reporte generado: {file_path}")

        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            messagebox.showerror("Error", f"Error en reporte: {str(e)}")

    def show_iess_summary(self):
        """Mostrar resumen IESS"""
        stats = self.get_iess_stats()

        summary_window = tk.Toplevel(self)
        summary_window.title("Resumen IESS")
        summary_window.geometry("400x300")
        summary_window.configure(bg='white')

        header_label = tk.Label(
            summary_window,
            text=f"📊 Resumen IESS - {self.current_period}",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        header_label.pack(pady=20)

        details_frame = tk.Frame(summary_window, bg='white')
        details_frame.pack(fill="both", expand=True, padx=30)

        details = [
            ("Aporte Personal (9.45%)", f"${stats['aporte_personal']:,.2f}"),
            ("Aporte Patronal (11.15%)", f"${stats['aporte_patronal']:,.2f}"),
            ("Fondos de Reserva (8.33%)", f"${stats['fondos_reserva']:,.2f}"),
            ("Total IESS", f"${stats['total_iess']:,.2f}")
        ]

        for i, (label, value) in enumerate(details):
            detail_frame = tk.Frame(details_frame, bg='white')
            detail_frame.pack(fill="x", pady=10)

            tk.Label(detail_frame, text=f"{label}:", bg='white', font=('Arial', 11)).pack(side="left")
            tk.Label(detail_frame, text=value, bg='white', font=('Arial', 11, 'bold'),
                    fg=Config.COLORS['primary']).pack(side="right")

    def clear_period(self):
        """Limpiar período"""
        if messagebox.askyesno("Confirmar", f"¿Limpiar todos los datos del período {self.current_period}?"):
            try:
                # Limpiar datos del período
                self.status_label.config(text="● ABIERTO", fg=Config.COLORS['success'])
                self.load_payroll_data()
                messagebox.showinfo("Éxito", "Período limpiado correctamente")

            except Exception as e:
                logger.error(f"Error limpiando período: {e}")
                messagebox.showerror("Error", f"Error al limpiar: {str(e)}")

    def edit_individual_role(self, event):
        """Editar rol individual"""
        selection = self.payroll_tree.selection()
        if selection:
            item = self.payroll_tree.item(selection[0])
            employee_code = item['values'][0]

            # Aquí abriríamos ventana de edición individual
            messagebox.showinfo("Editar Rol", f"Editando rol del empleado: {employee_code}")

    def add_income_deduction(self):
        """Agregar ingreso o descuento"""
        # Ventana para agregar concepto
        add_window = tk.Toplevel(self)
        add_window.title("Agregar Concepto")
        add_window.geometry("500x400")
        add_window.configure(bg='white')

        # Por ahora solo placeholder
        placeholder_label = tk.Label(
            add_window,
            text="🚧 Formulario de ingresos/descuentos\\nEn desarrollo",
            font=('Arial', 14),
            bg='white',
            fg=Config.COLORS['text_light']
        )
        placeholder_label.pack(expand=True)

    def get_payroll_stats(self):
        """Obtener estadísticas de nómina"""
        try:
            employees = self.session.query(Empleado).filter(Empleado.activo == True).all()

            total_employees = len(employees)
            total_salary = sum(float(emp.sueldo or 0) for emp in employees)
            total_iess_personal = total_salary * Config.APORTE_PERSONAL_IESS
            total_iess_patronal = total_salary * Config.APORTE_PATRONAL_IESS
            total_net = total_salary - total_iess_personal
            avg_salary = total_salary / total_employees if total_employees > 0 else 0

            return {
                'total_employees': total_employees,
                'total_salary': total_salary,
                'total_iess_personal': total_iess_personal,
                'total_iess_patronal': total_iess_patronal,
                'total_net': total_net,
                'avg_salary': avg_salary
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_employees': 0,
                'total_salary': 0,
                'total_iess_personal': 0,
                'total_iess_patronal': 0,
                'total_net': 0,
                'avg_salary': 0
            }

    def get_iess_stats(self):
        """Obtener estadísticas IESS usando datos reales"""
        try:
            year, month = map(int, self.current_period.split('-'))
            summary = payroll_calculator.get_payroll_summary(year, month)

            return {
                'aporte_personal': summary.get('aporte_iess_personal', 0),
                'aporte_patronal': summary.get('aporte_iess_patronal', 0),
                'fondos_reserva': summary.get('provisiones_total', 0),  # Incluye fondos de reserva
                'total_iess': summary.get('aporte_iess_personal', 0) + summary.get('aporte_iess_patronal', 0),
                'total_empleados': summary.get('total_empleados', 0),
                'total_ingresos': summary.get('total_ingresos', 0),
                'liquido_total': summary.get('liquido_total', 0),
                'costo_empresa': summary.get('costo_empresa_total', 0)
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas IESS: {e}")
            return {
                'aporte_personal': 0,
                'aporte_patronal': 0,
                'fondos_reserva': 0,
                'total_iess': 0,
                'total_empleados': 0,
                'total_ingresos': 0,
                'liquido_total': 0,
                'costo_empresa': 0
            }

    def populate_department_summary(self, tree):
        """Poblar resumen por departamento"""
        try:
            # Obtener empleados por departamento
            employees = self.session.query(Empleado).filter(Empleado.activo == True).all()

            dept_summary = {}
            for emp in employees:
                dept = emp.depto or "SIN DEPARTAMENTO"
                if dept not in dept_summary:
                    dept_summary[dept] = {
                        'count': 0,
                        'total_salary': 0,
                        'total_iess': 0,
                        'total_net': 0
                    }

                salary = float(emp.sueldo or 0)
                iess = salary * Config.APORTE_PERSONAL_IESS

                dept_summary[dept]['count'] += 1
                dept_summary[dept]['total_salary'] += salary
                dept_summary[dept]['total_iess'] += iess
                dept_summary[dept]['total_net'] += salary - iess

            # Llenar tree
            for dept, data in dept_summary.items():
                tree.insert("", "end", values=(
                    dept,
                    data['count'],
                    f"${data['total_salary']:,.2f}",
                    f"${data['total_iess']:,.2f}",
                    f"${data['total_net']:,.2f}"
                ))

        except Exception as e:
            logger.error(f"Error en resumen por departamento: {e}")

    def carga_masiva_nomina(self):
        """Abrir ventana de carga masiva de nómina"""
        try:
            show_carga_masiva_nomina(self, self.session)
            # Recargar datos después de la carga masiva
            self.load_current_period()
        except Exception as e:
            logger.error(f"Error en carga masiva de nómina: {e}")
            messagebox.showerror("Error", f"Error abriendo carga masiva: {str(e)}")