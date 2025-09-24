#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componente de Carga Masiva - Sistema SGN
Funcionalidades para importación y procesamiento masivo de datos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import csv
from datetime import date, datetime
from decimal import Decimal
import sys
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class CargaMasivaComponent:
    """Componente reutilizable para carga masiva de datos"""

    def __init__(self, parent, session, entity_type, columns_mapping, validation_rules=None):
        """
        Inicializar componente de carga masiva

        Args:
            parent: Widget padre
            session: Sesión de base de datos
            entity_type: Tipo de entidad (empleados, nomina, etc.)
            columns_mapping: Mapeo de columnas {col_excel: campo_bd}
            validation_rules: Reglas de validación personalizadas
        """
        self.parent = parent
        self.session = session
        self.entity_type = entity_type
        self.columns_mapping = columns_mapping
        self.validation_rules = validation_rules or {}
        self.data_frame = None
        self.errors = []

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz de carga masiva"""
        # Ventana principal
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Carga Masiva - {self.entity_type.title()}")
        self.window.geometry("900x700")
        self.window.transient(self.parent)
        self.window.grab_set()

        # Header
        header_frame = tk.Frame(self.window, bg='#2c5282', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f"CARGA MASIVA DE {self.entity_type.upper()}",
            font=('Arial', 16, 'bold'),
            bg='#2c5282',
            fg='white'
        ).pack(pady=15)

        # Notebook para pasos
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear pestañas
        self.create_file_selection_tab()
        self.create_mapping_tab()
        self.create_validation_tab()
        self.create_processing_tab()

    def create_file_selection_tab(self):
        """Crear pestaña de selección de archivo"""
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text="1. Seleccionar Archivo")

        # Instrucciones
        instructions_frame = tk.LabelFrame(file_frame, text="Instrucciones", font=('Arial', 10, 'bold'))
        instructions_frame.pack(fill=tk.X, padx=10, pady=10)

        instructions_text = f"""
        PASOS PARA CARGA MASIVA DE {self.entity_type.upper()}:

        1. Prepare un archivo Excel (.xlsx) o CSV (.csv) con los datos
        2. Asegúrese de que la primera fila contenga los nombres de las columnas
        3. Verifique que los datos estén completos y en el formato correcto
        4. Seleccione el archivo usando el botón "Examinar"
        5. Revise el mapeo de columnas en la siguiente pestaña
        6. Valide los datos antes de procesarlos

        FORMATOS SOPORTADOS: Excel (.xlsx), CSV (.csv)
        """

        tk.Label(
            instructions_frame,
            text=instructions_text,
            font=('Arial', 9),
            justify=tk.LEFT,
            wraplength=800
        ).pack(padx=10, pady=10)

        # Selección de archivo
        file_selection_frame = tk.LabelFrame(file_frame, text="Seleccionar Archivo", font=('Arial', 10, 'bold'))
        file_selection_frame.pack(fill=tk.X, padx=10, pady=10)

        selection_grid = tk.Frame(file_selection_frame)
        selection_grid.pack(padx=10, pady=10)

        tk.Label(selection_grid, text="Archivo:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(selection_grid, textvariable=self.file_path_var, width=50, state='readonly')
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(
            selection_grid,
            text="Examinar",
            command=self.browse_file,
            bg='#4299e1',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15
        ).grid(row=0, column=2, padx=5, pady=5)

        # Información del archivo
        self.file_info_frame = tk.LabelFrame(file_frame, text="Información del Archivo", font=('Arial', 10, 'bold'))
        self.file_info_frame.pack(fill=tk.X, padx=10, pady=10)

        self.file_info_labels = {}
        info_fields = ["Nombre:", "Tamaño:", "Filas:", "Columnas:", "Estado:"]
        for i, field in enumerate(info_fields):
            tk.Label(self.file_info_frame, text=field, font=('Arial', 9, 'bold')).grid(
                row=i//2, column=(i%2)*2, sticky=tk.W, padx=10, pady=2
            )
            label = tk.Label(self.file_info_frame, text="", font=('Arial', 9), width=25)
            label.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=10, pady=2)
            self.file_info_labels[field] = label

        # Botón siguiente
        next_frame = tk.Frame(file_frame)
        next_frame.pack(side=tk.BOTTOM, pady=10)

        self.next_button1 = tk.Button(
            next_frame,
            text="Siguiente: Mapeo de Columnas",
            command=self.next_to_mapping,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8,
            state='disabled'
        )
        self.next_button1.pack()

    def create_mapping_tab(self):
        """Crear pestaña de mapeo de columnas"""
        mapping_frame = ttk.Frame(self.notebook)
        self.notebook.add(mapping_frame, text="2. Mapeo de Columnas")

        # Instrucciones
        tk.Label(
            mapping_frame,
            text="Configure el mapeo entre las columnas del archivo y los campos del sistema:",
            font=('Arial', 10, 'bold')
        ).pack(pady=10)

        # Área de mapeo con scroll
        self.create_mapping_area(mapping_frame)

        # Botones
        mapping_buttons_frame = tk.Frame(mapping_frame)
        mapping_buttons_frame.pack(side=tk.BOTTOM, pady=10)

        tk.Button(
            mapping_buttons_frame,
            text="← Anterior",
            command=lambda: self.notebook.select(0),
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        self.next_button2 = tk.Button(
            mapping_buttons_frame,
            text="Siguiente: Validación →",
            command=self.next_to_validation,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            state='disabled'
        )
        self.next_button2.pack(side=tk.LEFT, padx=5)

    def create_mapping_area(self, parent):
        """Crear área de mapeo con scroll"""
        # Frame con scroll
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.mapping_scroll_frame = tk.Frame(canvas)

        self.mapping_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.mapping_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        self.mapping_canvas = canvas

    def create_validation_tab(self):
        """Crear pestaña de validación"""
        validation_frame = ttk.Frame(self.notebook)
        self.notebook.add(validation_frame, text="3. Validación")

        # Información de validación
        tk.Label(
            validation_frame,
            text="Validación de datos importados:",
            font=('Arial', 12, 'bold')
        ).pack(pady=10)

        # Estadísticas de validación
        stats_frame = tk.LabelFrame(validation_frame, text="Estadísticas", font=('Arial', 10, 'bold'))
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.validation_stats = {}
        stats_fields = ["Total Registros:", "Registros Válidos:", "Registros con Errores:", "Estado:"]
        for i, field in enumerate(stats_fields):
            tk.Label(stats_frame, text=field, font=('Arial', 9, 'bold')).grid(
                row=i//2, column=(i%2)*2, sticky=tk.W, padx=10, pady=2
            )
            label = tk.Label(stats_frame, text="0", font=('Arial', 9), width=20)
            label.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=10, pady=2)
            self.validation_stats[field] = label

        # Lista de errores
        errors_frame = tk.LabelFrame(validation_frame, text="Errores Encontrados", font=('Arial', 10, 'bold'))
        errors_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para errores
        columns = ('fila', 'campo', 'valor', 'error')
        self.errors_tree = ttk.Treeview(errors_frame, columns=columns, show='headings', height=12)

        headings = ['Fila', 'Campo', 'Valor', 'Error']
        for col, heading in zip(columns, headings):
            self.errors_tree.heading(col, text=heading)
            self.errors_tree.column(col, width=150)

        # Scrollbar para errores
        errors_scroll = ttk.Scrollbar(errors_frame, orient=tk.VERTICAL, command=self.errors_tree.yview)
        self.errors_tree.configure(yscrollcommand=errors_scroll.set)

        self.errors_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        errors_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones
        validation_buttons_frame = tk.Frame(validation_frame)
        validation_buttons_frame.pack(side=tk.BOTTOM, pady=10)

        tk.Button(
            validation_buttons_frame,
            text="← Anterior",
            command=lambda: self.notebook.select(1),
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            validation_buttons_frame,
            text="Validar Datos",
            command=self.validate_data,
            bg='#9f7aea',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        self.next_button3 = tk.Button(
            validation_buttons_frame,
            text="Siguiente: Procesamiento →",
            command=self.next_to_processing,
            bg='#48bb78',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            state='disabled'
        )
        self.next_button3.pack(side=tk.LEFT, padx=5)

    def create_processing_tab(self):
        """Crear pestaña de procesamiento"""
        processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(processing_frame, text="4. Procesamiento")

        # Información
        tk.Label(
            processing_frame,
            text="Procesamiento e importación de datos:",
            font=('Arial', 12, 'bold')
        ).pack(pady=10)

        # Opciones de procesamiento
        options_frame = tk.LabelFrame(processing_frame, text="Opciones", font=('Arial', 10, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        self.skip_errors_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Omitir registros con errores",
            variable=self.skip_errors_var,
            font=('Arial', 10)
        ).pack(anchor=tk.W, padx=10, pady=5)

        self.backup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Crear respaldo antes de importar",
            variable=self.backup_var,
            font=('Arial', 10)
        ).pack(anchor=tk.W, padx=10, pady=5)

        # Progreso
        progress_frame = tk.LabelFrame(processing_frame, text="Progreso", font=('Arial', 10, 'bold'))
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        self.progress_var = tk.StringVar(value="Listo para procesar")
        tk.Label(progress_frame, textvariable=self.progress_var, font=('Arial', 10)).pack(pady=5)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # Resultados
        results_frame = tk.LabelFrame(processing_frame, text="Resultados", font=('Arial', 10, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.results_text = tk.Text(results_frame, height=10, font=('Courier', 9))
        results_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scroll.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones
        processing_buttons_frame = tk.Frame(processing_frame)
        processing_buttons_frame.pack(side=tk.BOTTOM, pady=10)

        tk.Button(
            processing_buttons_frame,
            text="← Anterior",
            command=lambda: self.notebook.select(2),
            bg='#ed8936',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            processing_buttons_frame,
            text="Procesar Datos",
            command=self.process_data,
            bg='#e53e3e',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            processing_buttons_frame,
            text="Cerrar",
            command=self.window.destroy,
            bg='#718096',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15
        ).pack(side=tk.LEFT, padx=5)

    def browse_file(self):
        """Examinar y seleccionar archivo"""
        filetypes = [
            ("Archivos Excel", "*.xlsx"),
            ("Archivos CSV", "*.csv"),
            ("Todos los archivos", "*.*")
        ]

        file_path = filedialog.askopenfilename(
            title=f"Seleccionar archivo para {self.entity_type}",
            filetypes=filetypes
        )

        if file_path:
            self.file_path_var.set(file_path)
            self.load_file_info(file_path)

    def load_file_info(self, file_path):
        """Cargar información del archivo"""
        try:
            # Determinar tipo de archivo y cargar
            if file_path.lower().endswith('.xlsx'):
                self.data_frame = pd.read_excel(file_path)
            elif file_path.lower().endswith('.csv'):
                self.data_frame = pd.read_csv(file_path)
            else:
                raise ValueError("Formato de archivo no soportado")

            # Actualizar información
            file_size = Path(file_path).stat().st_size
            size_mb = file_size / (1024 * 1024)

            self.file_info_labels["Nombre:"].config(text=Path(file_path).name)
            self.file_info_labels["Tamaño:"].config(text=f"{size_mb:.2f} MB")
            self.file_info_labels["Filas:"].config(text=str(len(self.data_frame)))
            self.file_info_labels["Columnas:"].config(text=str(len(self.data_frame.columns)))
            self.file_info_labels["Estado:"].config(text="Cargado correctamente", fg='green')

            # Habilitar siguiente paso
            self.next_button1.config(state='normal')

        except Exception as e:
            self.file_info_labels["Estado:"].config(text=f"Error: {str(e)}", fg='red')
            messagebox.showerror("Error", f"Error cargando archivo: {str(e)}")

    def next_to_mapping(self):
        """Ir a pestaña de mapeo"""
        if self.data_frame is not None:
            self.populate_mapping()
            self.notebook.select(1)
        else:
            messagebox.showwarning("Advertencia", "Primero seleccione un archivo válido")

    def populate_mapping(self):
        """Poblar área de mapeo"""
        # Limpiar área de mapeo
        for widget in self.mapping_scroll_frame.winfo_children():
            widget.destroy()

        # Header
        tk.Label(
            self.mapping_scroll_frame,
            text="Columna del Archivo",
            font=('Arial', 10, 'bold'),
            bg='lightgray'
        ).grid(row=0, column=0, sticky='ew', padx=2, pady=2)

        tk.Label(
            self.mapping_scroll_frame,
            text="Campo del Sistema",
            font=('Arial', 10, 'bold'),
            bg='lightgray'
        ).grid(row=0, column=1, sticky='ew', padx=2, pady=2)

        tk.Label(
            self.mapping_scroll_frame,
            text="Vista Previa",
            font=('Arial', 10, 'bold'),
            bg='lightgray'
        ).grid(row=0, column=2, sticky='ew', padx=2, pady=2)

        # Crear mapeos
        self.column_mappings = {}
        available_fields = list(self.columns_mapping.values())

        for i, col in enumerate(self.data_frame.columns):
            row = i + 1

            # Columna del archivo
            tk.Label(
                self.mapping_scroll_frame,
                text=col,
                font=('Arial', 9),
                relief=tk.RAISED,
                bg='white'
            ).grid(row=row, column=0, sticky='ew', padx=2, pady=1)

            # Campo del sistema
            mapping_combo = ttk.Combobox(
                self.mapping_scroll_frame,
                values=["[No mapear]"] + available_fields,
                state='readonly',
                width=25
            )
            mapping_combo.grid(row=row, column=1, sticky='ew', padx=2, pady=1)

            # Auto-mapeo si encuentra coincidencia
            auto_mapped = False
            for sys_col, db_field in self.columns_mapping.items():
                if col.lower().replace(' ', '_') == sys_col.lower() or col.lower() == db_field.lower():
                    mapping_combo.set(db_field)
                    auto_mapped = True
                    break

            if not auto_mapped:
                mapping_combo.set("[No mapear]")

            self.column_mappings[col] = mapping_combo

            # Vista previa
            preview_value = str(self.data_frame[col].iloc[0] if len(self.data_frame) > 0 else "")[:30]
            tk.Label(
                self.mapping_scroll_frame,
                text=preview_value,
                font=('Arial', 8),
                fg='gray',
                relief=tk.SUNKEN,
                bg='#f8f9fa'
            ).grid(row=row, column=2, sticky='ew', padx=2, pady=1)

        # Configurar columnas expandibles
        for col in range(3):
            self.mapping_scroll_frame.grid_columnconfigure(col, weight=1)

        # Habilitar siguiente paso
        self.next_button2.config(state='normal')

        # Actualizar scroll region
        self.mapping_scroll_frame.update_idletasks()
        self.mapping_canvas.configure(scrollregion=self.mapping_canvas.bbox("all"))

    def next_to_validation(self):
        """Ir a pestaña de validación"""
        self.notebook.select(2)

    def validate_data(self):
        """Validar datos"""
        try:
            self.errors = []
            valid_count = 0

            # Obtener mapeos activos
            active_mappings = {}
            for col, combo in self.column_mappings.items():
                field = combo.get()
                if field != "[No mapear]":
                    active_mappings[col] = field

            # Validar cada fila
            for index, row in self.data_frame.iterrows():
                row_valid = True

                for col, field in active_mappings.items():
                    value = row[col]

                    # Validaciones básicas
                    if pd.isna(value) or str(value).strip() == "":
                        if field in ['nombres', 'apellidos', 'cedula']:  # Campos obligatorios
                            self.errors.append({
                                'fila': index + 2,  # +2 porque index empieza en 0 y hay header
                                'campo': field,
                                'valor': str(value),
                                'error': 'Campo obligatorio vacío'
                            })
                            row_valid = False
                        continue

                    # Validaciones específicas
                    if field == 'cedula':
                        if not self.validate_cedula(str(value)):
                            self.errors.append({
                                'fila': index + 2,
                                'campo': field,
                                'valor': str(value),
                                'error': 'Cédula inválida'
                            })
                            row_valid = False

                    elif field == 'email':
                        if not self.validate_email(str(value)):
                            self.errors.append({
                                'fila': index + 2,
                                'campo': field,
                                'valor': str(value),
                                'error': 'Email inválido'
                            })
                            row_valid = False

                    elif field == 'sueldo':
                        try:
                            float_val = float(value)
                            if float_val < 0:
                                self.errors.append({
                                    'fila': index + 2,
                                    'campo': field,
                                    'valor': str(value),
                                    'error': 'Sueldo no puede ser negativo'
                                })
                                row_valid = False
                        except:
                            self.errors.append({
                                'fila': index + 2,
                                'campo': field,
                                'valor': str(value),
                                'error': 'Sueldo debe ser numérico'
                            })
                            row_valid = False

                if row_valid:
                    valid_count += 1

            # Actualizar estadísticas
            total_records = len(self.data_frame)
            error_count = total_records - valid_count

            self.validation_stats["Total Registros:"].config(text=str(total_records))
            self.validation_stats["Registros Válidos:"].config(text=str(valid_count), fg='green')
            self.validation_stats["Registros con Errores:"].config(text=str(error_count), fg='red')

            if error_count == 0:
                self.validation_stats["Estado:"].config(text="✓ Validación exitosa", fg='green')
                self.next_button3.config(state='normal')
            else:
                self.validation_stats["Estado:"].config(text="⚠ Errores encontrados", fg='orange')

            # Mostrar errores
            self.show_validation_errors()

        except Exception as e:
            messagebox.showerror("Error", f"Error en validación: {str(e)}")

    def show_validation_errors(self):
        """Mostrar errores de validación"""
        # Limpiar árbol de errores
        for item in self.errors_tree.get_children():
            self.errors_tree.delete(item)

        # Agregar errores
        for error in self.errors:
            self.errors_tree.insert('', 'end', values=(
                error['fila'],
                error['campo'],
                error['valor'],
                error['error']
            ))

    def validate_cedula(self, cedula):
        """Validar cédula ecuatoriana"""
        if len(cedula) != 10:
            return False

        try:
            digits = [int(d) for d in cedula]

            # Validar dígitos
            for i in range(9):
                if i % 2 == 0:  # Posiciones pares
                    digits[i] *= 2
                    if digits[i] > 9:
                        digits[i] -= 9

            sum_digits = sum(digits[:9])
            check_digit = (10 - (sum_digits % 10)) % 10

            return check_digit == digits[9]
        except:
            return False

    def validate_email(self, email):
        """Validar formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def next_to_processing(self):
        """Ir a pestaña de procesamiento"""
        self.notebook.select(3)

    def process_data(self):
        """Procesar e importar datos"""
        try:
            # Mostrar confirmación
            if not messagebox.askyesno(
                "Confirmar",
                f"¿Está seguro de procesar {len(self.data_frame)} registros?\nEsta acción no se puede deshacer."
            ):
                return

            # Configurar progreso
            self.progress_var.set("Iniciando procesamiento...")
            self.progress_bar['maximum'] = len(self.data_frame)
            self.progress_bar['value'] = 0
            self.window.update()

            # Obtener mapeos activos
            active_mappings = {}
            for col, combo in self.column_mappings.items():
                field = combo.get()
                if field != "[No mapear]":
                    active_mappings[col] = field

            # Procesar registros
            processed = 0
            errors = 0
            results_log = []

            results_log.append(f"=== PROCESAMIENTO MASIVO DE {self.entity_type.upper()} ===")
            results_log.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            results_log.append(f"Total registros: {len(self.data_frame)}")
            results_log.append("")

            for index, row in self.data_frame.iterrows():
                try:
                    # Actualizar progreso
                    self.progress_var.set(f"Procesando registro {index + 1} de {len(self.data_frame)}")
                    self.progress_bar['value'] = index + 1
                    self.window.update()

                    # Preparar datos para inserción
                    record_data = {}
                    for col, field in active_mappings.items():
                        value = row[col]
                        if not pd.isna(value):
                            record_data[field] = value

                    # Aquí iría la lógica específica de inserción según entity_type
                    # Por ahora simulamos el procesamiento
                    success = self.insert_record(record_data)

                    if success:
                        processed += 1
                        results_log.append(f"[OK] Fila {index + 2}: Procesado exitosamente")
                    else:
                        errors += 1
                        results_log.append(f"[ERROR] Fila {index + 2}: Error en procesamiento")

                except Exception as e:
                    errors += 1
                    results_log.append(f"[ERROR] Fila {index + 2}: {str(e)}")

            # Finalizar
            results_log.append("")
            results_log.append("=== RESUMEN ===")
            results_log.append(f"Registros procesados: {processed}")
            results_log.append(f"Errores: {errors}")
            results_log.append(f"Tasa de éxito: {(processed/len(self.data_frame)*100):.1f}%")

            # Mostrar resultados
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "\n".join(results_log))

            self.progress_var.set("Procesamiento completado")

            messagebox.showinfo(
                "Procesamiento Completado",
                f"Procesamiento finalizado:\n\n"
                f"• Registros procesados: {processed}\n"
                f"• Errores: {errors}\n"
                f"• Tasa de éxito: {(processed/len(self.data_frame)*100):.1f}%"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error en procesamiento: {str(e)}")

    def insert_record(self, record_data):
        """Insertar registro en base de datos (método a sobrescribir)"""
        # Este método debe ser sobrescrito por cada módulo específico
        # Por ahora retorna True para simular éxito
        return True


def show_carga_masiva_empleados(parent, session):
    """Mostrar ventana de carga masiva para empleados"""
    columns_mapping = {
        'codigo_empleado': 'empleado',
        'nombres': 'nombres',
        'apellidos': 'apellidos',
        'cedula': 'cedula',
        'fecha_nacimiento': 'fecha_nac',
        'sexo': 'sexo',
        'estado_civil': 'estado_civil',
        'direccion': 'direccion',
        'telefono': 'telefono',
        'celular': 'celular',
        'email': 'email',
        'cargo': 'cargo',
        'departamento': 'depto',
        'sueldo': 'sueldo',
        'fecha_ingreso': 'fecha_ing',
        'tipo_trabajador': 'tipo_tra',
        'tipo_pago': 'tipo_pgo',
        'estado': 'estado',
        'banco': 'banco',
        'cuenta_banco': 'cuenta_banco'
    }

    carga_masiva = CargaMasivaComponent(
        parent=parent,
        session=session,
        entity_type="empleados",
        columns_mapping=columns_mapping
    )

    return carga_masiva


def show_carga_masiva_nomina(parent, session):
    """Mostrar ventana de carga masiva para nómina"""
    columns_mapping = {
        'codigo_empleado': 'empleado',
        'periodo': 'periodo',
        'dias_trabajados': 'dias_trabajados',
        'horas_extras': 'horas_extras',
        'comisiones': 'comisiones',
        'bonificaciones': 'bonificaciones',
        'otros_ingresos': 'otros_ingresos',
        'descuentos': 'descuentos',
        'prestamos': 'prestamos',
        'otros_descuentos': 'otros_descuentos'
    }

    carga_masiva = CargaMasivaComponent(
        parent=parent,
        session=session,
        entity_type="nomina",
        columns_mapping=columns_mapping
    )

    return carga_masiva