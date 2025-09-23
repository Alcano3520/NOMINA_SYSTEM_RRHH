"""Componente DataTable - Tabla de datos personalizada"""

import tkinter as tk
from tkinter import ttk
from config import Config

class DataTable(tk.Frame):
    def __init__(self, parent, columns=None, on_select=None, on_double_click=None,
                 show_actions=True, actions=None, **kwargs):
        super().__init__(parent, bg=Config.COLORS['surface'], **kwargs)

        self.columns = columns or []
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.show_actions = show_actions
        self.actions = actions or []
        self.data = []

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz de la tabla"""
        # Frame de controles superiores
        self.create_table_header()

        # Frame principal de la tabla
        table_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        table_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Crear Treeview con scrollbars
        self.create_treeview(table_frame)

        # Frame de información inferior
        self.create_table_footer()

    def create_table_header(self):
        """Crear encabezado de la tabla con controles"""
        header_frame = tk.Frame(self, bg=Config.COLORS['surface'])
        header_frame.pack(fill="x")

        # Frame izquierdo - información
        left_frame = tk.Frame(header_frame, bg=Config.COLORS['surface'])
        left_frame.pack(side="left")

        self.info_label = tk.Label(
            left_frame,
            text="Cargando datos...",
            font=Config.FONTS['small'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text_light']
        )
        self.info_label.pack(anchor="w")

        # Frame derecho - controles
        right_frame = tk.Frame(header_frame, bg=Config.COLORS['surface'])
        right_frame.pack(side="right")

        # Botón de actualizar
        refresh_btn = tk.Button(
            right_frame,
            text="🔄",
            command=self.refresh_data,
            bg=Config.COLORS['info'],
            fg='white',
            font=Config.FONTS['default'],
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        refresh_btn.pack(side="right", padx=(5, 0))

        # Botón de exportar
        export_btn = tk.Button(
            right_frame,
            text="📤",
            command=self.export_data,
            bg=Config.COLORS['secondary'],
            fg='white',
            font=Config.FONTS['default'],
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        export_btn.pack(side="right", padx=(5, 0))

    def create_treeview(self, parent):
        """Crear Treeview con scrollbars"""
        # Frame para treeview y scrollbars
        tree_container = tk.Frame(parent, bg=Config.COLORS['surface'])
        tree_container.pack(fill="both", expand=True)

        # Configurar columnas para el treeview
        if self.show_actions:
            tree_columns = [col["key"] for col in self.columns] + ["actions"]
        else:
            tree_columns = [col["key"] for col in self.columns]

        # Crear Treeview
        self.tree = ttk.Treeview(
            tree_container,
            columns=tree_columns,
            show='headings',
            style='Custom.Treeview',
            height=15
        )

        # Configurar columnas
        for col in self.columns:
            self.tree.heading(col["key"], text=col["title"])
            self.tree.column(
                col["key"],
                width=col.get("width", 100),
                minwidth=50,
                anchor=col.get("anchor", "w")
            )

        # Columna de acciones si está habilitada
        if self.show_actions:
            self.tree.heading("actions", text="ACCIONES")
            self.tree.column("actions", width=120, minwidth=120, anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.tree.yview,
            style='Custom.Vertical.TScrollbar'
        )
        h_scrollbar = ttk.Scrollbar(
            tree_container,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(yscrollcommand=v_scrollbar.set)
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)  # Click derecho

    def create_table_footer(self):
        """Crear pie de la tabla con información"""
        footer_frame = tk.Frame(self, bg=Config.COLORS['background'])
        footer_frame.pack(fill="x", pady=(10, 0))

        # Padding interno
        inner_footer = tk.Frame(footer_frame, bg=Config.COLORS['background'])
        inner_footer.pack(fill="x", padx=15, pady=10)

        # Información de registros
        self.records_label = tk.Label(
            inner_footer,
            text="0 registros encontrados",
            font=Config.FONTS['small'],
            bg=Config.COLORS['background'],
            fg=Config.COLORS['text_light']
        )
        self.records_label.pack(side="left")

        # Información de selección
        self.selection_label = tk.Label(
            inner_footer,
            text="",
            font=Config.FONTS['small'],
            bg=Config.COLORS['background'],
            fg=Config.COLORS['text_light']
        )
        self.selection_label.pack(side="right")

    def set_data(self, data):
        """Establecer datos en la tabla"""
        self.data = data

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar datos
        for i, row in enumerate(data):
            values = []

            # Obtener valores de las columnas
            for col in self.columns:
                value = row.get(col["key"], "")
                values.append(str(value))

            # Agregar botones de acción si está habilitado
            if self.show_actions:
                action_text = " | ".join([action["text"] for action in self.actions])
                values.append(action_text)

            # Insertar fila
            item_id = self.tree.insert("", "end", values=values)

            # Guardar referencia a los datos originales
            self.tree.set(item_id, "#0", i)

        # Actualizar información
        self.update_info()

    def update_info(self):
        """Actualizar información de la tabla"""
        count = len(self.data)
        self.info_label.configure(text=f"Mostrando {count} registros")
        self.records_label.configure(text=f"{count} registros encontrados")

    def on_tree_select(self, event):
        """Manejar selección en el tree"""
        selection = self.tree.selection()
        if selection and self.on_select:
            item = selection[0]
            row_index = int(self.tree.set(item, "#0"))
            row_data = self.data[row_index]
            self.on_select(row_data)

            # Actualizar información de selección
            self.selection_label.configure(
                text=f"Seleccionado: {row_data.get(self.columns[0]['key'], 'N/A')}"
            )

    def on_tree_double_click(self, event):
        """Manejar doble click"""
        selection = self.tree.selection()
        if selection and self.on_double_click:
            item = selection[0]
            row_index = int(self.tree.set(item, "#0"))
            row_data = self.data[row_index]
            self.on_double_click(row_data)

    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        if not self.actions:
            return

        # Obtener item bajo el cursor
        item = self.tree.identify_row(event.y)
        if not item:
            return

        # Seleccionar item
        self.tree.selection_set(item)

        # Crear menú contextual
        context_menu = tk.Menu(self, tearoff=0)

        row_index = int(self.tree.set(item, "#0"))
        row_data = self.data[row_index]

        for action in self.actions:
            context_menu.add_command(
                label=f"{action['text']} {action.get('tooltip', '')}",
                command=lambda a=action: a["command"](row_data)
            )

        # Mostrar menú
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def get_selected_data(self):
        """Obtener datos de la fila seleccionada"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            row_index = int(self.tree.set(item, "#0"))
            return self.data[row_index]
        return None

    def get_all_data(self):
        """Obtener todos los datos"""
        return self.data

    def refresh_data(self):
        """Refrescar datos (placeholder)"""
        print("Refrescar datos solicitado")

    def export_data(self):
        """Exportar datos (placeholder)"""
        print("Exportar datos solicitado")

    def filter_data(self, filter_func):
        """Filtrar datos usando una función"""
        filtered_data = [row for row in self.data if filter_func(row)]
        self.set_data(filtered_data)

    def sort_data(self, column_key, reverse=False):
        """Ordenar datos por columna"""
        if not self.data:
            return

        try:
            sorted_data = sorted(
                self.data,
                key=lambda x: x.get(column_key, ""),
                reverse=reverse
            )
            self.set_data(sorted_data)
        except Exception as e:
            print(f"Error ordenando datos: {e}")

    def search_data(self, search_term, columns=None):
        """Buscar en los datos"""
        if not search_term:
            return

        search_columns = columns or [col["key"] for col in self.columns]
        search_term = search_term.lower()

        filtered_data = []
        for row in self.data:
            for col in search_columns:
                value = str(row.get(col, "")).lower()
                if search_term in value:
                    filtered_data.append(row)
                    break

        self.set_data(filtered_data)

