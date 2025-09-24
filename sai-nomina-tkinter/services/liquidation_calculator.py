#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiquidationCalculator - Sistema SGN
Cálculo de liquidaciones y finiquitos según normativa ecuatoriana 2024
"""

import sys
from pathlib import Path
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
from dateutil.relativedelta import relativedelta

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_session
from database.models import Empleado, Control, Liquidacion, RolPago, Vacacion, DecimoTercer, DecimoCuarto

logger = logging.getLogger(__name__)

class LiquidationCalculator:
    """Calculadora de liquidaciones ecuatorianas"""

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
                "INDEMNIZACION_RATE": Decimal("1.0"),  # 1 mes por año
                "DESAHUCIO_RATE": Decimal("0.25"),  # 25% último sueldo
                "MAX_INDEMNIZACION_YEARS": 25,  # Máximo 25 años
                "VACATION_RATE": Decimal("0.04167"),  # 1/24 del sueldo
            }

            for key, value in default_params.items():
                if key not in params:
                    params[key] = value

            return params

        except Exception as e:
            logger.error(f"Error cargando parámetros: {e}")
            return {
                "SBU": Decimal("460.00"),
                "INDEMNIZACION_RATE": Decimal("1.0"),
                "DESAHUCIO_RATE": Decimal("0.25"),
                "MAX_INDEMNIZACION_YEARS": 25,
                "VACATION_RATE": Decimal("0.04167"),
            }

    def calculate_liquidation(self, empleado, termination_date, termination_type, termination_reason=""):
        """
        Calcular liquidación completa de empleado

        Args:
            empleado: Objeto Empleado
            termination_date: Fecha de terminación
            termination_type: Tipo ("RENUNCIA", "DESPIDO_INTEMPESTIVO", "DESPIDO_JUSTIFICADO", "MUTUO_ACUERDO", "TERMINACION_CONTRATO")
            termination_reason: Motivo de terminación

        Returns:
            dict: Cálculo completo de liquidación
        """
        try:
            # Validaciones básicas
            if not empleado.fecha_ing:
                raise ValueError(f"Empleado {empleado.empleado} no tiene fecha de ingreso")

            if termination_date < empleado.fecha_ing:
                raise ValueError("Fecha de terminación no puede ser anterior a fecha de ingreso")

            # Cálculo de tiempo trabajado
            years_worked = self.calculate_years_worked(empleado.fecha_ing, termination_date)
            days_worked = (termination_date - empleado.fecha_ing).days

            # Sueldo base
            base_salary = empleado.sueldo or self.parameters["SBU"]

            # === CÁLCULOS DE LIQUIDACIÓN ===

            # 1. Sueldo proporcional del mes de salida
            proportional_salary = self.calculate_proportional_salary(
                base_salary, termination_date
            )

            # 2. Vacaciones no gozadas
            vacation_payment = self.calculate_vacation_settlement(empleado, termination_date)

            # 3. Décimo tercero proporcional
            decimo_tercero = self.calculate_proportional_decimo_tercero(
                empleado, termination_date, base_salary
            )

            # 4. Décimo cuarto proporcional
            decimo_cuarto = self.calculate_proportional_decimo_cuarto(
                empleado, termination_date
            )

            # 5. Fondos de reserva (si aplica)
            fondos_reserva = self.calculate_fondos_reserva_settlement(
                empleado, termination_date, base_salary
            )

            # 6. Indemnización (según tipo de terminación)
            indemnizacion = self.calculate_indemnizacion(
                base_salary, years_worked, termination_type
            )

            # 7. Desahucio (si aplica)
            desahucio = self.calculate_desahucio(
                base_salary, years_worked, termination_type
            )

            # 8. Bonificación por desahucio del empleador (si aplica)
            bonificacion_desahucio = self.calculate_bonificacion_desahucio(
                base_salary, years_worked, termination_type
            )

            # === TOTALES ===
            total_haberes = (
                proportional_salary + vacation_payment + decimo_tercero +
                decimo_cuarto + fondos_reserva + indemnizacion +
                desahucio + bonificacion_desahucio
            )

            # Descuentos (préstamos pendientes, anticipos, etc.)
            total_descuentos = self.calculate_liquidation_deductions(empleado, termination_date)

            # Líquido a recibir
            liquido_recibir = total_haberes - total_descuentos

            return {
                # Información del empleado
                "empleado_codigo": empleado.empleado,
                "empleado_nombre": f"{empleado.nombres} {empleado.apellidos}",
                "fecha_ingreso": empleado.fecha_ing,
                "fecha_terminacion": termination_date,
                "tipo_terminacion": termination_type,
                "motivo_terminacion": termination_reason,
                "tiempo_servicio": {
                    "años": int(years_worked),
                    "años_decimales": float(years_worked),
                    "dias_totales": days_worked
                },

                # Sueldo base
                "sueldo_base": self.round_currency(base_salary),

                # Conceptos de liquidación
                "sueldo_proporcional": self.round_currency(proportional_salary),
                "vacaciones_pendientes": vacation_payment,
                "decimo_tercero_proporcional": self.round_currency(decimo_tercero),
                "decimo_cuarto_proporcional": self.round_currency(decimo_cuarto),
                "fondos_reserva": self.round_currency(fondos_reserva),
                "indemnizacion": self.round_currency(indemnizacion),
                "desahucio": self.round_currency(desahucio),
                "bonificacion_desahucio": self.round_currency(bonificacion_desahucio),

                # Totales
                "total_haberes": self.round_currency(total_haberes),
                "total_descuentos": self.round_currency(total_descuentos),
                "liquido_recibir": self.round_currency(liquido_recibir),

                # Metadata
                "fecha_calculo": datetime.now(),
                "base_legal": self.get_legal_basis(termination_type),
                "observaciones": self.generate_liquidation_observations(
                    termination_type, years_worked, indemnizacion, desahucio
                )
            }

        except Exception as e:
            logger.error(f"Error calculando liquidación para {empleado.empleado}: {e}")
            raise

    def calculate_years_worked(self, hire_date, termination_date):
        """Calcular años trabajados con precisión decimal"""
        try:
            total_days = (termination_date - hire_date).days
            years = Decimal(str(total_days)) / Decimal("365.25")
            return self.round_decimal(years, 4)

        except Exception as e:
            logger.error(f"Error calculando años trabajados: {e}")
            return Decimal("0")

    def calculate_proportional_salary(self, base_salary, termination_date):
        """Calcular sueldo proporcional del último mes"""
        try:
            # Días del mes
            _, days_in_month = monthrange(termination_date.year, termination_date.month)

            # Días trabajados en el mes
            days_worked = termination_date.day

            # Sueldo diario
            daily_salary = base_salary / 30  # Base 30 días

            # Proporcional
            return daily_salary * days_worked

        except Exception as e:
            logger.error(f"Error calculando sueldo proporcional: {e}")
            return Decimal("0")

    def calculate_vacation_settlement(self, empleado, termination_date):
        """Calcular vacaciones pendientes en liquidación"""
        try:
            from services.vacation_calculator import vacation_calculator

            # Calcular balance de vacaciones
            balance = vacation_calculator.calculate_vacation_balance(empleado, termination_date)

            # Días disponibles
            available_days = balance["dias_disponibles"]

            if available_days <= 0:
                return {
                    "dias_pendientes": 0,
                    "valor_por_dia": Decimal("0"),
                    "total_vacaciones": Decimal("0"),
                    "detalle": "Sin vacaciones pendientes"
                }

            # Calcular pago
            payment_calc = vacation_calculator.calculate_vacation_payment(
                empleado, available_days, termination_date
            )

            return {
                "dias_pendientes": available_days,
                "valor_por_dia": payment_calc["tarifa_diaria"],
                "total_vacaciones": payment_calc["total_pago"],
                "detalle": f"{available_days} días × ${payment_calc['tarifa_diaria']:.2f} = ${payment_calc['total_pago']:.2f}"
            }

        except Exception as e:
            logger.error(f"Error calculando vacaciones de liquidación: {e}")
            return {
                "dias_pendientes": 0,
                "valor_por_dia": Decimal("0"),
                "total_vacaciones": Decimal("0"),
                "detalle": f"Error: {str(e)}"
            }

    def calculate_proportional_decimo_tercero(self, empleado, termination_date, base_salary):
        """Calcular décimo tercero proporcional"""
        try:
            # Período del décimo tercero: Diciembre 1 año anterior a Noviembre 30 año actual
            current_year = termination_date.year

            # Si estamos antes de diciembre, el período es del año anterior
            if termination_date.month < 12:
                period_start = date(current_year - 1, 12, 1)
                period_end = date(current_year, 11, 30)
            else:
                period_start = date(current_year, 12, 1)
                period_end = date(current_year + 1, 11, 30)

            # Fecha efectiva de inicio (no antes del ingreso)
            effective_start = max(period_start, empleado.fecha_ing)

            # Fecha efectiva de fin (fecha de terminación)
            effective_end = min(termination_date, period_end)

            if effective_end <= effective_start:
                return Decimal("0")

            # Días trabajados en el período
            days_worked = (effective_end - effective_start).days + 1
            total_days_period = (period_end - period_start).days + 1

            # Obtener ingresos del período (o estimar basado en sueldo actual)
            # Por simplicidad, usar sueldo base actual
            monthly_income = base_salary

            # Décimo tercero completo sería monthly_income / 12 * meses
            months_in_period = 12
            annual_equivalent = monthly_income * months_in_period
            full_decimo = annual_equivalent / 12

            # Proporcional
            proportional_decimo = (full_decimo * days_worked) / total_days_period

            return proportional_decimo

        except Exception as e:
            logger.error(f"Error calculando décimo tercero proporcional: {e}")
            return Decimal("0")

    def calculate_proportional_decimo_cuarto(self, empleado, termination_date):
        """Calcular décimo cuarto proporcional"""
        try:
            # Período del décimo cuarto: Agosto 1 año anterior a Julio 31 año actual
            current_year = termination_date.year

            if termination_date.month >= 8:
                period_start = date(current_year, 8, 1)
                period_end = date(current_year + 1, 7, 31)
            else:
                period_start = date(current_year - 1, 8, 1)
                period_end = date(current_year, 7, 31)

            # Fecha efectiva de inicio
            effective_start = max(period_start, empleado.fecha_ing)
            effective_end = min(termination_date, period_end)

            if effective_end <= effective_start:
                return Decimal("0")

            # Días trabajados
            days_worked = (effective_end - effective_start).days + 1
            total_days_period = (period_end - period_start).days + 1

            # SBU (décimo cuarto es fijo)
            sbu = self.parameters["SBU"]

            # Proporcional
            proportional_decimo = (sbu * days_worked) / total_days_period

            return proportional_decimo

        except Exception as e:
            logger.error(f"Error calculando décimo cuarto proporcional: {e}")
            return Decimal("0")

    def calculate_fondos_reserva_settlement(self, empleado, termination_date, base_salary):
        """Calcular fondos de reserva pendientes"""
        try:
            # Fondos de reserva aplican después de 1 año
            years_worked = self.calculate_years_worked(empleado.fecha_ing, termination_date)

            if years_worked < 1:
                return Decimal("0")

            # Fondos de reserva del último año (8.33% del sueldo mensual)
            fondos_rate = Decimal("0.0833")  # 8.33%

            # Calcular fondos acumulados del año en curso
            # Por simplicidad, usar sueldo actual
            monthly_fondos = base_salary * fondos_rate

            # Meses del año actual hasta la fecha de terminación
            year_start = date(termination_date.year, 1, 1)
            effective_start = max(year_start, empleado.fecha_ing)

            if termination_date <= effective_start:
                return Decimal("0")

            days_this_year = (termination_date - effective_start).days + 1
            proportional_fondos = (monthly_fondos * days_this_year) / 365

            return proportional_fondos

        except Exception as e:
            logger.error(f"Error calculando fondos de reserva: {e}")
            return Decimal("0")

    def calculate_indemnizacion(self, base_salary, years_worked, termination_type):
        """Calcular indemnización según tipo de terminación"""
        try:
            if termination_type in ["RENUNCIA", "DESPIDO_JUSTIFICADO", "TERMINACION_CONTRATO"]:
                return Decimal("0")  # No hay indemnización

            if termination_type in ["DESPIDO_INTEMPESTIVO"]:
                # Indemnización: 1 sueldo por año trabajado
                max_years = self.parameters["MAX_INDEMNIZACION_YEARS"]
                applicable_years = min(float(years_worked), max_years)

                indemnizacion = base_salary * Decimal(str(applicable_years))
                return indemnizacion

            if termination_type in ["MUTUO_ACUERDO"]:
                # Según acuerdo, por defecto 50% de la indemnización
                max_years = self.parameters["MAX_INDEMNIZACION_YEARS"]
                applicable_years = min(float(years_worked), max_years)

                indemnizacion = (base_salary * Decimal(str(applicable_years))) / 2
                return indemnizacion

            return Decimal("0")

        except Exception as e:
            logger.error(f"Error calculando indemnización: {e}")
            return Decimal("0")

    def calculate_desahucio(self, base_salary, years_worked, termination_type):
        """Calcular desahucio"""
        try:
            if termination_type in ["DESPIDO_JUSTIFICADO", "RENUNCIA"]:
                return Decimal("0")  # No hay desahucio

            # Desahucio: 25% del último sueldo por año trabajado
            desahucio_rate = self.parameters["DESAHUCIO_RATE"]  # 0.25

            desahucio = base_salary * desahucio_rate * years_worked
            return desahucio

        except Exception as e:
            logger.error(f"Error calculando desahucio: {e}")
            return Decimal("0")

    def calculate_bonificacion_desahucio(self, base_salary, years_worked, termination_type):
        """Calcular bonificación por desahucio del empleador"""
        try:
            if termination_type not in ["DESPIDO_INTEMPESTIVO"]:
                return Decimal("0")

            # Bonificación: 25% adicional cuando el empleador da el desahucio
            bonificacion_rate = self.parameters["DESAHUCIO_RATE"]  # 0.25

            bonificacion = base_salary * bonificacion_rate * years_worked
            return bonificacion

        except Exception as e:
            logger.error(f"Error calculando bonificación de desahucio: {e}")
            return Decimal("0")

    def calculate_liquidation_deductions(self, empleado, termination_date):
        """Calcular descuentos en liquidación"""
        try:
            # Aquí se incluirían préstamos pendientes, anticipos, etc.
            # Por ahora retornar 0, se implementaría con el módulo de préstamos
            return Decimal("0")

        except Exception as e:
            logger.error(f"Error calculando descuentos de liquidación: {e}")
            return Decimal("0")

    def get_legal_basis(self, termination_type):
        """Obtener base legal según tipo de terminación"""
        legal_basis = {
            "RENUNCIA": "Código del Trabajo - Art. 172: Renuncia voluntaria del trabajador",
            "DESPIDO_INTEMPESTIVO": "Código del Trabajo - Art. 188: Despido intempestivo",
            "DESPIDO_JUSTIFICADO": "Código del Trabajo - Art. 172: Despido con justa causa",
            "MUTUO_ACUERDO": "Código del Trabajo - Art. 169: Terminación por mutuo consentimiento",
            "TERMINACION_CONTRATO": "Código del Trabajo - Art. 169: Terminación de contrato"
        }

        return legal_basis.get(termination_type, "Base legal no especificada")

    def generate_liquidation_observations(self, termination_type, years_worked, indemnizacion, desahucio):
        """Generar observaciones para la liquidación"""
        observations = []

        if termination_type == "DESPIDO_INTEMPESTIVO":
            observations.append("Despido intempestivo - Se aplica indemnización completa")

        if years_worked >= 1:
            observations.append("Empleado con más de 1 año - Aplican todos los beneficios")
        else:
            observations.append("Empleado con menos de 1 año - Fondos de reserva no aplicables")

        if indemnizacion > 0:
            observations.append(f"Indemnización calculada: ${indemnizacion:.2f}")

        if desahucio > 0:
            observations.append(f"Desahucio calculado: ${desahucio:.2f}")

        return " | ".join(observations)

    def save_liquidation(self, liquidation_data, approved_by=None):
        """Guardar liquidación en la base de datos"""
        try:
            # Verificar si ya existe
            existing = self.session.query(Liquidacion).filter(
                Liquidacion.empleado_codigo == liquidation_data["empleado_codigo"],
                Liquidacion.fecha_terminacion == liquidation_data["fecha_terminacion"]
            ).first()

            if existing:
                liquidacion = existing
                liquidacion.fecha_modificacion = datetime.now()
            else:
                liquidacion = Liquidacion(
                    empleado_codigo=liquidation_data["empleado_codigo"],
                    fecha_terminacion=liquidation_data["fecha_terminacion"],
                    fecha_creacion=datetime.now()
                )
                self.session.add(liquidacion)

            # Actualizar campos
            liquidacion.tipo_terminacion = liquidation_data["tipo_terminacion"]
            liquidacion.motivo = liquidation_data["motivo_terminacion"]
            liquidacion.años_servicio = float(liquidation_data["tiempo_servicio"]["años_decimales"])
            liquidacion.sueldo_base = float(liquidation_data["sueldo_base"])
            liquidacion.sueldo_proporcional = float(liquidation_data["sueldo_proporcional"])

            # Vacaciones
            vacation_data = liquidation_data["vacaciones_pendientes"]
            liquidacion.vacaciones_dias = vacation_data["dias_pendientes"]
            liquidacion.vacaciones_valor = float(vacation_data["total_vacaciones"])

            liquidacion.decimo_tercero = float(liquidation_data["decimo_tercero_proporcional"])
            liquidacion.decimo_cuarto = float(liquidation_data["decimo_cuarto_proporcional"])
            liquidacion.fondos_reserva = float(liquidation_data["fondos_reserva"])
            liquidacion.indemnizacion = float(liquidation_data["indemnizacion"])
            liquidacion.desahucio = float(liquidation_data["desahucio"])
            liquidacion.total_haberes = float(liquidation_data["total_haberes"])
            liquidacion.total_descuentos = float(liquidation_data["total_descuentos"])
            liquidacion.liquido_pagar = float(liquidation_data["liquido_recibir"])
            liquidacion.estado = "CALCULADO"

            if approved_by:
                liquidacion.aprobado_por = approved_by
                liquidacion.fecha_aprobacion = datetime.now()

            self.session.commit()
            logger.info(f"Liquidación guardada para empleado {liquidation_data['empleado_codigo']}")

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error guardando liquidación: {e}")
            raise

    def round_currency(self, amount):
        """Redondear cantidad a 2 decimales"""
        if amount is None:
            return Decimal("0.00")
        return Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def round_decimal(self, amount, places):
        """Redondear decimal a N lugares"""
        if amount is None:
            return Decimal("0")
        quantizer = Decimal("0." + "0" * places)
        return Decimal(str(amount)).quantize(quantizer, rounding=ROUND_HALF_UP)

# Instancia global
liquidation_calculator = LiquidationCalculator()