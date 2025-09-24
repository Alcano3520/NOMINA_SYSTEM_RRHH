#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear datos de prueba completos para el sistema SAI
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from database.connection import get_session
from database.models import *
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data():
    """Crear datos de prueba completos"""
    try:
        session = get_session()

        logger.info("🚀 Creando datos de prueba...")

        # 1. Crear clientes adicionales
        if session.query(Cliente).count() == 0:
            clientes = [
                Cliente(
                    codigo="CLI001",
                    ruc="0992345678001",
                    razon_social="CENTRO COMERCIAL PRINCIPAL",
                    direccion="Av. 9 de Octubre 123",
                    telefono="04-2345678",
                    email="info@principal.com",
                    estado="ACTIVO"
                ),
                Cliente(
                    codigo="CLI002",
                    ruc="0992345679001",
                    razon_social="PLAZA SHOPPING CENTER",
                    direccion="Av. Francisco de Orellana 456",
                    telefono="04-2345679",
                    email="contacto@plaza.com",
                    estado="ACTIVO"
                )
            ]
            session.add_all(clientes)
            session.commit()
            logger.info("✅ Clientes creados")

        # 2. Crear departamentos adicionales
        existing_deps = {d.codigo for d in session.query(Departamento).all()}

        all_departamentos = [
            ("DEP002", "SEGURIDAD PLAZA", "PLAZA SHOPPING CENTER", 2, "Av. Francisco de Orellana 456", "Norte")
        ]

        departamentos_nuevos = []
        for codigo, nombre_codigo, nombre_real, cliente_id, direccion, sector in all_departamentos:
            if codigo not in existing_deps:
                dept = Departamento(
                    codigo=codigo,
                    nombre_codigo=nombre_codigo,
                    nombre_real=nombre_real,
                    cliente_id=cliente_id,
                    direccion=direccion,
                    sector=sector,
                    tipo_puesto="COMERCIAL",
                    guardias_requeridos=8,
                    turnos_por_dia=2,
                    horas_por_turno=12,
                    sueldo_base=480.00,
                    estado="ACTIVO",
                    activo=True
                )
                departamentos_nuevos.append(dept)

        if departamentos_nuevos:
            session.add_all(departamentos_nuevos)
            session.commit()
            logger.info(f"✅ {len(departamentos_nuevos)} departamentos nuevos creados")

        # 3. Crear cargos
        if session.query(Cargo).count() <= 1:
            cargos = [
                Cargo(
                    codigo="001",
                    nombre="GUARDIA DE SEGURIDAD",
                    sueldo_base=460.00,
                    nivel=1,
                    descripcion="Guardia de seguridad básico"
                ),
                Cargo(
                    codigo="002",
                    nombre="SUPERVISOR DE SEGURIDAD",
                    sueldo_base=650.00,
                    nivel=2,
                    descripcion="Supervisor de equipo de seguridad"
                ),
                Cargo(
                    codigo="003",
                    nombre="JEFE DE SEGURIDAD",
                    sueldo_base=850.00,
                    nivel=3,
                    descripcion="Jefe de operaciones de seguridad"
                )
            ]
            session.add_all(cargos)
            session.commit()
            logger.info("✅ Cargos creados")

        # 4. Crear empleados de prueba
        if session.query(Empleado).count() == 0:
            base_date = datetime.now().date()
            empleados = [
                Empleado(
                    codigo="EMP001",
                    cedula="1234567890",
                    nombres="Juan Carlos",
                    apellidos="Pérez González",
                    fecha_nacimiento=date(1985, 3, 15),
                    fecha_ingreso=base_date - timedelta(days=365 * 2),  # 2 años
                    cargo_codigo="001",
                    depto="DEP001",
                    sueldo_basico=460.00,
                    estado_civil="SOLTERO",
                    genero="MASCULINO",
                    telefono="0987654321",
                    email="juan.perez@email.com",
                    direccion="Calle Principal 123",
                    activo=True
                ),
                Empleado(
                    codigo="EMP002",
                    cedula="0987654321",
                    nombres="María Elena",
                    apellidos="Rodríguez Silva",
                    fecha_nacimiento=date(1990, 7, 20),
                    fecha_ingreso=base_date - timedelta(days=365),  # 1 año
                    cargo_codigo="001",
                    depto="DEP001",
                    sueldo_basico=460.00,
                    estado_civil="CASADO",
                    genero="FEMENINO",
                    telefono="0987654322",
                    email="maria.rodriguez@email.com",
                    direccion="Av. Secundaria 456",
                    activo=True
                ),
                Empleado(
                    codigo="EMP003",
                    cedula="1122334455",
                    nombres="Carlos Eduardo",
                    apellidos="González López",
                    fecha_nacimiento=date(1982, 11, 10),
                    fecha_ingreso=base_date - timedelta(days=365 * 5),  # 5 años
                    cargo_codigo="002",
                    depto="DEP002",
                    sueldo_basico=650.00,
                    estado_civil="CASADO",
                    genero="MASCULINO",
                    telefono="0987654323",
                    email="carlos.gonzalez@email.com",
                    direccion="Urbanización Norte 789",
                    activo=True
                ),
                Empleado(
                    codigo="EMP004",
                    cedula="5566778899",
                    nombres="Ana Patricia",
                    apellidos="Martínez Vega",
                    fecha_nacimiento=date(1988, 1, 25),
                    fecha_ingreso=base_date - timedelta(days=365 * 3),  # 3 años
                    cargo_codigo="001",
                    depto="DEP002",
                    sueldo_basico=460.00,
                    estado_civil="SOLTERO",
                    genero="FEMENINO",
                    telefono="0987654324",
                    email="ana.martinez@email.com",
                    direccion="Sector Sur 321",
                    activo=True
                ),
                Empleado(
                    codigo="EMP005",
                    cedula="9988776655",
                    nombres="Roberto Miguel",
                    apellidos="Fernández Castro",
                    fecha_nacimiento=date(1975, 9, 5),
                    fecha_ingreso=base_date - timedelta(days=365 * 8),  # 8 años
                    cargo_codigo="003",
                    depto="DEP001",
                    sueldo_basico=850.00,
                    estado_civil="CASADO",
                    genero="MASCULINO",
                    telefono="0987654325",
                    email="roberto.fernandez@email.com",
                    direccion="Villa Los Pinos 147",
                    activo=True
                )
            ]
            session.add_all(empleados)
            session.commit()
            logger.info("✅ Empleados de prueba creados")

        # 5. Crear parámetros de control actualizados
        existing_controls = {c.parametro: c for c in session.query(Control).all()}

        control_params = {
            "SBU": ("460.00", "Salario Básico Unificado 2024", "NUMBER"),
            "APORTE_PERSONAL_IESS": ("0.0945", "Aporte Personal IESS 9.45%", "NUMBER"),
            "APORTE_PATRONAL_IESS": ("0.1215", "Aporte Patronal IESS 12.15%", "NUMBER"),
            "FONDOS_RESERVA_RATE": ("0.0833", "Fondos de Reserva 8.33%", "NUMBER"),
            "IMPUESTO_RENTA_BASE": ("11902", "Base exenta Impuesto Renta 2024", "NUMBER"),
            "EMPRESA_NOMBRE": ("INSEVIG CIA. LTDA.", "Nombre de la empresa", "STRING"),
            "EMPRESA_RUC": ("0992123456001", "RUC de la empresa", "STRING"),
            "DECIMO_CUARTO_MONTO": ("460.00", "Monto Décimo Cuarto (SBU)", "NUMBER")
        }

        for param, (valor, desc, tipo) in control_params.items():
            if param not in existing_controls:
                control = Control(parametro=param, valor=valor, descripcion=desc, tipo=tipo)
                session.add(control)
            else:
                existing_controls[param].valor = valor
                existing_controls[param].descripcion = desc
                existing_controls[param].tipo = tipo

        session.commit()
        logger.info("✅ Parámetros de control actualizados")

        # 6. Crear algunos registros históricos para pruebas
        # Roles de pago del mes anterior
        last_month = base_date.replace(day=1) - timedelta(days=1)
        period = f"{last_month.year:04d}-{last_month.month:02d}"

        if session.query(RolPago).filter_by(periodo=period).count() == 0:
            roles_prueba = [
                RolPago(
                    empleado_codigo="EMP001",
                    periodo=period,
                    dias_trabajados=30,
                    sueldo_basico=460.00,
                    horas_extras=0.00,
                    ingresos_adicionales=0.00,
                    total_ingresos=460.00,
                    aporte_iess=43.47,  # 9.45%
                    impuesto_renta=0.00,
                    total_descuentos=43.47,
                    liquido_recibir=416.53,
                    decimo_tercero=38.33,  # 1/12
                    decimo_cuarto=38.33,   # SBU/12
                    vacaciones=19.17,      # 1/24
                    fondos_reserva=38.31,  # 8.33%
                    aporte_patronal=55.89, # 12.15%
                    estado="PROCESADO",
                    fecha_creacion=datetime.now()
                ),
                RolPago(
                    empleado_codigo="EMP003",
                    periodo=period,
                    dias_trabajados=30,
                    sueldo_basico=650.00,
                    horas_extras=50.00,
                    ingresos_adicionales=0.00,
                    total_ingresos=700.00,
                    aporte_iess=66.15,
                    impuesto_renta=0.00,
                    total_descuentos=66.15,
                    liquido_recibir=633.85,
                    decimo_tercero=58.33,
                    decimo_cuarto=38.33,
                    vacaciones=27.08,
                    fondos_reserva=58.31,
                    aporte_patronal=85.05,
                    estado="PROCESADO",
                    fecha_creacion=datetime.now()
                )
            ]
            session.add_all(roles_prueba)
            session.commit()
            logger.info("✅ Roles de pago de prueba creados")

        logger.info("🎉 Datos de prueba creados completamente!")
        logger.info(f"📊 Resumen:")
        logger.info(f"   - Clientes: {session.query(Cliente).count()}")
        logger.info(f"   - Departamentos: {session.query(Departamento).count()}")
        logger.info(f"   - Cargos: {session.query(Cargo).count()}")
        logger.info(f"   - Empleados: {session.query(Empleado).count()}")
        logger.info(f"   - Parámetros: {session.query(Control).count()}")
        logger.info(f"   - Roles de pago: {session.query(RolPago).count()}")

        return True

    except Exception as e:
        logger.error(f"❌ Error creando datos de prueba: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    create_test_data()