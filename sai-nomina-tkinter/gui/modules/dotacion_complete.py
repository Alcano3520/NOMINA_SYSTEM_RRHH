#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Dotación Completo - Sistema SAI
Gestión de elementos de dotación y uniformes para empleados
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

class DotacionCompleteModule(tk.Frame):
    """Módulo completo de dotación"""

    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables
        self.selected_employee = None
        self.selected_item = None
        self.tipo_dotacion_var = tk.StringVar(value="uniforme")

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
            text="GESTIÓN DE DOTACIÓN",
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
        self.create_asignacion_tab()
        self.create_inventario_tab()
        self.create_entrega_tab()
        self.create_reportes_tab()

    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = tk.Frame(self, bg='#e2e8f0', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=2)
        toolbar.pack_propagate(False)

        # Botones principales
        buttons = [
            ("Nueva Asignación", self.new_assignment, '#4299e1'),
            ("Registrar Entrega", self.register_delivery, '#48bb78'),
            ("Inventario", self.manage_inventory, '#ed8936'),
            ("Devolución", self.register_return, '#9f7aea'),
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

    def create_asignacion_tab(self):
        """Crear pestaña de asignación de dotación"""
        asignacion_frame = ttk.Frame(self.notebook)
        self.notebook.add(asignacion_frame, text="Asignación")

        # Panel superior - Formulario de asignación
        form_frame = tk.LabelFrame(asignacion_frame, text="Nueva Asignación de Dotación", font=('Arial', 11, 'bold'))
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_assignment_form(form_frame)

        # Panel inferior - Lista de asignaciones pendientes
        pending_frame = tk.LabelFrame(asignacion_frame, text="Asignaciones Pendientes", font=('Arial', 11, 'bold'))
        pending_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_pending_assignments_list(pending_frame)

    def create_assignment_form(self, parent):
        """Crear formulario de asignación"""
        form_grid = tk.Frame(parent)
        form_grid.pack(padx=10, pady=10)

        # Empleado
        tk.Label(form_grid, text="Empleado:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.emp_combo = ttk.Combobox(form_grid, state='readonly', width=40)
        self.emp_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.emp_combo.bind('<<ComboboxSelected>>', self.on_employee_selected)

        # Información del empleado
        emp_info_frame = tk.LabelFrame(form_grid, text="Información del Empleado")
        emp_info_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)

        self.emp_info_labels = {}
        info_fields = ["Cargo:", "Departamento:", "Talla Camisa:", "Talla Pantalón:", "Talla Zapatos:"]
        for i, field in enumerate(info_fields):
            tk.Label(emp_info_frame, text=field, font=('Arial', 9)).grid(
                row=i//3, column=(i%3)*2, sticky=tk.W, padx=5, pady=2
            )
            label = tk.Label(emp_info_frame, text="", font=('Arial', 9), relief=tk.SUNKEN, width=15)
            label.grid(row=i//3, column=(i%3)*2+1, sticky=tk.W, padx=5, pady=2)
            self.emp_info_labels[field] = label

        # Tipo de dotación
        tk.Label(form_grid, text="Tipo de Dotación:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        tipo_frame = tk.Frame(form_grid)
        tipo_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        tipos = [
            ("Uniforme", "uniforme"),
            ("Calzado", "calzado"),
            ("EPP", "epp"),
            ("Otros", "otros")
        ]

        for i, (text, value) in enumerate(tipos):
            tk.Radiobutton(
                tipo_frame,
                text=text,
                variable=self.tipo_dotacion_var,
                value=value,
                command=self.update_items_list,
                font=('Arial', 9)
            ).grid(row=0, column=i, sticky=tk.W, padx=10)

        # Período de asignación
        tk.Label(form_grid, text="Período:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.periodo_combo = ttk.Combobox(
            form_grid,
            values=[str(year) for year in range(2024, 2030)],
            state='readonly',
            width=10
        )
        self.periodo_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.periodo_combo.set(str(date.today().year))

        # Fecha de asignación
        tk.Label(form_grid, text="Fecha Asignación:", font=('Arial', 10, 'bold')).grid(row=3, column=2, sticky=tk.W, padx=10, pady=5)
        self.fecha_asignacion_entry = tk.Entry(form_grid, width=12)
        self.fecha_asignacion_entry.grid(row=3, column=3, sticky=tk.W, padx=5, pady=5)
        self.fecha_asignacion_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Lista de elementos a asignar
        elements_frame = tk.LabelFrame(form_grid, text="Elementos a Asignar")
        elements_frame.grid(row=4, column=0, columnspan=4, sticky='ew', pady=10)

        # Treeview para elementos
        columns = ('item', 'descripcion', 'talla', 'cantidad', 'costo')
        self.elements_tree = ttk.Treeview(elements_frame, columns=columns, show='headings', height=6)

        # Configurar columnas
        headings = ['Elemento', 'Descripción', 'Talla', 'Cantidad', 'Costo Unit.']
        widths = [120, 200, 80, 80, 100]

        for col, heading, width in zip(columns, headings, widths):
            self.elements_tree.heading(col, text=heading)
            self.elements_tree.column(col, width=width)

        # Scrollbar
        elem_scroll = ttk.Scrollbar(elements_frame, orient=tk.VERTICAL, command=self.elements_tree.yview)
        self.elements_tree.configure(yscrollcommand=elem_scroll.set)

        # Pack
        self.elements_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        elem_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones para agregar/quitar elementos
        btn_frame = tk.Frame(elements_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame,
            text="Agregar Elemento",
            command=self.add_element,
            bg='#48bb78',
            fg='white',
            font=('Arial', 9),
            padx=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Quitar Elemento",
            command=self.remove_element,
            bg='#e53e3e',
            fg='white',
            font=('Arial', 9),
            padx=10
        ).pack(side=tk.LEFT, padx=5)

        # Total y observaciones
        total_frame = tk.Frame(form_grid)
        total_frame.grid(row=5, column=0, columnspan=4, sticky='ew', pady=10)

        tk.Label(total_frame, text="Total Asignación:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.total_label = tk.Label(total_frame, text="$0.00", font=('Arial', 10, 'bold'), fg='blue')
        self.total_label.pack(side=tk.LEFT, padx=10)

        tk.Label(total_frame, text="Observaciones:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(20,5))
        self.obs_entry = tk.Entry(total_frame, width=30)
        self.obs_entry.pack(side=tk.LEFT, padx=5)

        # Botones de acción
        action_frame = tk.Frame(form_grid)
        action_frame.grid(row=6, column=0, columnspan=4, pady=15)

        tk.Button(
            action_frame,
            text="Guardar Asignación",
            command=self.save_assignment,
            bg='#4299e1',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            action_frame,
            text="Limpiar",
            command=self.clear_assignment_form,
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    def create_pending_assignments_list(self, parent):
        """Crear lista de asignaciones pendientes"""
        # Filtros
        filter_frame = tk.Frame(parent)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Filtrar por:", font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        self.filter_estado_combo = ttk.Combobox(
            filter_frame,
            values=["TODAS", "PENDIENTE", "ENTREGADA", "DEVUELTA"],
            state='readonly',
            width=12
        )
        self.filter_estado_combo.pack(side=tk.LEFT, padx=5)
        self.filter_estado_combo.set("PENDIENTE")

        tk.Button(
            filter_frame,
            text="Actualizar",
            command=self.update_assignments_list,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=10
        ).pack(side=tk.LEFT, padx=10)

        # Lista de asignaciones
        columns = ('fecha', 'empleado', 'tipo', 'elementos', 'total', 'estado')
        self.assignments_tree = ttk.Treeview(parent, columns=columns, show='headings')

        # Configurar columnas
        headings = ['Fecha', 'Empleado', 'Tipo', 'Elementos', 'Total', 'Estado']
        for col, heading in zip(columns, headings):
            self.assignments_tree.heading(col, text=heading)
            self.assignments_tree.column(col, width=100)

        # Scrollbars
        assign_scroll_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.assignments_tree.yview)
        assign_scroll_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.assignments_tree.xview)

        self.assignments_tree.configure(yscrollcommand=assign_scroll_y.set, xscrollcommand=assign_scroll_x.set)

        # Pack
        self.assignments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        assign_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        assign_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar datos de ejemplo
        self.load_sample_assignments()

        # Bind events
        self.assignments_tree.bind('<Double-1>', self.edit_assignment)

    def create_inventario_tab(self):
        """Crear pestaña de inventario"""
        inventario_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventario_frame, text="Inventario")

        # Panel de gestión de inventario
        manage_frame = tk.LabelFrame(inventario_frame, text="Gestión de Inventario", font=('Arial', 11, 'bold'))
        manage_frame.pack(fill=tk.X, padx=10, pady=5)

        # Formulario de nuevo elemento
        self.create_inventory_form(manage_frame)

        # Lista de inventario
        inventory_list_frame = tk.LabelFrame(inventario_frame, text="Inventario Actual", font=('Arial', 11, 'bold'))
        inventory_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_inventory_list(inventory_list_frame)

    def create_inventory_form(self, parent):
        """Crear formulario de inventario"""
        form_frame = tk.Frame(parent)
        form_frame.pack(padx=10, pady=10)

        # Primera fila
        tk.Label(form_frame, text="Código:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.inv_codigo_entry = tk.Entry(form_frame, width=12)
        self.inv_codigo_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form_frame, text="Nombre:", font=('Arial', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=2)
        self.inv_nombre_entry = tk.Entry(form_frame, width=25)
        self.inv_nombre_entry.grid(row=0, column=3, padx=5, pady=2)

        # Segunda fila
        tk.Label(form_frame, text="Categoría:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.inv_categoria_combo = ttk.Combobox(
            form_frame,
            values=["UNIFORME", "CALZADO", "EPP", "OTROS"],
            state='readonly',
            width=12
        )
        self.inv_categoria_combo.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(form_frame, text="Tallas:", font=('Arial', 9, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=10, pady=2)
        self.inv_tallas_entry = tk.Entry(form_frame, width=25)
        self.inv_tallas_entry.grid(row=1, column=3, padx=5, pady=2)
        self.inv_tallas_entry.insert(0, "S,M,L,XL")

        # Tercera fila
        tk.Label(form_frame, text="Stock Inicial:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.inv_stock_entry = tk.Entry(form_frame, width=12)
        self.inv_stock_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(form_frame, text="Costo Unitario:", font=('Arial', 9, 'bold')).grid(row=2, column=2, sticky=tk.W, padx=10, pady=2)
        self.inv_costo_entry = tk.Entry(form_frame, width=12)
        self.inv_costo_entry.grid(row=2, column=3, padx=5, pady=2)

        # Botones
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)

        tk.Button(
            btn_frame,
            text="Agregar al Inventario",
            command=self.add_to_inventory,
            bg='#48bb78',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Actualizar Stock",
            command=self.update_stock,
            bg='#ed8936',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

    def create_inventory_list(self, parent):
        """Crear lista de inventario"""
        # Filtros
        filter_frame = tk.Frame(parent)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Categoría:", font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        self.inv_filter_combo = ttk.Combobox(
            filter_frame,
            values=["TODAS", "UNIFORME", "CALZADO", "EPP", "OTROS"],
            state='readonly',
            width=12
        )
        self.inv_filter_combo.pack(side=tk.LEFT, padx=5)
        self.inv_filter_combo.set("TODAS")

        tk.Button(
            filter_frame,
            text="Filtrar",
            command=self.filter_inventory,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=10
        ).pack(side=tk.LEFT, padx=10)

        # Lista
        columns = ('codigo', 'nombre', 'categoria', 'tallas', 'stock', 'asignado', 'disponible', 'costo')
        self.inventory_tree = ttk.Treeview(parent, columns=columns, show='headings')

        # Configurar columnas
        headings = ['Código', 'Nombre', 'Categoría', 'Tallas', 'Stock', 'Asignado', 'Disponible', 'Costo']
        for col, heading in zip(columns, headings):
            self.inventory_tree.heading(col, text=heading)
            self.inventory_tree.column(col, width=90)

        # Scrollbars
        inv_scroll_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        inv_scroll_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.inventory_tree.xview)

        self.inventory_tree.configure(yscrollcommand=inv_scroll_y.set, xscrollcommand=inv_scroll_x.set)

        # Pack
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        inv_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        inv_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar inventario de ejemplo
        self.load_sample_inventory()

    def create_entrega_tab(self):
        """Crear pestaña de entrega"""
        entrega_frame = ttk.Frame(self.notebook)
        self.notebook.add(entrega_frame, text="Control de Entregas")

        # Panel de registro de entrega
        delivery_frame = tk.LabelFrame(entrega_frame, text="Registrar Entrega", font=('Arial', 11, 'bold'))
        delivery_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_delivery_form(delivery_frame)

        # Panel de historial de entregas
        history_frame = tk.LabelFrame(entrega_frame, text="Historial de Entregas", font=('Arial', 11, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_delivery_history(history_frame)

    def create_delivery_form(self, parent):
        """Crear formulario de entrega"""
        form_frame = tk.Frame(parent)
        form_frame.pack(padx=10, pady=10)

        # Asignación
        tk.Label(form_frame, text="Asignación:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.delivery_assignment_combo = ttk.Combobox(form_frame, state='readonly', width=50)
        self.delivery_assignment_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        # Fecha de entrega
        tk.Label(form_frame, text="Fecha Entrega:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.delivery_date_entry = tk.Entry(form_frame, width=12)
        self.delivery_date_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.delivery_date_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Entregado por
        tk.Label(form_frame, text="Entregado por:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)
        self.delivered_by_entry = tk.Entry(form_frame, width=20)
        self.delivered_by_entry.grid(row=1, column=3, padx=5, pady=5)

        # Estado de elementos
        tk.Label(form_frame, text="Estado:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        estado_frame = tk.Frame(form_frame)
        estado_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.delivery_estado_var = tk.StringVar(value="entregado")
        estados = [("Entregado Completo", "entregado"), ("Entrega Parcial", "parcial"), ("Devolución", "devolucion")]

        for i, (text, value) in enumerate(estados):
            tk.Radiobutton(
                estado_frame,
                text=text,
                variable=self.delivery_estado_var,
                value=value,
                font=('Arial', 9)
            ).pack(side=tk.LEFT, padx=10)

        # Observaciones
        tk.Label(form_frame, text="Observaciones:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.delivery_obs_text = tk.Text(form_frame, width=60, height=3)
        self.delivery_obs_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

        # Botón de registro
        tk.Button(
            form_frame,
            text="Registrar Entrega",
            command=self.save_delivery,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).grid(row=4, column=1, pady=15)

    def create_delivery_history(self, parent):
        """Crear historial de entregas"""
        # Filtros
        filter_frame = tk.Frame(parent)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Período:", font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        self.hist_period_combo = ttk.Combobox(
            filter_frame,
            values=[str(year) for year in range(2020, 2030)],
            state='readonly',
            width=8
        )
        self.hist_period_combo.pack(side=tk.LEFT, padx=5)
        self.hist_period_combo.set(str(date.today().year))

        tk.Button(
            filter_frame,
            text="Buscar",
            command=self.search_delivery_history,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=10
        ).pack(side=tk.LEFT, padx=10)

        # Historial
        columns = ('fecha', 'empleado', 'elementos', 'entregado_por', 'estado', 'observaciones')
        self.delivery_history_tree = ttk.Treeview(parent, columns=columns, show='headings')

        # Configurar columnas
        headings = ['Fecha', 'Empleado', 'Elementos', 'Entregado Por', 'Estado', 'Observaciones']
        for col, heading in zip(columns, headings):
            self.delivery_history_tree.heading(col, text=heading)
            self.delivery_history_tree.column(col, width=120)

        # Scrollbars
        hist_scroll_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.delivery_history_tree.yview)
        hist_scroll_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.delivery_history_tree.xview)

        self.delivery_history_tree.configure(yscrollcommand=hist_scroll_y.set, xscrollcommand=hist_scroll_x.set)

        # Pack
        self.delivery_history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        hist_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        hist_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar historial de ejemplo
        self.load_sample_delivery_history()

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

        self.report_type_var = tk.StringVar(value="asignaciones")
        report_types = [
            ("Asignaciones por Período", "asignaciones"),
            ("Estado de Inventario", "inventario"),
            ("Entregas Realizadas", "entregas"),
            ("Costos de Dotación", "costos"),
            ("Reposiciones Necesarias", "reposiciones")
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
        filter_frame.grid(row=0, column=1, rowspan=6, sticky=tk.N, padx=30)

        tk.Label(filter_frame, text="Filtros:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        tk.Label(filter_frame, text="Período:", font=('Arial', 9)).pack(anchor=tk.W, pady=(10,0))
        self.rep_period_combo = ttk.Combobox(
            filter_frame,
            values=[str(year) for year in range(2020, 2030)],
            state='readonly',
            width=12
        )
        self.rep_period_combo.pack(anchor=tk.W, pady=2)
        self.rep_period_combo.set(str(date.today().year))

        tk.Label(filter_frame, text="Categoría:", font=('Arial', 9)).pack(anchor=tk.W, pady=(10,0))
        self.rep_category_combo = ttk.Combobox(
            filter_frame,
            values=["TODAS", "UNIFORME", "CALZADO", "EPP", "OTROS"],
            state='readonly',
            width=12
        )
        self.rep_category_combo.pack(anchor=tk.W, pady=2)
        self.rep_category_combo.set("TODAS")

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
    def load_data(self):
        """Cargar datos iniciales"""
        try:
            # Cargar empleados
            empleados = self.session.query(Empleado).filter_by(activo=True).all()
            emp_values = [f"{emp.empleado} - {emp.nombres} {emp.apellidos}" for emp in empleados]
            self.emp_combo['values'] = emp_values

            # Cargar departamentos para reportes
            departamentos = self.session.query(Departamento).filter_by(activo=True).all()
            dept_values = ["TODOS"] + [dept.nombre for dept in departamentos]
            self.rep_dept_combo['values'] = dept_values
            self.rep_dept_combo.set("TODOS")

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos: {str(e)}")

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

                # Actualizar labels (simular tallas)
                self.emp_info_labels["Cargo:"].config(text=cargo_nombre)
                self.emp_info_labels["Departamento:"].config(text=dept_nombre)
                self.emp_info_labels["Talla Camisa:"].config(text="M")  # Placeholder
                self.emp_info_labels["Talla Pantalón:"].config(text="32")  # Placeholder
                self.emp_info_labels["Talla Zapatos:"].config(text="42")  # Placeholder

        except Exception as e:
            messagebox.showerror("Error", f"Error cargando información del empleado: {str(e)}")

    def update_items_list(self):
        """Actualizar lista de elementos según tipo"""
        tipo = self.tipo_dotacion_var.get()
        # Aquí se cargarían los elementos según el tipo seleccionado
        # Por ahora es un placeholder

    def load_sample_assignments(self):
        """Cargar asignaciones de ejemplo"""
        sample_data = [
            ("15/01/2024", "001001 - Juan Perez", "UNIFORME", "Camisa, Pantalón", "$75.00", "PENDIENTE"),
            ("20/01/2024", "001002 - Maria Gonzalez", "CALZADO", "Zapatos de Seguridad", "$45.00", "ENTREGADA"),
            ("25/01/2024", "001003 - Carlos Rodriguez", "EPP", "Casco, Chaleco", "$35.00", "PENDIENTE"),
        ]

        for data in sample_data:
            self.assignments_tree.insert('', 'end', values=data)

    def load_sample_inventory(self):
        """Cargar inventario de ejemplo"""
        sample_data = [
            ("UNI001", "Camisa Polo", "UNIFORME", "S,M,L,XL", "100", "25", "75", "$15.00"),
            ("UNI002", "Pantalón Drill", "UNIFORME", "28,30,32,34,36", "80", "20", "60", "$25.00"),
            ("CAL001", "Zapatos Seguridad", "CALZADO", "38,39,40,41,42,43", "50", "15", "35", "$45.00"),
            ("EPP001", "Casco Seguridad", "EPP", "Único", "30", "5", "25", "$12.00"),
            ("EPP002", "Chaleco Reflectivo", "EPP", "S,M,L,XL", "40", "10", "30", "$8.00"),
        ]

        for data in sample_data:
            self.inventory_tree.insert('', 'end', values=data)

    def load_sample_delivery_history(self):
        """Cargar historial de entregas de ejemplo"""
        sample_data = [
            ("20/01/2024", "001002 - Maria Gonzalez", "Zapatos de Seguridad", "Ana Martinez", "ENTREGADO", "Entrega completa"),
            ("18/01/2024", "001004 - Ana Martinez", "Camisa, Pantalón", "Luis Vargas", "ENTREGADO", ""),
            ("15/01/2024", "001001 - Juan Perez", "Casco Seguridad", "Ana Martinez", "ENTREGADO", "Reposición"),
        ]

        for data in sample_data:
            self.delivery_history_tree.insert('', 'end', values=data)

    # Métodos de eventos
    def new_assignment(self):
        """Nueva asignación"""
        self.notebook.select(0)  # Ir a pestaña de asignación

    def register_delivery(self):
        """Registrar entrega"""
        self.notebook.select(2)  # Ir a pestaña de entrega

    def manage_inventory(self):
        """Gestionar inventario"""
        self.notebook.select(1)  # Ir a pestaña de inventario

    def register_return(self):
        """Registrar devolución"""
        messagebox.showinfo("Información", "Función de devolución en desarrollo")

    def generate_reports(self):
        """Generar reportes"""
        self.notebook.select(3)  # Ir a pestaña de reportes

    def add_element(self):
        """Agregar elemento a la asignación"""
        # Aquí se abriría un diálogo para seleccionar elementos
        messagebox.showinfo("Información", "Selector de elementos en desarrollo")

    def remove_element(self):
        """Quitar elemento de la asignación"""
        selection = self.elements_tree.selection()
        if selection:
            self.elements_tree.delete(selection[0])
            self.calculate_total()

    def calculate_total(self):
        """Calcular total de la asignación"""
        total = Decimal('0.00')
        for item in self.elements_tree.get_children():
            values = self.elements_tree.item(item)['values']
            if len(values) > 4:
                try:
                    cantidad = int(values[3])
                    costo = Decimal(values[4].replace('$', ''))
                    total += cantidad * costo
                except:
                    pass

        self.total_label.config(text=f"${total:.2f}")

    def save_assignment(self):
        """Guardar asignación"""
        if not self.emp_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un empleado")
            return

        messagebox.showinfo("Éxito", "Asignación guardada exitosamente")
        self.clear_assignment_form()

    def clear_assignment_form(self):
        """Limpiar formulario de asignación"""
        self.emp_combo.set("")
        self.obs_entry.delete(0, tk.END)
        self.total_label.config(text="$0.00")

        # Limpiar labels de empleado
        for label in self.emp_info_labels.values():
            label.config(text="")

        # Limpiar lista de elementos
        for item in self.elements_tree.get_children():
            self.elements_tree.delete(item)

    def update_assignments_list(self):
        """Actualizar lista de asignaciones"""
        messagebox.showinfo("Información", "Lista actualizada")

    def edit_assignment(self, event):
        """Editar asignación"""
        selection = self.assignments_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Edición de asignación en desarrollo")

    def add_to_inventory(self):
        """Agregar elemento al inventario"""
        if not all([self.inv_codigo_entry.get(), self.inv_nombre_entry.get(),
                   self.inv_categoria_combo.get(), self.inv_stock_entry.get()]):
            messagebox.showwarning("Advertencia", "Complete todos los campos obligatorios")
            return

        messagebox.showinfo("Éxito", "Elemento agregado al inventario")

    def update_stock(self):
        """Actualizar stock"""
        selection = self.inventory_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Actualización de stock en desarrollo")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un elemento")

    def filter_inventory(self):
        """Filtrar inventario"""
        messagebox.showinfo("Información", "Filtro aplicado")

    def save_delivery(self):
        """Guardar entrega"""
        if not self.delivery_assignment_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione una asignación")
            return

        messagebox.showinfo("Éxito", "Entrega registrada exitosamente")

    def search_delivery_history(self):
        """Buscar en historial de entregas"""
        messagebox.showinfo("Información", "Búsqueda actualizada")

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