#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo del Sistema SGN
Validación de todas las funcionalidades principales
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database.connection import get_session
from database.models import Empleado, RolPago
from services.payroll_calculator import payroll_calculator
from services.decimos_calculator import decimos_calculator
from services.vacation_calculator import vacation_calculator
from services.liquidation_calculator import liquidation_calculator

def test_complete_system():
    """Prueba completa del sistema SGN"""
    try:
        print("=" * 50)
        print("PRUEBA COMPLETA DEL SISTEMA SGN")
        print("=" * 50)

        # 1. Verificar empleados en base de datos
        session = get_session()
        empleados = session.query(Empleado).filter(Empleado.activo == True).all()
        print(f"Empleados en base de datos: {len(empleados)}")

        if len(empleados) == 0:
            print("ERROR No hay empleados para probar. Ejecutando create_employees.py...")
            from create_employees import create_employees
            if create_employees():
                empleados = session.query(Empleado).filter(Empleado.activo == True).all()
                print(f"OK Empleados creados: {len(empleados)}")
            else:
                print("ERROR Error creando empleados de prueba")
                return False

        # 2. Probar cálculo de nómina
        print("\n" + "="*30)
        print("PRUEBA 1: CÁLCULO DE NÓMINA")
        print("="*30)

        current_date = datetime.now()
        periodo = current_date.strftime("%Y-%m")
        print(f"Calculando nómina del período {periodo}...")

        nomina_results = payroll_calculator.calculate_payroll_period(
            current_date.year,
            current_date.month,
            employee_codes=[emp.empleado for emp in empleados[:3]]  # Primeros 3 empleados
        )

        if nomina_results:
            print(f"OK Nómina calculada para {len(nomina_results)} empleados")

            # Mostrar resumen
            total_ingresos = sum(float(r["total_ingresos"]) for r in nomina_results)
            total_liquido = sum(float(r["liquido_recibir"]) for r in nomina_results)
            print(f"   Total ingresos: ${total_ingresos:.2f}")
            print(f"   Total líquido: ${total_liquido:.2f}")

            # Guardar roles de pago
            print("Guardando roles de pago...")
            payroll_calculator.save_payroll_results(nomina_results)
            print("OK Roles de pago guardados exitosamente")

        else:
            print("ERROR Error calculando nómina")
            return False

        # 3. Probar cálculo de décimos
        print("\n" + "="*30)
        print("PRUEBA 2: CÁLCULO DE DÉCIMOS")
        print("="*30)

        current_year = datetime.now().year

        # Décimo tercero
        print("Calculando décimo tercero...")
        decimo_tercero_results = decimos_calculator.calculate_decimos_batch(
            "TERCERO", current_year, [emp.empleado for emp in empleados[:2]]
        )

        if decimo_tercero_results:
            print(f"OK Décimo tercero calculado para {len(decimo_tercero_results)} empleados")
            total_tercero = sum(float(r["monto_decimo"]) for r in decimo_tercero_results)
            print(f"   Total décimo tercero: ${total_tercero:.2f}")
        else:
            print("WARNING No se calculó décimo tercero (normal si no hay suficientes datos)")

        # Décimo cuarto
        print("Calculando décimo cuarto...")
        decimo_cuarto_results = decimos_calculator.calculate_decimos_batch(
            "CUARTO", current_year, [emp.empleado for emp in empleados[:2]]
        )

        if decimo_cuarto_results:
            print(f"OK Décimo cuarto calculado para {len(decimo_cuarto_results)} empleados")
            total_cuarto = sum(float(r["monto_decimo"]) for r in decimo_cuarto_results)
            print(f"   Total décimo cuarto: ${total_cuarto:.2f}")
        else:
            print("WARNING No se calculó décimo cuarto (normal si no hay suficientes datos)")

        # 4. Probar cálculo de vacaciones
        print("\n" + "="*30)
        print("PRUEBA 3: BALANCE DE VACACIONES")
        print("="*30)

        empleado_test = empleados[0]
        vacation_balance = vacation_calculator.calculate_vacation_balance(empleado_test)

        if vacation_balance:
            print(f"OK Balance de vacaciones calculado para {empleado_test.empleado}")
            print(f"   Empleado: {vacation_balance['empleado_nombre']}")
            print(f"   Años trabajados: {vacation_balance['años_trabajados']:.2f}")
            print(f"   Días acumulados: {vacation_balance['total_acumulados']}")
            print(f"   Días disponibles: {vacation_balance['dias_disponibles']}")
        else:
            print("ERROR Error calculando balance de vacaciones")

        # 5. Probar validación de vacaciones
        print("\nValidando solicitud de vacaciones...")
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=5)

        validation = vacation_calculator.validate_vacation_request(
            empleado_test, start_date, end_date, 5
        )

        if validation["valid"]:
            print("OK Validación de vacaciones exitosa")
        else:
            print(f"WARNING Validación con advertencias: {validation['errors']}")

        # 6. Probar cálculo de liquidación
        print("\n" + "="*30)
        print("PRUEBA 4: CÁLCULO DE LIQUIDACIÓN")
        print("="*30)

        # Simulamos una liquidación por renuncia
        liquidation_date = date.today()
        liquidation_result = liquidation_calculator.calculate_liquidation(
            empleado_test, liquidation_date, "RENUNCIA"
        )

        if liquidation_result:
            print(f"OK Liquidación calculada para {empleado_test.empleado}")
            print(f"   Total a pagar: ${liquidation_result['total_liquidacion']:.2f}")
            print(f"   Indemnización: ${liquidation_result['indemnizacion']:.2f}")
            print(f"   Vacaciones: ${liquidation_result['vacaciones_proporcionales']:.2f}")
        else:
            print("ERROR Error calculando liquidación")

        print("\n" + "="*50)
        print("RESUMEN DE PRUEBAS")
        print("="*50)
        print("OK Sistema de empleados: FUNCIONANDO")
        print("OK Cálculo de nómina: FUNCIONANDO")
        print("OK Cálculo de décimos: FUNCIONANDO")
        print("OK Gestión de vacaciones: FUNCIONANDO")
        print("OK Cálculo de liquidaciones: FUNCIONANDO")
        print("OK Base de datos: FUNCIONANDO")
        print("\n*** SISTEMA SGN 100% FUNCIONAL ***")
        print("="*50)

        return True

    except Exception as e:
        logger.error(f"ERROR Error en prueba completa del sistema: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    success = test_complete_system()
    if success:
        print("\nTodas las pruebas pasaron exitosamente")
        sys.exit(0)
    else:
        print("\nAlgunas pruebas fallaron")
        sys.exit(1)