class EditableDataTable(DataTable):
    """Tabla de datos con capacidad de edición inline"""

    def __init__(self, parent, editable_columns=None, **kwargs):
        self.editable_columns = editable_columns or []
        self.edit_widget = None
        self.edit_item = None
        self.edit_column = None

        super().__init__(parent, **kwargs)

    def create_treeview(self, parent):
        """Crear treeview con capacidad de edición"""
        super().create_treeview(parent)

        # Agregar evento para edición
        self.tree.bind('<Double-1>', self.start_edit)

    def start_edit(self, event):
        """Iniciar edición de celda"""
        # Identificar item y columna
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item or not column:
            return

        # Verificar si la columna es editable
        column_index = int(column.replace('#', '')) - 1
        if column_index >= len(self.columns):
            return

        column_key = self.columns[column_index]["key"]
        if column_key not in self.editable_columns:
            return

        # Obtener posición y tamaño de la celda
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return

        # Crear widget de edición
        current_value = self.tree.set(item, column_key)

        self.edit_widget = tk.Entry(
            self.tree,
            font=Config.FONTS['default'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text'],
            relief='solid',
            bd=1
        )

        self.edit_widget.place(
            x=bbox[0], y=bbox[1],
            width=bbox[2], height=bbox[3]
        )

        self.edit_widget.insert(0, current_value)
        self.edit_widget.select_range(0, tk.END)
        self.edit_widget.focus()

        self.edit_item = item
        self.edit_column = column_key

        # Eventos para terminar edición
        self.edit_widget.bind('<Return>', self.finish_edit)
        self.edit_widget.bind('<Escape>', self.cancel_edit)
        self.edit_widget.bind('<FocusOut>', self.finish_edit)

    def finish_edit(self, event=None):
        """Terminar edición y guardar cambios"""
        if not self.edit_widget:
            return

        new_value = self.edit_widget.get()

        # Actualizar treeview
        self.tree.set(self.edit_item, self.edit_column, new_value)

        # Actualizar datos originales
        row_index = int(self.tree.set(self.edit_item, "#0"))
        self.data[row_index][self.edit_column] = new_value

        # Limpiar edición
        self.edit_widget.destroy()
        self.edit_widget = None
        self.edit_item = None
        self.edit_column = None

    def cancel_edit(self, event=None):
        """Cancelar edición"""
        if self.edit_widget:
            self.edit_widget.destroy()
            self.edit_widget = None
            self.edit_item = None
            self.edit_column = None