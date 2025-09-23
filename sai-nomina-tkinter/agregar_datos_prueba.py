#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar datos de prueba al Sistema SAI
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.connection import get_session
from database.models import Empleado, Departamento, Cargo
from datetime import date
from decimal import Decimal

def agregar_datos_prueba():
    """Agregar datos de prueba a la base de datos"""
    session = get_session()

    try:
        print("Agregando datos de prueba...")

        # Verificar si ya existen datos
        if session.query(Empleado).count() > 0:
            print("Ya existen datos en la base de datos.")
            respuesta = input("¿Desea agregar más datos de prueba? (s/n): ")
            if respuesta.lower() != 's':
                return

        # Crear departamentos
        departamentos = [
            Departamento(codigo='001', nombre='ADMINISTRACION', activo=True),
            Departamento(codigo='002', nombre='OPERACIONES', activo=True),
            Departamento(codigo='003', nombre='SUPERVISION', activo=True),
            Departamento(codigo='004', nombre='RECURSOS HUMANOS', activo=True)
        ]

        for dept in departamentos:
            existing = session.query(Departamento).filter_by(codigo=dept.codigo).first()
            if not existing:
                session.add(dept)

        # Crear cargos
        cargos = [
            Cargo(codigo='001', nombre='GUARDIA DE SEGURIDAD', activo=True),
            Cargo(codigo='002', nombre='SUPERVISOR DE TURNO', activo=True),
            Cargo(codigo='003', nombre='JEFE DE OPERACIONES', activo=True),
            Cargo(codigo='004', nombre='COORDINADOR RRHH', activo=True),
            Cargo(codigo='005', nombre='GERENTE GENERAL', activo=True)
        ]

        for cargo in cargos:
            existing = session.query(Cargo).filter_by(codigo=cargo.codigo).first()
            if not existing:
                session.add(cargo)

        session.commit()

        # Crear empleados de prueba
        empleados = [
            {
                'empleado': '001001',
                'nombres': 'JUAN CARLOS',
                'apellidos': 'PEREZ GONZALEZ',
                'cedula': '1234567890',
                'fecha_nac': date(1985, 3, 15),
                'sexo': 'M',
                'estado_civil': 'C',
                'direccion': 'AV. AMAZONAS Y COLON, QUITO',
                'telefono': '022345678',
                'celular': '0987654321',
                'email': 'juan.perez@insevig.com',
                'cargo': '001',
                'depto': '002',
                'sueldo': Decimal('500.00'),
                'fecha_ing': date(2023, 1, 15),
                'tipo_tra': 1,
                'tipo_pgo': 3,
                'estado': 'ACT',
                'banco': '001',
                'cuenta_banco': '1234567890',
                'activo': True
            },
            {
                'empleado': '001002',
                'nombres': 'MARIA FERNANDA',
                'apellidos': 'GONZALEZ LOPEZ',
                'cedula': '0987654321',
                'fecha_nac': date(1990, 7, 22),
                'sexo': 'F',
                'estado_civil': 'S',
                'direccion': 'CALLE ROCAFUERTE 123, QUITO',
                'telefono': '022876543',
                'celular': '0998765432',
                'email': 'maria.gonzalez@insevig.com',
                'cargo': '002',
                'depto': '003',
                'sueldo': Decimal('800.00'),
                'fecha_ing': date(2022, 6, 10),
                'tipo_tra': 2,
                'tipo_pgo': 3,
                'estado': 'ACT',
                'banco': '002',
                'cuenta_banco': '0987654321',
                'activo': True
            },
            {
                'empleado': '001003',
                'nombres': 'CARLOS ANDRES',
                'apellidos': 'RODRIGUEZ SILVA',
                'cedula': '1122334455',
                'fecha_nac': date(1988, 11, 8),
                'sexo': 'M',
                'estado_civil': 'C',
                'direccion': 'SECTOR LA CAROLINA, QUITO',
                'telefono': '022334455',
                'celular': '0987123456',
                'email': 'carlos.rodriguez@insevig.com',
                'cargo': '003',
                'depto': '002',
                'sueldo': Decimal('1200.00'),
                'fecha_ing': date(2021, 3, 1),
                'tipo_tra': 2,
                'tipo_pgo': 3,
                'estado': 'ACT',
                'banco': '003',
                'cuenta_banco': '1122334455',
                'activo': True
            },
            {
                'empleado': '001004',
                'nombres': 'ANA LUCIA',
                'apellidos': 'MARTINEZ TORRES',
                'cedula': '2233445566',
                'fecha_nac': date(1992, 5, 17),
                'sexo': 'F',
                'estado_civil': 'S',
                'direccion': 'AV. 6 DE DICIEMBRE, QUITO',
                'telefono': '022445566',
                'celular': '0987234567',
                'email': 'ana.martinez@insevig.com',
                'cargo': '004',
                'depto': '004',
                'sueldo': Decimal('900.00'),
                'fecha_ing': date(2022, 9, 15),
                'tipo_tra': 2,
                'tipo_pgo': 3,
                'estado': 'ACT',
                'banco': '001',
                'cuenta_banco': '2233445566',
                'activo': True
            },
            {
                'empleado': '001005',
                'nombres': 'LUIS EDUARDO',
                'apellidos': 'VARGAS MORENO',
                'cedula': '3344556677',
                'fecha_nac': date(1980, 12, 3),
                'sexo': 'M',
                'estado_civil': 'C',
                'direccion': 'SECTOR CUMBAYA, QUITO',
                'telefono': '022556677',
                'celular': '0987345678',
                'email': 'luis.vargas@insevig.com',
                'cargo': '005',
                'depto': '001',
                'sueldo': Decimal('2000.00'),
                'fecha_ing': date(2020, 1, 10),
                'tipo_tra': 3,
                'tipo_pgo': 3,
                'estado': 'ACT',
                'banco': '004',
                'cuenta_banco': '3344556677',
                'activo': True
            },
            {
                'empleado': '001006',
                'nombres': 'PATRICIA ISABEL',
                'apellidos': 'JIMENEZ CASTRO',
                'cedula': '4455667788',
                'fecha_nac': date(1987, 8, 25),
                'sexo': 'F',
                'estado_civil': 'C',
                'direccion': 'VALLE DE LOS CHILLOS, QUITO',
                'telefono': '022667788',
                'celular': '0987456789',
                'email': 'patricia.jimenez@insevig.com',
                'cargo': '001',
                'depto': '002',
                'sueldo': Decimal('480.00'),
                'fecha_ing': date(2023, 5, 20),
                'tipo_tra': 1,
                'tipo_pgo': 3,
                'estado': 'ACT',
                'banco': '002',
                'cuenta_banco': '4455667788',
                'activo': True
            },
            {
                'empleado': '001007',
                'nombres': 'DIEGO ALEJANDRO',
                'apellidos': 'HERRERA RIOS',
                'cedula': '5566778899',
                'fecha_nac': date(1991, 2, 14),
                'sexo': 'M',
                'estado_civil': 'S',
                'direccion': 'SECTOR IÑAQUITO, QUITO',
                'telefono': '022778899',
                'celular': '0987567890',
                'email': 'diego.herrera@insevig.com',
                'cargo': '001',
                'depto': '002',
                'sueldo': Decimal('520.00'),
                'fecha_ing': date(2023, 2, 28),
                'tipo_tra': 1,
                'tipo_pgo': 3,
                'estado': 'ACT',
                'banco': '003',
                'cuenta_banco': '5566778899',
                'activo': True
            },
            {
                'empleado': '001008',
                'nombres': 'VERONICA ELIZABETH',
                'apellidos': 'MENDEZ RUIZ',
                'cedula': '6677889900',
                'fecha_nac': date(1989, 10, 12),
                'sexo': 'F',
                'estado_civil': 'C',
                'direccion': 'SECTOR TUMBACO, QUITO',
                'telefono': '022889900',
                'celular': '0987678901',
                'email': 'veronica.mendez@insevig.com',
                'cargo': '002',
                'depto': '003',
                'sueldo': Decimal('750.00'),
                'fecha_ing': date(2022, 11, 5),
                'tipo_tra': 2,
                'tipo_pgo': 3,
                'estado': 'ACT',
                'banco': '001',
                'cuenta_banco': '6677889900',
                'activo': True
            }
        ]

        for emp_data in empleados:
            existing = session.query(Empleado).filter_by(empleado=emp_data['empleado']).first()
            if not existing:
                empleado = Empleado(**emp_data)
                session.add(empleado)

        session.commit()
        print(f"[OK] Datos de prueba agregados correctamente")
        print(f"[OK] Total empleados en base de datos: {session.query(Empleado).count()}")

    except Exception as e:
        print(f"Error agregando datos: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    agregar_datos_prueba()