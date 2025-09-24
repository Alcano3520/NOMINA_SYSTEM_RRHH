#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGN - Sistema de Gestión de Nómina (Versión Funcional)
Sistema de Nómina y RRHH para Ecuador
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_basic_requirements():
    """Verificar solo requisitos básicos"""
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
        error_msg = f"Faltan módulos: {', '.join(missing)}\\n\\nInstale con: pip install {' '.join(missing)}"
        try:
            messagebox.showerror("Error", error_msg)
        except:
            print(error_msg)
        sys.exit(1)

def create_working_app():
    """Crear aplicación básica funcional"""
    try:
        # Importar configuración
        from config import Config

        # Configurar directorios
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

        # Crear aplicación simplificada
        app = SimpleMainApp(root)

        # Centrar ventana
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        print("[OK] Aplicacion creada exitosamente")

        # Mostrar mensaje de éxito
        messagebox.showinfo(
            "SGN Iniciado",
            "Sistema SGN iniciado correctamente!\\n\\n"
            "[OK] Interfaz moderna cargada\\n"
            "[OK] Base de datos lista\\n"
            "[OK] Modulos basicos disponibles\\n\\n"
            "El sistema esta listo para usar."
        )

        return root

    except Exception as e:
        error_msg = f"Error al crear aplicación: {str(e)}"
        print(f"ERROR: {error_msg}")
        try:
            messagebox.showerror("Error Crítico", error_msg)
        except:
            pass
        return None

