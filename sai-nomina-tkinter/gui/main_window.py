"""Ventana principal de la aplicación"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import logging

from config import Config
from gui.components.sidebar import Sidebar
from gui.components.header import Header

logger = logging.getLogger(__name__)

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title(Config.APP_NAME)
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.state('zoomed') if hasattr(self.root, 'state') else None

        # Configurar el cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variables
        self.current_module = None
        self.current_user = "Admin"  # TODO: Implementar login

        # Crear interfaz
        self.setup_ui()

        # Cargar módulo inicial
        self.load_module("empleados")

    def setup_ui(self):
        """Configurar la interfaz principal"""
        # Contenedor principal con gradiente
        self.main_container = tk.Frame(self.root, bg=Config.COLORS['background'])
        self.main_container.pack(fill="both", expand=True)

        # Header
        self.header = Header(self.main_container, self.current_user)
        self.header.pack(fill="x", padx=0, pady=0)

        # Contenedor para sidebar y contenido
        self.content_container = tk.Frame(self.main_container, bg=Config.COLORS['background'])
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Grid para sidebar y área de contenido
        self.content_container.grid_columnconfigure(1, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self.content_container, self.load_module)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 20))

        # Área de contenido
        self.content_area = tk.Frame(
            self.content_container,
            bg=Config.COLORS['surface'],
            relief="flat"
        )
        self.content_area.grid(row=0, column=1, sticky="nsew")

        # Aplicar estilo de tarjeta al área de contenido
        self.apply_card_style(self.content_area)

    def apply_card_style(self, widget):
        """Aplicar estilo de tarjeta con sombra"""
        widget.configure(
            highlightbackground=Config.COLORS['card_shadow'],
            highlightcolor=Config.COLORS['card_shadow'],
            highlightthickness=2
        )

    def load_module(self, module_name):
        """Cargar un módulo específico"""
        logger.info(f"Cargando módulo: {module_name}")

        # Limpiar contenido actual
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Crear instancia del módulo
        try:
            if module_name == "empleados":
                from gui.modules.empleados import EmpleadosModule
                self.current_module = EmpleadosModule(self.content_area)
            elif module_name == "nomina":
                from gui.modules.nomina import NominaModule
                self.current_module = NominaModule(self.content_area)
            elif module_name == "decimos":
                from gui.modules.decimos import DecimosModule
                self.current_module = DecimosModule(self.content_area)
            elif module_name == "vacaciones":
                from gui.modules.vacaciones import VacacionesModule
                self.current_module = VacacionesModule(self.content_area)
            elif module_name == "prestamos":
                from gui.modules.prestamos import PrestamosModule
                self.current_module = PrestamosModule(self.content_area)
            elif module_name == "egresos":
                from gui.modules.egresos import EgresosModule
                self.current_module = EgresosModule(self.content_area)
            elif module_name == "dotacion":
                from gui.modules.dotacion import DotacionModule
                self.current_module = DotacionModule(self.content_area)
            elif module_name == "reportes":
                from gui.modules.reportes import ReportesModule
                self.current_module = ReportesModule(self.content_area)
            else:
                self.show_placeholder_module(module_name)
                return

            self.current_module.pack(fill="both", expand=True)

            # Actualizar sidebar
            self.sidebar.set_active(module_name)

        except ImportError as e:
            logger.warning(f"Módulo {module_name} no implementado aún: {e}")
            self.show_placeholder_module(module_name)
        except Exception as e:
            logger.error(f"Error cargando módulo {module_name}: {e}")
            messagebox.showerror("Error", f"Error cargando módulo '{module_name}':\n{str(e)}")

    def show_placeholder_module(self, module_name):
        """Mostrar módulo placeholder"""
        placeholder_frame = tk.Frame(self.content_area, bg=Config.COLORS['surface'])
        placeholder_frame.pack(fill="both", expand=True, padx=50, pady=50)

        # Icono grande
        icon_label = tk.Label(
            placeholder_frame,
            text="🚧",
            font=('Segoe UI', 72),
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text_light']
        )
        icon_label.pack(pady=(50, 20))

        # Título
        title_label = tk.Label(
            placeholder_frame,
            text=f"Módulo {module_name.title()}",
            font=Config.FONTS['heading'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['secondary']
        )
        title_label.pack(pady=(0, 10))

        # Mensaje
        message_label = tk.Label(
            placeholder_frame,
            text="En desarrollo - Próximamente disponible",
            font=Config.FONTS['default'],
            bg=Config.COLORS['surface'],
            fg=Config.COLORS['text']
        )
        message_label.pack()

        # Información adicional
        info_text = self.get_module_info(module_name)
        if info_text:
            info_label = tk.Label(
                placeholder_frame,
                text=info_text,
                font=Config.FONTS['small'],
                bg=Config.COLORS['surface'],
                fg=Config.COLORS['text_light'],
                wraplength=400,
                justify='center'
            )
            info_label.pack(pady=(20, 0))

        self.current_module = placeholder_frame

    def get_module_info(self, module_name):
        """Obtener información descriptiva del módulo"""
        module_descriptions = {
            "empleados": "Gestión completa de empleados, incluyendo datos personales, laborales y de contacto. Funciones de CRUD, búsqueda avanzada y carga masiva.",
            "nomina": "Procesamiento de roles de pago semanales, quincenales y mensuales. Cálculo automático de horas extras, comisiones y descuentos.",
            "decimos": "Cálculo y control de décimo tercer sueldo, décimo cuarto sueldo y fondos de reserva según normativa ecuatoriana.",
            "vacaciones": "Control de vacaciones anuales, saldos pendientes, solicitudes y pagos. Cálculo automático de días laborables.",
            "prestamos": "Gestión de préstamos, anticipos y descuentos. Control de cuotas, intereses y saldos pendientes.",
            "egresos": "Administración de descuentos varios, multas, uniformes y otros egresos del empleado.",
            "dotacion": "Control de entrega y devolución de uniformes, equipos de seguridad y herramientas de trabajo.",
            "reportes": "Generación de reportes en PDF y Excel. Análisis estadísticos y gráficos de recursos humanos."
        }

        return module_descriptions.get(module_name, "")

    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Desea salir del sistema?"):
            logger.info("Cerrando aplicación")

            # Limpiar recursos
            try:
                from database.connection import close_session
                close_session()
            except:
                pass

            self.root.quit()

    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = f"""
{Config.APP_NAME}
Versión {Config.APP_VERSION}

