#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DecimosCalculator - Sistema SAI
Cálculo de décimos tercero y cuarto según normativa ecuatoriana 2024
"""

import sys
from pathlib import Path
import logging
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
from dateutil.relativedelta import relativedelta

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_session
from database.models import Empleado, Control, DecimoTercer, DecimoCuarto, RolPago, IngresoDescuento

logger = logging.getLogger(__name__)

class DecimosCalculator:
    """Calculadora de décimos ecuatorianos"""

    def __init__(self):
        self.session = get_session()
        self.parameters = self.load_parameters()

    def load_parameters(self):
        """Cargar parámetros del sistema"""
        try:
            params = {}
            controls = self.session.query(Control).all()

            for control in controls:
                if control.tipo == "NUMBER":
                    params[control.parametro] = Decimal(str(control.valor))
                else:
                    params[control.parametro] = control.valor

            # Parámetros por defecto Ecuador 2024
            default_params = {
                "SBU": Decimal("460.00"),  # Salario Básico Unificado 2024
                "DECIMO_TERCER_RATE": Decimal("0.0833"),    # 1/12
                "DECIMO_CUARTO_MONTO": Decimal("460.00"),   # SBU 2024
            }

            for key, value in default_params.items():
                if key not in params:
                    params[key] = value

            return params

        except Exception as e:
            logger.error(f"Error cargando parámetros: {e}")
            return {
                "SBU": Decimal("460.00"),
                "DECIMO_TERCER_RATE": Decimal("0.0833"),
                "DECIMO_CUARTO_MONTO": Decimal("460.00"),
            }

    def calculate_decimo_tercero(self, empleado, calculation_year):
        """
        Calcular décimo tercero sueldo (Bono Navideño)

        Args:
            empleado: Objeto Empleado
            calculation_year: Año de cálculo (período diciembre 1 - noviembre 30)

        Returns:
            dict: Resultado del cálculo de décimo tercero
        """
        try:
            # Período de cálculo: Diciembre año anterior a Noviembre año actual
            period_start = date(calculation_year - 1, 12, 1)
            period_end = date(calculation_year, 11, 30)

            # Verificar que el empleado esté activo
            if not empleado.activo:
                raise ValueError(f"Empleado {empleado.codigo} no está activo")

            # Calcular fecha de inicio efectiva (no antes de la fecha de ingreso)
            effective_start = period_start
            if empleado.fecha_ingreso and empleado.fecha_ingreso > period_start:
                effective_start = empleado.fecha_ingreso

            # Calcular fecha de fin efectiva
            effective_end = period_end
            if empleado.fecha_salida and empleado.fecha_salida < period_end:
                effective_end = empleado.fecha_salida

            # Días trabajados en el período
            days_worked = (effective_end - effective_start).days + 1
            total_days_period = (period_end - period_start).days + 1

            # Obtener ingresos del período desde roles de pago
            total_ingresos = self.get_employee_income_period(empleado, effective_start, effective_end)

            # Calcular décimo tercero: (Total ingresos del período / 12)
            # O proporcional según días trabajados
            if days_worked >= total_days_period:
                # Año completo
                decimo_tercero = total_ingresos / 12
            else:
                # Proporcional
                decimo_tercero = (total_ingresos * days_worked) / (total_days_period * 12)

            # Redondear
            decimo_tercero = self.round_currency(decimo_tercero)

            return {
                "empleado_codigo": empleado.codigo,
                "empleado_nombre": f"{empleado.nombres} {empleado.apellidos}",
                "tipo": "DECIMO_TERCERO",
                "año_calculo": calculation_year,
                "periodo_inicio": effective_start,
                "periodo_fin": effective_end,
                "dias_trabajados": days_worked,
                "total_dias_periodo": total_days_period,
                "total_ingresos_periodo": self.round_currency(total_ingresos),
                "monto_decimo": decimo_tercero,
                "fecha_calculo": datetime.now(),
                "base_calculo": "Total ingresos gravables del período",
                "formula": f"{total_ingresos:.2f} / 12 = {decimo_tercero:.2f}" if days_worked >= total_days_period else f"({total_ingresos:.2f} * {days_worked}) / ({total_days_period} * 12) = {decimo_tercero:.2f}"
            }

        except Exception as e:
            logger.error(f"Error calculando décimo tercero para {empleado.codigo}: {e}")
            raise

    def calculate_decimo_cuarto(self, empleado, calculation_year):
        """
        Calcular décimo cuarto sueldo (Bono Escolar)

        Args:
            empleado: Objeto Empleado
            calculation_year: Año de cálculo (período agosto 1 - julio 31)

        Returns:
            dict: Resultado del cálculo de décimo cuarto
        """
        try:
            # Período de cálculo: Agosto año anterior a Julio año actual
            period_start = date(calculation_year - 1, 8, 1)
            period_end = date(calculation_year, 7, 31)

            # Verificar que el empleado esté activo
            if not empleado.activo:
                raise ValueError(f"Empleado {empleado.codigo} no está activo")

            # Calcular fecha de inicio efectiva
            effective_start = period_start
            if empleado.fecha_ingreso and empleado.fecha_ingreso > period_start:
                effective_start = empleado.fecha_ingreso

            # Calcular fecha de fin efectiva
            effective_end = period_end
            if empleado.fecha_salida and empleado.fecha_salida < period_end:
                effective_end = empleado.fecha_salida

            # Días trabajados en el período
            days_worked = (effective_end - effective_start).days + 1
            total_days_period = (period_end - period_start).days + 1

            # El décimo cuarto es fijo = SBU actual
            sbu = self.parameters["DECIMO_CUARTO_MONTO"]

            # Calcular proporcional según días trabajados
            if days_worked >= total_days_period:
                # Período completo
                decimo_cuarto = sbu
            else:
                # Proporcional
                decimo_cuarto = (sbu * days_worked) / total_days_period

            # Redondear
            decimo_cuarto = self.round_currency(decimo_cuarto)

            return {
                "empleado_codigo": empleado.codigo,
                "empleado_nombre": f"{empleado.nombres} {empleado.apellidos}",
                "tipo": "DECIMO_CUARTO",
                "año_calculo": calculation_year,
                "periodo_inicio": effective_start,
                "periodo_fin": effective_end,
                "dias_trabajados": days_worked,
                "total_dias_periodo": total_days_period,
                "sbu_base": self.round_currency(sbu),
                "monto_decimo": decimo_cuarto,
                "fecha_calculo": datetime.now(),
                "base_calculo": f"SBU {calculation_year}: ${sbu}",
                "formula": f"${sbu:.2f}" if days_worked >= total_days_period else f"({sbu:.2f} * {days_worked}) / {total_days_period} = {decimo_cuarto:.2f}"
            }

        except Exception as e:
            logger.error(f"Error calculando décimo cuarto para {empleado.codigo}: {e}")
            raise

    def get_employee_income_period(self, empleado, start_date, end_date):
        """Obtener ingresos del empleado en un período específico"""
        try:
            total_ingresos = Decimal("0")

            # Obtener roles de pago del período
            start_period = start_date.strftime("%Y-%m")
            end_period = end_date.strftime("%Y-%m")

            # Generar lista de períodos mensuales
            current_date = start_date.replace(day=1)  # Primer día del mes de inicio
            periods = []

            while current_date <= end_date:
                periods.append(current_date.strftime("%Y-%m"))
                # Avanzar al siguiente mes
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)

            # Sumar ingresos de todos los períodos
            for period in periods:
                roles = self.session.query(RolPago).filter(
                    RolPago.empleado_codigo == empleado.codigo,
                    RolPago.periodo == period
                ).all()

                for rol in roles:
                    # Sumar todos los ingresos gravables
                    total_ingresos += Decimal(str(rol.total_ingresos or 0))

            # Si no hay roles de pago registrados, usar sueldo básico estimado
            if total_ingresos == 0:
                sueldo_basico = empleado.sueldo_basico or self.parameters["SBU"]
                months_in_period = len(periods)
                total_ingresos = sueldo_basico * months_in_period

            return total_ingresos

        except Exception as e:
            logger.error(f"Error obteniendo ingresos del período: {e}")
            return Decimal("0")

    def calculate_decimos_batch(self, decimo_type, calculation_year, employee_codes=None):
        """
        Calcular décimos para múltiples empleados

        Args:
            decimo_type: "TERCERO" o "CUARTO"
            calculation_year: Año de cálculo
            employee_codes: Lista de códigos de empleados (opcional)

        Returns:
            list: Lista de resultados de cálculo
        """
        try:
            # Query base de empleados activos
            query = self.session.query(Empleado).filter(Empleado.activo == True)

            # Filtrar por códigos específicos si se proporcionan
            if employee_codes:
                query = query.filter(Empleado.codigo.in_(employee_codes))

            empleados = query.all()
            results = []

            for empleado in empleados:
                try:
                    if decimo_type.upper() == "TERCERO":
                        result = self.calculate_decimo_tercero(empleado, calculation_year)
                    elif decimo_type.upper() == "CUARTO":
                        result = self.calculate_decimo_cuarto(empleado, calculation_year)
                    else:
                        raise ValueError(f"Tipo de décimo inválido: {decimo_type}")

                    results.append(result)

                except Exception as e:
                    logger.error(f"Error calculando {decimo_type} para empleado {empleado.codigo}: {e}")
                    continue

            logger.info(f"Décimo {decimo_type} calculado para {len(results)} empleados del año {calculation_year}")
            return results

        except Exception as e:
            logger.error(f"Error calculando décimos en lote: {e}")
            raise

    def save_decimos_results(self, decimos_results, approved_by=None):
        """
        Guardar resultados de décimos en la base de datos

        Args:
            decimos_results: Lista de resultados de cálculo
            approved_by: Usuario que aprueba (opcional)
        """
        try:
            for result in decimos_results:
                if result["tipo"] == "DECIMO_TERCERO":
                    # Verificar si ya existe
                    existing = self.session.query(DecimoTercer).filter(
                        DecimoTercer.empleado_codigo == result["empleado_codigo"],
                        DecimoTercer.año == result["año_calculo"]
                    ).first()

                    if existing:
                        decimo = existing
                        decimo.fecha_modificacion = datetime.now()
                    else:
                        decimo = DecimoTercer(
                            empleado_codigo=result["empleado_codigo"],
                            año=result["año_calculo"],
                            fecha_creacion=datetime.now()
                        )
                        self.session.add(decimo)

                    # Actualizar campos
                    decimo.periodo_inicio = result["periodo_inicio"]
                    decimo.periodo_fin = result["periodo_fin"]
                    decimo.dias_trabajados = result["dias_trabajados"]
                    decimo.total_ingresos = float(result["total_ingresos_periodo"])
                    decimo.monto = float(result["monto_decimo"])
                    decimo.estado = "CALCULADO"

                elif result["tipo"] == "DECIMO_CUARTO":
                    # Verificar si ya existe
                    existing = self.session.query(DecimoCuarto).filter(
                        DecimoCuarto.empleado_codigo == result["empleado_codigo"],
                        DecimoCuarto.año == result["año_calculo"]
                    ).first()

                    if existing:
                        decimo = existing
                        decimo.fecha_modificacion = datetime.now()
                    else:
                        decimo = DecimoCuarto(
                            empleado_codigo=result["empleado_codigo"],
                            año=result["año_calculo"],
                            fecha_creacion=datetime.now()
                        )
                        self.session.add(decimo)

                    # Actualizar campos
                    decimo.periodo_inicio = result["periodo_inicio"]
                    decimo.periodo_fin = result["periodo_fin"]
                    decimo.dias_trabajados = result["dias_trabajados"]
                    decimo.sbu_base = float(result["sbu_base"])
                    decimo.monto = float(result["monto_decimo"])
                    decimo.estado = "CALCULADO"

                # Campos comunes
                if approved_by:
                    decimo.aprobado_por = approved_by
                    decimo.fecha_aprobacion = datetime.now()

            self.session.commit()
            logger.info(f"Guardados {len(decimos_results)} décimos")

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error guardando resultados de décimos: {e}")
            raise

    def get_decimos_summary(self, decimo_type, calculation_year):
        """Obtener resumen de décimos del año"""
        try:
            if decimo_type.upper() == "TERCERO":
                decimos = self.session.query(DecimoTercer).filter(
                    DecimoTercer.año == calculation_year
                ).all()
            elif decimo_type.upper() == "CUARTO":
                decimos = self.session.query(DecimoCuarto).filter(
                    DecimoCuarto.año == calculation_year
                ).all()
            else:
                return {}

            if not decimos:
                return {
                    "total_empleados": 0,
                    "total_monto": Decimal("0"),
                    "calculados": 0,
                    "aprobados": 0,
                    "pagados": 0
                }

            summary = {
                "total_empleados": len(decimos),
                "total_monto": sum(Decimal(str(d.monto)) for d in decimos),
                "calculados": len([d for d in decimos if d.estado == "CALCULADO"]),
                "aprobados": len([d for d in decimos if d.estado == "APROBADO"]),
                "pagados": len([d for d in decimos if d.estado == "PAGADO"])
            }

            # Redondear monto total
            summary["total_monto"] = self.round_currency(summary["total_monto"])

            return summary

        except Exception as e:
            logger.error(f"Error obteniendo resumen de décimos: {e}")
            return {}

    def round_currency(self, amount):
        """Redondear cantidad a 2 decimales"""
        if amount is None:
            return Decimal("0.00")
        return Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def get_employee_decimos_history(self, empleado_codigo, years=5):
        """Obtener historial de décimos de un empleado"""
        try:
            current_year = datetime.now().year
            history = []

            for year in range(current_year - years, current_year + 1):
                # Décimo tercero
                tercero = self.session.query(DecimoTercer).filter(
                    DecimoTercer.empleado_codigo == empleado_codigo,
                    DecimoTercer.año == year
                ).first()

                # Décimo cuarto
                cuarto = self.session.query(DecimoCuarto).filter(
                    DecimoCuarto.empleado_codigo == empleado_codigo,
                    DecimoCuarto.año == year
                ).first()

                history.append({
                    "año": year,
                    "decimo_tercero": {
                        "monto": float(tercero.monto) if tercero else 0,
                        "estado": tercero.estado if tercero else "NO_CALCULADO"
                    },
                    "decimo_cuarto": {
                        "monto": float(cuarto.monto) if cuarto else 0,
                        "estado": cuarto.estado if cuarto else "NO_CALCULADO"
                    },
                    "total": float(tercero.monto if tercero else 0) + float(cuarto.monto if cuarto else 0)
                })

            return history

        except Exception as e:
            logger.error(f"Error obteniendo historial de décimos: {e}")
            return []

# Instancia global
decimos_calculator = DecimosCalculator()