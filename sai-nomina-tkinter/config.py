"""Configuración global del sistema"""

import os
from pathlib import Path

class Config:
    # Rutas
    BASE_DIR = Path(__file__).parent
    DATABASE_PATH = BASE_DIR / "sai_nomina.db"
    REPORTS_DIR = BASE_DIR / "reports"
    BACKUPS_DIR = BASE_DIR / "backups"
    TEMPLATES_DIR = BASE_DIR / "assets" / "templates"

    # Base de datos
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

    # Aplicación
    APP_NAME = "SAI - Sistema Administrativo Integral"
    APP_VERSION = "1.0.0"
    COMPANY_NAME = "INSEVIG CIA. LTDA."

    # Ventana principal
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 800

    # Colores del tema (basados en el HTML)
    COLORS = {
        'primary': '#667eea',
        'primary_dark': '#764ba2',
        'secondary': '#1e3c72',
        'secondary_dark': '#2a5298',
        'background': '#f7fafc',
        'surface': '#ffffff',
        'text': '#4a5568',
        'text_light': '#a0aec0',
        'success': '#48bb78',
        'warning': '#ed8936',
        'danger': '#f56565',
        'info': '#4299e1',
        'card_shadow': '#e2e8f0',
        'border': '#e2e8f0',
        'hover': '#edf2f7'
    }

    # Fuentes
    FONTS = {
        'default': ('Segoe UI', 10),
        'heading': ('Segoe UI', 16, 'bold'),
        'subheading': ('Segoe UI', 12, 'bold'),
        'small': ('Segoe UI', 9),
        'icon': ('Segoe UI Symbol', 12),
        'number': ('Consolas', 10)
    }

    # Constantes Ecuador 2024
    SBU = 460.00
    APORTE_PERSONAL_IESS = 0.0945
    APORTE_PATRONAL_IESS = 0.1115
    FONDOS_RESERVA = 0.0833
    HORAS_EXTRAS_25 = 1.25
    HORAS_EXTRAS_50 = 1.5
    HORAS_EXTRAS_100 = 2.0
    JORNADA_SEMANAL = 40
    DIAS_VACACIONES_ANUAL = 15

    # Códigos de conceptos
    CONCEPTOS = {
        'SUELDO': '001',
        'HORAS_EXTRAS_25': '101',
        'HORAS_EXTRAS_50': '102',
        'HORAS_EXTRAS_100': '103',
        'COMISIONES': '104',
        'BONOS': '105',
        'SUBSIDIO_TRANSPORTE': '106',
        'SUBSIDIO_ALIMENTACION': '107',
        'DECIMO_TERCER': '201',
        'DECIMO_CUARTO': '202',
        'FONDOS_RESERVA': '203',
        'VACACIONES': '204',
        'LIQUIDACION': '205',
        'APORTE_IESS': '301',
        'IMPUESTO_RENTA': '302',
        'PRESTAMO': '401',
        'ANTICIPO': '402',
        'MULTA': '403',
        'DESCUENTO_UNIFORME': '404'
    }

    # Estados de empleados
    ESTADOS_EMPLEADO = {
        'ACT': 'Activo',
        'VAC': 'Vacaciones',
        'LIC': 'Licencia',
        'RET': 'Retirado',
        'JUB': 'Jubilado',
        'SUS': 'Suspendido'
    }

    # Tipos de trabajador
    TIPOS_TRABAJADOR = {
        1: 'Operativo',
        2: 'Administrativo',
        3: 'Ejecutivo'
    }

    # Tipos de pago
    TIPOS_PAGO = {
        1: 'Semanal',
        2: 'Quincenal',
        3: 'Mensual'
    }

    # Provincias Ecuador
    PROVINCIAS = [
        'AZUAY', 'BOLIVAR', 'CAÑAR', 'CARCHI', 'CHIMBORAZO', 'COTOPAXI',
        'EL ORO', 'ESMERALDAS', 'GALAPAGOS', 'GUAYAS', 'IMBABURA', 'LOJA',
        'LOS RIOS', 'MANABI', 'MORONA SANTIAGO', 'NAPO', 'ORELLANA',
        'PASTAZA', 'PICHINCHA', 'SANTA ELENA', 'SANTO DOMINGO', 'SUCUMBIOS',
        'TUNGURAHUA', 'ZAMORA CHINCHIPE'
    ]

    # Bancos Ecuador
    BANCOS = {
        '001': 'BANCO PICHINCHA',
        '002': 'BANCO GUAYAQUIL',
        '003': 'BANCO PACIFICO',
        '004': 'BANCO BOLIVARIANO',
        '005': 'BANCO INTERNACIONAL',
        '006': 'BANCO AUSTRO',
        '007': 'BANCO MACHALA',
        '008': 'PRODUBANCO',
        '009': 'BANCO SOLIDARIO',
        '010': 'BANCO PROCREDIT',
        '011': 'BANCO CAPITAL',
        '012': 'BANCO FINCA',
        '013': 'BANCO COOPNACIONAL',
        '014': 'BANCO LOJA'
    }

    # Configuraciones de interfaz
    UI_CONFIG = {
        'card_padding': 20,
        'section_spacing': 25,
        'button_padding': 15,
        'table_row_height': 35,
        'sidebar_width': 280,
        'border_radius': 8,
        'shadow_offset': 2
    }

    # Mensajes del sistema
    MESSAGES = {
        'welcome': f"Bienvenido al {APP_NAME}",
        'loading': "Cargando datos...",
        'saving': "Guardando información...",
        'success_save': "Información guardada correctamente",
        'error_save': "Error al guardar la información",
        'confirm_delete': "¿Está seguro de eliminar este registro?",
        'no_data': "No se encontraron datos",
        'invalid_data': "Los datos ingresados no son válidos",
        'export_success': "Datos exportados correctamente",
        'import_success': "Datos importados correctamente",
        'backup_success': "Respaldo creado correctamente"
    }

    # Validaciones
    VALIDATIONS = {
        'cedula_length': 10,
        'ruc_length': 13,
        'max_name_length': 50,
        'max_address_length': 200,
        'max_email_length': 100,
        'max_phone_length': 20,
        'min_salary': SBU,
        'max_salary': SBU * 50,
        'max_vacation_days': 30,
        'max_overtime_hours': 100
    }

    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios"""
        directories = [
            cls.REPORTS_DIR,
            cls.BACKUPS_DIR,
            cls.TEMPLATES_DIR,
            cls.BASE_DIR / "logs"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)