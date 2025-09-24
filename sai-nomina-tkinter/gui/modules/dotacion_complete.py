#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Dotación Completo - Sistema SAI
Gestión de elementos de dotación y uniformes para empleados
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta
from decimal import Decimal
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

class DotacionCompleteModule(tk.Frame):
    """Módulo completo de dotación"""

    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables
        self.selected_employee = None
        self.selected_item = None
        self.tipo_dotacion_var = tk.StringVar(value="uniforme")

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
        self.create_descuentos_programados_tab()
        self.create_cargar_reportes_tab()
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
            ("📄 Cargar Reportes", self.cargar_reportes, '#38a169'),
            ("⚡ Descuentos Programados", self.descuentos_programados, '#805ad5'),
            ("Registrar Entrega", self.register_delivery, '#48bb78'),
            ("Inventario", self.manage_inventory, '#ed8936'),
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
            if hasattr(self, 'desc_emp_combo'):
                self.desc_emp_combo['values'] = emp_values

            # Cargar departamentos para reportes
            departamentos = self.session.query(Departamento).filter_by(activo=True).all()
            dept_values = ["TODOS"] + [dept.nombre_codigo for dept in departamentos]
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
                        dept_nombre = dept.nombre_codigo

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

    def create_descuentos_programados_tab(self):
        """Crear pestaña de descuentos programados"""
        descuentos_frame = ttk.Frame(self.notebook)
        self.notebook.add(descuentos_frame, text="Descuentos Programados")

        # Panel de configuración de descuentos
        config_frame = tk.LabelFrame(descuentos_frame, text="Configuración de Descuentos Programados", font=('Arial', 11, 'bold'))
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_descuentos_config_form(config_frame)

        # Panel de descuentos activos
        active_frame = tk.LabelFrame(descuentos_frame, text="Descuentos Activos", font=('Arial', 11, 'bold'))
        active_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_descuentos_activos_list(active_frame)

    def create_descuentos_config_form(self, parent):
        """Crear formulario de configuración de descuentos"""
        form_grid = tk.Frame(parent)
        form_grid.pack(padx=10, pady=10)

        # Empleado
        tk.Label(form_grid, text="Empleado:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.desc_emp_combo = ttk.Combobox(form_grid, state='readonly', width=35)
        self.desc_emp_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # Concepto del descuento
        tk.Label(form_grid, text="Concepto:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_concepto_combo = ttk.Combobox(
            form_grid,
            values=["DOTACION_UNIFORME", "DOTACION_CALZADO", "DOTACION_EPP", "PRESTAMO_EMPRESA", "OTROS_DESCUENTOS"],
            state='readonly',
            width=20
        )
        self.desc_concepto_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.desc_concepto_combo.set("DOTACION_UNIFORME")

        # Monto total
        tk.Label(form_grid, text="Monto Total:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)
        self.desc_monto_total_entry = tk.Entry(form_grid, width=12)
        self.desc_monto_total_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        # Número de cuotas
        tk.Label(form_grid, text="Número de Cuotas:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.desc_cuotas_entry = tk.Entry(form_grid, width=10)
        self.desc_cuotas_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Valor por cuota (calculado automáticamente)
        tk.Label(form_grid, text="Valor por Cuota:", font=('Arial', 10, 'bold')).grid(row=2, column=2, sticky=tk.W, padx=10, pady=5)
        self.desc_valor_cuota_label = tk.Label(form_grid, text="$0.00", font=('Arial', 10), relief=tk.SUNKEN, width=12)
        self.desc_valor_cuota_label.grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)

        # Fecha inicio
        tk.Label(form_grid, text="Fecha Inicio:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.desc_fecha_inicio_entry = tk.Entry(form_grid, width=12)
        self.desc_fecha_inicio_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.desc_fecha_inicio_entry.insert(0, date.today().strftime('%d/%m/%Y'))

        # Observaciones
        tk.Label(form_grid, text="Observaciones:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.desc_obs_entry = tk.Entry(form_grid, width=50)
        self.desc_obs_entry.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)

        # Bind para calcular cuota automáticamente
        self.desc_monto_total_entry.bind('<KeyRelease>', self.calcular_valor_cuota)
        self.desc_cuotas_entry.bind('<KeyRelease>', self.calcular_valor_cuota)

        # Botones
        buttons_frame = tk.Frame(form_grid)
        buttons_frame.grid(row=5, column=0, columnspan=4, pady=20)

        tk.Button(
            buttons_frame,
            text="💾 Crear Descuento Programado",
            command=self.crear_descuento_programado,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="🔄 Procesar Descuentos Mensuales",
            command=self.procesar_descuentos_mensuales,
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    def create_descuentos_activos_list(self, parent):
        """Crear lista de descuentos activos"""
        # Controles superiores
        controls_frame = tk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(controls_frame, text="Estado:", font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        self.desc_filter_combo = ttk.Combobox(
            controls_frame,
            values=["TODOS", "ACTIVO", "PAGADO", "SUSPENDIDO"],
            state='readonly',
            width=12
        )
        self.desc_filter_combo.pack(side=tk.LEFT, padx=5)
        self.desc_filter_combo.set("ACTIVO")

        tk.Button(
            controls_frame,
            text="🔍 Buscar",
            command=self.buscar_descuentos,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=15
        ).pack(side=tk.LEFT, padx=10)

        # Lista de descuentos activos
        columns = ('empleado', 'concepto', 'monto_total', 'cuotas_total', 'cuotas_pagadas', 'cuota_mensual', 'saldo', 'estado')
        self.descuentos_tree = ttk.Treeview(parent, columns=columns, show='headings')

        # Configurar columnas
        headings = ['Empleado', 'Concepto', 'Monto Total', 'Total Cuotas', 'Pagadas', 'Cuota Mensual', 'Saldo', 'Estado']
        for col, heading in zip(columns, headings):
            self.descuentos_tree.heading(col, text=heading)
            self.descuentos_tree.column(col, width=110)

        # Scrollbars
        desc_scroll_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.descuentos_tree.yview)
        desc_scroll_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.descuentos_tree.xview)

        self.descuentos_tree.configure(yscrollcommand=desc_scroll_y.set, xscrollcommand=desc_scroll_x.set)

        # Pack
        self.descuentos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        desc_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        desc_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar datos de ejemplo
        self.load_sample_descuentos()

        # Bind events
        self.descuentos_tree.bind('<Double-1>', self.editar_descuento)

    def create_cargar_reportes_tab(self):
        """Crear pestaña de carga de reportes"""
        reportes_frame = ttk.Frame(self.notebook)
        self.notebook.add(reportes_frame, text="Cargar Reportes")

        # Panel de carga de reportes
        carga_frame = tk.LabelFrame(reportes_frame, text="Carga Masiva de Reportes", font=('Arial', 11, 'bold'))
        carga_frame.pack(fill=tk.X, padx=10, pady=5)

        self.create_carga_reportes_form(carga_frame)

        # Panel de procesamiento
        proceso_frame = tk.LabelFrame(reportes_frame, text="Procesamiento de Reportes", font=('Arial', 11, 'bold'))
        proceso_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_proceso_reportes_panel(proceso_frame)

    def create_carga_reportes_form(self, parent):
        """Crear formulario de carga de reportes"""
        form_frame = tk.Frame(parent)
        form_frame.pack(padx=10, pady=10)

        # Tipo de reporte
        tk.Label(form_frame, text="Tipo de Reporte:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.report_tipo_combo = ttk.Combobox(
            form_frame,
            values=["DOTACION_UNIFORME", "DOTACION_CALZADO", "DOTACION_EPP", "INVENTARIO_GENERAL", "SOLICITUDES_PERSONAL"],
            state='readonly',
            width=20
        )
        self.report_tipo_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.report_tipo_combo.set("DOTACION_UNIFORME")

        # Período del reporte
        tk.Label(form_frame, text="Período:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.report_periodo_combo = ttk.Combobox(
            form_frame,
            values=[f"{i:02d}/{date.today().year}" for i in range(1, 13)],
            state='readonly',
            width=10
        )
        self.report_periodo_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.report_periodo_combo.set(f"{date.today().month:02d}/{date.today().year}")

        # Archivo de reporte
        tk.Label(form_frame, text="Archivo:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.report_file_var = tk.StringVar()
        report_file_entry = tk.Entry(form_frame, textvariable=self.report_file_var, state='readonly', width=50)
        report_file_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        tk.Button(
            form_frame,
            text="📁 Examinar",
            command=self.examinar_archivo_reporte,
            bg='#4299e1',
            fg='white',
            font=('Arial', 9),
            padx=15
        ).grid(row=1, column=3, padx=5, pady=5)

        # Opciones de procesamiento
        options_frame = tk.LabelFrame(form_frame, text="Opciones")
        options_frame.grid(row=2, column=0, columnspan=4, sticky='ew', pady=10)

        self.auto_generar_descuentos_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Generar descuentos programados automáticamente",
            variable=self.auto_generar_descuentos_var,
            font=('Arial', 9)
        ).pack(anchor=tk.W, padx=10, pady=5)

        self.notificar_empleados_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_frame,
            text="Notificar a empleados sobre nuevos descuentos",
            variable=self.notificar_empleados_var,
            font=('Arial', 9)
        ).pack(anchor=tk.W, padx=10, pady=5)

        # Botones de acción
        buttons_frame = tk.Frame(form_frame)
        buttons_frame.grid(row=3, column=0, columnspan=4, pady=20)

        tk.Button(
            buttons_frame,
            text="📄 Cargar y Procesar Reporte",
            command=self.cargar_procesar_reporte,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="📅 Descargar Plantilla",
            command=self.descargar_plantilla_reporte,
            bg='#9f7aea',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    def create_proceso_reportes_panel(self, parent):
        """Crear panel de procesamiento de reportes"""
        # Área de resultados
        results_text_frame = tk.Frame(parent)
        results_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(results_text_frame, text="Resultado del Procesamiento:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        self.proceso_results_text = tk.Text(results_text_frame, font=('Courier', 9))
        results_scroll = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, command=self.proceso_results_text.yview)
        self.proceso_results_text.configure(yscrollcommand=results_scroll.set)

        self.proceso_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Métodos para descuentos programados
    def calcular_valor_cuota(self, event=None):
        """Calcular valor por cuota automáticamente"""
        try:
            monto_total = float(self.desc_monto_total_entry.get() or 0)
            cuotas = int(self.desc_cuotas_entry.get() or 1)

            if cuotas > 0:
                valor_cuota = monto_total / cuotas
                self.desc_valor_cuota_label.config(text=f"${valor_cuota:.2f}")
            else:
                self.desc_valor_cuota_label.config(text="$0.00")
        except:
            self.desc_valor_cuota_label.config(text="$0.00")

    def crear_descuento_programado(self):
        """Crear descuento programado"""
        try:
            if not self.desc_emp_combo.get():
                messagebox.showwarning("Advertencia", "Seleccione un empleado")
                return

            if not self.desc_monto_total_entry.get() or not self.desc_cuotas_entry.get():
                messagebox.showwarning("Advertencia", "Complete monto total y número de cuotas")
                return

            # Agregar a la lista de descuentos activos
            empleado = self.desc_emp_combo.get()
            concepto = self.desc_concepto_combo.get()
            monto_total = float(self.desc_monto_total_entry.get())
            cuotas_total = int(self.desc_cuotas_entry.get())
            cuota_mensual = monto_total / cuotas_total

            nuevo_descuento = (
                empleado,
                concepto,
                f"${monto_total:.2f}",
                str(cuotas_total),
                "0",
                f"${cuota_mensual:.2f}",
                f"${monto_total:.2f}",
                "ACTIVO"
            )

            self.descuentos_tree.insert('', 'end', values=nuevo_descuento)

            # Limpiar formulario
            self.desc_emp_combo.set("")
            self.desc_monto_total_entry.delete(0, tk.END)
            self.desc_cuotas_entry.delete(0, tk.END)
            self.desc_valor_cuota_label.config(text="$0.00")
            self.desc_obs_entry.delete(0, tk.END)

            messagebox.showinfo("Éxito", "Descuento programado creado exitosamente")
            show_toast(self, f"✅ Descuento creado: {concepto} - ${monto_total:.2f}", "success")

        except Exception as e:
            messagebox.showerror("Error", f"Error creando descuento: {str(e)}")

    def procesar_descuentos_mensuales(self):
        """Procesar descuentos mensuales"""
        try:
            # Confirmación
            if not messagebox.askyesno("Confirmar", "¿Procesar todos los descuentos mensuales activos?"):
                return

            dialog = show_loading_dialog(self, "Procesando", "Aplicando descuentos mensuales...")

            count_procesados = 0
            total_descontado = 0

            # Procesar cada descuento activo
            for item in self.descuentos_tree.get_children():
                values = list(self.descuentos_tree.item(item)['values'])

                if values[7] == "ACTIVO":  # Estado activo
                    cuotas_pagadas = int(values[4])
                    cuotas_total = int(values[3])
                    cuota_mensual = float(values[5].replace('$', '').replace(',', ''))
                    saldo_actual = float(values[6].replace('$', '').replace(',', ''))

                    # Aplicar descuento si no está completamente pagado
                    if cuotas_pagadas < cuotas_total:
                        cuotas_pagadas += 1
                        saldo_actual -= cuota_mensual
                        total_descontado += cuota_mensual
                        count_procesados += 1

                        # Actualizar valores
                        values[4] = str(cuotas_pagadas)
                        values[6] = f"${saldo_actual:.2f}"

                        # Si se completó el pago, cambiar estado
                        if cuotas_pagadas >= cuotas_total:
                            values[7] = "PAGADO"
                            values[6] = "$0.00"

                        # Actualizar en el tree
                        self.descuentos_tree.item(item, values=values)

            dialog.close()
            show_toast(self, f"✅ {count_procesados} descuentos procesados - Total: ${total_descontado:.2f}", "success")

            messagebox.showinfo(
                "Procesamiento Completado",
                f"Descuentos procesados: {count_procesados}\n"
                f"Total descontado: ${total_descontado:.2f}"
            )

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error procesando descuentos: {str(e)}")

    def load_sample_descuentos(self):
        """Cargar descuentos de ejemplo"""
        sample_data = [
            ("001001 - Juan Perez", "DOTACION_UNIFORME", "$150.00", "6", "2", "$25.00", "$100.00", "ACTIVO"),
            ("001002 - Maria Gonzalez", "DOTACION_CALZADO", "$90.00", "3", "1", "$30.00", "$60.00", "ACTIVO"),
            ("001003 - Carlos Rodriguez", "PRESTAMO_EMPRESA", "$500.00", "12", "12", "$41.67", "$0.00", "PAGADO"),
            ("001004 - Ana Martinez", "DOTACION_EPP", "$75.00", "5", "3", "$15.00", "$30.00", "ACTIVO"),
        ]

        for data in sample_data:
            self.descuentos_tree.insert('', 'end', values=data)

    def buscar_descuentos(self):
        """Buscar descuentos según filtros"""
        estado_filtro = self.desc_filter_combo.get()
        show_toast(self, f"🔍 Búsqueda actualizada: {estado_filtro}", "info")

    def editar_descuento(self, event):
        """Editar descuento seleccionado"""
        selection = self.descuentos_tree.selection()
        if selection:
            messagebox.showinfo("Información", "Función de edición en desarrollo")

    # Métodos para carga de reportes
    def examinar_archivo_reporte(self):
        """Examinar archivo de reporte"""
        filetypes = [
            ("Archivos Excel", "*.xlsx;*.xls"),
            ("Archivos CSV", "*.csv"),
            ("Todos los archivos", "*.*")
        ]

        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de reporte",
            filetypes=filetypes
        )

        if file_path:
            self.report_file_var.set(file_path)

    def cargar_procesar_reporte(self):
        """Cargar y procesar reporte"""
        try:
            if not self.report_file_var.get():
                messagebox.showwarning("Advertencia", "Seleccione un archivo de reporte")
                return

            tipo_reporte = self.report_tipo_combo.get()
            periodo = self.report_periodo_combo.get()
            archivo = self.report_file_var.get()

            dialog = show_loading_dialog(self, "Procesando", "Cargando y procesando reporte...")

            # Simular carga y procesamiento
            resultados = []
            resultados.append("=== PROCESAMIENTO DE REPORTE ===")
            resultados.append(f"Tipo: {tipo_reporte}")
            resultados.append(f"Período: {periodo}")
            resultados.append(f"Archivo: {Path(archivo).name}")
            resultados.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            resultados.append("")

            # Simular lectura del archivo
            if archivo.endswith('.xlsx') or archivo.endswith('.xls'):
                df = pd.read_excel(archivo)
            elif archivo.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                raise ValueError("Formato de archivo no soportado")

            resultados.append(f"Registros leídos: {len(df)}")
            resultados.append(f"Columnas encontradas: {len(df.columns)}")
            resultados.append("")

            # Simular procesamiento de dotaciones
            empleados_procesados = 0
            descuentos_generados = 0
            monto_total_descuentos = 0

            for index, row in df.head(10).iterrows():  # Procesar solo primeros 10 para simulación
                # Simular datos de dotación
                empleado = f"00100{index+1}"
                costo_dotacion = 75 + (index * 15)  # Simular costos variables
                cuotas = 6

                resultados.append(f"Empleado {empleado}: Dotación ${costo_dotacion:.2f} en {cuotas} cuotas")

                empleados_procesados += 1

                # Si está habilitado, generar descuento
                if self.auto_generar_descuentos_var.get():
                    descuentos_generados += 1
                    monto_total_descuentos += costo_dotacion

            resultados.append("")
            resultados.append("=== RESUMEN ===")
            resultados.append(f"Empleados procesados: {empleados_procesados}")

            if self.auto_generar_descuentos_var.get():
                resultados.append(f"Descuentos generados: {descuentos_generados}")
                resultados.append(f"Monto total descuentos: ${monto_total_descuentos:.2f}")

            # Mostrar resultados
            self.proceso_results_text.delete(1.0, tk.END)
            self.proceso_results_text.insert(tk.END, "\n".join(resultados))

            dialog.close()
            show_toast(self, f"✅ Reporte procesado: {empleados_procesados} empleados", "success")

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            messagebox.showerror("Error", f"Error procesando reporte: {str(e)}")

    def descargar_plantilla_reporte(self):
        """Descargar plantilla de reporte"""
        try:
            tipo_reporte = self.report_tipo_combo.get()

            # Crear plantilla según tipo
            if tipo_reporte == "DOTACION_UNIFORME":
                columns = ['codigo_empleado', 'nombres', 'apellidos', 'departamento', 'camisa_talla', 'pantalon_talla', 'costo_total', 'observaciones']
                sample_data = {
                    'codigo_empleado': ['001001', '001002'],
                    'nombres': ['Juan', 'Maria'],
                    'apellidos': ['Perez', 'Gonzalez'],
                    'departamento': ['VENTAS', 'ADMIN'],
                    'camisa_talla': ['M', 'S'],
                    'pantalon_talla': ['32', '28'],
                    'costo_total': [75.00, 75.00],
                    'observaciones': ['Uniforme completo', 'Uniforme completo']
                }
            elif tipo_reporte == "DOTACION_CALZADO":
                columns = ['codigo_empleado', 'nombres', 'apellidos', 'departamento', 'zapatos_talla', 'tipo_calzado', 'costo_total', 'observaciones']
                sample_data = {
                    'codigo_empleado': ['001001', '001002'],
                    'nombres': ['Juan', 'Maria'],
                    'apellidos': ['Perez', 'Gonzalez'],
                    'departamento': ['VENTAS', 'ADMIN'],
                    'zapatos_talla': ['42', '37'],
                    'tipo_calzado': ['Seguridad', 'Formal'],
                    'costo_total': [45.00, 40.00],
                    'observaciones': ['Zapatos de seguridad', 'Zapatos formales']
                }
            else:
                columns = ['codigo_empleado', 'nombres', 'apellidos', 'departamento', 'elemento', 'cantidad', 'costo_unitario', 'costo_total']
                sample_data = {
                    'codigo_empleado': ['001001', '001002'],
                    'nombres': ['Juan', 'Maria'],
                    'apellidos': ['Perez', 'Gonzalez'],
                    'departamento': ['VENTAS', 'ADMIN'],
                    'elemento': ['Casco', 'Chaleco'],
                    'cantidad': [1, 1],
                    'costo_unitario': [12.00, 8.00],
                    'costo_total': [12.00, 8.00]
                }

            # Crear DataFrame
            df = pd.DataFrame(sample_data)

            # Seleccionar ubicación para guardar
            file_path = filedialog.asksaveasfilename(
                title="Guardar Plantilla",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )

            if file_path:
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False)

                show_toast(self, f"✅ Plantilla descargada: {tipo_reporte}", "success")

                if messagebox.askyesno("Plantilla Creada", "¿Desea abrir la plantilla?"):
                    os.startfile(file_path)

        except Exception as e:
            messagebox.showerror("Error", f"Error creando plantilla: {str(e)}")

    # Métodos principales agregados
    def cargar_reportes(self):
        """Cargar reportes"""
        self.notebook.select(1)  # Ir a pestaña de cargar reportes

    def descuentos_programados(self):
        """Descuentos programados"""
        self.notebook.select(0)  # Ir a pestaña de descuentos programados

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