#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Empleados - Sistema SGN
Interfaz moderna con CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd
from datetime import datetime, date
import logging
from decimal import Decimal
import threading

from config_ctk import ConfigCTK
from database.connection import get_session
from database.models import Empleado, Departamento, Cargo

logger = logging.getLogger(__name__)

class EmpleadosModuleCTK(ctk.CTkFrame):
    """Módulo de empleados con CustomTkinter"""

    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.session = get_session()
        self.current_employee = None
        self.config = ConfigCTK

        self.pack(fill="both", expand=True)
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        """Configurar interfaz moderna del módulo"""
        # Header del módulo
        self.create_module_header()

        # Container principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Panel de búsqueda
        self.create_search_panel(main_container)

        # Container de contenido (lista + detalles)
        content_container = ctk.CTkFrame(main_container, fg_color="transparent")
        content_container.pack(fill="both", expand=True, pady=(10, 0))

        # Configurar grid para layout responsivo
        content_container.grid_columnconfigure(0, weight=1)  # Lista de empleados
        content_container.grid_columnconfigure(1, weight=2)  # Panel de detalles
        content_container.grid_rowconfigure(0, weight=1)

        # Panel izquierdo - Lista de empleados
        self.create_employee_list(content_container)

        # Panel derecho - Detalles del empleado
        self.create_employee_details(content_container)

    def create_module_header(self):
        """Crear header del módulo"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=15)

        # Título y descripción
        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 Gestión de Empleados",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Gestión completa del personal - Datos generales, ingresos, descuentos y más",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Separador
        separator = ctk.CTkFrame(header_frame, height=2)
        separator.pack(fill="x", pady=(15, 0))

    def create_search_panel(self, parent):
        """Crear panel de búsqueda moderno"""
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", pady=(0, 10))

        # Header del panel de búsqueda
        search_header = ctk.CTkLabel(
            search_frame,
            text="🔍 Búsqueda y Filtros",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_header.pack(anchor="w", padx=15, pady=(15, 5))

        # Container para los controles de búsqueda
        search_controls = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_controls.pack(fill="x", padx=15, pady=(0, 15))

        # Configurar grid para controles responsivos
        search_controls.grid_columnconfigure((0, 1, 2), weight=1)

        # Row 1 - Campos de búsqueda
        # Búsqueda por nombre
        name_label = ctk.CTkLabel(search_controls, text="Nombre:")
        name_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)

        self.name_search_var = ctk.StringVar()
        self.name_search_entry = ctk.CTkEntry(
            search_controls,
            textvariable=self.name_search_var,
            placeholder_text="Buscar por nombre...",
            height=32
        )
        self.name_search_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=5)

        # Búsqueda por cédula
        cedula_label = ctk.CTkLabel(search_controls, text="Cédula:")
        cedula_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.cedula_search_var = ctk.StringVar()
        self.cedula_search_entry = ctk.CTkEntry(
            search_controls,
            textvariable=self.cedula_search_var,
            placeholder_text="Buscar por cédula...",
            height=32
        )
        self.cedula_search_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Estado
        estado_label = ctk.CTkLabel(search_controls, text="Estado:")
        estado_label.grid(row=0, column=2, sticky="w", padx=(5, 0), pady=5)

        self.estado_search_var = ctk.StringVar(value="TODOS")
        self.estado_search_combo = ctk.CTkOptionMenu(
            search_controls,
            variable=self.estado_search_var,
            values=["TODOS", "ACT", "VAC", "LIC", "RET", "SUS"],
            height=32
        )
        self.estado_search_combo.grid(row=1, column=2, sticky="ew", padx=(5, 0), pady=5)

        # Row 2 - Botones de acción
        buttons_frame = ctk.CTkFrame(search_controls, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=10)

        # Botón buscar
        search_btn = ctk.CTkButton(
            buttons_frame,
            text="🔍 Buscar",
            command=self.search_employees,
            width=100,
            height=32
        )
        search_btn.pack(side="left", padx=(0, 5))

        # Botón limpiar
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Limpiar",
            command=self.clear_search,
            width=100,
            height=32,
            fg_color="gray"
        )
        clear_btn.pack(side="left", padx=5)

        # Botón nuevo empleado
        new_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Nuevo",
            command=self.new_employee,
            width=100,
            height=32,
            fg_color=self.config.CTK_COLORS['success']
        )
        new_btn.pack(side="left", padx=5)

        # Botón exportar
        export_btn = ctk.CTkButton(
            buttons_frame,
            text="📊 Exportar",
            command=self.export_employees,
            width=100,
            height=32,
            fg_color=self.config.CTK_COLORS['info']
        )
        export_btn.pack(side="left", padx=5)

    def create_employee_list(self, parent):
        """Crear lista de empleados moderna"""
        # Frame izquierdo
        left_frame = ctk.CTkFrame(parent)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Header de la lista
        list_header = ctk.CTkLabel(
            left_frame,
            text="📋 Lista de Empleados",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        list_header.pack(anchor="w", padx=15, pady=(15, 5))

        # Frame para la tabla de empleados
        table_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Crear scrollable frame para la lista
        self.employees_scrollable = ctk.CTkScrollableFrame(
            table_frame,
            label_text="Empleados",
            label_font=ctk.CTkFont(size=10, weight="bold")
        )
        self.employees_scrollable.pack(fill="both", expand=True)

        # Lista de empleados (se llenará dinámicamente)
        self.employee_buttons = []

    def create_employee_details(self, parent):
        """Crear panel de detalles del empleado"""
        # Frame derecho
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # Header del panel de detalles
        details_header = ctk.CTkFrame(right_frame, fg_color="transparent")
        details_header.pack(fill="x", padx=15, pady=15)

        self.details_title = ctk.CTkLabel(
            details_header,
            text="📄 Detalles del Empleado",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.details_title.pack(anchor="w")

        # Botones de acción
        action_frame = ctk.CTkFrame(details_header, fg_color="transparent")
        action_frame.pack(anchor="e", side="right")

        self.edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Editar",
            command=self.edit_employee,
            width=80,
            height=28,
            fg_color=self.config.CTK_COLORS['warning'],
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=(0, 5))

        self.save_btn = ctk.CTkButton(
            action_frame,
            text="💾 Guardar",
            command=self.save_employee,
            width=80,
            height=28,
            fg_color=self.config.CTK_COLORS['success'],
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=(0, 5))

        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Eliminar",
            command=self.delete_employee,
            width=80,
            height=28,
            fg_color=self.config.CTK_COLORS['danger'],
            state="disabled"
        )
        self.delete_btn.pack(side="left")

        # Notebook para pestañas de detalles
        self.details_notebook = ctk.CTkTabview(right_frame)
        self.details_notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Crear pestañas
        self.create_general_tab()
        self.create_personal_tab()
        self.create_job_tab()

    def create_general_tab(self):
        """Crear pestaña de datos generales"""
        tab = self.details_notebook.add("📋 General")

        # Scrollable frame para el contenido
        scrollable = ctk.CTkScrollableFrame(tab)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Información básica
        basic_frame = ctk.CTkFrame(scrollable)
        basic_frame.pack(fill="x", pady=(0, 10))

        basic_title = ctk.CTkLabel(
            basic_frame,
            text="Información Básica",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        basic_title.pack(anchor="w", padx=15, pady=(15, 10))

        # Grid para campos básicos
        fields_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        fields_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Configurar grid
        fields_frame.grid_columnconfigure((0, 2), weight=0)  # Labels
        fields_frame.grid_columnconfigure((1, 3), weight=1)  # Entries

        row = 0

        # Código empleado
        ctk.CTkLabel(fields_frame, text="Código:").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=5)
        self.codigo_var = ctk.StringVar()
        self.codigo_entry = ctk.CTkEntry(fields_frame, textvariable=self.codigo_var, width=100, state="disabled")
        self.codigo_entry.grid(row=row, column=1, sticky="ew", padx=(0, 15), pady=5)

        # Cédula
        ctk.CTkLabel(fields_frame, text="Cédula:").grid(row=row, column=2, sticky="w", padx=(0, 5), pady=5)
        self.cedula_var = ctk.StringVar()
        self.cedula_entry = ctk.CTkEntry(fields_frame, textvariable=self.cedula_var, width=120)
        self.cedula_entry.grid(row=row, column=3, sticky="ew", pady=5)

        row += 1

        # Nombres
        ctk.CTkLabel(fields_frame, text="Nombres:").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=5)
        self.nombres_var = ctk.StringVar()
        self.nombres_entry = ctk.CTkEntry(fields_frame, textvariable=self.nombres_var, width=200)
        self.nombres_entry.grid(row=row, column=1, columnspan=3, sticky="ew", pady=5)

        row += 1

        # Apellidos
        ctk.CTkLabel(fields_frame, text="Apellidos:").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=5)
        self.apellidos_var = ctk.StringVar()
        self.apellidos_entry = ctk.CTkEntry(fields_frame, textvariable=self.apellidos_var, width=200)
        self.apellidos_entry.grid(row=row, column=1, columnspan=3, sticky="ew", pady=5)

        # Fechas importantes
        dates_frame = ctk.CTkFrame(scrollable)
        dates_frame.pack(fill="x", pady=10)

        dates_title = ctk.CTkLabel(
            dates_frame,
            text="Fechas Importantes",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        dates_title.pack(anchor="w", padx=15, pady=(15, 10))

        # Grid para fechas
        date_fields = ctk.CTkFrame(dates_frame, fg_color="transparent")
        date_fields.pack(fill="x", padx=15, pady=(0, 15))

        date_fields.grid_columnconfigure((0, 2), weight=0)
        date_fields.grid_columnconfigure((1, 3), weight=1)

        row = 0

        # Fecha nacimiento
        ctk.CTkLabel(date_fields, text="F. Nacimiento:").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=5)
        self.fecha_nac_var = ctk.StringVar()
        self.fecha_nac_entry = ctk.CTkEntry(date_fields, textvariable=self.fecha_nac_var, placeholder_text="DD/MM/AAAA")
        self.fecha_nac_entry.grid(row=row, column=1, sticky="ew", padx=(0, 15), pady=5)

        # Fecha ingreso
        ctk.CTkLabel(date_fields, text="F. Ingreso:").grid(row=row, column=2, sticky="w", padx=(0, 5), pady=5)
        self.fecha_ing_var = ctk.StringVar()
        self.fecha_ing_entry = ctk.CTkEntry(date_fields, textvariable=self.fecha_ing_var, placeholder_text="DD/MM/AAAA")
        self.fecha_ing_entry.grid(row=row, column=3, sticky="ew", pady=5)

    def create_personal_tab(self):
        """Crear pestaña de datos personales"""
        tab = self.details_notebook.add("👤 Personal")

        # Placeholder para datos personales
        placeholder = ctk.CTkLabel(
            tab,
            text="🚧 Datos personales\\nPróximamente disponible",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        placeholder.pack(expand=True)

    def create_job_tab(self):
        """Crear pestaña de datos laborales"""
        tab = self.details_notebook.add("💼 Laboral")

        # Placeholder para datos laborales
        placeholder = ctk.CTkLabel(
            tab,
            text="🚧 Datos laborales\\nPróximamente disponible",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        placeholder.pack(expand=True)

    def load_employees(self):
        """Cargar empleados de la base de datos"""
        try:
            # Limpiar lista actual
            self.clear_employee_list()

            # Query empleados
            employees = self.session.query(Empleado).order_by(Empleado.apellidos, Empleado.nombres).all()

            # Crear botones para cada empleado
            for employee in employees:
                self.create_employee_button(employee)

            logger.info(f"Cargados {len(employees)} empleados")

        except Exception as e:
            logger.error(f"Error cargando empleados: {str(e)}")
            messagebox.showerror("Error", f"Error cargando empleados: {str(e)}")

    def clear_employee_list(self):
        """Limpiar lista de empleados"""
        for btn in self.employee_buttons:
            btn.destroy()
        self.employee_buttons.clear()

    def create_employee_button(self, employee):
        """Crear botón para un empleado"""
        # Crear frame para el empleado
        emp_frame = ctk.CTkFrame(self.employees_scrollable, height=60)
        emp_frame.pack(fill="x", pady=2)
        emp_frame.pack_propagate(False)

        # Información del empleado
        info_frame = ctk.CTkFrame(emp_frame, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=10, pady=8)

        # Nombre completo
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"{employee.nombres} {employee.apellidos}",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")

        # Información adicional
        info_text = f"ID: {employee.empleado} | Cédula: {employee.cedula} | Estado: {employee.estado or 'ACT'}"
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40"),
            anchor="w"
        )
        info_label.pack(anchor="w", pady=(2, 0))

        # Hacer clickeable todo el frame
        def on_click(event=None):
            self.select_employee(employee)

        emp_frame.bind("<Button-1>", on_click)
        info_frame.bind("<Button-1>", on_click)
        name_label.bind("<Button-1>", on_click)
        info_label.bind("<Button-1>", on_click)

        self.employee_buttons.append(emp_frame)

    def select_employee(self, employee):
        """Seleccionar empleado y mostrar detalles"""
        try:
            self.current_employee = employee
            self.show_employee_details(employee)

            # Habilitar botones de acción
            self.edit_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")

        except Exception as e:
            logger.error(f"Error seleccionando empleado: {str(e)}")
            messagebox.showerror("Error", f"Error mostrando detalles: {str(e)}")

    def show_employee_details(self, employee):
        """Mostrar detalles del empleado seleccionado"""
        try:
            # Llenar campos básicos
            self.codigo_var.set(employee.empleado or "")
            self.cedula_var.set(employee.cedula or "")
            self.nombres_var.set(employee.nombres or "")
            self.apellidos_var.set(employee.apellidos or "")

            # Fechas
            if employee.fecha_nac:
                self.fecha_nac_var.set(employee.fecha_nac.strftime("%d/%m/%Y"))
            else:
                self.fecha_nac_var.set("")

            if employee.fecha_ing:
                self.fecha_ing_var.set(employee.fecha_ing.strftime("%d/%m/%Y"))
            else:
                self.fecha_ing_var.set("")

            # Actualizar título
            self.details_title.configure(
                text=f"📄 {employee.nombres} {employee.apellidos}"
            )

        except Exception as e:
            logger.error(f"Error mostrando detalles: {str(e)}")

    def clear_employee_details(self):
        """Limpiar panel de detalles"""
        self.codigo_var.set("")
        self.cedula_var.set("")
        self.nombres_var.set("")
        self.apellidos_var.set("")
        self.fecha_nac_var.set("")
        self.fecha_ing_var.set("")

        self.details_title.configure(text="📄 Detalles del Empleado")

        # Deshabilitar botones
        self.edit_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")

        self.current_employee = None

    # Funciones de acción (placeholders por ahora)
    def search_employees(self):
        """Buscar empleados"""
        # Placeholder - implementar filtros
        self.load_employees()

    def clear_search(self):
        """Limpiar búsqueda"""
        self.name_search_var.set("")
        self.cedula_search_var.set("")
        self.estado_search_var.set("TODOS")
        self.load_employees()

    def new_employee(self):
        """Crear nuevo empleado"""
        messagebox.showinfo("Info", "Función de nuevo empleado en desarrollo")

    def edit_employee(self):
        """Editar empleado actual"""
        if self.current_employee:
            messagebox.showinfo("Info", f"Editando empleado: {self.current_employee.nombres}")

    def save_employee(self):
        """Guardar cambios del empleado"""
        messagebox.showinfo("Info", "Función de guardado en desarrollo")

    def delete_employee(self):
        """Eliminar empleado actual"""
        if self.current_employee:
            if messagebox.askyesno("Confirmar", f"¿Eliminar empleado {self.current_employee.nombres}?"):
                messagebox.showinfo("Info", "Función de eliminación en desarrollo")

    def export_employees(self):
        """Exportar empleados"""
        messagebox.showinfo("Info", "Función de exportación en desarrollo")