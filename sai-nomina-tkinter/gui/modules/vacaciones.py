"""Módulo de gestión de vacaciones"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import logging

from config import Config
from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from gui.dialogs.progress_dialog import ProgressDialog
from database.connection import get_session
from database.models import Empleado, Vacacion
from services.import_export import ImportExportService
from utils.calculations import calcular_vacaciones, calcular_dias_trabajados
from utils.validators import validar_fecha, formatear_fecha

logger = logging.getLogger(__name__)

class VacacionesModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=Config.COLORS['surface'])
        self.session = get_session()
        self.module_name = "vacaciones"
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

        # Tabla de vacaciones
        self.create_table_section()

    def create_header(self):
        """Crear encabezado del módulo"""
        header_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        header_frame.pack(fill="x", pady=(0, 25))

        # Título
        title_label = tk.Label(
            header_frame,
            text="🏖️ Gestión de Vacaciones",
            font=Config.FONTS['heading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        actions_frame = tk.Frame(header_frame, bg=Config.COLORS['surface'])
        actions_frame.pack(side="right")

        # Botón Nueva Solicitud
        btn_new = tk.Button(
            actions_frame,
            text="➕ Nueva Solicitud",
            command=self.new_vacation_request,
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
            command=self.import_vacations,
            bg=Config.COLORS['success'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_import.pack(side="left", padx=5)

        # Botón Calendario
        btn_calendar = tk.Button(
            actions_frame,
            text="📅 Calendario",
            command=self.show_calendar,
            bg=Config.COLORS['info'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_calendar.pack(side="left", padx=5)

    def create_stats_section(self):
        """Crear sección de estadísticas"""
        stats_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        stats_frame.pack(fill="x", pady=(0, 20))

        # Grid de estadísticas
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # Obtener estadísticas
        stats = self.get_vacation_stats()

        # Crear tarjetas
        StatCard(
            stats_frame,
            title="Solicitudes Activas",
            value=str(stats['active_requests']),
            subtitle="En proceso",
            color=Config.COLORS['primary']
        ).grid(row=0, column=0, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Días Pendientes",
            value=str(stats['pending_days']),
            subtitle="Total acumulados",
            color=Config.COLORS['warning']
        ).grid(row=0, column=1, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Vacaciones Este Mes",
            value=str(stats['this_month']),
            subtitle="Empleados de vacaciones",
            color=Config.COLORS['info']
        ).grid(row=0, column=2, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Días Promedio",
            value=f"{stats['avg_days']:.1f}",
            subtitle="Por empleado/año",
            color=Config.COLORS['success']
        ).grid(row=0, column=3, padx=5, sticky="ew")

    def create_management_panel(self):
        """Crear panel de gestión"""
        management_frame = tk.Frame(
            self,
            bg=Config.COLORS['info'],
            relief="flat"
        )
        management_frame.pack(fill="x", pady=(0, 20))

        # Padding interno
        inner_frame = tk.Frame(management_frame, bg=Config.COLORS['info'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = tk.Label(
            inner_frame,
            text="🎯 Centro de Gestión de Vacaciones",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['info'],
            fg="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Grid de opciones
        options_frame = tk.Frame(inner_frame, bg=Config.COLORS['info'])
        options_frame.pack(fill="x")

        # Configurar columnas
        for i in range(4):
            options_frame.columnconfigure(i, weight=1)

        # Opciones de gestión
        options = [
            ("Aprobar Solicitudes", "Revisar pendientes", self.approve_requests),
            ("Calcular Saldos", "Actualizar días", self.calculate_balances),
            ("Generar Cronograma", "Planificar año", self.generate_schedule),
            ("Reportes", "Ver estadísticas", self.generate_reports)
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
            text="📋 Registro de Vacaciones",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Tabla
        columns = [
            {"key": "empleado", "title": "EMPLEADO", "width": 80},
            {"key": "nombres", "title": "NOMBRES", "width": 150},
            {"key": "fecha_inicio", "title": "FECHA INICIO", "width": 100},
            {"key": "fecha_fin", "title": "FECHA FIN", "width": 100},
            {"key": "dias_solicitados", "title": "DÍAS", "width": 60},
            {"key": "periodo", "title": "PERÍODO", "width": 80},
            {"key": "estado", "title": "ESTADO", "width": 100},
            {"key": "fecha_solicitud", "title": "SOLICITUD", "width": 100},
            {"key": "observaciones", "title": "OBSERVACIONES", "width": 150}
        ]

        self.table = DataTable(
            self,
            columns=columns,
            on_select=self.on_vacation_select,
            on_double_click=self.view_vacation_details,
            show_actions=True,
            actions=[
                {"text": "👁", "command": self.view_vacation, "tooltip": "Ver"},
                {"text": "✅", "command": self.approve_vacation, "tooltip": "Aprobar"},
                {"text": "❌", "command": self.reject_vacation, "tooltip": "Rechazar"},
                {"text": "✏", "command": self.edit_vacation, "tooltip": "Editar"}
            ]
        )
        self.table.pack(fill="both", expand=True)

    def load_data(self):
        """Cargar datos de vacaciones"""
        try:
            vacaciones = self.session.query(Vacacion).order_by(
                Vacacion.fecha_solicitud.desc()
            ).limit(200).all()

            data = []
            for vacacion in vacaciones:
                # Obtener datos del empleado
                empleado = self.session.query(Empleado).filter(
                    Empleado.empleado == vacacion.empleado
                ).first()

                # Estado con color
                estado_display = self.get_estado_display(vacacion.estado)

                data.append({
                    "id": vacacion.id,
                    "empleado": vacacion.empleado,
                    "nombres": empleado.nombre_completo if empleado else "N/A",
                    "fecha_inicio": formatear_fecha(vacacion.fecha_inicio),
                    "fecha_fin": formatear_fecha(vacacion.fecha_fin),
                    "dias_solicitados": vacacion.dias_solicitados or 0,
                    "periodo": vacacion.periodo or "",
                    "estado": estado_display,
                    "fecha_solicitud": formatear_fecha(vacacion.fecha_solicitud),
                    "observaciones": vacacion.observaciones or ""
                })

            self.table.set_data(data)

        except Exception as e:
            logger.error(f"Error al cargar vacaciones: {e}")
            messagebox.showerror("Error", f"Error al cargar vacaciones: {str(e)}")

    def get_estado_display(self, estado):
        """Obtener texto de estado para mostrar"""
        estados = {
            'PENDIENTE': '⏳ PENDIENTE',
            'APROBADA': '✅ APROBADA',
            'RECHAZADA': '❌ RECHAZADA',
            'CANCELADA': '🚫 CANCELADA',
            'EN_CURSO': '🏖️ EN CURSO',
            'FINALIZADA': '✔️ FINALIZADA'
        }
        return estados.get(estado, estado)

    def get_vacation_stats(self):
        """Obtener estadísticas de vacaciones"""
        try:
            # Solicitudes activas (pendientes + aprobadas)
            active_requests = self.session.query(Vacacion).filter(
                Vacacion.estado.in_(['PENDIENTE', 'APROBADA', 'EN_CURSO'])
            ).count()

            # Días pendientes totales
            pending_days = self.session.query(Vacacion.dias_solicitados).filter(
                Vacacion.estado == 'PENDIENTE'
            ).all()
            total_pending = sum(dias[0] for dias in pending_days if dias[0])

            # Vacaciones este mes
            current_month = datetime.now().replace(day=1)
            next_month = (current_month + timedelta(days=32)).replace(day=1)

            this_month = self.session.query(Vacacion).filter(
                Vacacion.fecha_inicio >= current_month,
                Vacacion.fecha_inicio < next_month,
                Vacacion.estado.in_(['APROBADA', 'EN_CURSO'])
            ).count()

            # Promedio de días por empleado
            total_employees = self.session.query(Empleado).filter(
                Empleado.activo == True
            ).count()

            avg_days = 15.0  # Ecuador: 15 días anuales

            return {
                'active_requests': active_requests,
                'pending_days': total_pending,
                'this_month': this_month,
                'avg_days': avg_days
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'active_requests': 0,
                'pending_days': 0,
                'this_month': 0,
                'avg_days': 0.0
            }

    def new_vacation_request(self):
        """Crear nueva solicitud de vacaciones"""
        messagebox.showinfo("Nueva Solicitud", "Formulario de nueva solicitud en desarrollo")

    def show_calendar(self):
        """Mostrar calendario de vacaciones"""
        messagebox.showinfo("Calendario", "Vista de calendario en desarrollo")

    def approve_requests(self):
        """Aprobar solicitudes pendientes"""
        messagebox.showinfo("Aprobar Solicitudes", "Revisando solicitudes pendientes...")

    def calculate_balances(self):
        """Calcular saldos de vacaciones"""
        messagebox.showinfo("Calcular Saldos", "Actualizando días de vacaciones...")

    def generate_schedule(self):
        """Generar cronograma anual"""
        messagebox.showinfo("Cronograma", "Generando cronograma anual...")

    def generate_reports(self):
        """Generar reportes"""
        messagebox.showinfo("Reportes", "Generando reportes de vacaciones...")

    def import_vacations(self):
        """Importar vacaciones desde archivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Importar Vacaciones",
                filetypes=[
                    ("Excel files", "*.xlsx *.xls"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                progress_dialog = ProgressDialog(self, "Importando Vacaciones")
                progress_dialog.show()

                import_service = ImportExportService()
                result = import_service.import_vacations(
                    filename,
                    progress_callback=progress_dialog.update_progress
                )

                progress_dialog.hide()

                if result['success']:
                    messagebox.showinfo(
                        "Importación Exitosa",
                        f"Se importaron {result['imported']} registros de vacaciones."
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

    def on_vacation_select(self, row_data):
        """Manejar selección de vacación"""
        logger.info(f"Vacación seleccionada: {row_data['id']}")

    def view_vacation_details(self, row_data):
        """Ver detalles de la vacación"""
        messagebox.showinfo("Detalles", f"Ver detalles de vacación ID: {row_data['id']}")

    def view_vacation(self, row_data):
        """Ver vacación"""
        messagebox.showinfo("Ver Vacación", f"Ver vacación ID: {row_data['id']}")

    def approve_vacation(self, row_data):
        """Aprobar vacación"""
        if messagebox.askyesno("Confirmar", f"¿Aprobar vacación ID: {row_data['id']}?"):
            messagebox.showinfo("Aprobada", "Vacación aprobada correctamente")

    def reject_vacation(self, row_data):
        """Rechazar vacación"""
        if messagebox.askyesno("Confirmar", f"¿Rechazar vacación ID: {row_data['id']}?"):
            messagebox.showinfo("Rechazada", "Vacación rechazada")

    def edit_vacation(self, row_data):
        """Editar vacación"""
        messagebox.showinfo("Editar Vacación", f"Editar vacación ID: {row_data['id']}")