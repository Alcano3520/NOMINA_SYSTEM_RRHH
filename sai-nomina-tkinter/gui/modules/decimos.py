"""Módulo de gestión de décimos"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import logging

from config import Config
from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from gui.dialogs.progress_dialog import ProgressDialog
from database.connection import get_session
from database.models import Empleado, Decimo
from services.import_export import ImportExportService
from utils.calculations import calcular_decimo_tercer_sueldo, calcular_decimo_cuarto_sueldo
from utils.validators import validar_numero_positivo, formatear_sueldo

logger = logging.getLogger(__name__)

class DecimosModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=Config.COLORS['surface'])
        self.session = get_session()
        self.module_name = "decimos"
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

        # Tabla de décimos
        self.create_table_section()

    def create_header(self):
        """Crear encabezado del módulo"""
        header_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        header_frame.pack(fill="x", pady=(0, 25))

        # Título
        title_label = tk.Label(
            header_frame,
            text="🎁 Gestión de Décimos",
            font=Config.FONTS['heading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        actions_frame = tk.Frame(header_frame, bg=Config.COLORS['surface'])
        actions_frame.pack(side="right")

        # Botón Procesar Décimos
        btn_process = tk.Button(
            actions_frame,
            text="⚡ Procesar Décimos",
            command=self.process_decimos,
            bg=Config.COLORS['primary'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_process.pack(side="left", padx=5)

        # Botón Importar
        btn_import = tk.Button(
            actions_frame,
            text="⬆ Importar",
            command=self.import_decimos,
            bg=Config.COLORS['success'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_import.pack(side="left", padx=5)

        # Botón Exportar
        btn_export = tk.Button(
            actions_frame,
            text="⬇ Exportar",
            command=self.export_decimos,
            bg=Config.COLORS['info'],
            fg="white",
            font=Config.FONTS['default'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_export.pack(side="left", padx=5)

    def create_stats_section(self):
        """Crear sección de estadísticas"""
        stats_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        stats_frame.pack(fill="x", pady=(0, 20))

        # Grid de estadísticas
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # Obtener estadísticas
        stats = self.get_decimos_stats()

        # Crear tarjetas
        StatCard(
            stats_frame,
            title="Empleados Activos",
            value=str(stats['total_employees']),
            subtitle="Para procesamiento",
            color=Config.COLORS['primary']
        ).grid(row=0, column=0, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Décimo Tercero",
            value=f"${stats['decimo_tercero']:,.2f}",
            subtitle="Total anual estimado",
            color=Config.COLORS['success']
        ).grid(row=0, column=1, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Décimo Cuarto",
            value=f"${stats['decimo_cuarto']:,.2f}",
            subtitle="Total anual estimado",
            color=Config.COLORS['info']
        ).grid(row=0, column=2, padx=5, sticky="ew")

        StatCard(
            stats_frame,
            title="Procesados",
            value=str(stats['procesados']),
            subtitle="Este período",
            color=Config.COLORS['warning']
        ).grid(row=0, column=3, padx=5, sticky="ew")

    def create_processing_panel(self):
        """Crear panel de procesamiento"""
        processing_frame = tk.Frame(
            self,
            bg=Config.COLORS['success'],
            relief="flat"
        )
        processing_frame.pack(fill="x", pady=(0, 20))

        # Padding interno
        inner_frame = tk.Frame(processing_frame, bg=Config.COLORS['success'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = tk.Label(
            inner_frame,
            text="💰 Centro de Procesamiento de Décimos",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['success'],
            fg="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Grid de opciones
        options_frame = tk.Frame(inner_frame, bg=Config.COLORS['success'])
        options_frame.pack(fill="x")

        # Configurar columnas
        for i in range(4):
            options_frame.columnconfigure(i, weight=1)

        # Opciones de procesamiento
        options = [
            ("Décimo Tercero", "Procesar 13° sueldo", self.process_decimo_tercero),
            ("Décimo Cuarto", "Procesar 14° sueldo", self.process_decimo_cuarto),
            ("Provisiones", "Calcular provisiones", self.calculate_provisions),
            ("Reportes", "Generar reportes", self.generate_reports)
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
            text="📋 Registro de Décimos Procesados",
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
            {"key": "tipo_decimo", "title": "TIPO", "width": 100},
            {"key": "monto", "title": "MONTO", "width": 100},
            {"key": "fecha_pago", "title": "FECHA PAGO", "width": 100},
            {"key": "estado", "title": "ESTADO", "width": 80},
            {"key": "observaciones", "title": "OBSERVACIONES", "width": 150}
        ]

        self.table = DataTable(
            self,
            columns=columns,
            on_select=self.on_decimo_select,
            on_double_click=self.view_decimo_details,
            show_actions=True,
            actions=[
                {"text": "👁", "command": self.view_decimo, "tooltip": "Ver"},
                {"text": "✏", "command": self.edit_decimo, "tooltip": "Editar"},
                {"text": "🗑", "command": self.delete_decimo, "tooltip": "Eliminar"}
            ]
        )
        self.table.pack(fill="both", expand=True)

    def load_data(self):
        """Cargar datos de décimos"""
        try:
            decimos = self.session.query(Decimo).order_by(
                Decimo.periodo.desc()
            ).limit(200).all()

            data = []
            for decimo in decimos:
                # Obtener datos del empleado
                empleado = self.session.query(Empleado).filter(
                    Empleado.empleado == decimo.empleado
                ).first()

                tipo_text = "13° Sueldo" if decimo.tipo_decimo == 13 else "14° Sueldo"

                data.append({
                    "id": decimo.id,
                    "periodo": decimo.periodo,
                    "empleado": decimo.empleado,
                    "nombres": empleado.nombre_completo if empleado else "N/A",
                    "tipo_decimo": tipo_text,
                    "monto": f"${decimo.monto:.2f}" if decimo.monto else "$0.00",
                    "fecha_pago": decimo.fecha_pago.strftime("%d/%m/%Y") if decimo.fecha_pago else "",
                    "estado": decimo.estado or "PENDIENTE",
                    "observaciones": decimo.observaciones or ""
                })

            self.table.set_data(data)

        except Exception as e:
            logger.error(f"Error al cargar décimos: {e}")
            messagebox.showerror("Error", f"Error al cargar décimos: {str(e)}")

    def get_decimos_stats(self):
        """Obtener estadísticas de décimos"""
        try:
            total_employees = self.session.query(Empleado).filter(
                Empleado.activo == True,
                Empleado.estado == 'ACT'
            ).count()

            # Calcular décimo tercero estimado
            sueldos = self.session.query(Empleado.sueldo).filter(
                Empleado.activo == True,
                Empleado.estado == 'ACT'
            ).all()

            decimo_tercero = sum(sueldo[0] for sueldo in sueldos if sueldo[0])

            # Décimo cuarto (SBU por cada empleado)
            decimo_cuarto = total_employees * Config.SBU

            # Procesados este año
            current_year = datetime.now().year
            procesados = self.session.query(Decimo).filter(
                Decimo.periodo.like(f'{current_year}%'),
                Decimo.estado == 'PAGADO'
            ).count()

            return {
                'total_employees': total_employees,
                'decimo_tercero': float(decimo_tercero),
                'decimo_cuarto': float(decimo_cuarto),
                'procesados': procesados
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_employees': 0,
                'decimo_tercero': 0.0,
                'decimo_cuarto': 0.0,
                'procesados': 0
            }

    def process_decimos(self):
        """Procesar todos los décimos"""
        messagebox.showinfo("Procesar Décimos", "Función de procesamiento masivo en desarrollo")

    def process_decimo_tercero(self):
        """Procesar décimo tercero"""
        messagebox.showinfo("Décimo Tercero", "Procesando 13° sueldo...")

    def process_decimo_cuarto(self):
        """Procesar décimo cuarto"""
        messagebox.showinfo("Décimo Cuarto", "Procesando 14° sueldo...")

    def calculate_provisions(self):
        """Calcular provisiones"""
        messagebox.showinfo("Provisiones", "Calculando provisiones de décimos...")

    def generate_reports(self):
        """Generar reportes"""
        messagebox.showinfo("Reportes", "Generando reportes de décimos...")

    def import_decimos(self):
        """Importar décimos desde archivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Importar Décimos",
                filetypes=[
                    ("Excel files", "*.xlsx *.xls"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                progress_dialog = ProgressDialog(self, "Importando Décimos")
                progress_dialog.show()

                import_service = ImportExportService()
                result = import_service.import_decimos(
                    filename,
                    progress_callback=progress_dialog.update_progress
                )

                progress_dialog.hide()

                if result['success']:
                    messagebox.showinfo(
                        "Importación Exitosa",
                        f"Se importaron {result['imported']} décimos correctamente."
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

    def export_decimos(self):
        """Exportar décimos a archivo"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Exportar Décimos",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                import_service = ImportExportService()
                success = import_service.export_decimos(filename)

                if success:
                    messagebox.showinfo(
                        "Exportación Exitosa",
                        f"Décimos exportados a: {filename}"
                    )
                else:
                    messagebox.showerror("Error", "Error al exportar décimos")

        except Exception as e:
            logger.error(f"Error en exportación: {e}")
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def on_decimo_select(self, row_data):
        """Manejar selección de décimo"""
        logger.info(f"Décimo seleccionado: {row_data['id']}")

    def view_decimo_details(self, row_data):
        """Ver detalles del décimo"""
        messagebox.showinfo("Detalles", f"Ver detalles del décimo ID: {row_data['id']}")

    def view_decimo(self, row_data):
        """Ver décimo"""
        messagebox.showinfo("Ver Décimo", f"Ver décimo ID: {row_data['id']}")

    def edit_decimo(self, row_data):
        """Editar décimo"""
        messagebox.showinfo("Editar Décimo", f"Editar décimo ID: {row_data['id']}")

    def delete_decimo(self, row_data):
        """Eliminar décimo"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar décimo ID: {row_data['id']}?"):
            messagebox.showinfo("Eliminado", "Décimo eliminado correctamente")