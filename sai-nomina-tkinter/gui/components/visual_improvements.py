#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mejoras Visuales - Sistema SGN
Componentes para mejorar la experiencia visual del usuario
"""

import tkinter as tk
from tkinter import ttk
import math

class AnimatedButton(tk.Button):
    """Botón con efectos visuales animados"""

    def __init__(self, parent, **kwargs):
        # Colores para animación
        self.original_bg = kwargs.get('bg', '#4299e1')
        self.hover_bg = kwargs.get('hover_bg', self.darken_color(self.original_bg))
        self.active_bg = kwargs.get('active_bg', self.darken_color(self.hover_bg))

        # Configurar botón
        kwargs.update({
            'relief': 'flat',
            'cursor': 'hand2',
            'font': kwargs.get('font', ('Arial', 10, 'bold')),
            'padx': kwargs.get('padx', 15),
            'pady': kwargs.get('pady', 8)
        })

        super().__init__(parent, **kwargs)

        # Bind eventos para animación
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, event):
        """Efecto hover"""
        self.config(bg=self.hover_bg)

    def on_leave(self, event):
        """Salir del hover"""
        self.config(bg=self.original_bg)

    def on_click(self, event):
        """Efecto al hacer clic"""
        self.config(bg=self.active_bg)

    def on_release(self, event):
        """Efecto al soltar clic"""
        self.config(bg=self.hover_bg)

    def darken_color(self, color):
        """Oscurecer color para efectos"""
        color_map = {
            '#4299e1': '#3182ce',
            '#48bb78': '#38a169',
            '#ed8936': '#dd6b20',
            '#9f7aea': '#805ad5',
            '#e53e3e': '#c53030',
            '#38a169': '#2f855a'
        }
        return color_map.get(color, color)


class ModernCard(tk.Frame):
    """Tarjeta moderna con sombra y efectos"""

    def __init__(self, parent, title="", **kwargs):
        # Configuraciones por defecto
        default_config = {
            'bg': 'white',
            'relief': 'solid',
            'bd': 1,
            'padx': 15,
            'pady': 15
        }
        default_config.update(kwargs)

        super().__init__(parent, **default_config)

        if title:
            self.create_header(title)

    def create_header(self, title):
        """Crear header de la tarjeta"""
        header_frame = tk.Frame(self, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(
            header_frame,
            text=title,
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2d3748'
        )
        title_label.pack(anchor='w')

        # Línea separadora
        separator = tk.Frame(header_frame, bg='#e2e8f0', height=2)
        separator.pack(fill=tk.X, pady=(5, 0))


class StatusIndicator(tk.Frame):
    """Indicador de estado visual"""

    def __init__(self, parent, status="active", **kwargs):
        super().__init__(parent, bg=kwargs.get('bg', 'white'))

        self.status = status
        self.create_indicator()

    def create_indicator(self):
        """Crear indicador visual"""
        # Colores según estado
        status_colors = {
            'active': '#48bb78',
            'inactive': '#cbd5e0',
            'warning': '#ed8936',
            'error': '#e53e3e',
            'processing': '#4299e1'
        }

        status_texts = {
            'active': 'Activo',
            'inactive': 'Inactivo',
            'warning': 'Advertencia',
            'error': 'Error',
            'processing': 'Procesando'
        }

        color = status_colors.get(self.status, '#cbd5e0')
        text = status_texts.get(self.status, 'Estado')

        # Círculo indicador
        indicator_frame = tk.Frame(self, bg='white')
        indicator_frame.pack(fill=tk.X)

        circle_canvas = tk.Canvas(
            indicator_frame,
            width=12,
            height=12,
            bg='white',
            highlightthickness=0
        )
        circle_canvas.pack(side=tk.LEFT, padx=(0, 5))

        circle_canvas.create_oval(2, 2, 10, 10, fill=color, outline=color)

        # Texto del estado
        status_label = tk.Label(
            indicator_frame,
            text=text,
            font=('Arial', 9),
            bg='white',
            fg='#4a5568'
        )
        status_label.pack(side=tk.LEFT)

    def update_status(self, new_status):
        """Actualizar estado"""
        self.status = new_status
        for widget in self.winfo_children():
            widget.destroy()
        self.create_indicator()


class StatCard(ModernCard):
    """Tarjeta de estadística"""

    def __init__(self, parent, title="", value="0", subtitle="", icon="📊", color="#4299e1"):
        super().__init__(parent, title="")

        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        self.color = color

        self.create_content()

    def create_content(self):
        """Crear contenido de la estadística"""
        # Container principal
        content_frame = tk.Frame(self, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Header con icono y título
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Icono
        icon_label = tk.Label(
            header_frame,
            text=self.icon,
            font=('Arial', 16),
            bg='white'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # Título
        title_label = tk.Label(
            header_frame,
            text=self.title,
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#4a5568'
        )
        title_label.pack(side=tk.LEFT, anchor='w')

        # Valor principal
        self.value_label = tk.Label(
            content_frame,
            text=self.value,
            font=('Arial', 24, 'bold'),
            bg='white',
            fg=self.color
        )
        self.value_label.pack(anchor='w', pady=(0, 5))

        # Subtítulo
        if self.subtitle:
            subtitle_label = tk.Label(
                content_frame,
                text=self.subtitle,
                font=('Arial', 9),
                bg='white',
                fg='#718096'
            )
            subtitle_label.pack(anchor='w')

    def update_value(self, new_value, new_subtitle=None):
        """Actualizar valor mostrado"""
        self.value_label.config(text=str(new_value))
        if new_subtitle:
            self.subtitle = new_subtitle


class LoadingSpinner(tk.Frame):
    """Spinner de carga animado"""

    def __init__(self, parent, size=20, color="#4299e1", **kwargs):
        super().__init__(parent, **kwargs)

        self.size = size
        self.color = color
        self.angle = 0
        self.is_spinning = False

        self.canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            bg=kwargs.get('bg', 'white'),
            highlightthickness=0
        )
        self.canvas.pack()

        self.draw_spinner()

    def draw_spinner(self):
        """Dibujar spinner"""
        self.canvas.delete("all")

        center = self.size // 2
        radius = center - 2

        # Dibujar arcos para crear efecto de spinner
        for i in range(8):
            start_angle = self.angle + (i * 45)
            alpha = 1.0 - (i * 0.125)  # Efecto fade

            # Calcular posiciones
            x1 = center + (radius * 0.6) * math.cos(math.radians(start_angle))
            y1 = center + (radius * 0.6) * math.sin(math.radians(start_angle))
            x2 = center + radius * math.cos(math.radians(start_angle))
            y2 = center + radius * math.sin(math.radians(start_angle))

            # Color con alpha
            color = self.color
            if alpha < 1.0:
                # Simular transparencia con colores más claros
                color = self.blend_color(color, '#ffffff', 1 - alpha)

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=2,
                capstyle=tk.ROUND
            )

    def blend_color(self, color1, color2, ratio):
        """Mezclar dos colores"""
        # Conversión simple para simular alpha blending
        if color1 == "#4299e1":
            colors = ["#e6f3ff", "#ccebff", "#99d6ff", "#66c2ff", "#4299e1"]
            index = min(int(ratio * len(colors)), len(colors) - 1)
            return colors[index]
        return color1

    def start_spinning(self):
        """Iniciar animación"""
        self.is_spinning = True
        self.spin()

    def stop_spinning(self):
        """Detener animación"""
        self.is_spinning = False

    def spin(self):
        """Función de animación"""
        if self.is_spinning:
            self.angle = (self.angle + 30) % 360
            self.draw_spinner()
            self.after(100, self.spin)


class Toast(tk.Toplevel):
    """Notificación tipo toast"""

    def __init__(self, parent, message, toast_type="info", duration=3000):
        super().__init__(parent)

        self.message = message
        self.toast_type = toast_type
        self.duration = duration

        self.setup_window()
        self.create_content()
        self.show_toast()

    def setup_window(self):
        """Configurar ventana"""
        self.overrideredirect(True)  # Sin decoraciones
        self.attributes('-topmost', True)  # Siempre encima

        # Posición en esquina superior derecha
        screen_width = self.winfo_screenwidth()
        self.geometry(f"300x80+{screen_width-320}+20")

    def create_content(self):
        """Crear contenido del toast"""
        # Colores según tipo
        colors = {
            'info': {'bg': '#4299e1', 'fg': 'white'},
            'success': {'bg': '#48bb78', 'fg': 'white'},
            'warning': {'bg': '#ed8936', 'fg': 'white'},
            'error': {'bg': '#e53e3e', 'fg': 'white'}
        }

        color_config = colors.get(self.toast_type, colors['info'])

        # Frame principal
        main_frame = tk.Frame(
            self,
            bg=color_config['bg'],
            relief='solid',
            bd=1
        )
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Icono según tipo
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }

        icon = icons.get(self.toast_type, 'ℹ️')

        # Container del contenido
        content_frame = tk.Frame(main_frame, bg=color_config['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Icono
        icon_label = tk.Label(
            content_frame,
            text=icon,
            font=('Arial', 14),
            bg=color_config['bg'],
            fg=color_config['fg']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # Mensaje
        message_label = tk.Label(
            content_frame,
            text=self.message,
            font=('Arial', 10),
            bg=color_config['bg'],
            fg=color_config['fg'],
            wraplength=200
        )
        message_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def show_toast(self):
        """Mostrar y ocultar toast"""
        # Mostrar con efecto fade in
        self.attributes('-alpha', 0)
        self.fade_in()

        # Programar desaparición
        self.after(self.duration, self.fade_out)

    def fade_in(self, alpha=0):
        """Efecto fade in"""
        if alpha < 1:
            self.attributes('-alpha', alpha)
            self.after(50, lambda: self.fade_in(alpha + 0.1))

    def fade_out(self, alpha=1):
        """Efecto fade out"""
        if alpha > 0:
            self.attributes('-alpha', alpha)
            self.after(50, lambda: self.fade_out(alpha - 0.1))
        else:
            self.destroy()


# Funciones utilitarias
def show_toast(parent, message, toast_type="info", duration=3000):
    """Mostrar notificación toast"""
    return Toast(parent, message, toast_type, duration)

def create_stat_card(parent, title, value, subtitle="", icon="📊", color="#4299e1"):
    """Crear tarjeta de estadística"""
    return StatCard(parent, title, value, subtitle, icon, color)

def create_modern_button(parent, text, command=None, color="#4299e1", **kwargs):
    """Crear botón moderno con efectos"""
    return AnimatedButton(
        parent,
        text=text,
        command=command,
        bg=color,
        fg='white',
        **kwargs
    )