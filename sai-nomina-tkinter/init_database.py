#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos SAI
"""

import os
import sys
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent))

from database.connection import DatabaseManager
from database.models import (
    Base, Empleado, Departamento, Cliente, Cargo, Control,
    Usuario, Rol, LogAuditoria, SesionUsuario
)
from config import Config
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Crear base de datos y tablas"""
    try:
        logger.info("🚀 Iniciando creación de base de datos...")

        # Crear directorios necesarios
        Config.create_directories()

        # Eliminar DB existente si existe
        if Config.DATABASE_PATH.exists():
            Config.DATABASE_PATH.unlink()
            logger.info("🗑️ Base de datos anterior eliminada")

        # Crear base de datos
        db_manager = DatabaseManager()
        db_manager.create_tables()
        logger.info("📊 Tablas creadas exitosamente")

        # Verificar tablas creadas
        import sqlite3
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        logger.info("✅ Tablas creadas:")
        for table in tables:
            logger.info(f"   - {table[0]}")

        # Verificar estructura de departamentos
        cursor.execute("PRAGMA table_info(departamentos)")
        columns = cursor.fetchall()
        logger.info("📋 Estructura tabla departamentos:")
        for col in columns:
            logger.info(f"   - {col[1]} ({col[2]})")

        conn.close()

        # Insertar datos iniciales
        insert_initial_data()

        logger.info("🎉 Base de datos creada correctamente!")
        return True

    except Exception as e:
        logger.error(f"❌ Error creando base de datos: {e}")
        return False

def insert_initial_data():
    """Insertar datos iniciales"""
    try:
        from database.connection import get_session
        session = get_session()

        # Cliente ejemplo
        if not session.query(Cliente).first():
            cliente = Cliente(
                codigo="CLI001",
                ruc="0992345678001",
                razon_social="EMPRESA EJEMPLO S.A.",
                direccion="Av. Principal 123",
                telefono="04-2345678",
                email="info@ejemplo.com",
                estado="ACTIVO"
            )
            session.add(cliente)
            session.commit()
            logger.info("👤 Cliente inicial creado")

        # Departamento ejemplo
        if not session.query(Departamento).first():
            departamento = Departamento(
                codigo="DEP001",
                nombre_codigo="SEGURIDAD MALL",
                nombre_real="CENTRO COMERCIAL PRINCIPAL",
                cliente_id=1,
                direccion="Av. 9 de Octubre 123",
                sector="Centro",
                tipo_puesto="COMERCIAL",
                estado="ACTIVO"
            )
            session.add(departamento)
            session.commit()
            logger.info("🏢 Departamento inicial creado")

        # Cargo ejemplo
        if not session.query(Cargo).first():
            cargo = Cargo(
                codigo="001",
                nombre="GUARDIA DE SEGURIDAD",
                sueldo_base=460.00,
                nivel=1,
                descripcion="Guardia de seguridad básico"
            )
            session.add(cargo)
            session.commit()
            logger.info("💼 Cargo inicial creado")

        # Parámetros de control
        if not session.query(Control).first():
            parametros = [
                Control(parametro="SBU", valor="460.00", descripcion="Salario Básico Unificado", tipo="NUMBER"),
                Control(parametro="EMPRESA_NOMBRE", valor="INSEVIG CIA. LTDA.", descripcion="Nombre de la empresa", tipo="STRING"),
                Control(parametro="EMPRESA_RUC", valor="0992123456001", descripcion="RUC de la empresa", tipo="STRING")
            ]
            session.add_all(parametros)
            session.commit()
            logger.info("⚙️ Parámetros de control creados")

        session.close()

    except Exception as e:
        logger.error(f"❌ Error insertando datos iniciales: {e}")

if __name__ == "__main__":
    create_database()