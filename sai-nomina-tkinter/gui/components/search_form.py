"""Componente SearchForm - Formulario de búsqueda avanzada"""

import tkinter as tk
from tkinter import ttk
from config import Config

class SearchForm(tk.Frame):
    def __init__(self, parent, fields=None, on_search=None, on_clear=None, **kwargs):
        super().__init__(parent, bg=Config.COLORS['background'], **kwargs)

        self.fields = fields or []
        self.on_search = on_search
        self.on_clear = on_clear
        self.field_widgets = {}

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del formulario"""
        # Frame principal
        main_frame = tk.Frame(self, bg=Config.COLORS['background'])
        main_frame.pack(fill="both", expand=True)

        # Grid de campos
        fields_frame = tk.Frame(main_frame, bg=Config.COLORS['background'])
        fields_frame.pack(fill="x", pady=(0, 15))

        # Configurar grid para responsive design
        cols_per_row = 4
        for i in range(cols_per_row):
            fields_frame.columnconfigure(i, weight=1)

        # Crear campos
        for i, field in enumerate(self.fields):
            row = i // cols_per_row
            col = i % cols_per_row
            self.create_field(fields_frame, field, row, col)

        # Frame de botones
        buttons_frame = tk.Frame(main_frame, bg=Config.COLORS['background'])
        buttons_frame.pack(fill="x")

        # Botón de búsqueda
        search_btn = tk.Button(
            buttons_frame,
            text="🔍 Buscar",
            command=self.perform_search,
            bg=Config.COLORS['primary'],
            fg='white',
            font=Config.FONTS['default'],
            relief='flat',
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        search_btn.pack(side="left", padx=(0, 10))

        # Botón de limpiar
        clear_btn = tk.Button(
            buttons_frame,
            text="🗑️ Limpiar",
            command=self.clear_form,
            bg=Config.COLORS['secondary'],
            fg='white',
            font=Config.FONTS['default'],
            relief='flat',
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        clear_btn.pack(side="left")

        # Información de ayuda
        help_label = tk.Label(
            buttons_frame,
            text="💡 Use % como comodín para búsquedas parciales",
            font=Config.FONTS['small'],
            bg=Config.COLORS['background'],
            fg=Config.COLORS['text_light']
        )
        help_label.pack(side="right")

    def create_field(self, parent, field, row, col):
        """Crear un campo de búsqueda"""
        # Frame del campo
        field_frame = tk.Frame(parent, bg=Config.COLORS['background'])
        field_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

        # Label
        label = tk.Label(
            field_frame,
            text=field["label"],
            font=Config.FONTS['default'],
            bg=Config.COLORS['background'],
            fg=Config.COLORS['text'],
            anchor='w'
        )
        label.pack(fill="x", pady=(0, 5))

        # Widget según el tipo
        field_type = field.get("type", "entry")

        if field_type == "entry":
            widget = self.create_entry_field(field_frame, field)
        elif field_type == "combobox":
            widget = self.create_combobox_field(field_frame, field)
        elif field_type == "date":
            widget = self.create_date_field(field_frame, field)
        elif field_type == "number":
            widget = self.create_number_field(field_frame, field)
        else:
            widget = self.create_entry_field(field_frame, field)

        # Guardar referencia del widget
        self.field_widgets[field["name"]] = widget

        # Bind Enter para búsqueda rápida
        if hasattr(widget, 'bind'):
            widget.bind('<Return>', lambda e: self.perform_search())

    def create_entry_field(self, parent, field):
        """Crear campo de entrada de texto"""
        entry = tk.Entry(
            parent,
            font=Config.FONTS['default'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text'],
            relief='solid',
            bd=1,
            insertbackground=Config.COLORS['text']
        )
        entry.pack(fill="x")

        # Placeholder si está definido
        placeholder = field.get("placeholder", "")
        if placeholder:
            self.add_placeholder(entry, placeholder)

        return entry

    def create_combobox_field(self, parent, field):
        """Crear campo combobox"""
        values = field.get("values", [])

        combo = ttk.Combobox(
            parent,
            values=values,
            font=Config.FONTS['default'],
            style='Custom.TCombobox',
            state="readonly"
        )
        combo.pack(fill="x")

        # Seleccionar primer valor si hay valores
        if values:
            combo.set(values[0])

        return combo

    def create_date_field(self, parent, field):
        """Crear campo de fecha"""
        # Frame para fecha con botón de calendario
        date_frame = tk.Frame(parent, bg=Config.COLORS['background'])
        date_frame.pack(fill="x")

        date_entry = tk.Entry(
            date_frame,
            font=Config.FONTS['default'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text'],
            relief='solid',
            bd=1,
            width=12
        )
        date_entry.pack(side="left", fill="x", expand=True)

        # Botón de calendario
        cal_btn = tk.Button(
            date_frame,
            text="📅",
            command=lambda: self.show_calendar(date_entry),
            bg=Config.COLORS['info'],
            fg='white',
            font=Config.FONTS['small'],
            relief='flat',
            bd=0,
            padx=5,
            cursor='hand2'
        )
        cal_btn.pack(side="right", padx=(5, 0))

        # Placeholder
        self.add_placeholder(date_entry, "DD/MM/YYYY")

        return date_entry

    def create_number_field(self, parent, field):
        """Crear campo numérico"""
        number_entry = tk.Entry(
            parent,
            font=Config.FONTS['number'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text'],
            relief='solid',
            bd=1,
            justify='right'
        )
        number_entry.pack(fill="x")

        # Validación numérica
        def validate_number(char):
            return char.isdigit() or char in '.,- '

        vcmd = (parent.register(validate_number), '%S')
        number_entry.config(validate='key', validatecommand=vcmd)

        # Placeholder
        placeholder = field.get("placeholder", "0.00")
        self.add_placeholder(number_entry, placeholder)

        return number_entry

    def add_placeholder(self, widget, placeholder_text):
        """Agregar funcionalidad de placeholder"""
        def on_focus_in(event):
            if widget.get() == placeholder_text:
                widget.delete(0, tk.END)
                widget.configure(fg=Config.COLORS['text'])

        def on_focus_out(event):
            if not widget.get():
                widget.insert(0, placeholder_text)
                widget.configure(fg=Config.COLORS['text_light'])

        # Configurar placeholder inicial
        widget.insert(0, placeholder_text)
        widget.configure(fg=Config.COLORS['text_light'])

        # Bind eventos
        widget.bind('<FocusIn>', on_focus_in)
        widget.bind('<FocusOut>', on_focus_out)

    def show_calendar(self, date_entry):
        """Mostrar selector de calendario"""
        try:
            from tkcalendar import DateEntry
            # Implementar selector de fecha
            print(f"Abrir calendario para {date_entry}")
        except ImportError:
            # Fallback simple
            date_entry.delete(0, tk.END)
            from datetime import datetime
            date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

    def perform_search(self):
        """Realizar búsqueda con los valores del formulario"""
        if not self.on_search:
            return

        # Recopilar valores de todos los campos
        search_values = {}

        for field in self.fields:
            field_name = field["name"]
            widget = self.field_widgets.get(field_name)

            if widget:
                value = self.get_widget_value(widget, field)
                if value:  # Solo incluir valores no vacíos
                    search_values[field_name] = value

        # Llamar callback de búsqueda
        self.on_search(search_values)

    def get_widget_value(self, widget, field):
        """Obtener valor de un widget"""
        field_type = field.get("type", "entry")
        placeholder = field.get("placeholder", "")

        if isinstance(widget, ttk.Combobox):
            value = widget.get()
            # No incluir valor vacío o primer elemento si es placeholder
            if value and not value.startswith("---"):
                return value
        else:
            value = widget.get().strip()
            # No incluir placeholder o valores vacíos
            if value and value != placeholder:
                return value

        return None

    def clear_form(self):
        """Limpiar todos los campos del formulario"""
        for field in self.fields:
            field_name = field["name"]
            widget = self.field_widgets.get(field_name)

            if widget:
                self.clear_widget(widget, field)

        # Llamar callback de limpiar
        if self.on_clear:
            self.on_clear()

    def clear_widget(self, widget, field):
        """Limpiar un widget específico"""
        field_type = field.get("type", "entry")
        placeholder = field.get("placeholder", "")

        if isinstance(widget, ttk.Combobox):
            values = field.get("values", [])
            if values:
                widget.set(values[0])
        else:
            widget.delete(0, tk.END)
            if placeholder:
                widget.insert(0, placeholder)
                widget.configure(fg=Config.COLORS['text_light'])

    def set_field_value(self, field_name, value):
        """Establecer valor de un campo específico"""
        widget = self.field_widgets.get(field_name)
        if widget:
            if isinstance(widget, ttk.Combobox):
                widget.set(value)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
                widget.configure(fg=Config.COLORS['text'])

    def get_field_value(self, field_name):
        """Obtener valor de un campo específico"""
        widget = self.field_widgets.get(field_name)
        if widget:
            field = next((f for f in self.fields if f["name"] == field_name), None)
            if field:
                return self.get_widget_value(widget, field)
        return None

    def get_all_values(self):
        """Obtener todos los valores del formulario"""
        values = {}
        for field in self.fields:
            field_name = field["name"]
            value = self.get_field_value(field_name)
            if value:
                values[field_name] = value
        return values

    def set_field_enabled(self, field_name, enabled=True):
        """Habilitar/deshabilitar un campo"""
        widget = self.field_widgets.get(field_name)
        if widget:
            state = 'normal' if enabled else 'disabled'
            if isinstance(widget, ttk.Combobox):
                widget.configure(state=state)
            else:
                widget.configure(state=state)

    def add_validation(self, field_name, validation_func):
        """Agregar validación a un campo"""
        widget = self.field_widgets.get(field_name)
        if widget and hasattr(widget, 'bind'):
            def validate(event):
                value = widget.get()
                is_valid = validation_func(value)

                # Cambiar color según validación
                if is_valid:
                    widget.configure(bg=Config.COLORS['surface'])
                else:
                    widget.configure(bg='#ffebee')  # Rojo claro

            widget.bind('<KeyRelease>', validate)
            widget.bind('<FocusOut>', validate)