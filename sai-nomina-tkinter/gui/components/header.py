"""Componente Header - Encabezado principal"""

import tkinter as tk
from datetime import datetime
from config import Config

class Header(tk.Frame):
    def __init__(self, parent, current_user="Admin"):
        super().__init__(
            parent,
            bg=Config.COLORS['primary'],
            height=80,
            relief='flat'
        )

        self.current_user = current_user
        self.pack_propagate(False)

        self.setup_ui()
        self.update_clock()

    def setup_ui(self):
        """Configurar interfaz del header"""
        # Frame principal con gradiente
        main_frame = tk.Frame(self, bg=Config.COLORS['primary'])
        main_frame.pack(fill="both", expand=True, padx=25, pady=15)

        # Lado izquierdo - Título y breadcrumb
        left_frame = tk.Frame(main_frame, bg=Config.COLORS['primary'])
        left_frame.pack(side="left", fill="y")

        # Título principal
        title_label = tk.Label(
            left_frame,
            text=Config.APP_NAME,
            font=('Segoe UI', 18, 'bold'),
            bg=Config.COLORS['primary'],
            fg='white'
        )
        title_label.pack(anchor="w")

        # Subtítulo
        subtitle_label = tk.Label(
            left_frame,
            text="Sistema de Nómina y Recursos Humanos",
            font=Config.FONTS['default'],
            bg=Config.COLORS['primary'],
            fg='white'
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # Lado derecho - Información del usuario y reloj
        right_frame = tk.Frame(main_frame, bg=Config.COLORS['primary'])
        right_frame.pack(side="right", fill="y")

        # Frame de información
        info_frame = tk.Frame(right_frame, bg=Config.COLORS['primary'])
        info_frame.pack(anchor="e")

        # Reloj
        self.clock_label = tk.Label(
            info_frame,
            text="",
            font=('Consolas', 14, 'bold'),
            bg=Config.COLORS['primary'],
            fg='white'
        )
        self.clock_label.pack(anchor="e")

        # Fecha
        self.date_label = tk.Label(
            info_frame,
            text="",
            font=Config.FONTS['default'],
            bg=Config.COLORS['primary'],
            fg='white'
        )
        self.date_label.pack(anchor="e")

        # Separador
        separator = tk.Frame(
            info_frame,
            height=1,
            bg='white',
            width=150
        )
        separator.pack(fill="x", pady=8)

        # Información del usuario
        user_frame = tk.Frame(info_frame, bg=Config.COLORS['primary'])
        user_frame.pack(anchor="e")

        user_icon = tk.Label(
            user_frame,
            text="👤",
            font=Config.FONTS['default'],
            bg=Config.COLORS['primary'],
            fg='white'
        )
        user_icon.pack(side="left")

        user_label = tk.Label(
            user_frame,
            text=f"Usuario: {self.current_user}",
            font=Config.FONTS['default'],
            bg=Config.COLORS['primary'],
            fg='white'
        )
        user_label.pack(side="left", padx=(5, 0))

        # Empresa
        company_label = tk.Label(
            info_frame,
            text=Config.COMPANY_NAME,
            font=Config.FONTS['small'],
            bg=Config.COLORS['primary'],
            fg='white'
        )
        company_label.pack(anchor="e", pady=(2, 0))

    def update_clock(self):
        """Actualizar reloj en tiempo real"""
        now = datetime.now()

        # Formatear hora
        time_str = now.strftime("%H:%M:%S")
        self.clock_label.configure(text=time_str)

        # Formatear fecha
        date_str = now.strftime("%A, %d de %B de %Y")
        # Traducir días y meses al español
        days = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }

        months = {
            'January': 'Enero',
            'February': 'Febrero',
            'March': 'Marzo',
            'April': 'Abril',
            'May': 'Mayo',
            'June': 'Junio',
            'July': 'Julio',
            'August': 'Agosto',
            'September': 'Septiembre',
            'October': 'Octubre',
            'November': 'Noviembre',
            'December': 'Diciembre'
        }

        for eng, esp in days.items():
            date_str = date_str.replace(eng, esp)

        for eng, esp in months.items():
            date_str = date_str.replace(eng, esp)

        self.date_label.configure(text=date_str)

        # Programar siguiente actualización
        self.after(1000, self.update_clock)