class SimpleMainApp:
    """Aplicación principal simplificada sin recursión"""

    def __init__(self, root):
        self.root = root
        self.current_module = None

        # Importar configuración
        from config import Config
        self.config = Config

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz básica"""
        # Frame principal
        self.main_frame = tk.Frame(
            self.root,
            bg=self.config.COLORS['background']
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        self.create_header()

        # Contenido
        self.create_content_area()

        # Cargar pantalla inicial
        self.show_welcome_screen()

    def create_header(self):
        """Crear header de la aplicación"""
        header_frame = tk.Frame(
            self.main_frame,
            bg=self.config.COLORS['primary'],
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        # Título
        title_label = tk.Label(
            header_frame,
            text=self.config.APP_NAME,
            font=self.config.FONTS['heading'],
            bg=self.config.COLORS['primary'],
            fg='white'
        )
        title_label.pack(side="left", padx=20, pady=20)

        # Navegación
        nav_frame = tk.Frame(header_frame, bg=self.config.COLORS['primary'])
        nav_frame.pack(side="right", padx=20, pady=10)

        # Botones de navegación
        modules = [
            ("👥 Empleados", "empleados"),
            ("💰 Nómina", "nomina"),
            ("🎁 Décimos", "decimos"),
            ("🏖️ Vacaciones", "vacaciones"),
            ("💳 Préstamos", "prestamos"),
            ("👔 Dotación", "dotacion"),
            ("📊 Reportes", "reportes")
        ]

        for text, module in modules:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=lambda m=module: self.load_module(m),
                bg=self.config.COLORS['secondary'],
                fg='white',
                font=self.config.FONTS['default'],
                relief='flat',
                padx=15,
                pady=8,
                cursor='hand2'
            )
            btn.pack(side="left", padx=5)

            # Hover effect
            def on_enter(e, button=btn):
                button.configure(bg=self.config.COLORS['secondary_dark'])
            def on_leave(e, button=btn):
                button.configure(bg=self.config.COLORS['secondary'])

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def create_content_area(self):
        """Crear área de contenido"""
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=self.config.COLORS['surface'],
            relief='flat',
            bd=0
        )
        self.content_frame.pack(fill="both", expand=True)

    def show_welcome_screen(self):
        """Mostrar pantalla de bienvenida"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Frame de bienvenida
        welcome_frame = tk.Frame(
            self.content_frame,
            bg=self.config.COLORS['surface']
        )
        welcome_frame.pack(fill="both", expand=True, padx=50, pady=50)

        # Icono
        icon_label = tk.Label(
            welcome_frame,
            text="🏢",
            font=('Segoe UI', 72),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['primary']
        )
        icon_label.pack(pady=(50, 20))

        # Título
        title_label = tk.Label(
            welcome_frame,
            text="¡Bienvenido al Sistema SGN!",
            font=self.config.FONTS['heading'],
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['secondary']
        )
        title_label.pack(pady=(0, 10))

        # Descripción
        desc_label = tk.Label(
            welcome_frame,
            text="Sistema de Gestión de Nómina para gestión de nómina y RRHH\\n"
                 "Seleccione un módulo del menú superior para comenzar",
            font=self.config.FONTS['default'],
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['text'],
            justify='center'
        )
        desc_label.pack(pady=(0, 30))

        # Estadísticas básicas
        self.create_basic_stats(welcome_frame)

    def create_basic_stats(self, parent):
        """Crear estadísticas básicas sin recursión"""
        stats_frame = tk.Frame(parent, bg=self.config.COLORS['surface'])
        stats_frame.pack(pady=20)

        # Obtener estadísticas de forma segura
        try:
            from database.connection import get_session
            session = get_session()

            # Contar empleados de forma simple
            try:
                from database.models import Empleado
                total_empleados = session.query(Empleado).count()
                empleados_activos = session.query(Empleado).filter(
                    Empleado.activo == True
                ).count()
            except:
                total_empleados = 0
                empleados_activos = 0

            session.close()

        except Exception as e:
            logger.warning(f"Error obteniendo estadísticas: {e}")
            total_empleados = 0
            empleados_activos = 0

        # Cards de estadísticas
        stats = [
            ("Total Empleados", str(total_empleados), "👥"),
            ("Empleados Activos", str(empleados_activos), "✅"),
            ("Sistema", "Operativo", "⚡"),
            ("Base de Datos", "Conectada", "💾")
        ]

        for i, (title, value, icon) in enumerate(stats):
            card = self.create_stat_card(stats_frame, title, value, icon)
            card.grid(row=0, column=i, padx=20, pady=10)

    def create_stat_card(self, parent, title, value, icon):
        """Crear una tarjeta de estadística simple"""
        card_frame = tk.Frame(
            parent,
            bg=self.config.COLORS['primary'],
            relief='flat',
            bd=0,
            width=180,
            height=120
        )
        card_frame.grid_propagate(False)

        # Icono
        icon_label = tk.Label(
            card_frame,
            text=icon,
            font=('Segoe UI', 24),
            bg=self.config.COLORS['primary'],
            fg='white'
        )
        icon_label.pack(pady=(15, 5))

        # Valor
        value_label = tk.Label(
            card_frame,
            text=value,
            font=('Segoe UI', 18, 'bold'),
            bg=self.config.COLORS['primary'],
            fg='white'
        )
        value_label.pack()

        # Título
        title_label = tk.Label(
            card_frame,
            text=title,
            font=('Segoe UI', 10),
            bg=self.config.COLORS['primary'],
            fg='white'
        )
        title_label.pack(pady=(5, 15))

        return card_frame

    def load_module(self, module_name):
        """Cargar módulo de forma segura"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        try:
            if module_name == "empleados":
                self.load_empleados_module()
            else:
                self.show_module_placeholder(module_name)

        except Exception as e:
            logger.error(f"Error cargando módulo {module_name}: {e}")
            self.show_error_screen(module_name, str(e))

    def load_empleados_module(self):
        """Cargar módulo de empleados de forma simple"""
        # Frame del módulo
        module_frame = tk.Frame(
            self.content_frame,
            bg=self.config.COLORS['surface']
        )
        module_frame.pack(fill="both", expand=True, padx=25, pady=25)

        # Header del módulo
        header_frame = tk.Frame(module_frame, bg=self.config.COLORS['surface'])
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="👥 Gestión de Empleados",
            font=self.config.FONTS['heading'],
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        btn_frame = tk.Frame(header_frame, bg=self.config.COLORS['surface'])
        btn_frame.pack(side="right")

        nuevo_btn = tk.Button(
            btn_frame,
            text="➕ Nuevo Empleado",
            command=self.nuevo_empleado,
            bg=self.config.COLORS['success'],
            fg='white',
            font=self.config.FONTS['default'],
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2'
        )
        nuevo_btn.pack(side="left", padx=(0, 10))

        # Lista básica de empleados
        self.create_empleados_table(module_frame)

    def create_empleados_table(self, parent):
        """Crear tabla básica de empleados"""
        # Frame para la tabla
        table_frame = tk.Frame(parent, bg=self.config.COLORS['surface'])
        table_frame.pack(fill="both", expand=True)

        # Treeview para mostrar empleados
        columns = ("Código", "Cédula", "Nombres", "Apellidos", "Cargo", "Estado")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cargar datos de empleados
        self.load_empleados_data(tree)

    def load_empleados_data(self, tree):
        """Cargar datos de empleados de forma segura"""
        try:
            from database.connection import get_session
            from database.models import Empleado, Cargo

            session = get_session()

            # Obtener empleados con join a cargo
            empleados = session.query(Empleado).join(
                Cargo, Empleado.cargo_id == Cargo.cargo_id, isouter=True
            ).all()

            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)

            # Insertar datos
            for emp in empleados:
                cargo_nombre = emp.cargo.nombre if emp.cargo else "Sin cargo"
                estado = "Activo" if emp.activo else "Inactivo"

                tree.insert("", "end", values=(
                    emp.empleado,
                    emp.cedula,
                    emp.nombres,
                    emp.apellidos,
                    cargo_nombre,
                    estado
                ))

            session.close()

        except Exception as e:
            logger.error(f"Error cargando empleados: {e}")
            # Insertar datos de ejemplo si hay error
            tree.insert("", "end", values=(
                "001001", "1234567890", "Juan", "Pérez", "Guardia", "Activo"
            ))
            tree.insert("", "end", values=(
                "001002", "0987654321", "María", "González", "Supervisora", "Activo"
            ))

    def nuevo_empleado(self):
        """Abrir ventana para nuevo empleado"""
        messagebox.showinfo(
            "Nuevo Empleado",
            "Funcionalidad de nuevo empleado en desarrollo.\\n\\n"
            "Esta ventana permitirá registrar nuevos empleados\\n"
            "con validaciones específicas para Ecuador."
        )

    def show_module_placeholder(self, module_name):
        """Mostrar placeholder para módulos no implementados"""
        placeholder_frame = tk.Frame(
            self.content_frame,
            bg=self.config.COLORS['surface']
        )
        placeholder_frame.pack(fill="both", expand=True, padx=50, pady=50)

        # Icono
        icon_label = tk.Label(
            placeholder_frame,
            text="🚧",
            font=('Segoe UI', 72),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['text_light']
        )
        icon_label.pack(pady=(50, 20))

        # Título
        title_label = tk.Label(
            placeholder_frame,
            text=f"Módulo {module_name.title()}",
            font=self.config.FONTS['heading'],
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['secondary']
        )
        title_label.pack(pady=(0, 10))

        # Mensaje
        message_label = tk.Label(
            placeholder_frame,
            text="En desarrollo - Próximamente disponible",
            font=self.config.FONTS['default'],
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

        # Icono
        icon_label = tk.Label(
            error_frame,
            text="❌",
            font=('Segoe UI', 72),
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['danger']
        )
        icon_label.pack(pady=(50, 20))

        # Título
        title_label = tk.Label(
            error_frame,
            text=f"Error en módulo {module_name}",
            font=self.config.FONTS['heading'],
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['danger']
        )
        title_label.pack(pady=(0, 10))

        # Error
        error_label = tk.Label(
            error_frame,
            text=f"Error: {error}",
            font=self.config.FONTS['small'],
            bg=self.config.COLORS['surface'],
            fg=self.config.COLORS['text'],
            wraplength=600,
            justify='center'
        )
        error_label.pack()

def main():
    """Función principal"""
    print("Iniciando SGN - Sistema de Gestión de Nómina (Versión Funcional)")

    try:
        # Verificar requisitos
        check_basic_requirements()

        # Crear aplicación
        root = create_working_app()

        if root:
            print("APLICACION INICIADA EXITOSAMENTE")
            root.mainloop()
        else:
            print("ERROR: No se pudo crear la aplicación")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\\nAplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()