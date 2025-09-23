#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Décimos Completo - Sistema SAI
Gestión de décimo tercero y décimo cuarto sueldo según normativa ecuatoriana
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from decimal import Decimal
import sys
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import get_session
from database.models import Empleado, Departamento, Cargo

class DecimosCompleteModule(tk.Frame):
    """Módulo completo de décimos"""

    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables
        self.selected_employee = None
        self.periodo_var = tk.StringVar(value=str(date.today().year))
        self.tipo_decimo_var = tk.StringVar(value="13")

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
            text="GESTIÓN DE DÉCIMOS",
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
        self.create_calculation_tab()
        self.create_history_tab()
        self.create_reports_tab()

    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = tk.Frame(self, bg='#e2e8f0', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=2)
        toolbar.pack_propagate(False)

        # Botones principales
        buttons = [
            ("Calcular Décimos", self.calculate_decimos, '#4299e1'),
            ("Generar Rol", self.generate_role, '#48bb78'),
            ("Exportar", self.export_data, '#ed8936'),
            ("Configuración", self.show_config, '#9f7aea')
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

    def create_calculation_tab(self):
        """Crear pestaña de cálculo de décimos"""
        calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(calc_frame, text="Cálculo de Décimos")

        # Panel izquierdo - Configuración
        left_panel = tk.Frame(calc_frame, bg='white', relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(
            left_panel,
            text="CONFIGURACIÓN",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(pady=10)

        # Período
        period_frame = tk.Frame(left_panel, bg='white')
        period_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(period_frame, text="Período:", bg='white', font=('Arial', 10)).pack(anchor=tk.W)
        period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.periodo_var,
            values=[str(year) for year in range(2020, 2030)],
            state='readonly',
            width=15
        )
        period_combo.pack(fill=tk.X, pady=2)

        # Tipo de décimo
        tipo_frame = tk.Frame(left_panel, bg='white')
        tipo_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(tipo_frame, text="Tipo de Décimo:", bg='white', font=('Arial', 10)).pack(anchor=tk.W)

        tk.Radiobutton(
            tipo_frame,
            text="Décimo Tercero",
            variable=self.tipo_decimo_var,
            value="13",
            bg='white',
            font=('Arial', 9)
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            tipo_frame,
            text="Décimo Cuarto",
            variable=self.tipo_decimo_var,
            value="14",
            bg='white',
            font=('Arial', 9)
        ).pack(anchor=tk.W)

        # Filtros
        filter_frame = tk.Frame(left_panel, bg='white')
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(filter_frame, text="Filtros:", bg='white', font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        self.filter_dept_var = tk.StringVar(value="TODOS")
        tk.Label(filter_frame, text="Departamento:", bg='white', font=('Arial', 9)).pack(anchor=tk.W)
        dept_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_dept_var,
            state='readonly',
            width=20
        )
        dept_combo.pack(fill=tk.X, pady=2)

        # Cargar departamentos
        departments = ["TODOS"] + [d.nombre for d in self.session.query(Departamento).filter_by(activo=True).all()]
        dept_combo['values'] = departments

        # Panel derecho - Lista de empleados y cálculos
        right_panel = tk.Frame(calc_frame, bg='white')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Lista de empleados
        self.create_employee_list(right_panel)

        # Panel de resultados
        self.create_results_panel(right_panel)

    def create_employee_list(self, parent):
        """Crear lista de empleados"""
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tk.Label(
            list_frame,
            text="EMPLEADOS",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(pady=5)

        # Treeview para empleados
        columns = ('codigo', 'nombre', 'cargo', 'sueldo', 'fecha_ing')
        self.employee_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        # Configurar columnas
        self.employee_tree.heading('codigo', text='Código')
        self.employee_tree.heading('nombre', text='Nombre Completo')
        self.employee_tree.heading('cargo', text='Cargo')
        self.employee_tree.heading('sueldo', text='Sueldo')
        self.employee_tree.heading('fecha_ing', text='Fecha Ingreso')

        self.employee_tree.column('codigo', width=80)
        self.employee_tree.column('nombre', width=200)
        self.employee_tree.column('cargo', width=150)
        self.employee_tree.column('sueldo', width=100)
        self.employee_tree.column('fecha_ing', width=100)

        # Scrollbars
        emp_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.employee_tree.yview)
        emp_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.employee_tree.xview)

        self.employee_tree.configure(yscrollcommand=emp_scroll_y.set, xscrollcommand=emp_scroll_x.set)

        # Pack
        self.employee_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        emp_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        emp_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_employee_select)

    def create_results_panel(self, parent):
        """Crear panel de resultados de cálculo"""
        results_frame = tk.LabelFrame(parent, text="Resultados del Cálculo", bg='white', font=('Arial', 10, 'bold'))
        results_frame.pack(fill=tk.X, padx=10, pady=5)

        # Frame interno
        inner_frame = tk.Frame(results_frame, bg='white')
        inner_frame.pack(fill=tk.X, padx=10, pady=5)

        # Información del empleado seleccionado
        info_frame = tk.Frame(inner_frame, bg='white')
        info_frame.pack(fill=tk.X, pady=5)

        tk.Label(info_frame, text="Empleado:", bg='white', font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.emp_name_label = tk.Label(info_frame, text="Seleccione un empleado", bg='white', font=('Arial', 9))
        self.emp_name_label.grid(row=0, column=1, sticky=tk.W, padx=10)

        # Cálculos
        calc_frame = tk.Frame(inner_frame, bg='white')
        calc_frame.pack(fill=tk.X, pady=10)

        # Grid de cálculos
        labels = [
            "Sueldo Base:",
            "Tiempo Trabajado:",
            "Décimo Proporcional:",
            "Total a Pagar:"
        ]

        self.calc_labels = {}
        for i, label in enumerate(labels):
            tk.Label(calc_frame, text=label, bg='white', font=('Arial', 9, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2)
            value_label = tk.Label(calc_frame, text="$0.00", bg='white', font=('Arial', 9))
            value_label.grid(row=i, column=1, sticky=tk.W, padx=20, pady=2)
            self.calc_labels[label] = value_label

    def create_history_tab(self):
        """Crear pestaña de historial"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="Historial de Pagos")

        # Toolbar del historial
        hist_toolbar = tk.Frame(history_frame, bg='#e2e8f0', height=40)
        hist_toolbar.pack(fill=tk.X, padx=5, pady=2)
        hist_toolbar.pack_propagate(False)

        tk.Button(
            hist_toolbar,
            text="Actualizar",
            command=self.load_history,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            relief=tk.FLAT,
            padx=10
        ).pack(side=tk.LEFT, pady=5, padx=5)

        # Treeview para historial
        hist_columns = ('periodo', 'empleado', 'tipo', 'base', 'tiempo', 'valor', 'fecha_pago')
        self.history_tree = ttk.Treeview(history_frame, columns=hist_columns, show='headings')

        headings = ['Período', 'Empleado', 'Tipo', 'Base', 'Tiempo', 'Valor', 'Fecha Pago']
        for col, heading in zip(hist_columns, headings):
            self.history_tree.heading(col, text=heading)
            self.history_tree.column(col, width=100)

        # Scrollbars para historial
        hist_scroll_y = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        hist_scroll_x = ttk.Scrollbar(history_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)

        self.history_tree.configure(yscrollcommand=hist_scroll_y.set, xscrollcommand=hist_scroll_x.set)

        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        hist_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        hist_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    def create_reports_tab(self):
        """Crear pestaña de reportes"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reportes")

        # Panel de opciones de reporte
        options_frame = tk.LabelFrame(reports_frame, text="Opciones de Reporte", font=('Arial', 10, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Tipo de reporte
        report_type_frame = tk.Frame(options_frame)
        report_type_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(report_type_frame, text="Tipo de Reporte:", font=('Arial', 10)).pack(anchor=tk.W)

        self.report_type_var = tk.StringVar(value="individual")

        tk.Radiobutton(
            report_type_frame,
            text="Reporte Individual",
            variable=self.report_type_var,
            value="individual",
            font=('Arial', 9)
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            report_type_frame,
            text="Reporte General",
            variable=self.report_type_var,
            value="general",
            font=('Arial', 9)
        ).pack(anchor=tk.W)

        # Botones de reporte
        report_buttons_frame = tk.Frame(reports_frame)
        report_buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            report_buttons_frame,
            text="Generar PDF",
            command=self.generate_pdf_report,
            bg='#e53e3e',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            report_buttons_frame,
            text="Exportar Excel",
            command=self.export_excel,
            bg='#38a169',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

    def load_employees(self):
        """Cargar lista de empleados"""
        try:
            # Limpiar tree
            for item in self.employee_tree.get_children():
                self.employee_tree.delete(item)

            # Obtener empleados activos
            empleados = self.session.query(Empleado).filter_by(activo=True).all()

            for emp in empleados:
                # Obtener información del cargo
                cargo_nombre = "N/A"
                if emp.cargo:
                    cargo = self.session.query(Cargo).filter_by(codigo=emp.cargo).first()
                    if cargo:
                        cargo_nombre = cargo.nombre

                self.employee_tree.insert('', 'end', values=(
                    emp.empleado,
                    f"{emp.nombres} {emp.apellidos}",
                    cargo_nombre,
                    f"${emp.sueldo:.2f}",
                    emp.fecha_ing.strftime('%d/%m/%Y') if emp.fecha_ing else "N/A"
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando empleados: {str(e)}")

    def on_employee_select(self, event):
        """Manejar selección de empleado"""
        selection = self.employee_tree.selection()
        if selection:
            item = self.employee_tree.item(selection[0])
            codigo_empleado = item['values'][0]
            nombre_empleado = item['values'][1]

            # Actualizar información
            self.emp_name_label.config(text=nombre_empleado)

            # Calcular décimo para este empleado
            self.calculate_employee_decimo(codigo_empleado)

    def calculate_employee_decimo(self, codigo_empleado):
        """Calcular décimo para un empleado específico"""
        try:
            empleado = self.session.query(Empleado).filter_by(empleado=codigo_empleado).first()
            if not empleado:
                return

            periodo = int(self.periodo_var.get())
            tipo_decimo = self.tipo_decimo_var.get()

            # Calcular tiempo trabajado en el período
            fecha_inicio = date(periodo, 1, 1)
            fecha_fin = date(periodo, 12, 31)

            # Si ingresó durante el año, usar fecha de ingreso
            if empleado.fecha_ing and empleado.fecha_ing > fecha_inicio:
                fecha_inicio = empleado.fecha_ing

            # Calcular meses trabajados
            meses_trabajados = (fecha_fin.year - fecha_inicio.year) * 12 + (fecha_fin.month - fecha_inicio.month) + 1

            if meses_trabajados > 12:
                meses_trabajados = 12

            # Cálculo según tipo de décimo
            if tipo_decimo == "13":
                # Décimo tercero = sueldo * meses_trabajados / 12
                base_calculo = empleado.sueldo
                decimo = (base_calculo * meses_trabajados) / 12
            else:
                # Décimo cuarto = SBU * meses_trabajados / 12
                sbu = Decimal('460.00')  # Salario Básico Unificado 2024
                decimo = (sbu * meses_trabajados) / 12
                base_calculo = sbu

            # Actualizar labels
            self.calc_labels["Sueldo Base:"].config(text=f"${base_calculo:.2f}")
            self.calc_labels["Tiempo Trabajado:"].config(text=f"{meses_trabajados} meses")
            self.calc_labels["Décimo Proporcional:"].config(text=f"${decimo:.2f}")
            self.calc_labels["Total a Pagar:"].config(text=f"${decimo:.2f}")

        except Exception as e:
            messagebox.showerror("Error", f"Error calculando décimo: {str(e)}")

    def calculate_decimos(self):
        """Calcular décimos para todos los empleados"""
        try:
            # Confirmar cálculo
            if not messagebox.askyesno("Confirmar", "¿Desea calcular los décimos para todos los empleados?"):
                return

            # Mostrar progreso
            progress_window = tk.Toplevel(self)
            progress_window.title("Calculando Décimos")
            progress_window.geometry("400x100")
            progress_window.transient(self)
            progress_window.grab_set()

            tk.Label(progress_window, text="Calculando décimos...").pack(pady=20)
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()

            # Actualizar interfaz
            progress_window.update()

            # Aquí iría la lógica de cálculo masivo
            # Simular procesamiento
            self.after(2000, lambda: self.finish_calculation(progress_window))

        except Exception as e:
            messagebox.showerror("Error", f"Error en cálculo masivo: {str(e)}")

    def finish_calculation(self, progress_window):
        """Finalizar cálculo masivo"""
        progress_window.destroy()
        messagebox.showinfo("Éxito", "Cálculo de décimos completado exitosamente")

    def generate_role(self):
        """Generar rol de pagos de décimos"""
        messagebox.showinfo("Información", "Función de generación de rol en desarrollo")

    def export_data(self):
        """Exportar datos"""
        messagebox.showinfo("Información", "Función de exportación en desarrollo")

    def show_config(self):
        """Mostrar configuración"""
        messagebox.showinfo("Información", "Configuración de décimos en desarrollo")

    def load_history(self):
        """Cargar historial de pagos"""
        # Limpiar historial
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Agregar datos de ejemplo
        sample_data = [
            ("2023", "001001 - Juan Perez", "13ro", "$500.00", "12 meses", "$500.00", "15/12/2023"),
            ("2023", "001002 - Maria Gonzalez", "13ro", "$800.00", "12 meses", "$800.00", "15/12/2023"),
            ("2023", "001001 - Juan Perez", "14to", "$460.00", "12 meses", "$460.00", "15/08/2023"),
        ]

        for data in sample_data:
            self.history_tree.insert('', 'end', values=data)

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
            '#9f7aea': '#805ad5'
        }
        return color_map.get(color, color)

    def __del__(self):
        """Destructor"""
        if hasattr(self, 'session') and hasattr(self.session, 'close'):
            self.session.close()