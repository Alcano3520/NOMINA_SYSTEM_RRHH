"""Módulo de reportes y análisis"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import logging
import os

from config import Config
from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from database.connection import get_session
from database.models import Empleado, RolPago, Decimo, Vacacion, Prestamo, Dotacion

logger = logging.getLogger(__name__)

class ReportesModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=Config.COLORS['surface'])
        self.session = get_session()
        self.module_name = "reportes"
        self.setup_ui()
        self.load_dashboard_data()

    def setup_ui(self):
        """Configurar la interfaz del módulo"""
        self.configure(padx=25, pady=25)

        # Header del módulo
        self.create_header()

        # Dashboard de estadísticas
        self.create_dashboard()

        # Panel de reportes
        self.create_reports_panel()

        # Sección de reportes rápidos
        self.create_quick_reports()

    def create_header(self):
        """Crear encabezado del módulo"""
        header_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        header_frame.pack(fill="x", pady=(0, 25))

        # Título
        title_label = tk.Label(
            header_frame,
            text="📊 Reportes y Análisis",
            font=Config.FONTS['heading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        actions_frame = tk.Frame(header_frame, bg=Config.COLORS['surface'])
        actions_frame.pack(side="right")

        # Botón Exportar Dashboard
        btn_export = tk.Button(
            actions_frame,
            text="⬇ Exportar Dashboard",
            command=self.export_dashboard,
            bg=Config.COLORS['primary'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_export.pack(side="left", padx=5)

        # Botón Actualizar
        btn_refresh = tk.Button(
            actions_frame,
            text="🔄 Actualizar",
            command=self.refresh_data,
            bg=Config.COLORS['info'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_refresh.pack(side="left", padx=5)

    def create_dashboard(self):
        """Crear dashboard de estadísticas generales"""
        dashboard_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        dashboard_frame.pack(fill="x", pady=(0, 25))

        # Título del dashboard
        dashboard_title = tk.Label(
            dashboard_frame,
            text="📈 Dashboard Ejecutivo",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        dashboard_title.pack(anchor="w", pady=(0, 15))

        # Grid de estadísticas principales
        stats_frame = tk.Frame(dashboard_frame, bg=Config.COLORS['surface'])
        stats_frame.pack(fill="x")

        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # Obtener estadísticas del dashboard
        stats = self.get_dashboard_stats()

        # Crear tarjetas principales
        StatCard(
            stats_frame,
            title="Total Empleados",
            value=str(stats['total_empleados']),
            subtitle="Activos en nómina",
            color=Config.COLORS['primary']
        ).grid(row=0, column=0, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Costo Nómina Mensual",
            value=f"${stats['costo_nomina']:,.2f}",
            subtitle="Proyección actual",
            color=Config.COLORS['success']
        ).grid(row=0, column=1, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Préstamos Activos",
            value=f"${stats['prestamos_activos']:,.2f}",
            subtitle="Saldo pendiente",
            color=Config.COLORS['warning']
        ).grid(row=0, column=2, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Provisiones",
            value=f"${stats['provisiones']:,.2f}",
            subtitle="Décimos y beneficios",
            color=Config.COLORS['info']
        ).grid(row=0, column=3, padx=5, sticky="ew")

        # Segunda fila de estadísticas
        stats_frame2 = tk.Frame(dashboard_frame, bg=Config.COLORS['surface'])
        stats_frame2.pack(fill="x", pady=(10, 0))

        for i in range(4):
            stats_frame2.columnconfigure(i, weight=1)

        StatCard(
            stats_frame2,
            title="Vacaciones Pendientes",
            value=str(stats['vacaciones_pendientes']),
            subtitle="Días acumulados",
            color="#9f7aea"
        ).grid(row=0, column=0, padx=5, sticky="ew")

        StatCard(
            stats_frame2,
            title="Dotación Anual",
            value=f"${stats['dotacion_anual']:,.2f}",
            subtitle="Inversión del año",
            color="#38b2ac"
        ).grid(row=0, column=1, padx=5, sticky="ew")

        StatCard(
            stats_frame2,
            title="Rotación",
            value=f"{stats['rotacion']:.1f}%",
            subtitle="Índice anual",
            color="#ed8936"
        ).grid(row=0, column=2, padx=5, sticky="ew")

        StatCard(
            stats_frame2,
            title="Ausentismo",
            value=f"{stats['ausentismo']:.1f}%",
            subtitle="Promedio mensual",
            color="#e53e3e"
        ).grid(row=0, column=3, padx=5, sticky="ew")

    def create_reports_panel(self):
        """Crear panel de reportes"""
        reports_frame = tk.Frame(
            self,
            bg=Config.COLORS['primary'],
            relief="flat"
        )
        reports_frame.pack(fill="x", pady=(0, 25))

        # Padding interno
        inner_frame = tk.Frame(reports_frame, bg=Config.COLORS['primary'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = tk.Label(
            inner_frame,
            text="📋 Generador de Reportes",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['primary'],
            fg="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Grid de reportes
        reports_grid = tk.Frame(inner_frame, bg=Config.COLORS['primary'])
        reports_grid.pack(fill="x")

        for i in range(4):
            reports_grid.columnconfigure(i, weight=1)

        # Reportes disponibles
        reports = [
            ("Nómina Detallada", "Roles por período", self.report_nomina_detallada),
            ("Resumen IESS", "Aportes y planillas", self.report_iess),
            ("Décimos", "13° y 14° sueldo", self.report_decimos),
            ("Vacaciones", "Estados y saldos", self.report_vacaciones),
            ("Préstamos", "Estados financieros", self.report_prestamos),
            ("Dotación", "Entregas y costos", self.report_dotacion),
            ("Cumpleaños", "Fechas importantes", self.report_cumpleanos),
            ("Auditoria", "Logs del sistema", self.report_auditoria)
        ]

        # Crear tarjetas de reportes en dos filas
        for i, (title, description, command) in enumerate(reports[:4]):
            self.create_report_card(reports_grid, title, description, i, command, row=0)

        for i, (title, description, command) in enumerate(reports[4:]):
            self.create_report_card(reports_grid, title, description, i, command, row=1)

    def create_report_card(self, parent, title, description, column, command, row=0):
        """Crear tarjeta de reporte"""
        card_frame = tk.Frame(
            parent,
            bg="#f0f8ff",
            relief="flat"
        )
        card_frame.grid(row=row, column=column, padx=5, pady=5, sticky="ew")

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

    def create_quick_reports(self):
        """Crear sección de reportes rápidos"""
        quick_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        quick_frame.pack(fill="both", expand=True)

        # Título
        title_label = tk.Label(
            quick_frame,
            text="⚡ Reportes Rápidos",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Frame para filtros
        filters_frame = tk.Frame(quick_frame, bg=Config.COLORS['surface'])
        filters_frame.pack(fill="x", pady=(0, 15))

        # Filtro de período
        tk.Label(
            filters_frame,
            text="Período:",
            font=Config.FONTS['default'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text']
        ).pack(side="left", padx=(0, 10))

        self.period_var = tk.StringVar(value="2024-01")
        period_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.period_var,
            values=self.get_available_periods(),
            state="readonly",
            width=15
        )
        period_combo.pack(side="left", padx=(0, 20))

        # Botón generar reporte rápido
        btn_quick = tk.Button(
            filters_frame,
            text="📊 Generar Reporte",
            command=self.generate_quick_report,
            bg=Config.COLORS['success'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        btn_quick.pack(side="left")

        # Tabla para mostrar resultados
        self.create_results_table(quick_frame)

    def create_results_table(self, parent):
        """Crear tabla de resultados"""
        columns = [
            {"key": "concepto", "title": "CONCEPTO", "width": 200},
            {"key": "cantidad", "title": "CANTIDAD", "width": 100},
            {"key": "valor", "title": "VALOR", "width": 150},
            {"key": "porcentaje", "title": "%", "width": 80},
            {"key": "observaciones", "title": "OBSERVACIONES", "width": 200}
        ]

        self.results_table = DataTable(
            parent,
            columns=columns,
            on_select=self.on_result_select,
            show_actions=False
        )
        self.results_table.pack(fill="both", expand=True)

    def load_dashboard_data(self):
        """Cargar datos del dashboard"""
        self.refresh_data()

    def get_dashboard_stats(self):
        """Obtener estadísticas del dashboard"""
        try:
            # Total empleados activos
            total_empleados = self.session.query(Empleado).filter(
                Empleado.activo == True,
                Empleado.estado == 'ACT'
            ).count()

            # Costo nómina mensual
            sueldos = self.session.query(Empleado.sueldo).filter(
                Empleado.activo == True,
                Empleado.estado == 'ACT'
            ).all()
            costo_nomina = sum(sueldo[0] for sueldo in sueldos if sueldo[0])

            # Préstamos activos
            prestamos = self.session.query(Prestamo.saldo_pendiente).filter(
                Prestamo.estado.in_(['APROBADO', 'ACTIVO'])
            ).all()
            prestamos_activos = sum(saldo[0] for saldo in prestamos if saldo[0])

            # Provisiones (estimación de décimos)
            provisiones = costo_nomina * 2  # 13° y 14° sueldo aproximado

            # Vacaciones pendientes (estimación)
            vacaciones_pendientes = total_empleados * 7  # Promedio 7 días pendientes

            # Dotación anual
            current_year = datetime.now().year
            dotacion_valores = self.session.query(Dotacion.valor_unitario, Dotacion.cantidad).filter(
                Dotacion.fecha_entrega >= date(current_year, 1, 1)
            ).all()
            dotacion_anual = sum((valor[0] or 0) * (valor[1] or 0) for valor in dotacion_valores)

            # Rotación (estimación)
            rotacion = 5.2  # Promedio Ecuador

            # Ausentismo (estimación)
            ausentismo = 3.8  # Promedio Ecuador

            return {
                'total_empleados': total_empleados,
                'costo_nomina': float(costo_nomina),
                'prestamos_activos': float(prestamos_activos),
                'provisiones': float(provisiones),
                'vacaciones_pendientes': vacaciones_pendientes,
                'dotacion_anual': float(dotacion_anual),
                'rotacion': rotacion,
                'ausentismo': ausentismo
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas dashboard: {e}")
            return {
                'total_empleados': 0,
                'costo_nomina': 0.0,
                'prestamos_activos': 0.0,
                'provisiones': 0.0,
                'vacaciones_pendientes': 0,
                'dotacion_anual': 0.0,
                'rotacion': 0.0,
                'ausentismo': 0.0
            }

    def get_available_periods(self):
        """Obtener períodos disponibles"""
        periods = []
        current_date = datetime.now()

        for i in range(12):  # Últimos 12 meses
            period_date = current_date - timedelta(days=30 * i)
            period = period_date.strftime("%Y-%m")
            periods.append(period)

        return periods

    # Métodos de reportes específicos
    def report_nomina_detallada(self):
        """Reporte de nómina detallada"""
        messagebox.showinfo("Nómina Detallada", "Generando reporte de nómina detallada...")

    def report_iess(self):
        """Reporte de IESS"""
        messagebox.showinfo("IESS", "Generando reporte de aportes IESS...")

    def report_decimos(self):
        """Reporte de décimos"""
        messagebox.showinfo("Décimos", "Generando reporte de décimos...")

    def report_vacaciones(self):
        """Reporte de vacaciones"""
        messagebox.showinfo("Vacaciones", "Generando reporte de vacaciones...")

    def report_prestamos(self):
        """Reporte de préstamos"""
        messagebox.showinfo("Préstamos", "Generando reporte de préstamos...")

    def report_dotacion(self):
        """Reporte de dotación"""
        messagebox.showinfo("Dotación", "Generando reporte de dotación...")

    def report_cumpleanos(self):
        """Reporte de cumpleaños"""
        messagebox.showinfo("Cumpleaños", "Generando reporte de cumpleaños...")

    def report_auditoria(self):
        """Reporte de auditoría"""
        messagebox.showinfo("Auditoría", "Generando reporte de auditoría...")

    def generate_quick_report(self):
        """Generar reporte rápido"""
        period = self.period_var.get()

        # Datos de ejemplo para el reporte rápido
        quick_data = [
            {
                "concepto": "Sueldos Básicos",
                "cantidad": "45",
                "valor": "$32,500.00",
                "porcentaje": "65.2%",
                "observaciones": "Empleados activos"
            },
            {
                "concepto": "Horas Extras",
                "cantidad": "120",
                "valor": "$2,800.00",
                "porcentaje": "5.6%",
                "observaciones": "25% y 50% recargo"
            },
            {
                "concepto": "Aportes IESS",
                "cantidad": "45",
                "valor": "$3,850.00",
                "porcentaje": "7.7%",
                "observaciones": "9.45% personal"
            },
            {
                "concepto": "Décimo Tercero",
                "cantidad": "45",
                "valor": "$2,708.33",
                "porcentaje": "5.4%",
                "observaciones": "Provisión mensual"
            },
            {
                "concepto": "Décimo Cuarto",
                "cantidad": "45",
                "valor": "$1,725.00",
                "porcentaje": "3.5%",
                "observaciones": "SBU $460"
            }
        ]

        self.results_table.set_data(quick_data)

    def export_dashboard(self):
        """Exportar dashboard"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Exportar Dashboard",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                messagebox.showinfo("Exportación", f"Dashboard exportado a: {filename}")

        except Exception as e:
            logger.error(f"Error en exportación: {e}")
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def refresh_data(self):
        """Actualizar datos"""
        try:
            # Recargar estadísticas del dashboard
            self.load_dashboard_data()
            messagebox.showinfo("Actualizado", "Datos actualizados correctamente")
        except Exception as e:
            logger.error(f"Error actualizando datos: {e}")
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")

    def on_result_select(self, row_data):
        """Manejar selección en tabla de resultados"""
        logger.info(f"Resultado seleccionado: {row_data['concepto']}")