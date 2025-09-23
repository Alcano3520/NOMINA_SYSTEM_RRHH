"""Módulo de gestión de dotación y uniformes"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import logging

from config import Config
from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from gui.dialogs.progress_dialog import ProgressDialog
from database.connection import get_session
from database.models import Empleado, Dotacion
from services.import_export import ImportExportService
from utils.validators import validar_numero_positivo, formatear_sueldo

logger = logging.getLogger(__name__)

class DotacionModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=Config.COLORS['surface'])
        self.session = get_session()
        self.module_name = "dotacion"
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configurar la interfaz del módulo"""
        self.configure(padx=25, pady=25)

        # Header del módulo
        self.create_header()

        # Estadísticas
        self.create_stats_section()

        # Panel de gestión
        self.create_management_panel()

        # Tabla de dotación
        self.create_table_section()

    def create_header(self):
        """Crear encabezado del módulo"""
        header_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        header_frame.pack(fill="x", pady=(0, 25))

        # Título
        title_label = tk.Label(
            header_frame,
            text="👔 Gestión de Dotación",
            font=Config.FONTS['heading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        actions_frame = tk.Frame(header_frame, bg=Config.COLORS['surface'])
        actions_frame.pack(side="right")

        # Botón Nueva Entrega
        btn_new = tk.Button(
            actions_frame,
            text="➕ Nueva Entrega",
            command=self.new_delivery,
            bg=Config.COLORS['primary'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_new.pack(side="left", padx=5)

        # Botón Importar
        btn_import = tk.Button(
            actions_frame,
            text="⬆ Importar",
            command=self.import_dotacion,
            bg=Config.COLORS['success'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_import.pack(side="left", padx=5)

        # Botón Inventario
        btn_inventory = tk.Button(
            actions_frame,
            text="📦 Inventario",
            command=self.manage_inventory,
            bg=Config.COLORS['info'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_inventory.pack(side="left", padx=5)

    def create_stats_section(self):
        """Crear sección de estadísticas"""
        stats_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        stats_frame.pack(fill="x", pady=(0, 20))

        # Grid de estadísticas
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # Obtener estadísticas
        stats = self.get_dotacion_stats()

        # Crear tarjetas
        StatCard(
            stats_frame,
            title="Entregas del Año",
            value=str(stats['year_deliveries']),
            subtitle="Total registradas",
            color=Config.COLORS['primary']
        ).grid(row=0, column=0, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Valor Total",
            value=f"${stats['total_value']:,.2f}",
            subtitle="Invertido en dotación",
            color=Config.COLORS['success']
        ).grid(row=0, column=1, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Pendientes",
            value=str(stats['pending_deliveries']),
            subtitle="Por entregar",
            color=Config.COLORS['warning']
        ).grid(row=0, column=2, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Empleados Dotados",
            value=str(stats['equipped_employees']),
            subtitle="Este año",
            color=Config.COLORS['info']
        ).grid(row=0, column=3, padx=5, sticky="ew")

    def create_management_panel(self):
        """Crear panel de gestión"""
        management_frame = tk.Frame(
            self,
            bg=Config.COLORS['secondary'],
            relief="flat"
        )
        management_frame.pack(fill="x", pady=(0, 20))

        # Padding interno
        inner_frame = tk.Frame(management_frame, bg=Config.COLORS['secondary'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = tk.Label(
            inner_frame,
            text="👕 Centro de Gestión de Dotación",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['secondary'],
            fg="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Grid de opciones
        options_frame = tk.Frame(inner_frame, bg=Config.COLORS['secondary'])
        options_frame.pack(fill="x")

        # Configurar columnas
        for i in range(4):
            options_frame.columnconfigure(i, weight=1)

        # Opciones de gestión
        options = [
            ("Uniformes", "Gestionar uniformes", self.manage_uniforms),
            ("Equipos de Trabajo", "EPP y herramientas", self.manage_equipment),
            ("Control de Tallas", "Inventario por tallas", self.manage_sizes),
            ("Reportes", "Estados y entregas", self.generate_reports)
        ]

        for i, (title, description, command) in enumerate(options):
            self.create_option_card(options_frame, title, description, i, command)

    def create_option_card(self, parent, title, description, column, command):
        """Crear tarjeta de opción"""
        card_frame = tk.Frame(
            parent,
            bg="#f0f8ff",
            relief="flat"
        )
        card_frame.grid(row=0, column=column, padx=5, pady=5, sticky="ew")

        # Bind click event
        card_frame.bind("<Button-1>", lambda e: command())

        # Contenido
        inner = tk.Frame(card_frame, bg="#f0f8ff")
        inner.pack(fill="both", expand=True, padx=15, pady=15)

        title_label = tk.Label(
            inner,
            text=title,
            font=Config.FONTS['default'],
            bg="#f0f8ff",
            fg="white"
        )
        title_label.pack()

        desc_label = tk.Label(
            inner,
            text=description,
            font=Config.FONTS['small'],
            bg="#f0f8ff",
            fg="white"
        )
        desc_label.pack(pady=(5, 0))

        # Bind events for hover effect
        for widget in [card_frame, inner, title_label, desc_label]:
            widget.bind("<Enter>", lambda e: card_frame.configure(bg="#e6f3ff"))
            widget.bind("<Leave>", lambda e: card_frame.configure(bg="#f0f8ff"))
            widget.bind("<Button-1>", lambda e: command())

    def create_table_section(self):
        """Crear sección de tabla"""
        # Título
        title_label = tk.Label(
            self,
            text="📋 Registro de Entregas de Dotación",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Tabla
        columns = [
            {"key": "empleado", "title": "EMPLEADO", "width": 80},
            {"key": "nombres", "title": "NOMBRES", "width": 150},
            {"key": "tipo_articulo", "title": "ARTÍCULO", "width": 120},
            {"key": "descripcion", "title": "DESCRIPCIÓN", "width": 150},
            {"key": "talla", "title": "TALLA", "width": 60},
            {"key": "cantidad", "title": "CANT.", "width": 60},
            {"key": "valor_unitario", "title": "VALOR", "width": 80},
            {"key": "fecha_entrega", "title": "ENTREGA", "width": 100},
            {"key": "estado", "title": "ESTADO", "width": 100}
        ]

        self.table = DataTable(
            self,
            columns=columns,
            on_select=self.on_dotacion_select,
            on_double_click=self.view_dotacion_details,
            show_actions=True,
            actions=[
                {"text": "👁", "command": self.view_dotacion, "tooltip": "Ver"},
                {"text": "✏", "command": self.edit_dotacion, "tooltip": "Editar"},
                {"text": "📋", "command": self.print_receipt, "tooltip": "Imprimir Recibo"},
                {"text": "🔄", "command": self.return_item, "tooltip": "Devolver"}
            ]
        )
        self.table.pack(fill="both", expand=True)

    def load_data(self):
        """Cargar datos de dotación"""
        try:
            dotaciones = self.session.query(Dotacion).order_by(
                Dotacion.fecha_entrega.desc()
            ).limit(200).all()

            data = []
            for dotacion in dotaciones:
                # Obtener datos del empleado
                empleado = self.session.query(Empleado).filter(
                    Empleado.empleado == dotacion.empleado
                ).first()

                # Estado con color
                estado_display = self.get_estado_display(dotacion.estado)

                data.append({
                    "id": dotacion.id,
                    "empleado": dotacion.empleado,
                    "nombres": empleado.nombre_completo if empleado else "N/A",
                    "tipo_articulo": self.get_tipo_articulo_text(dotacion.tipo_articulo),
                    "descripcion": dotacion.descripcion or "",
                    "talla": dotacion.talla or "",
                    "cantidad": dotacion.cantidad or 0,
                    "valor_unitario": f"${dotacion.valor_unitario:.2f}" if dotacion.valor_unitario else "$0.00",
                    "fecha_entrega": dotacion.fecha_entrega.strftime("%d/%m/%Y") if dotacion.fecha_entrega else "",
                    "estado": estado_display
                })

            self.table.set_data(data)

        except Exception as e:
            logger.error(f"Error al cargar dotación: {e}")
            messagebox.showerror("Error", f"Error al cargar dotación: {str(e)}")

    def get_tipo_articulo_text(self, tipo):
        """Obtener texto del tipo de artículo"""
        tipos = {
            'UNIFORME': 'Uniforme',
            'CALZADO': 'Calzado',
            'EPP': 'Equipo Protección',
            'HERRAMIENTA': 'Herramienta',
            'EQUIPO': 'Equipo de Trabajo',
            'ACCESORIO': 'Accesorio'
        }
        return tipos.get(tipo, tipo)

    def get_estado_display(self, estado):
        """Obtener texto de estado para mostrar"""
        estados = {
            'ENTREGADO': '✅ ENTREGADO',
            'PENDIENTE': '⏳ PENDIENTE',
            'DEVUELTO': '🔄 DEVUELTO',
            'DAÑADO': '⚠️ DAÑADO',
            'PERDIDO': '❌ PERDIDO'
        }
        return estados.get(estado, estado)

    def get_dotacion_stats(self):
        """Obtener estadísticas de dotación"""
        try:
            # Entregas del año actual
            current_year = datetime.now().year
            year_deliveries = self.session.query(Dotacion).filter(
                Dotacion.fecha_entrega >= date(current_year, 1, 1),
                Dotacion.estado == 'ENTREGADO'
            ).count()

            # Valor total invertido
            valores = self.session.query(Dotacion.valor_unitario, Dotacion.cantidad).filter(
                Dotacion.fecha_entrega >= date(current_year, 1, 1),
                Dotacion.estado == 'ENTREGADO'
            ).all()

            total_value = sum((valor[0] or 0) * (valor[1] or 0) for valor in valores)

            # Entregas pendientes
            pending_deliveries = self.session.query(Dotacion).filter(
                Dotacion.estado == 'PENDIENTE'
            ).count()

            # Empleados que recibieron dotación este año
            equipped_employees = self.session.query(Dotacion.empleado).filter(
                Dotacion.fecha_entrega >= date(current_year, 1, 1),
                Dotacion.estado == 'ENTREGADO'
            ).distinct().count()

            return {
                'year_deliveries': year_deliveries,
                'total_value': float(total_value),
                'pending_deliveries': pending_deliveries,
                'equipped_employees': equipped_employees
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'year_deliveries': 0,
                'total_value': 0.0,
                'pending_deliveries': 0,
                'equipped_employees': 0
            }

    def new_delivery(self):
        """Crear nueva entrega"""
        messagebox.showinfo("Nueva Entrega", "Formulario de nueva entrega en desarrollo")

    def manage_inventory(self):
        """Gestionar inventario"""
        messagebox.showinfo("Inventario", "Gestión de inventario en desarrollo")

    def manage_uniforms(self):
        """Gestionar uniformes"""
        messagebox.showinfo("Uniformes", "Gestión de uniformes...")

    def manage_equipment(self):
        """Gestionar equipos de trabajo"""
        messagebox.showinfo("Equipos", "Gestión de EPP y herramientas...")

    def manage_sizes(self):
        """Gestionar control de tallas"""
        messagebox.showinfo("Tallas", "Control de inventario por tallas...")

    def generate_reports(self):
        """Generar reportes"""
        messagebox.showinfo("Reportes", "Generando reportes de dotación...")

    def import_dotacion(self):
        """Importar dotación desde archivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Importar Dotación",
                filetypes=[
                    ("Excel files", "*.xlsx *.xls"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                progress_dialog = ProgressDialog(self, "Importando Dotación")
                progress_dialog.show()

                import_service = ImportExportService()
                result = import_service.import_dotacion(
                    filename,
                    progress_callback=progress_dialog.update_progress
                )

                progress_dialog.hide()

                if result['success']:
                    messagebox.showinfo(
                        "Importación Exitosa",
                        f"Se importaron {result['imported']} registros de dotación."
                    )
                    self.load_data()
                else:
                    messagebox.showerror(
                        "Error en Importación",
                        f"Error: {result['error']}"
                    )

        except Exception as e:
            logger.error(f"Error en importación: {e}")
            messagebox.showerror("Error", f"Error al importar: {str(e)}")

    def on_dotacion_select(self, row_data):
        """Manejar selección de dotación"""
        logger.info(f"Dotación seleccionada: {row_data['id']}")

    def view_dotacion_details(self, row_data):
        """Ver detalles de la dotación"""
        messagebox.showinfo("Detalles", f"Ver detalles de dotación ID: {row_data['id']}")

    def view_dotacion(self, row_data):
        """Ver dotación"""
        messagebox.showinfo("Ver Dotación", f"Ver dotación ID: {row_data['id']}")

    def edit_dotacion(self, row_data):
        """Editar dotación"""
        messagebox.showinfo("Editar Dotación", f"Editar dotación ID: {row_data['id']}")

    def print_receipt(self, row_data):
        """Imprimir recibo de entrega"""
        messagebox.showinfo("Imprimir", f"Imprimiendo recibo de entrega ID: {row_data['id']}")

    def return_item(self, row_data):
        """Devolver artículo"""
        if messagebox.askyesno("Confirmar", f"¿Registrar devolución del artículo ID: {row_data['id']}?"):
            messagebox.showinfo("Devuelto", "Artículo marcado como devuelto")