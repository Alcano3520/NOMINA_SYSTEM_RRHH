"""Módulo de procesamiento de nómina"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import logging

from config import Config
from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from database.connection import get_session
from database.models import RolPago, Empleado

logger = logging.getLogger(__name__)

class NominaModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=Config.COLORS['surface'])
        self.session = get_session()
        self.module_name = "nomina"
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configurar la interfaz del módulo"""
        self.configure(padx=25, pady=25)

        # Header del módulo
        self.create_header()

        # Estadísticas
        self.create_stats_section()

        # Panel de procesamiento
        self.create_processing_panel()

        # Tabla de roles
        self.create_table_section()

    def create_header(self):
        """Crear encabezado del módulo"""
        header_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        header_frame.pack(fill="x", pady=(0, 25))

        # Título
        title_label = tk.Label(
            header_frame,
            text="💰 Procesamiento de Nómina",
            font=Config.FONTS['heading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        actions_frame = tk.Frame(header_frame, bg=Config.COLORS['surface'])
        actions_frame.pack(side="right")

        # Botón Procesar Nómina
        btn_process = tk.Button(
            actions_frame,
            text="⚡ Procesar Nómina",
            command=self.process_payroll,
            bg=Config.COLORS['primary'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_process.pack(side="left", padx=5)

        # Botón Carga Masiva
        btn_import = tk.Button(
            actions_frame,
            text="⬆ Carga Conceptos",
            command=self.import_concepts,
            bg=Config.COLORS['success'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_import.pack(side="left", padx=5)

    def create_stats_section(self):
        """Crear sección de estadísticas"""
        stats_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        stats_frame.pack(fill="x", pady=(0, 20))

        # Grid de estadísticas
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # Obtener estadísticas
        stats = self.get_payroll_stats()

        # Crear tarjetas
        StatCard(
            stats_frame,
            title="Empleados en Nómina",
            value=str(stats['total_employees']),
            subtitle="Activos para procesar",
            color=Config.COLORS['primary']
        ).grid(row=0, column=0, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Nómina del Mes",
            value=f"${stats['monthly_payroll']:,.2f}",
            subtitle="Total estimado",
            color=Config.COLORS['success']
        ).grid(row=0, column=1, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Roles Procesados",
            value=str(stats['processed_roles']),
            subtitle="Este período",
            color=Config.COLORS['info']
        ).grid(row=0, column=2, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Pendientes de Pago",
            value=str(stats['pending_payment']),
            subtitle="Roles aprobados",
            color=Config.COLORS['warning']
        ).grid(row=0, column=3, padx=5, sticky="ew")

    def create_processing_panel(self):
        """Crear panel de procesamiento"""
        # Frame con color de fondo especial
        processing_frame = tk.Frame(
            self,
            bg=Config.COLORS['info'],
            relief="flat"
        )
        processing_frame.pack(fill="x", pady=(0, 20))

        # Padding interno
        inner_frame = tk.Frame(processing_frame, bg=Config.COLORS['info'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = tk.Label(
            inner_frame,
            text="⚙️ Centro de Procesamiento",
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

        # Opciones de procesamiento
        options = [
            ("Nómina Semanal", "Procesar roles semanales"),
            ("Nómina Quincenal", "Procesar roles quincenales"),
            ("Nómina Mensual", "Procesar roles mensuales"),
            ("Provisiones", "Calcular provisiones")
        ]

        for i, (title, description) in enumerate(options):
            self.create_option_card(options_frame, title, description, i)

    def create_option_card(self, parent, title, description, column):
        """Crear tarjeta de opción"""
        card_frame = tk.Frame(
            parent,
            bg="#f0f8ff",
            relief="flat"
        )
        card_frame.grid(row=0, column=column, padx=5, pady=5, sticky="ew")

        # Contenido
        inner = tk.Frame(card_frame, bg="#f0f8ff")
        inner.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            inner,
            text=title,
            font=Config.FONTS['default'],
            bg="#f0f8ff",
            fg="white"
        ).pack()

        tk.Label(
            inner,
            text=description,
            font=Config.FONTS['small'],
            bg="#f0f8ff",
            fg="white"
        ).pack(pady=(5, 0))

    def create_table_section(self):
        """Crear sección de tabla"""
        # Título
        title_label = tk.Label(
            self,
            text="📋 Roles de Pago Procesados",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Tabla
        columns = [
            {"key": "periodo", "title": "PERÍODO", "width": 80},
            {"key": "empleado", "title": "EMPLEADO", "width": 80},
            {"key": "nombres", "title": "NOMBRES", "width": 150},
            {"key": "tipo_nomina", "title": "TIPO", "width": 80},
            {"key": "dias_trabajados", "title": "DÍAS", "width": 60},
            {"key": "total_ingresos", "title": "INGRESOS", "width": 100},
            {"key": "total_descuentos", "title": "DESCUENTOS", "width": 100},
            {"key": "neto_pagar", "title": "NETO", "width": 100},
            {"key": "estado", "title": "ESTADO", "width": 80},
            {"key": "fecha_proceso", "title": "PROCESADO", "width": 100}
        ]

        self.table = DataTable(
            self,
            columns=columns,
            on_select=self.on_role_select,
            on_double_click=self.view_role_details,
            show_actions=True,
            actions=[
                {"text": "👁", "command": self.view_role, "tooltip": "Ver"},
                {"text": "💰", "command": self.pay_role, "tooltip": "Pagar"}
            ]
        )
        self.table.pack(fill="both", expand=True)

    def load_data(self):
        """Cargar datos de roles de pago"""
        try:
            roles = self.session.query(RolPago).order_by(
                RolPago.periodo.desc()
            ).limit(100).all()

            data = []
            for rol in roles:
                # Obtener datos del empleado
                empleado = self.session.query(Empleado).filter(
                    Empleado.empleado == rol.empleado
                ).first()

                data.append({
                    "id": rol.id,
                    "periodo": rol.periodo,
                    "empleado": rol.empleado,
                    "nombres": empleado.nombre_completo if empleado else "N/A",
                    "tipo_nomina": self.get_tipo_nomina_text(rol.tipo_nomina),
                    "dias_trabajados": rol.dias_trabajados or 0,
                    "total_ingresos": f"${rol.total_ingresos:.2f}" if rol.total_ingresos else "$0.00",
                    "total_descuentos": f"${rol.total_descuentos:.2f}" if rol.total_descuentos else "$0.00",
                    "neto_pagar": f"${rol.neto_pagar:.2f}" if rol.neto_pagar else "$0.00",
                    "estado": rol.estado or "BORRADOR",
                    "fecha_proceso": rol.fecha_proceso.strftime("%d/%m/%Y") if rol.fecha_proceso else ""
                })

            self.table.set_data(data)

        except Exception as e:
            logger.error(f"Error al cargar roles: {e}")
            messagebox.showerror("Error", f"Error al cargar roles: {str(e)}")

    def get_payroll_stats(self):
        """Obtener estadísticas de nómina"""
        try:
            total_employees = self.session.query(Empleado).filter(
                Empleado.activo == True,
                Empleado.estado == 'ACT'
            ).count()

            # Calcular nómina mensual estimada
            sueldos = self.session.query(Empleado.sueldo).filter(
                Empleado.activo == True,
                Empleado.estado == 'ACT'
            ).all()

            monthly_payroll = sum(sueldo[0] for sueldo in sueldos if sueldo[0])

            # Roles procesados este mes
            current_month = datetime.now().strftime('%Y-%m')
            processed_roles = self.session.query(RolPago).filter(
                RolPago.periodo == current_month,
                RolPago.estado == 'PROCESADO'
            ).count()

            # Pendientes de pago
            pending_payment = self.session.query(RolPago).filter(
                RolPago.estado == 'PROCESADO'
            ).count()

            return {
                'total_employees': total_employees,
                'monthly_payroll': float(monthly_payroll),
                'processed_roles': processed_roles,
                'pending_payment': pending_payment
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_employees': 0,
                'monthly_payroll': 0.0,
                'processed_roles': 0,
                'pending_payment': 0
            }

    def get_tipo_nomina_text(self, tipo):
        """Convertir tipo de nómina a texto"""
        tipos = {1: "Semanal", 2: "Quincenal", 3: "Mensual"}
        return tipos.get(tipo, "Desconocido")

    def process_payroll(self):
        """Procesar nómina"""
        messagebox.showinfo("Procesar Nómina", "Función de procesamiento de nómina en desarrollo")

    def import_concepts(self):
        """Importar conceptos de nómina"""
        messagebox.showinfo("Carga Masiva", "Función de carga masiva de conceptos en desarrollo")

    def on_role_select(self, row_data):
        """Manejar selección de rol"""
        logger.info(f"Rol seleccionado: {row_data['id']}")

    def view_role_details(self, row_data):
        """Ver detalles del rol"""
        messagebox.showinfo("Detalles", f"Ver detalles del rol ID: {row_data['id']}")

    def view_role(self, row_data):
        """Ver rol"""
        messagebox.showinfo("Ver Rol", f"Ver rol ID: {row_data['id']}")

    def pay_role(self, row_data):
        """Pagar rol"""
        if messagebox.askyesno("Confirmar Pago", f"¿Confirmar pago del rol ID: {row_data['id']}?"):
            messagebox.showinfo("Pago", "Rol marcado como pagado")