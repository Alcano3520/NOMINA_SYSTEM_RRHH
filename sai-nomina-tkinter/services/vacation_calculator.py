#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VacationCalculator - Sistema SAI
Cálculo de vacaciones según normativa ecuatoriana 2024
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
from database.models import Empleado, Control, Vacacion, RolPago

logger = logging.getLogger(__name__)

class VacationCalculator:
    """Calculadora de vacaciones ecuatorianas"""

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
                "VACATION_DAYS_PER_YEAR": 15,  # 15 días calendario por año
                "VACATION_RATE": Decimal("0.04167"),  # 1/24 del sueldo mensual
                "MIN_VACATION_DAYS": 1,  # Mínimo días para solicitar
                "MAX_ADVANCE_VACATION_DAYS": 90,  # Máximo días de anticipación
            }

            for key, value in default_params.items():
                if key not in params:
                    params[key] = value

            return params

        except Exception as e:
            logger.error(f"Error cargando parámetros: {e}")
            return {
                "SBU": Decimal("460.00"),
                "VACATION_DAYS_PER_YEAR": 15,
                "VACATION_RATE": Decimal("0.04167"),
                "MIN_VACATION_DAYS": 1,
                "MAX_ADVANCE_VACATION_DAYS": 90,
            }

    def calculate_vacation_balance(self, empleado, as_of_date=None):
        """
        Calcular saldo de vacaciones de un empleado

        Args:
            empleado: Objeto Empleado
            as_of_date: Fecha de cálculo (opcional, por defecto hoy)

        Returns:
            dict: Balance de vacaciones
        """
        try:
            if as_of_date is None:
                as_of_date = date.today()

            # Verificar que el empleado esté activo
            if not empleado.activo:
                raise ValueError(f"Empleado {empleado.empleado} no está activo")

            # Fecha de ingreso
            if not empleado.fecha_ing:
                raise ValueError(f"Empleado {empleado.empleado} no tiene fecha de ingreso")

            hire_date = empleado.fecha_ing

            # Calcular tiempo trabajado
            if as_of_date < hire_date:
                raise ValueError("Fecha de cálculo no puede ser anterior a la fecha de ingreso")

            # Calcular años completos trabajados
            years_worked = self.calculate_years_worked(hire_date, as_of_date)

            # Días de vacaciones ganados por año completo
            days_per_year = self.parameters["VACATION_DAYS_PER_YEAR"]
            total_earned_days = int(years_worked) * days_per_year

            # Calcular días proporcionales del año actual
            current_year_days = self.calculate_current_year_vacation_days(
                hire_date, as_of_date, days_per_year
            )

            total_accrued_days = total_earned_days + current_year_days

            # Obtener días utilizados
            used_days = self.get_used_vacation_days(empleado, hire_date, as_of_date)

            # Días pendientes/solicitados
            pending_days = self.get_pending_vacation_days(empleado, as_of_date)

            # Balance disponible
            available_days = total_accrued_days - used_days - pending_days

            return {
                "empleado_codigo": empleado.empleado,
                "empleado_nombre": f"{empleado.nombres} {empleado.apellidos}",
                "fecha_ingreso": hire_date,
                "fecha_calculo": as_of_date,
                "años_trabajados": years_worked,
                "años_completos": int(years_worked),
                "dias_por_año": days_per_year,
                "dias_ganados_años_completos": total_earned_days,
                "dias_año_actual": current_year_days,
                "total_acumulados": total_accrued_days,
                "dias_utilizados": used_days,
                "dias_pendientes": pending_days,
                "dias_disponibles": available_days,
                "proximo_acumulo": self.get_next_accrual_date(hire_date, as_of_date),
                "fecha_calculo_sistema": datetime.now()
            }

        except Exception as e:
            logger.error(f"Error calculando balance de vacaciones para {empleado.empleado}: {e}")
            raise

    def calculate_years_worked(self, hire_date, as_of_date):
        """Calcular años trabajados con precisión decimal"""
        try:
            # Diferencia en días
            total_days = (as_of_date - hire_date).days

            # Convertir a años (365.25 días por año considerando años bisiestos)
            years = Decimal(str(total_days)) / Decimal("365.25")

            return self.round_decimal(years, 4)  # 4 decimales de precisión

        except Exception as e:
            logger.error(f"Error calculando años trabajados: {e}")
            return Decimal("0")

    def calculate_current_year_vacation_days(self, hire_date, as_of_date, days_per_year):
        """Calcular días de vacaciones proporcionales del año actual"""
        try:
            # Fecha de aniversario más reciente
            current_year = as_of_date.year
            anniversary_this_year = date(current_year, hire_date.month, hire_date.day)

            # Si el aniversario de este año aún no ha pasado, usar el año anterior
            if anniversary_this_year > as_of_date:
                anniversary_this_year = date(current_year - 1, hire_date.month, hire_date.day)

            # Días transcurridos desde el último aniversario
            days_since_anniversary = (as_of_date - anniversary_this_year).days

            # Calcular días proporcionales
            proportion = Decimal(str(days_since_anniversary)) / Decimal("365")
            proportional_days = proportion * Decimal(str(days_per_year))

            # Redondear hacia abajo (no se pueden tener fracciones de días)
            return float(int(proportional_days))

        except Exception as e:
            logger.error(f"Error calculando días del año actual: {e}")
            return 0

    def get_used_vacation_days(self, empleado, from_date, to_date):
        """Obtener días de vacaciones utilizados en un período"""
        try:
            used_vacations = self.session.query(Vacacion).filter(
                Vacacion.empleado_codigo == empleado.empleado,
                Vacacion.estado == "APROBADO",
                Vacacion.fecha_inicio >= from_date,
                Vacacion.fecha_inicio <= to_date
            ).all()

            total_used = sum(v.dias_solicitados for v in used_vacations)
            return total_used

        except Exception as e:
            logger.error(f"Error obteniendo días utilizados: {e}")
            return 0

    def get_pending_vacation_days(self, empleado, as_of_date):
        """Obtener días de vacaciones pendientes/solicitados"""
        try:
            pending_vacations = self.session.query(Vacacion).filter(
                Vacacion.empleado_codigo == empleado.empleado,
                Vacacion.estado.in_(["PENDIENTE", "APROBADO"]),
                Vacacion.fecha_inicio >= as_of_date
            ).all()

            total_pending = sum(v.dias_solicitados for v in pending_vacations)
            return total_pending

        except Exception as e:
            logger.error(f"Error obteniendo días pendientes: {e}")
            return 0

    def get_next_accrual_date(self, hire_date, as_of_date):
        """Obtener próxima fecha de acumulación de vacaciones"""
        try:
            current_year = as_of_date.year
            next_anniversary = date(current_year + 1, hire_date.month, hire_date.day)

            return next_anniversary

        except Exception as e:
            logger.error(f"Error calculando próxima fecha de acumulación: {e}")
            return None

    def calculate_vacation_payment(self, empleado, vacation_days, payment_date=None):
        """
        Calcular pago por vacaciones

        Args:
            empleado: Objeto Empleado
            vacation_days: Días de vacaciones a pagar
            payment_date: Fecha de pago (opcional)

        Returns:
            dict: Cálculo de pago de vacaciones
        """
        try:
            if payment_date is None:
                payment_date = date.today()

            # Sueldo base del empleado
            base_salary = empleado.sueldo or self.parameters["SBU"]

            # En Ecuador, las vacaciones se pagan con 1/24 del sueldo anual
            # Es decir, por cada día de vacaciones se paga 1/24 del sueldo mensual
            vacation_daily_rate = base_salary * self.parameters["VACATION_RATE"]

            # Cálculo total
            total_payment = vacation_daily_rate * Decimal(str(vacation_days))

            return {
                "empleado_codigo": empleado.empleado,
                "empleado_nombre": f"{empleado.nombres} {empleado.apellidos}",
                "dias_vacaciones": vacation_days,
                "sueldo_base": self.round_currency(base_salary),
                "tarifa_diaria": self.round_currency(vacation_daily_rate),
                "total_pago": self.round_currency(total_payment),
                "fecha_calculo": payment_date,
                "formula": f"{base_salary:.2f} × {self.parameters['VACATION_RATE']:.5f} × {vacation_days} = {total_payment:.2f}",
                "base_legal": "Código del Trabajo Ecuador - Art. 69: 1/24 del sueldo anual"
            }

        except Exception as e:
            logger.error(f"Error calculando pago de vacaciones: {e}")
            raise

    def validate_vacation_request(self, empleado, start_date, end_date, requested_days):
        """
        Validar solicitud de vacaciones

        Args:
            empleado: Objeto Empleado
            start_date: Fecha de inicio
            end_date: Fecha de fin
            requested_days: Días solicitados

        Returns:
            dict: Resultado de validación
        """
        try:
            errors = []
            warnings = []

            # Validaciones básicas
            if start_date >= end_date:
                errors.append("La fecha de inicio debe ser anterior a la fecha de fin")

            if requested_days < self.parameters["MIN_VACATION_DAYS"]:
                errors.append(f"Mínimo {self.parameters['MIN_VACATION_DAYS']} día(s) de vacaciones")

            # Validar que no sea muy anticipado
            max_advance_days = self.parameters["MAX_ADVANCE_VACATION_DAYS"]
            if start_date > date.today() + timedelta(days=max_advance_days):
                warnings.append(f"Solicitud con más de {max_advance_days} días de anticipación")

            # Verificar balance disponible
            balance = self.calculate_vacation_balance(empleado, start_date)
            if requested_days > balance["dias_disponibles"]:
                errors.append(
                    f"Días solicitados ({requested_days}) exceden días disponibles "
                    f"({balance['dias_disponibles']})"
                )

            # Verificar conflictos con otras vacaciones
            conflicts = self.check_vacation_conflicts(empleado, start_date, end_date)
            if conflicts:
                errors.append(f"Conflicto con vacaciones existentes: {conflicts}")

            # Validar días laborables (opcional)
            business_days = self.calculate_business_days(start_date, end_date)
            if abs(business_days - requested_days) > 2:  # Tolerancia de 2 días
                warnings.append(
                    f"Días solicitados ({requested_days}) difieren significativamente "
                    f"de días laborables ({business_days})"
                )

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "balance_info": balance,
                "business_days": business_days,
                "validation_date": datetime.now()
            }

        except Exception as e:
            logger.error(f"Error validando solicitud de vacaciones: {e}")
            return {
                "valid": False,
                "errors": [f"Error del sistema: {str(e)}"],
                "warnings": [],
                "balance_info": {},
                "business_days": 0,
                "validation_date": datetime.now()
            }

    def check_vacation_conflicts(self, empleado, start_date, end_date):
        """Verificar conflictos con vacaciones existentes"""
        try:
            existing_vacations = self.session.query(Vacacion).filter(
                Vacacion.empleado_codigo == empleado.empleado,
                Vacacion.estado.in_(["PENDIENTE", "APROBADO"]),
                # Verificar solapamiento de fechas
                Vacacion.fecha_inicio <= end_date,
                Vacacion.fecha_fin >= start_date
            ).all()

            conflicts = []
            for vacation in existing_vacations:
                conflicts.append(
                    f"{vacation.fecha_inicio.strftime('%d/%m/%Y')} - "
                    f"{vacation.fecha_fin.strftime('%d/%m/%Y')} ({vacation.estado})"
                )

            return conflicts

        except Exception as e:
            logger.error(f"Error verificando conflictos: {e}")
            return []

    def calculate_business_days(self, start_date, end_date):
        """Calcular días laborables entre dos fechas"""
        try:
            business_days = 0
            current_date = start_date

            while current_date <= end_date:
                # Lunes a Viernes (0-4)
                if current_date.weekday() < 5:
                    business_days += 1
                current_date += timedelta(days=1)

            return business_days

        except Exception as e:
            logger.error(f"Error calculando días laborables: {e}")
            return 0

    def get_vacation_report(self, department=None, year=None):
        """Generar reporte de vacaciones"""
        try:
            if year is None:
                year = date.today().year

            # Query base
            query = self.session.query(Empleado).filter(Empleado.activo == True)

            # Filtrar por departamento si se especifica
            if department:
                query = query.filter(Empleado.depto == department)

            empleados = query.all()
            report_data = []

            for empleado in empleados:
                balance = self.calculate_vacation_balance(empleado)

                # Vacaciones del año
                year_vacations = self.session.query(Vacacion).filter(
                    Vacacion.empleado_codigo == empleado.empleado,
                    Vacacion.fecha_inicio >= date(year, 1, 1),
                    Vacacion.fecha_inicio <= date(year, 12, 31)
                ).all()

                days_taken = sum(v.dias_solicitados for v in year_vacations if v.estado == "APROBADO")
                days_pending = sum(v.dias_solicitados for v in year_vacations if v.estado == "PENDIENTE")

                report_data.append({
                    "codigo": empleado.empleado,
                    "nombre_completo": f"{empleado.nombres} {empleado.apellidos}",
                    "departamento": empleado.depto or "SIN ASIGNAR",
                    "fecha_ingreso": empleado.fecha_ing,
                    "años_servicio": balance["años_trabajados"],
                    "dias_acumulados": balance["total_acumulados"],
                    "dias_utilizados": balance["dias_utilizados"],
                    "dias_disponibles": balance["dias_disponibles"],
                    "dias_tomados_año": days_taken,
                    "dias_pendientes_año": days_pending,
                    "proximo_acumulo": balance["proximo_acumulo"]
                })

            return {
                "año": year,
                "departamento": department or "TODOS",
                "total_empleados": len(report_data),
                "fecha_reporte": datetime.now(),
                "empleados": report_data
            }

        except Exception as e:
            logger.error(f"Error generando reporte de vacaciones: {e}")
            return {}

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
vacation_calculator = VacationCalculator()