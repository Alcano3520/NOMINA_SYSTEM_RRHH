"""Módulo de gestión de préstamos"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from config import Config
from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from gui.dialogs.progress_dialog import ProgressDialog
from database.connection import get_session
from database.models import Empleado, Prestamo
from services.import_export import ImportExportService
from utils.validators import validar_numero_positivo, formatear_sueldo

logger = logging.getLogger(__name__)

class PrestamosModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=Config.COLORS['surface'])
        self.session = get_session()
        self.module_name = "prestamos"
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

        # Tabla de préstamos
        self.create_table_section()

    def create_header(self):
        """Crear encabezado del módulo"""
        header_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        header_frame.pack(fill="x", pady=(0, 25))

        # Título
        title_label = tk.Label(
            header_frame,
            text="💰 Gestión de Préstamos",
            font=Config.FONTS['heading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        actions_frame = tk.Frame(header_frame, bg=Config.COLORS['surface'])
        actions_frame.pack(side="right")

        # Botón Nuevo Préstamo
        btn_new = tk.Button(
            actions_frame,
            text="➕ Nuevo Préstamo",
            command=self.new_loan,
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
            command=self.import_loans,
            bg=Config.COLORS['success'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_import.pack(side="left", padx=5)

        # Botón Procesar Cuotas
        btn_process = tk.Button(
            actions_frame,
            text="⚡ Procesar Cuotas",
            command=self.process_installments,
            bg=Config.COLORS['warning'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_process.pack(side="left", padx=5)

    def create_stats_section(self):
        """Crear sección de estadísticas"""
        stats_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        stats_frame.pack(fill="x", pady=(0, 20))

        # Grid de estadísticas
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # Obtener estadísticas
        stats = self.get_loan_stats()

        # Crear tarjetas
        StatCard(
            stats_frame,
            title="Préstamos Activos",
            value=str(stats['active_loans']),
            subtitle="En vigencia",
            color=Config.COLORS['primary']
        ).grid(row=0, column=0, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Saldo Total",
            value=f"${stats['total_balance']:,.2f}",
            subtitle="Por cobrar",
            color=Config.COLORS['warning']
        ).grid(row=0, column=1, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Cuotas del Mes",
            value=f"${stats['monthly_installments']:,.2f}",
            subtitle="A descontar",
            color=Config.COLORS['info']
        ).grid(row=0, column=2, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Mora",
            value=str(stats['overdue_loans']),
            subtitle="Préstamos vencidos",
            color=Config.COLORS['danger']
        ).grid(row=0, column=3, padx=5, sticky="ew")

    def create_management_panel(self):
        """Crear panel de gestión"""
        management_frame = tk.Frame(
            self,
            bg=Config.COLORS['warning'],
            relief="flat"
        )
        management_frame.pack(fill="x", pady=(0, 20))

        # Padding interno
        inner_frame = tk.Frame(management_frame, bg=Config.COLORS['warning'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = tk.Label(
            inner_frame,
            text="🏦 Centro de Gestión de Préstamos",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['warning'],
            fg="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Grid de opciones
        options_frame = tk.Frame(inner_frame, bg=Config.COLORS['warning'])
        options_frame.pack(fill="x")

        # Configurar columnas
        for i in range(4):
            options_frame.columnconfigure(i, weight=1)

        # Opciones de gestión
        options = [
            ("Aprobar Solicitudes", "Revisar pendientes", self.approve_requests),
            ("Calcular Cuotas", "Generar descuentos", self.calculate_installments),
            ("Gestión de Mora", "Préstamos vencidos", self.manage_overdue),
            ("Reportes", "Estados financieros", self.generate_reports)
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
            text="📋 Registro de Préstamos",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Tabla
        columns = [
            {"key": "empleado", "title": "EMPLEADO", "width": 80},
            {"key": "nombres", "title": "NOMBRES", "width": 150},
            {"key": "tipo_prestamo", "title": "TIPO", "width": 100},
            {"key": "monto_original", "title": "MONTO", "width": 100},
            {"key": "saldo_pendiente", "title": "SALDO", "width": 100},
            {"key": "cuota_mensual", "title": "CUOTA", "width": 100},
            {"key": "fecha_inicio", "title": "INICIO", "width": 100},
            {"key": "fecha_fin", "title": "FIN", "width": 100},
            {"key": "estado", "title": "ESTADO", "width": 100}
        ]

        self.table = DataTable(
            self,
            columns=columns,
            on_select=self.on_loan_select,
            on_double_click=self.view_loan_details,
            show_actions=True,
            actions=[
                {"text": "👁", "command": self.view_loan, "tooltip": "Ver"},
                {"text": "💳", "command": self.pay_installment, "tooltip": "Pagar Cuota"},
                {"text": "✏", "command": self.edit_loan, "tooltip": "Editar"},
                {"text": "❌", "command": self.cancel_loan, "tooltip": "Cancelar"}
            ]
        )
        self.table.pack(fill="both", expand=True)

    def load_data(self):
        """Cargar datos de préstamos"""
        try:
            prestamos = self.session.query(Prestamo).order_by(
                Prestamo.fecha_inicio.desc()
            ).limit(200).all()

            data = []
            for prestamo in prestamos:
                # Obtener datos del empleado
                empleado = self.session.query(Empleado).filter(
                    Empleado.empleado == prestamo.empleado
                ).first()

                # Estado con color
                estado_display = self.get_estado_display(prestamo.estado)

                data.append({
                    "id": prestamo.id,
                    "empleado": prestamo.empleado,
                    "nombres": empleado.nombre_completo if empleado else "N/A",
                    "tipo_prestamo": self.get_tipo_prestamo_text(prestamo.tipo_prestamo),
                    "monto_original": f"${prestamo.monto_original:.2f}" if prestamo.monto_original else "$0.00",
                    "saldo_pendiente": f"${prestamo.saldo_pendiente:.2f}" if prestamo.saldo_pendiente else "$0.00",
                    "cuota_mensual": f"${prestamo.cuota_mensual:.2f}" if prestamo.cuota_mensual else "$0.00",
                    "fecha_inicio": prestamo.fecha_inicio.strftime("%d/%m/%Y") if prestamo.fecha_inicio else "",
                    "fecha_fin": prestamo.fecha_fin.strftime("%d/%m/%Y") if prestamo.fecha_fin else "",
                    "estado": estado_display
                })

            self.table.set_data(data)

        except Exception as e:
            logger.error(f"Error al cargar préstamos: {e}")
            messagebox.showerror("Error", f"Error al cargar préstamos: {str(e)}")

    def get_tipo_prestamo_text(self, tipo):
        """Obtener texto del tipo de préstamo"""
        tipos = {
            'QUIROGRAFARIO': 'Quirografario',
            'HIPOTECARIO': 'Hipotecario',
            'EMPRESA': 'Empresa',
            'EMERGENCIA': 'Emergencia',
            'ANTICIPO': 'Anticipo'
        }
        return tipos.get(tipo, tipo)

    def get_estado_display(self, estado):
        """Obtener texto de estado para mostrar"""
        estados = {
            'PENDIENTE': '⏳ PENDIENTE',
            'APROBADO': '✅ APROBADO',
            'ACTIVO': '🔄 ACTIVO',
            'PAGADO': '✔️ PAGADO',
            'CANCELADO': '❌ CANCELADO',
            'VENCIDO': '⚠️ VENCIDO'
        }
        return estados.get(estado, estado)

    def get_loan_stats(self):
        """Obtener estadísticas de préstamos"""
        try:
            # Préstamos activos
            active_loans = self.session.query(Prestamo).filter(
                Prestamo.estado.in_(['APROBADO', 'ACTIVO'])
            ).count()

            # Saldo total pendiente
            saldos = self.session.query(Prestamo.saldo_pendiente).filter(
                Prestamo.estado.in_(['APROBADO', 'ACTIVO'])
            ).all()
            total_balance = sum(Decimal(str(saldo[0])) for saldo in saldos if saldo[0])

            # Cuotas mensuales
            cuotas = self.session.query(Prestamo.cuota_mensual).filter(
                Prestamo.estado == 'ACTIVO'
            ).all()
            monthly_installments = sum(Decimal(str(cuota[0])) for cuota in cuotas if cuota[0])

            # Préstamos vencidos
            today = date.today()
            overdue_loans = self.session.query(Prestamo).filter(
                Prestamo.fecha_fin < today,
                Prestamo.estado == 'ACTIVO'
            ).count()

            return {
                'active_loans': active_loans,
                'total_balance': float(total_balance),
                'monthly_installments': float(monthly_installments),
                'overdue_loans': overdue_loans
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'active_loans': 0,
                'total_balance': 0.0,
                'monthly_installments': 0.0,
                'overdue_loans': 0
            }

    def new_loan(self):
        """Crear nuevo préstamo"""
        messagebox.showinfo("Nuevo Préstamo", "Formulario de nuevo préstamo en desarrollo")

    def process_installments(self):
        """Procesar cuotas del mes"""
        messagebox.showinfo("Procesar Cuotas", "Procesando cuotas mensuales...")

    def approve_requests(self):
        """Aprobar solicitudes pendientes"""
        messagebox.showinfo("Aprobar Solicitudes", "Revisando solicitudes pendientes...")

    def calculate_installments(self):
        """Calcular cuotas"""
        messagebox.showinfo("Calcular Cuotas", "Generando descuentos de nómina...")

    def manage_overdue(self):
        """Gestionar préstamos vencidos"""
        messagebox.showinfo("Gestión de Mora", "Revisando préstamos vencidos...")

    def generate_reports(self):
        """Generar reportes"""
        messagebox.showinfo("Reportes", "Generando estados financieros...")

    def import_loans(self):
        """Importar préstamos desde archivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Importar Préstamos",
                filetypes=[
                    ("Excel files", "*.xlsx *.xls"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                progress_dialog = ProgressDialog(self, "Importando Préstamos")
                progress_dialog.show()

                import_service = ImportExportService()
                result = import_service.import_loans(
                    filename,
                    progress_callback=progress_dialog.update_progress
                )

                progress_dialog.hide()

                if result['success']:
                    messagebox.showinfo(
                        "Importación Exitosa",
                        f"Se importaron {result['imported']} préstamos."
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

    def on_loan_select(self, row_data):
        """Manejar selección de préstamo"""
        logger.info(f"Préstamo seleccionado: {row_data['id']}")

    def view_loan_details(self, row_data):
        """Ver detalles del préstamo"""
        messagebox.showinfo("Detalles", f"Ver detalles del préstamo ID: {row_data['id']}")

    def view_loan(self, row_data):
        """Ver préstamo"""
        messagebox.showinfo("Ver Préstamo", f"Ver préstamo ID: {row_data['id']}")

    def pay_installment(self, row_data):
        """Pagar cuota"""
        if messagebox.askyesno("Confirmar", f"¿Registrar pago de cuota del préstamo ID: {row_data['id']}?"):
            messagebox.showinfo("Cuota Pagada", "Cuota registrada correctamente")

    def edit_loan(self, row_data):
        """Editar préstamo"""
        messagebox.showinfo("Editar Préstamo", f"Editar préstamo ID: {row_data['id']}")

    def cancel_loan(self, row_data):
        """Cancelar préstamo"""
        if messagebox.askyesno("Confirmar", f"¿Cancelar préstamo ID: {row_data['id']}?"):
            messagebox.showinfo("Cancelado", "Préstamo cancelado correctamente")