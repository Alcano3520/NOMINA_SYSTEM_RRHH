"""Componente StatCard - Tarjetas de estadísticas"""

import tkinter as tk
from config import Config

class StatCard(tk.Frame):
    def __init__(self, parent, title="", value="", subtitle="", color=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.color = color or Config.COLORS['primary']

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz de la tarjeta"""
        # Configurar el frame principal
        self.configure(
            bg=Config.COLORS['surface'],
            relief='flat',
            bd=0
        )

        # Frame interno con padding
        inner_frame = tk.Frame(
            self,
            bg=Config.COLORS['surface']
        )
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Frame superior - valor principal
        top_frame = tk.Frame(inner_frame, bg=Config.COLORS['surface'])
        top_frame.pack(fill="x")

        # Icono/Indicador de color
        color_indicator = tk.Frame(
            top_frame,
            bg=self.color,
            width=4,
            height=40
        )
        color_indicator.pack(side="left", fill="y", padx=(0, 15))
        color_indicator.pack_propagate(False)

        # Contenedor del contenido
        content_frame = tk.Frame(top_frame, bg=Config.COLORS['surface'])
        content_frame.pack(side="left", fill="both", expand=True)

        # Valor principal (grande)
        self.value_label = tk.Label(
            content_frame,
            text=self.value,
            font=('Segoe UI', 28, 'bold'),
            bg=Config.COLORS['surface'],
            fg=self.color,
            anchor='w'
        )
        self.value_label.pack(anchor="w")

        # Título
        self.title_label = tk.Label(
            content_frame,
            text=self.title,
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text'],
            anchor='w'
        )
        self.title_label.pack(anchor="w", pady=(5, 0))

        # Subtítulo/cambio
        if self.subtitle:
            self.subtitle_label = tk.Label(
                content_frame,
                text=self.subtitle,
                font=Config.FONTS['small'],
                bg=Config.COLORS['surface'],
                fg=Config.COLORS['text_light'],
                anchor='w'
            )
            self.subtitle_label.pack(anchor="w", pady=(5, 0))

        # Efecto de sombra (simulado)
        self.apply_card_style()

    def apply_card_style(self):
        """Aplicar estilo de tarjeta con efecto de sombra"""
        # Simular sombra con configuración de relieve
        self.configure(
            highlightbackground=Config.COLORS['card_shadow'],
            highlightcolor=Config.COLORS['card_shadow'],
            highlightthickness=1
        )

        # Efecto hover
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        # Aplicar bind a todos los widgets hijos
        for widget in self.winfo_children():
            self.bind_recursive(widget)

    def bind_recursive(self, widget):
        """Aplicar eventos recursivamente a widgets hijos"""
        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)

        for child in widget.winfo_children():
            self.bind_recursive(child)

    def on_enter(self, event):
        """Efecto al pasar el mouse sobre la tarjeta"""
        self.configure(bg=Config.COLORS['hover'])
        self.update_children_bg(self, Config.COLORS['hover'])

    def on_leave(self, event):
        """Efecto al quitar el mouse de la tarjeta"""
        self.configure(bg=Config.COLORS['surface'])
        self.update_children_bg(self, Config.COLORS['surface'])

    def update_children_bg(self, widget, color):
        """Actualizar color de fondo de widgets hijos"""
        for child in widget.winfo_children():
            if isinstance(child, (tk.Frame, tk.Label)) and child.cget('bg') != self.color:
                child.configure(bg=color)
            self.update_children_bg(child, color)

    def update_value(self, new_value):
        """Actualizar valor de la tarjeta"""
        self.value = new_value
        self.value_label.configure(text=new_value)

    def update_subtitle(self, new_subtitle):
        """Actualizar subtítulo de la tarjeta"""
        self.subtitle = new_subtitle
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.configure(text=new_subtitle)

class MetricCard(StatCard):
    """Tarjeta de métrica con indicador de tendencia"""

    def __init__(self, parent, title="", value="", previous_value="",
                 format_type="number", **kwargs):
        self.previous_value = previous_value
        self.format_type = format_type

        # Calcular cambio y tendencia
        subtitle = self.calculate_change()

        super().__init__(parent, title=title, value=value, subtitle=subtitle, **kwargs)

    def calculate_change(self):
        """Calcular cambio y tendencia"""
        if not self.previous_value or self.previous_value == 0:
            return "Sin datos previos"

        try:
            current = float(str(self.value).replace(',', '').replace('$', ''))
            previous = float(str(self.previous_value).replace(',', '').replace('$', ''))

            if previous == 0:
                return "Sin datos previos"

            change = current - previous
            percent_change = (change / previous) * 100

            # Determinar símbolo y color
            if change > 0:
                symbol = "↗"
                color = Config.COLORS['success']
            elif change < 0:
                symbol = "↘"
                color = Config.COLORS['danger']
            else:
                symbol = "→"
                color = Config.COLORS['text_light']

            if self.format_type == "currency":
                return f"{symbol} ${abs(change):.2f} ({abs(percent_change):.1f}%)"
            else:
                return f"{symbol} {abs(change):.0f} ({abs(percent_change):.1f}%)"

        except (ValueError, TypeError):
            return "Datos inválidos"

class ComplianceCard(tk.Frame):
    """Tarjeta especial para cumplimiento legal"""

    def __init__(self, parent, items=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.items = items or []
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz de cumplimiento"""
        # Configurar frame principal con color de éxito
        self.configure(
            bg=Config.COLORS['success'],
            relief='flat',
            bd=0
        )

        # Frame interno
        inner_frame = tk.Frame(self, bg=Config.COLORS['success'])
        inner_frame.pack(fill="both", expand=True, padx=25, pady=20)

        # Título
        title_label = tk.Label(
            inner_frame,
            text="⚖ Cumplimiento Ecuador - Sector Seguridad",
            font=Config.FONTS['subheading'],
            bg=Config.COLORS['success'],
            fg='white'
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Grid de elementos de cumplimiento
        grid_frame = tk.Frame(inner_frame, bg=Config.COLORS['success'])
        grid_frame.pack(fill="x")

        # Configurar grid
        for i in range(6):
            grid_frame.columnconfigure(i, weight=1)

        # Elementos por defecto si no se proporcionan
        default_items = [
            ("Aportaciones IESS", "100%"),
            ("Décimo Tercer Sueldo", "Al día"),
            ("Décimo Cuarto Sueldo", "Al día"),
            ("Fondos de Reserva", "Calculado"),
            ("Vacaciones Pagadas", "95.2%"),
            ("Horas Extras Reguladas", "Controlado")
        ]

        items_to_use = self.items if self.items else default_items

        for i, (label, value) in enumerate(items_to_use):
            self.create_compliance_item(grid_frame, label, value, i)

    def create_compliance_item(self, parent, label, value, column):
        """Crear elemento de cumplimiento"""
        # Frame del item con fondo semi-transparente
        item_frame = tk.Frame(
            parent,
            bg='#e8f5e8',  # Verde claro compatible
            relief='flat'
        )
        item_frame.grid(row=0, column=column, padx=5, pady=5, sticky="ew")

        # Frame interno
        inner = tk.Frame(item_frame, bg='#e8f5e8')
        inner.pack(fill="both", expand=True, padx=15, pady=15)

        # Label
        label_widget = tk.Label(
            inner,
            text=label,
            font=Config.FONTS['small'],
            bg='#e8f5e8',
            fg='#2d5a2d',
            wraplength=100,
            justify='center'
        )
        label_widget.pack()

        # Valor
        value_widget = tk.Label(
            inner,
            text=value,
            font=('Segoe UI', 16, 'bold'),
            bg='#e8f5e8',
            fg='#2d5a2d'
        )
        value_widget.pack(pady=(5, 0))