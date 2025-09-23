"""Inicialización de la base de datos con datos de ejemplo"""

import logging
from datetime import datetime, date
from decimal import Decimal

from database.connection import DatabaseManager, get_session
from database.models import (
    Base, Empleado, Departamento, Cargo, Control
)
from config import Config

logger = logging.getLogger(__name__)

def initialize_database():
    """Inicializar base de datos con estructura y datos iniciales"""
    try:
        db_manager = DatabaseManager()

        # Crear tablas
        logger.info("Creando estructura de base de datos...")
        db_manager.create_tables()

        # Insertar datos iniciales solo si es necesario
        logger.info("Verificando datos iniciales...")
        try:
            insert_initial_data()
        except Exception as e:
            logger.warning(f"Los datos iniciales ya existen o hubo un error: {e}")
            # No es crítico, continuar

        logger.info("Base de datos inicializada correctamente")

    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise

def insert_initial_data():
    """Insertar datos iniciales del sistema"""
    session = get_session()

    try:
        # Verificar si ya existen datos
        if (session.query(Departamento).count() > 0 and
            session.query(Cargo).count() > 0):
            logger.info("Datos iniciales ya existen, saltando inserción")
            return

        # Limpiar datos existentes si hay inconsistencias
        if session.query(Departamento).count() > 0 or session.query(Cargo).count() > 0:
            logger.info("Limpiando datos inconsistentes...")
            session.query(Departamento).delete()
            session.query(Cargo).delete()
            session.commit()

        # Insertar departamentos
        departamentos = [
            Departamento(codigo='001', nombre='SEGURIDAD FISICA', responsable=None),
            Departamento(codigo='002', nombre='ADMINISTRACION', responsable=None),
            Departamento(codigo='003', nombre='RECURSOS HUMANOS', responsable=None),
            Departamento(codigo='004', nombre='CONTABILIDAD', responsable=None),
            Departamento(codigo='005', nombre='SISTEMAS', responsable=None),
            Departamento(codigo='006', nombre='SUPERVISION', responsable=None),
            Departamento(codigo='007', nombre='OPERACIONES', responsable=None),
            Departamento(codigo='008', nombre='LOGISTICA', responsable=None),
            Departamento(codigo='009', nombre='CAPACITACION', responsable=None),
            Departamento(codigo='010', nombre='CONTROL DE CALIDAD', responsable=None)
        ]

        for depto in departamentos:
            session.add(depto)

        # Insertar cargos
        cargos = [
            # Cargos operativos
            Cargo(codigo='GUA', nombre='GUARDIA DE SEGURIDAD', sueldo_base=460.00, nivel=1),
            Cargo(codigo='GU2', nombre='GUARDIA ARMADO', sueldo_base=480.00, nivel=1),
            Cargo(codigo='CON', nombre='CONSERJE', sueldo_base=460.00, nivel=1),
            Cargo(codigo='VIG', nombre='VIGILANTE', sueldo_base=460.00, nivel=1),
            Cargo(codigo='CHO', nombre='CHOFER', sueldo_base=500.00, nivel=1),

            # Cargos de supervisión
            Cargo(codigo='SUP', nombre='SUPERVISOR', sueldo_base=650.00, nivel=2),
            Cargo(codigo='JEF', nombre='JEFE DE TURNO', sueldo_base=700.00, nivel=2),
            Cargo(codigo='COO', nombre='COORDINADOR', sueldo_base=750.00, nivel=2),

            # Cargos administrativos
            Cargo(codigo='ASI', nombre='ASISTENTE ADMINISTRATIVO', sueldo_base=550.00, nivel=2),
            Cargo(codigo='SEC', nombre='SECRETARIA', sueldo_base=500.00, nivel=2),
            Cargo(codigo='REC', nombre='RECEPCIONISTA', sueldo_base=480.00, nivel=2),
            Cargo(codigo='CON', nombre='CONTADOR', sueldo_base=800.00, nivel=3),
            Cargo(codigo='AUD', nombre='AUDITOR', sueldo_base=900.00, nivel=3),

            # Cargos ejecutivos
            Cargo(codigo='GER', nombre='GERENTE', sueldo_base=1500.00, nivel=3),
            Cargo(codigo='SUG', nombre='SUBGERENTE', sueldo_base=1200.00, nivel=3),
            Cargo(codigo='DIR', nombre='DIRECTOR', sueldo_base=1800.00, nivel=3),
            Cargo(codigo='JRH', nombre='JEFE DE RECURSOS HUMANOS', sueldo_base=1000.00, nivel=3)
        ]

        for cargo in cargos:
            session.add(cargo)

        # Parámetros del sistema
        parametros = [
            # Parámetros Ecuador 2024
            Control(
                parametro='SBU_2024',
                valor='460.00',
                descripcion='Salario Básico Unificado 2024',
                tipo='NUMBER',
                categoria='ECUADOR'
            ),
            Control(
                parametro='APORTE_PERSONAL_IESS',
                valor='0.0945',
                descripcion='Aporte personal IESS (9.45%)',
                tipo='NUMBER',
                categoria='ECUADOR'
            ),
            Control(
                parametro='APORTE_PATRONAL_IESS',
                valor='0.1115',
                descripcion='Aporte patronal IESS (11.15%)',
                tipo='NUMBER',
                categoria='ECUADOR'
            ),
            Control(
                parametro='FONDOS_RESERVA',
                valor='0.0833',
                descripcion='Fondos de reserva (8.33%)',
                tipo='NUMBER',
                categoria='ECUADOR'
            ),
            Control(
                parametro='HORAS_EXTRAS_25',
                valor='1.25',
                descripcion='Recargo horas extras 25%',
                tipo='NUMBER',
                categoria='ECUADOR'
            ),
            Control(
                parametro='HORAS_EXTRAS_50',
                valor='1.50',
                descripcion='Recargo horas extras 50%',
                tipo='NUMBER',
                categoria='ECUADOR'
            ),
            Control(
                parametro='HORAS_EXTRAS_100',
                valor='2.00',
                descripcion='Recargo horas extras 100%',
                tipo='NUMBER',
                categoria='ECUADOR'
            ),
            Control(
                parametro='DIAS_VACACIONES',
                valor='15',
                descripcion='Días de vacaciones anuales',
                tipo='NUMBER',
                categoria='ECUADOR'
            ),

            # Parámetros del sistema
            Control(
                parametro='EMPRESA_NOMBRE',
                valor='INSEVIG CIA. LTDA.',
                descripcion='Nombre de la empresa',
                tipo='STRING',
                categoria='EMPRESA'
            ),
            Control(
                parametro='EMPRESA_RUC',
                valor='1792146739001',
                descripcion='RUC de la empresa',
                tipo='STRING',
                categoria='EMPRESA'
            ),
            Control(
                parametro='EMPRESA_DIRECCION',
                valor='Av. Principal 123, Quito, Ecuador',
                descripcion='Dirección de la empresa',
                tipo='STRING',
                categoria='EMPRESA'
            ),
            Control(
                parametro='EMPRESA_TELEFONO',
                valor='02-2345678',
                descripcion='Teléfono de la empresa',
                tipo='STRING',
                categoria='EMPRESA'
            ),
            Control(
                parametro='PERIODO_ACTUAL',
                valor=datetime.now().strftime('%Y-%m'),
                descripcion='Período actual de nómina',
                tipo='STRING',
                categoria='NOMINA'
            ),
            Control(
                parametro='BACKUP_AUTO',
                valor='TRUE',
                descripcion='Respaldo automático activado',
                tipo='BOOLEAN',
                categoria='SISTEMA'
            )
        ]

        for param in parametros:
            session.add(param)

        # Empleados de ejemplo (solo algunos para demostración)
        empleados_ejemplo = [
            Empleado(
                empleado='001001',
                nombres='JUAN CARLOS',
                apellidos='PEREZ GARCIA',
                cedula='1234567890',
                fecha_nac=date(1985, 3, 15),
                sexo='M',
                estado_civil='C',
                direccion='Av. Amazonas 123, Quito',
                telefono='022345678',
                celular='0987654321',
                email='juan.perez@empresa.com',
                cargo='GUA',
                depto='001',
                seccion='GUA',
                sueldo=Decimal('460.00'),
                fecha_ing=date(2023, 1, 1),
                tipo_tra=1,
                tipo_pgo=1,
                estado='ACT',
                banco='001',
                cuenta_banco='1234567890',
                tipo_cuenta='A',
                created_by='SYSTEM'
            ),
            Empleado(
                empleado='001002',
                nombres='MARIA FERNANDA',
                apellidos='RODRIGUEZ LOPEZ',
                cedula='0987654321',
                fecha_nac=date(1990, 7, 22),
                sexo='F',
                estado_civil='S',
                direccion='Calle Los Rosales 456, Quito',
                telefono='022567890',
                celular='0976543210',
                email='maria.rodriguez@empresa.com',
                cargo='SUP',
                depto='006',
                seccion='SUP',
                sueldo=Decimal('650.00'),
                fecha_ing=date(2022, 6, 15),
                tipo_tra=2,
                tipo_pgo=2,
                estado='ACT',
                banco='002',
                cuenta_banco='0987654321',
                tipo_cuenta='A',
                created_by='SYSTEM'
            ),
            Empleado(
                empleado='001003',
                nombres='CARLOS ALBERTO',
                apellidos='SANCHEZ MORALES',
                cedula='1122334455',
                fecha_nac=date(1988, 11, 10),
                sexo='M',
                estado_civil='C',
                direccion='Sector Norte, Mz. 15, Casa 8',
                telefono='023456789',
                celular='0965432109',
                email='carlos.sanchez@empresa.com',
                cargo='JRH',
                depto='003',
                seccion='ADM',
                sueldo=Decimal('1000.00'),
                fecha_ing=date(2021, 3, 1),
                tipo_tra=3,
                tipo_pgo=3,
                estado='ACT',
                banco='003',
                cuenta_banco='1122334455',
                tipo_cuenta='C',
                created_by='SYSTEM'
            )
        ]

        for emp in empleados_ejemplo:
            session.add(emp)

        # Commit de todos los datos
        session.commit()
        logger.info("Datos iniciales insertados correctamente")

    except Exception as e:
        session.rollback()
        logger.error(f"Error insertando datos iniciales: {e}")
        raise
    finally:
        session.close()

def reset_database():
    """Resetear base de datos eliminando todos los datos"""
    try:
        db_manager = DatabaseManager()

        logger.info("Eliminando estructura de base de datos...")
        db_manager.drop_tables()

        logger.info("Recreando estructura...")
        db_manager.create_tables()

        logger.info("Insertando datos iniciales...")
        insert_initial_data()

        logger.info("Base de datos reseteada correctamente")

    except Exception as e:
        logger.error(f"Error reseteando base de datos: {e}")
        raise

if __name__ == "__main__":
    # Para pruebas directas
    initialize_database()