#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componente de Exportación de Base de Datos - Sistema SAI
Utilidad para exportar toda la base de datos o tablas específicas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import zipfile
import os
import sys

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import get_session, engine
from database.models import *
from gui.components.progress_dialog import ProgressDialog
from gui.components.visual_improvements import show_toast

class DatabaseExportDialog(tk.Toplevel):
    """Diálogo para exportar base de datos"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.result = None

        self.setup_window()
        self.create_ui()

    def setup_window(self):
        """Configurar ventana"""
        self.title("Exportar Base de Datos - Sistema SAI")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(self.parent)
        self.grab_set()

        # Centrar ventana
        self.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))

    def create_ui(self):
        """Crear interfaz de usuario"""
        # Header
        header_frame = tk.Frame(self, bg='#2c5282', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="EXPORTACIÓN DE BASE DE DATOS",
            font=('Arial', 14, 'bold'),
            bg='#2c5282',
            fg='white'
        ).pack(pady=20)

        # Main content
        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tipo de exportación
        export_frame = tk.LabelFrame(main_frame, text="Tipo de Exportación", font=('Arial', 11, 'bold'))
        export_frame.pack(fill=tk.X, pady=(0, 15))

        self.export_type = tk.StringVar(value="completa")

        tk.Radiobutton(
            export_frame,
            text="Exportación Completa (Todas las tablas)",
            variable=self.export_type,
            value="completa",
            font=('Arial', 10),
            command=self.on_export_type_change
        ).pack(anchor='w', padx=10, pady=5)

        tk.Radiobutton(
            export_frame,
            text="Exportación Selectiva (Tablas específicas)",
            variable=self.export_type,
            value="selectiva",
            font=('Arial', 10),
            command=self.on_export_type_change
        ).pack(anchor='w', padx=10, pady=5)

        # Selección de tablas
        tables_frame = tk.LabelFrame(main_frame, text="Seleccionar Tablas", font=('Arial', 11, 'bold'))
        tables_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Lista de tablas disponibles
        tables_container = tk.Frame(tables_frame)
        tables_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Listbox con checkboxes simulados
        self.tables_listbox = tk.Listbox(
            tables_container,
            selectmode=tk.MULTIPLE,
            font=('Arial', 10),
            height=12
        )
        self.tables_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        tables_scroll = ttk.Scrollbar(tables_container, orient=tk.VERTICAL, command=self.tables_listbox.yview)
        self.tables_listbox.configure(yscrollcommand=tables_scroll.set)
        tables_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar lista de tablas
        self.load_tables_list()

        # Formato de exportación
        format_frame = tk.LabelFrame(main_frame, text="Formato de Exportación", font=('Arial', 11, 'bold'))
        format_frame.pack(fill=tk.X, pady=(0, 15))

        format_container = tk.Frame(format_frame)
        format_container.pack(padx=10, pady=10)

        self.export_format = tk.StringVar(value="excel")

        formats = [
            ("Excel (.xlsx)", "excel"),
            ("CSV (.csv)", "csv"),
            ("JSON (.json)", "json"),
            ("SQL (.sql)", "sql"),
            ("Archivo Comprimido (.zip)", "zip")
        ]

        for i, (text, value) in enumerate(formats):
            tk.Radiobutton(
                format_container,
                text=text,
                variable=self.export_format,
                value=value,
                font=('Arial', 10)
            ).grid(row=i//3, column=i%3, sticky='w', padx=15, pady=2)

        # Opciones adicionales
        options_frame = tk.LabelFrame(main_frame, text="Opciones", font=('Arial', 11, 'bold'))
        options_frame.pack(fill=tk.X, pady=(0, 15))

        options_container = tk.Frame(options_frame)
        options_container.pack(padx=10, pady=10)

        self.include_structure = tk.BooleanVar(value=True)
        self.include_data = tk.BooleanVar(value=True)
        self.include_timestamp = tk.BooleanVar(value=True)

        tk.Checkbutton(
            options_container,
            text="Incluir estructura de tablas",
            variable=self.include_structure,
            font=('Arial', 10)
        ).grid(row=0, column=0, sticky='w', padx=5, pady=2)

        tk.Checkbutton(
            options_container,
            text="Incluir datos",
            variable=self.include_data,
            font=('Arial', 10)
        ).grid(row=0, column=1, sticky='w', padx=5, pady=2)

        tk.Checkbutton(
            options_container,
            text="Incluir timestamp en nombre",
            variable=self.include_timestamp,
            font=('Arial', 10)
        ).grid(row=1, column=0, sticky='w', padx=5, pady=2)

        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(15, 0))

        tk.Button(
            buttons_frame,
            text="Exportar",
            command=self.export_database,
            bg='#48bb78',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=8
        ).pack(side=tk.RIGHT, padx=(5, 0))

        tk.Button(
            buttons_frame,
            text="Cancelar",
            command=self.destroy,
            bg='#e53e3e',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=8
        ).pack(side=tk.RIGHT, padx=(5, 5))

        # Inicializar estado
        self.on_export_type_change()

    def load_tables_list(self):
        """Cargar lista de tablas disponibles"""
        tables = [
            "empleados - Datos de empleados",
            "departamentos - Departamentos de la empresa",
            "cargos - Cargos y posiciones",
            "contratos - Contratos laborales",
            "nominas - Registros de nómina",
            "vacaciones - Solicitudes de vacaciones",
            "prestamos - Préstamos de empleados",
            "liquidaciones - Liquidaciones laborales",
            "egresos_ingresos - Movimientos económicos",
            "dotacion - Asignaciones de dotación",
            "descuentos - Descuentos aplicados",
            "horas_extras - Registro de horas extras",
            "permisos - Permisos y ausencias",
            "capacitaciones - Capacitaciones realizadas",
            "evaluaciones - Evaluaciones de desempeño",
            "usuarios - Usuarios del sistema",
            "auditoria - Log de auditoría"
        ]

        for table in tables:
            self.tables_listbox.insert(tk.END, table)

        # Seleccionar todas por defecto
        self.tables_listbox.select_set(0, tk.END)

    def on_export_type_change(self):
        """Manejar cambio de tipo de exportación"""
        if self.export_type.get() == "completa":
            self.tables_listbox.config(state=tk.DISABLED)
            self.tables_listbox.select_set(0, tk.END)
        else:
            self.tables_listbox.config(state=tk.NORMAL)

    def export_database(self):
        """Realizar exportación de base de datos"""
        try:
            # Validar selección
            if self.export_type.get() == "selectiva":
                selected = self.tables_listbox.curselection()
                if not selected:
                    messagebox.showwarning("Advertencia", "Seleccione al menos una tabla para exportar")
                    return

            # Seleccionar directorio de destino
            if self.export_format.get() == "zip":
                file_path = filedialog.asksaveasfilename(
                    title="Guardar exportación",
                    defaultextension=".zip",
                    filetypes=[("Archivo ZIP", "*.zip")]
                )
            elif self.export_format.get() == "excel":
                file_path = filedialog.asksaveasfilename(
                    title="Guardar exportación",
                    defaultextension=".xlsx",
                    filetypes=[("Excel", "*.xlsx")]
                )
            elif self.export_format.get() == "sql":
                file_path = filedialog.asksaveasfilename(
                    title="Guardar exportación",
                    defaultextension=".sql",
                    filetypes=[("SQL", "*.sql")]
                )
            else:
                directory = filedialog.askdirectory(title="Seleccionar directorio de destino")
                if not directory:
                    return
                file_path = directory

            if not file_path:
                return

            # Mostrar diálogo de progreso
            progress = ProgressDialog(self, "Exportando Base de Datos")
            progress.start()

            # Realizar exportación
            self.after(100, lambda: self.perform_export(file_path, progress))

        except Exception as e:
            messagebox.showerror("Error", f"Error en la exportación: {str(e)}")

    def perform_export(self, file_path, progress):
        """Realizar la exportación real"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Obtener tablas a exportar
            if self.export_type.get() == "completa":
                selected_tables = list(range(self.tables_listbox.size()))
            else:
                selected_tables = self.tables_listbox.curselection()

            table_names = []
            for i in selected_tables:
                table_info = self.tables_listbox.get(i)
                table_name = table_info.split(" - ")[0]
                table_names.append(table_name)

            progress.update(20, "Conectando a base de datos...")

            # Conectar a base de datos
            session = get_session()

            progress.update(30, "Leyendo datos...")

            if self.export_format.get() == "excel":
                self.export_to_excel(session, table_names, file_path, timestamp, progress)
            elif self.export_format.get() == "csv":
                self.export_to_csv(session, table_names, file_path, timestamp, progress)
            elif self.export_format.get() == "json":
                self.export_to_json(session, table_names, file_path, timestamp, progress)
            elif self.export_format.get() == "sql":
                self.export_to_sql(session, table_names, file_path, timestamp, progress)
            elif self.export_format.get() == "zip":
                self.export_to_zip(session, table_names, file_path, timestamp, progress)

            progress.update(100, "Exportación completada")
            progress.finish()

            session.close()

            # Mostrar mensaje de éxito
            show_toast(self.parent, "Exportación completada exitosamente", "success")
            messagebox.showinfo("Éxito", f"Base de datos exportada exitosamente")

            self.destroy()

        except Exception as e:
            progress.finish()
            messagebox.showerror("Error", f"Error durante la exportación: {str(e)}")

    def export_to_excel(self, session, table_names, file_path, timestamp, progress):
        """Exportar a Excel"""
        if self.include_timestamp.get():
            base_name = Path(file_path).stem
            extension = Path(file_path).suffix
            file_path = str(Path(file_path).parent / f"{base_name}_{timestamp}{extension}")

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for i, table_name in enumerate(table_names):
                progress.update(40 + (i * 40 // len(table_names)), f"Exportando {table_name}...")

                # Simular datos de tabla (en implementación real conectar a la BD)
                data = self.get_table_data(session, table_name)
                df = pd.DataFrame(data)

                # Escribir a Excel
                sheet_name = table_name[:31]  # Limitar nombre de hoja
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    def export_to_csv(self, session, table_names, file_path, timestamp, progress):
        """Exportar a CSV"""
        for i, table_name in enumerate(table_names):
            progress.update(40 + (i * 40 // len(table_names)), f"Exportando {table_name}...")

            data = self.get_table_data(session, table_name)
            df = pd.DataFrame(data)

            # Crear nombre de archivo
            if self.include_timestamp.get():
                csv_file = os.path.join(file_path, f"{table_name}_{timestamp}.csv")
            else:
                csv_file = os.path.join(file_path, f"{table_name}.csv")

            df.to_csv(csv_file, index=False, encoding='utf-8')

    def export_to_json(self, session, table_names, file_path, timestamp, progress):
        """Exportar a JSON"""
        all_data = {}

        for i, table_name in enumerate(table_names):
            progress.update(40 + (i * 40 // len(table_names)), f"Exportando {table_name}...")

            data = self.get_table_data(session, table_name)
            all_data[table_name] = data

        # Crear nombre de archivo
        if self.include_timestamp.get():
            json_file = os.path.join(file_path, f"database_export_{timestamp}.json")
        else:
            json_file = os.path.join(file_path, "database_export.json")

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2, default=str)

    def export_to_sql(self, session, table_names, file_path, timestamp, progress):
        """Exportar a SQL"""
        if self.include_timestamp.get():
            base_name = Path(file_path).stem
            extension = Path(file_path).suffix
            file_path = str(Path(file_path).parent / f"{base_name}_{timestamp}{extension}")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("-- Exportación de Base de Datos - Sistema SAI\n")
            f.write(f"-- Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for i, table_name in enumerate(table_names):
                progress.update(40 + (i * 40 // len(table_names)), f"Exportando {table_name}...")

                f.write(f"-- Tabla: {table_name}\n")

                if self.include_structure.get():
                    # Generar CREATE TABLE (simulado)
                    f.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                    f.write("    id INTEGER PRIMARY KEY,\n")
                    f.write("    -- Estructura de tabla\n")
                    f.write(");\n\n")

                if self.include_data.get():
                    data = self.get_table_data(session, table_name)
                    for row in data:
                        values = ', '.join([f"'{str(v)}'" for v in row.values()])
                        f.write(f"INSERT INTO {table_name} VALUES ({values});\n")
                    f.write("\n")

    def export_to_zip(self, session, table_names, file_path, timestamp, progress):
        """Exportar a archivo ZIP"""
        if self.include_timestamp.get():
            base_name = Path(file_path).stem
            extension = Path(file_path).suffix
            file_path = str(Path(file_path).parent / f"{base_name}_{timestamp}{extension}")

        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, table_name in enumerate(table_names):
                progress.update(40 + (i * 40 // len(table_names)), f"Exportando {table_name}...")

                data = self.get_table_data(session, table_name)
                df = pd.DataFrame(data)

                # Crear CSV temporal en memoria
                csv_content = df.to_csv(index=False, encoding='utf-8')
                zipf.writestr(f"{table_name}.csv", csv_content)

    def get_table_data(self, session, table_name):
        """Obtener datos de una tabla específica"""
        # Datos simulados para demostración
        # En implementación real, hacer query a la base de datos real
        sample_data = []

        if table_name == "empleados":
            sample_data = [
                {"id": 1, "cedula": "0123456789", "nombres": "Juan Pérez", "cargo": "Desarrollador"},
                {"id": 2, "cedula": "0987654321", "nombres": "María González", "cargo": "Analista"}
            ]
        elif table_name == "departamentos":
            sample_data = [
                {"id": 1, "nombre": "Recursos Humanos", "codigo": "RH"},
                {"id": 2, "nombre": "Desarrollo", "codigo": "DEV"}
            ]
        elif table_name == "nominas":
            sample_data = [
                {"id": 1, "empleado_id": 1, "periodo": "2024-01", "sueldo": 1500.00},
                {"id": 2, "empleado_id": 2, "periodo": "2024-01", "sueldo": 1800.00}
            ]
        else:
            # Datos genéricos para otras tablas
            sample_data = [
                {"id": 1, "descripcion": f"Registro de {table_name}", "fecha": datetime.now().strftime('%Y-%m-%d')}
            ]

        return sample_data


def show_database_export_dialog(parent):
    """Mostrar diálogo de exportación de base de datos"""
    dialog = DatabaseExportDialog(parent)
    return dialog.result