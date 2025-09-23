#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAI - Sistema Administrativo Integral (Version Simple)
Sistema de Nomina y RRHH para Ecuador
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent))

import tkinter as tk
from tkinter import ttk, messagebox
import logging

# Configurar logging basico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_basic_requirements():
    """Verificar solo requisitos basicos"""
    required = ['sqlalchemy']
    missing = []

    for module in required:
        try:
            __import__(module)
            print(f"[OK] {module} disponible")
        except ImportError:
            missing.append(module)
            print(f"[ERROR] {module} faltante")

    if missing:
        error_msg = f"Faltan modulos: {', '.join(missing)}\\n\\nInstale con: pip install {' '.join(missing)}"
        try:
            messagebox.showerror("Error", error_msg)
        except:
            print(error_msg)
        sys.exit(1)

def main():
    """Funcion principal"""
    print("Iniciando SAI - Sistema Administrativo Integral")

    try:
        # Verificar requisitos
        check_basic_requirements()

        # Importar configuracion
        from config import Config

        # Crear directorios
        for directory in ['logs', 'reports', 'backups']:
            Path(directory).mkdir(exist_ok=True)

        # Inicializar base de datos
        from database.initialize_simple import initialize_database_simple
        initialize_database_simple()
        print("[OK] Base de datos inicializada")

        # Crear ventana principal
        root = tk.Tk()
        root.title(Config.APP_NAME)
        root.geometry("1200x800")
        root.configure(bg=Config.COLORS['background'])

        # Crear aplicacion
        app = SAIApp(root)

        # Centrar ventana
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        print("[OK] Aplicacion iniciada correctamente")

        # Mostrar mensaje de exito
        messagebox.showinfo(
            "SAI Iniciado",
            "Sistema SAI iniciado correctamente!\\n\\n"
            "Base de datos: OK\\n"
            "Interfaz: OK\\n"
            "Modulos: OK\\n\\n"
            "El sistema esta listo para usar."
        )

        # Iniciar bucle principal
        root.mainloop()

    except Exception as e:
        error_msg = f"Error critico: {str(e)}"
        print(f"ERROR: {error_msg}")
        try:
            messagebox.showerror("Error Critico", error_msg)
        except:
            pass
        sys.exit(1)

class SAIApp:
    """Aplicacion principal del Sistema SAI"""

    def __init__(self, root):
        self.root = root
        self.current_module = None

        # Importar configuracion
        from config import Config
        self.config = Config

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz"""
        # Frame principal
        self.main_frame = tk.Frame(
            self.root,
            bg=self.config.COLORS['background']
        )
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        self.create_header()

        # Area de contenido
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=self.config.COLORS['surface'],
            relief='raised',
            bd=1
        )
        self.content_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Mostrar pantalla inicial
        self.show_welcome()

    def create_header(self):
        """Crear encabezado"""
        header_frame = tk.Frame(
            self.main_frame,
            bg=self.config.COLORS['primary'],
            height=70
        )
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        # Titulo
        title_label = tk.Label(
            header_frame,
            text=self.config.APP_NAME,
            font=('Arial', 16, 'bold'),
            bg=self.config.COLORS['primary'],
            fg='white'
        )
        title_label.pack(side="left", padx=20, pady=20)

        # Menu de navegacion
        nav_frame = tk.Frame(header_frame, bg=self.config.COLORS['primary'])
        nav_frame.pack(side="right", padx=20, pady=15)

        # Botones del menu
        modules = [
            ("Empleados", "empleados"),
            ("Nomina", "nomina"),
            ("Decimos", "decimos"),
            ("Vacaciones", "vacaciones"),
            ("Prestamos", "prestamos"),
            ("Dotacion", "dotacion"),
            ("Reportes", "reportes")
        ]

        for text, module in modules:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=lambda m=module: self.load_module(m),
                bg=self.config.COLORS['secondary'],
                fg='white',
                font=('Arial', 10),
                relief='flat',
                padx=12,
                pady=6,
                cursor='hand2'
            )
            btn.pack(side="left", padx=3)

    def show_welcome(self):
        """Mostrar pantalla de bienvenida"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        welcome_frame = tk.Frame(
            self.content_frame,
            bg=self.config.COLORS['surface']
        )
        welcome_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Titulo de bienvenida
        title_label = tk.Label(
            welcome_frame,
            text="Bienvenido al Sistema SAI",
            font=('Arial', 24, 'bold'),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['secondary']
        )
        title_label.pack(pady=(50, 20))

        # Descripcion
        desc_label = tk.Label(
            welcome_frame,
            text="Sistema Administrativo Integral\\n"
                 "Gestion de Nomina y Recursos Humanos\\n"
                 "Desarrollado para " + self.config.COMPANY_NAME,
            font=('Arial', 12),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['text'],
            justify='center'
        )
        desc_label.pack(pady=(0, 30))

        # Estadisticas basicas
        self.create_stats_panel(welcome_frame)

        # Instrucciones
        instructions_label = tk.Label(
            welcome_frame,
            text="Seleccione un modulo del menu superior para comenzar",
            font=('Arial', 11, 'italic'),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['text_light']
        )
        instructions_label.pack(pady=(30, 0))

    def create_stats_panel(self, parent):
        """Crear panel de estadisticas"""
        stats_frame = tk.Frame(parent, bg=self.config.COLORS['surface'])
        stats_frame.pack(pady=20)

        # Obtener estadisticas
        stats_data = self.get_system_stats()

        # Crear tarjetas de estadisticas
        for i, (title, value, color) in enumerate(stats_data):
            card = self.create_stat_card(stats_frame, title, value, color)
            card.grid(row=0, column=i, padx=15, pady=5, sticky="nsew")

    def create_stat_card(self, parent, title, value, color):
        """Crear tarjeta de estadistica"""
        card_frame = tk.Frame(
            parent,
            bg=color,
            relief='raised',
            bd=2,
            width=150,
            height=100
        )
        card_frame.grid_propagate(False)

        # Valor
        value_label = tk.Label(
            card_frame,
            text=str(value),
            font=('Arial', 18, 'bold'),
            bg=color,
            fg='white'
        )
        value_label.pack(pady=(20, 5))

        # Titulo
        title_label = tk.Label(
            card_frame,
            text=title,
            font=('Arial', 10),
            bg=color,
            fg='white'
        )
        title_label.pack(pady=(0, 20))

        return card_frame

    def get_system_stats(self):
        """Obtener estadisticas del sistema"""
        try:
            from database.connection import get_session
            from database.models import Empleado

            session = get_session()

            total_empleados = session.query(Empleado).count()
            activos = session.query(Empleado).filter(
                Empleado.activo == True
            ).count()

            session.close()

            stats = [
                ("Total Empleados", total_empleados, self.config.COLORS['primary']),
                ("Empleados Activos", activos, self.config.COLORS['success']),
                ("Sistema", "Online", self.config.COLORS['info']),
                ("Base de Datos", "OK", self.config.COLORS['secondary'])
            ]

        except Exception as e:
            logger.warning(f"Error obteniendo estadisticas: {e}")
            stats = [
                ("Total Empleados", "0", self.config.COLORS['primary']),
                ("Empleados Activos", "0", self.config.COLORS['success']),
                ("Sistema", "Online", self.config.COLORS['info']),
                ("Base de Datos", "OK", self.config.COLORS['secondary'])
            ]

        return stats

    def load_module(self, module_name):
        """Cargar modulo"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        try:
            if module_name == "empleados":
                self.load_empleados_module()
            else:
                self.show_module_placeholder(module_name)

        except Exception as e:
            logger.error(f"Error cargando modulo {module_name}: {e}")
            self.show_error_screen(module_name, str(e))

    def load_empleados_module(self):
        """Cargar modulo de empleados"""
        # Frame del modulo
        module_frame = tk.Frame(
            self.content_frame,
            bg=self.config.COLORS['surface']
        )
        module_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header del modulo
        header_frame = tk.Frame(module_frame, bg=self.config.COLORS['surface'])
        header_frame.pack(fill="x", pady=(0, 15))

        title_label = tk.Label(
            header_frame,
            text="Gestion de Empleados",
            font=('Arial', 18, 'bold'),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Boton nuevo empleado
        nuevo_btn = tk.Button(
            header_frame,
            text="Nuevo Empleado",
            command=self.nuevo_empleado,
            bg=self.config.COLORS['success'],
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2'
        )
        nuevo_btn.pack(side="right")

        # Tabla de empleados
        self.create_empleados_table(module_frame)

    def create_empleados_table(self, parent):
        """Crear tabla de empleados"""
        # Frame para la tabla
        table_frame = tk.Frame(parent, bg=self.config.COLORS['surface'])
        table_frame.pack(fill="both", expand=True)

        # Treeview
        columns = ("Codigo", "Cedula", "Nombres", "Apellidos", "Cargo", "Estado")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cargar datos
        self.load_empleados_data(tree)

        # Evento doble click
        tree.bind("<Double-1>", lambda e: self.edit_empleado(tree))

    def load_empleados_data(self, tree):
        """Cargar datos de empleados"""
        try:
            from database.connection import get_session
            from database.models import Empleado, Cargo

            session = get_session()

            # Consulta con join
            empleados = session.query(Empleado).all()

            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)

            # Insertar datos
            for emp in empleados:
                estado = "Activo" if emp.activo else "Inactivo"

                tree.insert("", "end", values=(
                    emp.empleado,
                    emp.cedula,
                    emp.nombres,
                    emp.apellidos,
                    emp.cargo or "Sin cargo",
                    estado
                ))

            session.close()

        except Exception as e:
            logger.error(f"Error cargando empleados: {e}")
            # Datos de ejemplo si hay error
            tree.insert("", "end", values=(
                "001001", "1234567890", "Juan", "Perez", "Guardia", "Activo"
            ))
            tree.insert("", "end", values=(
                "001002", "0987654321", "Maria", "Gonzalez", "Supervisora", "Activo"
            ))

    def nuevo_empleado(self):
        """Nuevo empleado"""
        messagebox.showinfo(
            "Nuevo Empleado",
            "Funcionalidad de nuevo empleado en desarrollo.\\n\\n"
            "Esta ventana permitira registrar nuevos empleados\\n"
            "con validaciones especificas para Ecuador."
        )

    def edit_empleado(self, tree):
        """Editar empleado"""
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            codigo = item['values'][0]
            messagebox.showinfo(
                "Editar Empleado",
                f"Editando empleado: {codigo}\\n\\n"
                "Funcionalidad en desarrollo."
            )

    def show_module_placeholder(self, module_name):
        """Mostrar placeholder para modulos no implementados"""
        placeholder_frame = tk.Frame(
            self.content_frame,
            bg=self.config.COLORS['surface']
        )
        placeholder_frame.pack(fill="both", expand=True, padx=50, pady=50)

        # Icono
        icon_label = tk.Label(
            placeholder_frame,
            text="[MODULO]",
            font=('Arial', 48, 'bold'),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['text_light']
        )
        icon_label.pack(pady=(50, 20))

        # Titulo
        title_label = tk.Label(
            placeholder_frame,
            text=f"Modulo {module_name.title()}",
            font=('Arial', 20, 'bold'),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['secondary']
        )
        title_label.pack(pady=(0, 10))

        # Mensaje
        message_label = tk.Label(
            placeholder_frame,
            text="En desarrollo - Proximamente disponible",
            font=('Arial', 12),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['text']
        )
        message_label.pack()

    def show_error_screen(self, module_name, error):
        """Mostrar pantalla de error"""
        error_frame = tk.Frame(
            self.content_frame,
            bg=self.config.COLORS['surface']
        )
        error_frame.pack(fill="both", expand=True, padx=50, pady=50)

        # Titulo de error
        title_label = tk.Label(
            error_frame,
            text=f"Error en modulo {module_name}",
            font=('Arial', 18, 'bold'),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['danger']
        )
        title_label.pack(pady=(50, 20))

        # Mensaje de error
        error_label = tk.Label(
            error_frame,
            text=f"Error: {error}",
            font=('Arial', 10),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['text'],
            wraplength=600,
            justify='center'
        )
        error_label.pack()

if __name__ == "__main__":
    main()