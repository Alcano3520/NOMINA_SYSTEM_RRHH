"""Inicialización simplificada de la base de datos"""

import logging
from datetime import datetime, date
from decimal import Decimal

from database.connection import DatabaseManager, get_session
from database.models import Base

logger = logging.getLogger(__name__)

def initialize_database_simple():
    """Inicializar base de datos simple sin datos iniciales"""
    try:
        db_manager = DatabaseManager()

        # Crear tablas
        logger.info("Creando estructura de base de datos...")
        db_manager.create_tables()

        logger.info("Base de datos inicializada correctamente (modo simple)")

    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise