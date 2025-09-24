#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración global del sistema - CustomTkinter
Sistema de Gestión de Nómina (SGN)
"""

import os
from pathlib import Path
import customtkinter as ctk

class ConfigCTK:
    """Configuración optimizada para CustomTkinter"""

    # Rutas (mantener compatibilidad)
    BASE_DIR = Path(__file__).parent
    DATABASE_PATH = BASE_DIR / "sai_nomina.db"
    REPORTS_DIR = BASE_DIR / "reports"
    BACKUPS_DIR = BASE_DIR / "backups"
    TEMPLATES_DIR = BASE_DIR / "assets" / "templates"

    # Base de datos
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

    # Aplicación
    APP_NAME = "Sistema de Gestión de Nómina (SGN)"
    APP_VERSION = "2.0.0"
    COMPANY_NAME = "INSEVIG CIA. LTDA."

    # Configuración de ventanas para diseño compacto y responsivo
    WINDOW_CONFIG = {
        'main': {
            'size': (600, 400),
            'min_size': (500, 350),
            'geometry': "600x400"
        },
        'login': {
            'size': (600, 400),
            'min_size': (500, 350),
            'geometry': "600x400"
        },
        'module': {
            'size': (800, 600),
            'min_size': (600, 400),
            'geometry': "800x600"
        }
    }

    # Configuración de tema CustomTkinter
    CTK_THEME = {
        'appearance_mode': "light",  # "light", "dark", "system"
        'color_theme': "blue",       # "blue", "green", "dark-blue"
        'scaling': 1.0               # Factor de escala para UI
    }

    # Colores personalizados para CustomTkinter
    CTK_COLORS = {
        # Colores primarios del sistema
        'primary': "#1f538d",
        'primary_dark': "#14375e",
        'secondary': "#2b77ad",
        'secondary_dark': "#1e547a",

        # Colores de estado
        'success': "#22c55e",
        'warning': "#f59e0b",
        'danger': "#ef4444",
        'info': "#3b82f6",

        # Colores de fondo y superficie
        'background': "#f8fafc",
        'surface': "#ffffff",
        'surface_dark': "#f1f5f9",

        # Colores de texto
        'text_primary': "#1e293b",
        'text_secondary': "#64748b",
        'text_light': "#94a3b8",
        'text_white': "#ffffff",

        # Colores de borde y separadores
        'border': "#e2e8f0",
        'border_light': "#f1f5f9",
        'shadow': "rgba(0, 0, 0, 0.1)"
    }

    # Fuentes optimizadas para CustomTkinter
    CTK_FONTS = {
        'default': ctk.CTkFont(size=12),
        'small': ctk.CTkFont(size=10),
        'large': ctk.CTkFont(size=14),
        'title': ctk.CTkFont(size=18, weight="bold"),
        'heading': ctk.CTkFont(size=16, weight="bold"),
        'subheading': ctk.CTkFont(size=14, weight="bold"),
        'button': ctk.CTkFont(size=12, weight="bold"),
        'label': ctk.CTkFont(size=11),
        'number': ctk.CTkFont(family="Consolas", size=11)
    }

    # Configuración de espaciado y dimensiones compactas
    UI_SPACING = {
        'xs': 4,   # Espaciado extra pequeño
        'sm': 8,   # Espaciado pequeño
        'md': 12,  # Espaciado medio
        'lg': 16,  # Espaciado grande
        'xl': 20,  # Espaciado extra grande
        'xxl': 24  # Espaciado máximo
    }

    # Configuración de widgets CustomTkinter
    CTK_WIDGET_CONFIG = {
        'button': {
            'height': 32,
            'corner_radius': 6,
            'font': ctk.CTkFont(size=12)
        },
        'button_small': {
            'height': 28,
            'corner_radius': 4,
            'font': ctk.CTkFont(size=10)
        },
        'entry': {
            'height': 32,
            'corner_radius': 6,
            'font': ctk.CTkFont(size=12)
        },
        'frame': {
            'corner_radius': 8
        },
        'label': {
            'font': ctk.CTkFont(size=12)
        },
        'optionmenu': {
            'height': 32,
            'corner_radius': 6,
            'font': ctk.CTkFont(size=12)
        }
    }

    # Constantes Ecuador 2024 (mantener compatibilidad)
    SBU = 460.00
    APORTE_PERSONAL_IESS = 0.0945
    APORTE_PATRONAL_IESS = 0.1115
    FONDOS_RESERVA = 0.0833
    HORAS_EXTRAS_25 = 1.25
    HORAS_EXTRAS_50 = 1.5
    HORAS_EXTRAS_100 = 2.0
    JORNADA_SEMANAL = 40
    DIAS_VACACIONES_ANUAL = 15

    # Códigos de conceptos (mantener compatibilidad)
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

    # Estados de empleados (mantener compatibilidad)
    ESTADOS_EMPLEADO = {
        'ACT': 'Activo',
        'VAC': 'Vacaciones',
        'LIC': 'Licencia',
        'RET': 'Retirado',
        'JUB': 'Jubilado',
        'SUS': 'Suspendido'
    }

    # Tipos de trabajador (mantener compatibilidad)
    TIPOS_TRABAJADOR = {
        1: 'Operativo',
        2: 'Administrativo',
        3: 'Ejecutivo'
    }

    # Tipos de pago (mantener compatibilidad)
    TIPOS_PAGO = {
        1: 'Semanal',
        2: 'Quincenal',
        3: 'Mensual'
    }

    # Provincias Ecuador (mantener compatibilidad)
    PROVINCIAS = [
        'AZUAY', 'BOLIVAR', 'CAÑAR', 'CARCHI', 'CHIMBORAZO', 'COTOPAXI',
        'EL ORO', 'ESMERALDAS', 'GALAPAGOS', 'GUAYAS', 'IMBABURA', 'LOJA',
        'LOS RIOS', 'MANABI', 'MORONA SANTIAGO', 'NAPO', 'ORELLANA',
        'PASTAZA', 'PICHINCHA', 'SANTA ELENA', 'SANTO DOMINGO', 'SUCUMBIOS',
        'TUNGURAHUA', 'ZAMORA CHINCHIPE'
    ]

    # Bancos Ecuador (mantener compatibilidad)
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

    # Mensajes del sistema (mantener compatibilidad)
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

    # Validaciones (mantener compatibilidad)
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
    def setup_ctk_theme(cls):
        """Configurar tema de CustomTkinter"""
        ctk.set_appearance_mode(cls.CTK_THEME['appearance_mode'])
        ctk.set_default_color_theme(cls.CTK_THEME['color_theme'])

        # Configurar escalado si es necesario
        if cls.CTK_THEME['scaling'] != 1.0:
            ctk.set_widget_scaling(cls.CTK_THEME['scaling'])

    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios (mantener compatibilidad)"""
        directories = [
            cls.REPORTS_DIR,
            cls.BACKUPS_DIR,
            cls.TEMPLATES_DIR,
            cls.BASE_DIR / "logs"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_window_config(cls, window_type='main'):
        """Obtener configuración de ventana específica"""
        return cls.WINDOW_CONFIG.get(window_type, cls.WINDOW_CONFIG['main'])

    @classmethod
    def create_styled_button(cls, parent, text, command=None, style='default'):
        """Crear botón con estilo predefinido"""
        config = cls.CTK_WIDGET_CONFIG['button'].copy()

        if style == 'small':
            config.update(cls.CTK_WIDGET_CONFIG['button_small'])
        elif style == 'primary':
            config['fg_color'] = cls.CTK_COLORS['primary']
        elif style == 'success':
            config['fg_color'] = cls.CTK_COLORS['success']
        elif style == 'warning':
            config['fg_color'] = cls.CTK_COLORS['warning']
        elif style == 'danger':
            config['fg_color'] = cls.CTK_COLORS['danger']

        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            **config
        )

    @classmethod
    def create_styled_entry(cls, parent, placeholder=""):
        """Crear entrada de texto con estilo predefinido"""
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            **cls.CTK_WIDGET_CONFIG['entry']
        )

    @classmethod
    def create_styled_frame(cls, parent, **kwargs):
        """Crear frame con estilo predefinido"""
        config = cls.CTK_WIDGET_CONFIG['frame'].copy()
        config.update(kwargs)
        return ctk.CTkFrame(parent, **config)

# Mantener compatibilidad con código existente
Config = ConfigCTK