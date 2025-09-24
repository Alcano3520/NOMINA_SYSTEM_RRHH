#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para crear empleados de prueba
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date, timedelta
import logging

from database.connection import get_session
from database.models import Empleado

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_employees():
    """Crear empleados de prueba"""
    try:
        session = get_session()

        # Verificar si ya existen empleados
        if session.query(Empleado).count() > 0:
            logger.info(f"Ya existen {session.query(Empleado).count()} empleados en la base de datos")
            return True

        logger.info("🚀 Creando empleados de prueba...")

        base_date = datetime.now().date()
        empleados = [
            Empleado(
                empleado="001",
                cedula="1234567890",
                nombres="Juan Carlos",
                apellidos="Pérez González",
                fecha_nac=date(1985, 3, 15),
                fecha_ing=base_date - timedelta(days=365 * 2),  # 2 años
                cargo="001",
                depto="001",
                sueldo=460.00,
                estado_civil="S",
                sexo="M",
                telefono="0987654321",
                email="juan.perez@email.com",
                direccion="Calle Principal 123",
                activo=True
            ),
            Empleado(
                empleado="002",
                cedula="0987654321",
                nombres="María Elena",
                apellidos="Rodríguez Silva",
                fecha_nac=date(1990, 7, 20),
                fecha_ing=base_date - timedelta(days=365),  # 1 año
                cargo="001",
                depto="001",
                sueldo=460.00,
                estado_civil="C",
                sexo="F",
                telefono="0987654322",
                email="maria.rodriguez@email.com",
                direccion="Av. Secundaria 456",
                activo=True
            ),
            Empleado(
                empleado="003",
                cedula="1122334455",
                nombres="Carlos Eduardo",
                apellidos="González López",
                fecha_nac=date(1982, 11, 10),
                fecha_ing=base_date - timedelta(days=365 * 5),  # 5 años
                cargo="001",
                depto="001",
                sueldo=650.00,
                estado_civil="C",
                sexo="M",
                telefono="0987654323",
                email="carlos.gonzalez@email.com",
                direccion="Urbanización Norte 789",
                activo=True
            )
        ]

        session.add_all(empleados)
        session.commit()

        logger.info(f"✅ {len(empleados)} empleados creados exitosamente!")
        for emp in empleados:
            logger.info(f"   - {emp.empleado}: {emp.nombres} {emp.apellidos}")

        return True

    except Exception as e:
        logger.error(f"❌ Error creando empleados: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    create_employees()