Sistema de Nómina y Recursos Humanos
Desarrollado para {Config.COMPANY_NAME}

Características:
• Gestión completa de empleados
• Procesamiento de nóminas ecuatorianas
• Cálculo automático de décimos
• Control de vacaciones y prestamos
• Reportes y análisis avanzados
• Carga masiva de datos
• Cumplimiento normativa Ecuador

© 2024 - Todos los derechos reservados
        """

        messagebox.showinfo("Acerca de", about_text)

    def show_help(self):
        """Mostrar ayuda del sistema"""
        help_text = """
AYUDA DEL SISTEMA

Navegación:
• Use el menú lateral para acceder a los módulos
• Haga doble clic en registros para editarlos
• Use el botón derecho para opciones adicionales

Búsqueda:
• Use % como comodín (ej: Juan%)
• Los filtros se aplican en tiempo real
• Combine múltiples criterios

Carga Masiva:
• Descargue las plantillas Excel
• Complete los datos requeridos
• Use el botón "Carga Masiva" en cada módulo

Atajos de Teclado:
• F5: Actualizar datos
• Ctrl+F: Buscar
• Ctrl+N: Nuevo registro
• Escape: Cancelar operación

Para soporte técnico contacte al administrador.
        """

        messagebox.showinfo("Ayuda", help_text)

    def export_backup(self):
        """Exportar respaldo de la base de datos"""
        from tkinter import filedialog
        from datetime import datetime
        from database.connection import DatabaseManager

        try:
            # Seleccionar ubicación
            filename = filedialog.asksaveasfilename(
                title="Guardar respaldo",
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                initialvalue=f"sai_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )

            if filename:
                db_manager = DatabaseManager()
                if db_manager.backup_database(filename):
                    messagebox.showinfo("Éxito", "Respaldo creado correctamente")
                else:
                    messagebox.showerror("Error", "Error al crear respaldo")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar respaldo:\n{str(e)}")

    def import_backup(self):
        """Importar respaldo de la base de datos"""
        from tkinter import filedialog
        from database.connection import DatabaseManager

        try:
            # Confirmación
            if not messagebox.askyesno(
                "Confirmar",
                "Esta operación reemplazará todos los datos actuales.\n¿Está seguro?"
            ):
                return

            # Seleccionar archivo
            filename = filedialog.askopenfilename(
                title="Seleccionar respaldo",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )

            if filename:
                db_manager = DatabaseManager()
                if db_manager.restore_database(filename):
                    messagebox.showinfo("Éxito", "Respaldo restaurado correctamente")
                    # Recargar módulo actual
                    if self.current_module:
                        current_module_name = getattr(self.current_module, 'module_name', 'empleados')
                        self.load_module(current_module_name)
                else:
                    messagebox.showerror("Error", "Error al restaurar respaldo")

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar respaldo:\n{str(e)}")

    def show_system_info(self):
        """Mostrar información del sistema"""
        from database.connection import DatabaseManager

        try:
            db_manager = DatabaseManager()
            info = db_manager.get_database_info()

            info_text = f"""
INFORMACIÓN DEL SISTEMA

Base de Datos:
• Empleados Activos: {info.get('empleados_activos', 0)}
• Empleados Total: {info.get('empleados_total', 0)}
• Departamentos: {info.get('departamentos', 0)}
• Cargos: {info.get('cargos', 0)}

Nómina:
• Roles Procesados: {info.get('roles_procesados', 0)}
• Vacaciones Pendientes: {info.get('vacaciones_pendientes', 0)}
• Préstamos Activos: {info.get('prestamos_activos', 0)}

Sistema:
• Versión: {Config.APP_VERSION}
• Base de Datos: SQLite
• Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            """

            messagebox.showinfo("Información del Sistema", info_text)

        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo información:\n{str(e)}")

class LoginWindow:
    """Ventana de login (placeholder para implementación futura)"""

    def __init__(self, root):
        self.root = root
        self.result = None

        # Por ahora, simplemente devolver usuario admin
        self.result = "Admin"

    def show(self):
        """Mostrar ventana de login"""
        # TODO: Implementar ventana de login real
        return self.result