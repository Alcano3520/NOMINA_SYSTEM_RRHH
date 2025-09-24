#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PayrollCalculator - Sistema SAI
Cálculos de nómina según normativa ecuatoriana 2024
"""

import sys
from pathlib import Path
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
# import holidays  # Not needed for basic functionality

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_session
from database.models import Empleado, Control, RolPago, IngresoDescuento

logger = logging.getLogger(__name__)

class PayrollCalculator:
    """Calculadora de nómina ecuatoriana"""

    def __init__(self):
        self.session = get_session()
        self.parameters = self.load_parameters()

    def load_parameters(self):
        """Cargar parámetros de control del sistema"""
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
                "APORTE_PERSONAL_IESS": Decimal("0.0945"),  # 9.45%
                "APORTE_PATRONAL_IESS": Decimal("0.1215"),  # 12.15%
                "FONDOS_RESERVA_RATE": Decimal("0.0833"),   # 8.33%
                "IMPUESTO_RENTA_BASE": Decimal("11902"),    # Base exenta anual 2024
                "DECIMO_TERCER_RATE": Decimal("0.0833"),    # 1/12
                "DECIMO_CUARTO_MONTO": Decimal("460.00"),   # SBU 2024
            }

            # Combinar con valores por defecto
            for key, value in default_params.items():
                if key not in params:
                    params[key] = value

            return params

        except Exception as e:
            logger.error(f"Error cargando parámetros: {e}")
            # Retornar parámetros por defecto en caso de error
            return {
                "SBU": Decimal("460.00"),
                "APORTE_PERSONAL_IESS": Decimal("0.0945"),
                "APORTE_PATRONAL_IESS": Decimal("0.1215"),
                "FONDOS_RESERVA_RATE": Decimal("0.0833"),
                "IMPUESTO_RENTA_BASE": Decimal("11902"),
                "DECIMO_TERCER_RATE": Decimal("0.0833"),
                "DECIMO_CUARTO_MONTO": Decimal("460.00"),
            }

    def calculate_employee_payroll(self, empleado, period_year, period_month, days_worked=None):
        """
        Calcular nómina individual de un empleado

        Args:
            empleado: Objeto Empleado
            period_year: Año del período
            period_month: Mes del período
            days_worked: Días trabajados (opcional, por defecto días del mes)

        Returns:
            dict: Resultados del cálculo de nómina
        """
        try:
            # Validaciones básicas
            if not empleado.activo:
                raise ValueError(f"Empleado {empleado.empleado} no está activo")

            # Días del período
            if days_worked is None:
                _, days_in_month = monthrange(period_year, period_month)
                days_worked = days_in_month

            # Sueldo básico proporcional
            sueldo_mensual = empleado.sueldo or self.parameters["SBU"]
            sueldo_diario = sueldo_mensual / 30  # Base 30 días
            sueldo_basico = sueldo_diario * days_worked

            # Horas extras (si existen)
            horas_extras_50 = self.get_overtime_hours(empleado, period_year, period_month, "50%")
            horas_extras_100 = self.get_overtime_hours(empleado, period_year, period_month, "100%")

            # Cálculo horas extras
            hora_ordinaria = sueldo_mensual / 240  # 30 días x 8 horas
            valor_horas_extras_50 = horas_extras_50 * hora_ordinaria * Decimal("1.5")
            valor_horas_extras_100 = horas_extras_100 * hora_ordinaria * Decimal("2.0")
            total_horas_extras = valor_horas_extras_50 + valor_horas_extras_100

            # Ingresos adicionales
            ingresos_adicionales = self.get_additional_income(empleado, period_year, period_month)

            # Total ingresos
            total_ingresos = sueldo_basico + total_horas_extras + ingresos_adicionales

            # Descuentos obligatorios
            # IESS - Aporte personal (9.45%)
            aporte_iess = total_ingresos * self.parameters["APORTE_PERSONAL_IESS"]

            # Impuesto a la Renta (si aplica)
            impuesto_renta = self.calculate_income_tax(empleado, total_ingresos * 12)  # Anualizado
            impuesto_renta_mensual = impuesto_renta / 12

            # Descuentos adicionales
            descuentos_adicionales = self.get_additional_deductions(empleado, period_year, period_month)

            # Total descuentos
            total_descuentos = aporte_iess + impuesto_renta_mensual + descuentos_adicionales

            # Líquido a recibir
            liquido_recibir = total_ingresos - total_descuentos

            # Provisiones (cálculo patronal)
            # Décimo tercero (1/12 del total ingresos anualizados)
            decimo_tercero = total_ingresos * self.parameters["DECIMO_TERCER_RATE"]

            # Décimo cuarto (proporcional al SBU)
            decimo_cuarto = self.parameters["DECIMO_CUARTO_MONTO"] / 12

            # Vacaciones (1/24 del sueldo anual)
            vacaciones = sueldo_mensual / 24

            # Fondos de reserva (si aplica - después de 1 año)
            fondos_reserva = Decimal("0")
            if self.employee_eligible_for_fondos_reserva(empleado):
                fondos_reserva = total_ingresos * self.parameters["FONDOS_RESERVA_RATE"]

            # Aporte patronal IESS
            aporte_patronal = total_ingresos * self.parameters["APORTE_PATRONAL_IESS"]

            # Resultado completo
            return {
                # Datos del empleado
                "empleado_codigo": empleado.empleado,
                "empleado_nombre": f"{empleado.nombres} {empleado.apellidos}",
                "periodo": f"{period_year:04d}-{period_month:02d}",
                "dias_trabajados": days_worked,

                # Ingresos
                "sueldo_basico": self.round_currency(sueldo_basico),
                "horas_extras_50": horas_extras_50,
                "valor_horas_extras_50": self.round_currency(valor_horas_extras_50),
                "horas_extras_100": horas_extras_100,
                "valor_horas_extras_100": self.round_currency(valor_horas_extras_100),
                "total_horas_extras": self.round_currency(total_horas_extras),
                "ingresos_adicionales": self.round_currency(ingresos_adicionales),
                "total_ingresos": self.round_currency(total_ingresos),

                # Descuentos
                "aporte_iess": self.round_currency(aporte_iess),
                "impuesto_renta": self.round_currency(impuesto_renta_mensual),
                "descuentos_adicionales": self.round_currency(descuentos_adicionales),
                "total_descuentos": self.round_currency(total_descuentos),

                # Líquido
                "liquido_recibir": self.round_currency(liquido_recibir),

                # Provisiones patronales
                "decimo_tercero": self.round_currency(decimo_tercero),
                "decimo_cuarto": self.round_currency(decimo_cuarto),
                "vacaciones": self.round_currency(vacaciones),
                "fondos_reserva": self.round_currency(fondos_reserva),
                "aporte_patronal": self.round_currency(aporte_patronal),

                # Costo total para el empleador
                "costo_total": self.round_currency(
                    total_ingresos + decimo_tercero + decimo_cuarto +
                    vacaciones + fondos_reserva + aporte_patronal
                ),

                # Metadata
                "fecha_calculo": datetime.now(),
                "calculado_por": "PayrollCalculator v1.0"
            }

        except Exception as e:
            logger.error(f"Error calculando nómina para {empleado.empleado}: {e}")
            raise

    def get_overtime_hours(self, empleado, year, month, overtime_type):
        """Obtener horas extras del empleado para el período"""
        try:
            # Aquí se consultarían las horas extras registradas
            # Por ahora retornamos 0, se implementará con el módulo de asistencia
            return Decimal("0")

        except Exception as e:
            logger.error(f"Error obteniendo horas extras: {e}")
            return Decimal("0")

    def get_additional_income(self, empleado, year, month):
        """Obtener ingresos adicionales del empleado"""
        try:
            period_start = date(year, month, 1)

            if month == 12:
                period_end = date(year + 1, 1, 1)
            else:
                period_end = date(year, month + 1, 1)

            # Consultar ingresos adicionales del período
            ingresos = self.session.query(IngresoDescuento).filter(
                IngresoDescuento.empleado == empleado.empleado,
                IngresoDescuento.tipo == "INGRESO",
                IngresoDescuento.fecha_desde >= period_start,
                IngresoDescuento.fecha_desde < period_end,
                IngresoDescuento.procesado == False
            ).all()

            total = sum(Decimal(str(ingreso.valor)) for ingreso in ingresos)
            return total

        except Exception as e:
            logger.error(f"Error obteniendo ingresos adicionales: {e}")
            return Decimal("0")

    def get_additional_deductions(self, empleado, year, month):
        """Obtener descuentos adicionales del empleado"""
        try:
            period_start = date(year, month, 1)

            if month == 12:
                period_end = date(year + 1, 1, 1)
            else:
                period_end = date(year, month + 1, 1)

            # Consultar descuentos del período
            descuentos = self.session.query(IngresoDescuento).filter(
                IngresoDescuento.empleado == empleado.empleado,
                IngresoDescuento.tipo == "DESCUENTO",
                IngresoDescuento.fecha_desde >= period_start,
                IngresoDescuento.fecha_desde < period_end,
                IngresoDescuento.procesado == False
            ).all()

            total = sum(Decimal(str(descuento.valor)) for descuento in descuentos)
            return total

        except Exception as e:
            logger.error(f"Error obteniendo descuentos adicionales: {e}")
            return Decimal("0")

    def calculate_income_tax(self, empleado, annual_income):
        """
        Calcular impuesto a la renta según tabla 2024

        Args:
            empleado: Objeto empleado
            annual_income: Ingreso anual gravable

        Returns:
            Decimal: Impuesto anual a pagar
        """
        try:
            # Tabla de impuesto a la renta 2024 Ecuador
            tax_brackets = [
                (Decimal("11902"), Decimal("0"), Decimal("0")),      # Fracción básica exenta
                (Decimal("15159"), Decimal("5"), Decimal("0")),      # 5% hasta $15,159
                (Decimal("19682"), Decimal("10"), Decimal("163")),   # 10% hasta $19,682
                (Decimal("26031"), Decimal("12"), Decimal("614")),   # 12% hasta $26,031
                (Decimal("34255"), Decimal("15"), Decimal("1376")), # 15% hasta $34,255
                (Decimal("45407"), Decimal("20"), Decimal("2611")), # 20% hasta $45,407
                (Decimal("60450"), Decimal("25"), Decimal("4844")), # 25% hasta $60,450
                (Decimal("80605"), Decimal("30"), Decimal("8900")), # 30% hasta $80,605
                (float('inf'), Decimal("35"), Decimal("14947"))     # 35% en adelante
            ]

            # Calcular impuesto
            for limit, rate, base_tax in tax_brackets:
                if annual_income <= limit:
                    excess = annual_income - (tax_brackets[tax_brackets.index((limit, rate, base_tax)) - 1][0] if tax_brackets.index((limit, rate, base_tax)) > 0 else Decimal("0"))
                    if excess > 0:
                        tax = base_tax + (excess * rate / 100)
                    else:
                        tax = base_tax
                    break
            else:
                # Tramo más alto
                excess = annual_income - Decimal("80605")
                tax = Decimal("14947") + (excess * Decimal("35") / 100)

            return max(Decimal("0"), tax)

        except Exception as e:
            logger.error(f"Error calculando impuesto a la renta: {e}")
            return Decimal("0")

    def employee_eligible_for_fondos_reserva(self, empleado):
        """Verificar si empleado es elegible para fondos de reserva"""
        try:
            # Fondos de reserva aplican después de 1 año de trabajo
            if empleado.fecha_ing:
                years_worked = (datetime.now().date() - empleado.fecha_ing).days / 365.25
                return years_worked >= 1
            return False

        except Exception as e:
            logger.error(f"Error verificando elegibilidad fondos de reserva: {e}")
            return False

    def round_currency(self, amount):
        """Redondear cantidad a 2 decimales"""
        if amount is None:
            return Decimal("0.00")
        return Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_payroll_period(self, period_year, period_month, employee_codes=None):
        """
        Calcular nómina de un período completo

        Args:
            period_year: Año del período
            period_month: Mes del período
            employee_codes: Lista de códigos de empleados (opcional)

        Returns:
            list: Lista de resultados de nómina
        """
        try:
            # Query base de empleados activos
            query = self.session.query(Empleado).filter(Empleado.activo == True)

            # Filtrar por códigos específicos si se proporcionan
            if employee_codes:
                query = query.filter(Empleado.empleado.in_(employee_codes))

            empleados = query.all()
            results = []

            for empleado in empleados:
                try:
                    result = self.calculate_employee_payroll(empleado, period_year, period_month)
                    results.append(result)

                except Exception as e:
                    logger.error(f"Error calculando nómina para empleado {empleado.empleado}: {e}")
                    continue

            logger.info(f"Nómina calculada para {len(results)} empleados del período {period_year}-{period_month:02d}")
            return results

        except Exception as e:
            logger.error(f"Error calculando nómina del período: {e}")
            raise

    def save_payroll_results(self, payroll_results, approved_by=None):
        """
        Guardar resultados de nómina en la base de datos

        Args:
            payroll_results: Lista de resultados de cálculo
            approved_by: Usuario que aprueba (opcional)
        """
        try:
            for result in payroll_results:
                # Verificar si ya existe el rol de pago
                existing_rol = self.session.query(RolPago).filter(
                    RolPago.empleado == result["empleado_codigo"],
                    RolPago.periodo == result["periodo"]
                ).first()

                if existing_rol:
                    # Actualizar rol existente
                    rol_pago = existing_rol
                else:
                    # Calcular fechas del período
                    year, month = map(int, result["periodo"].split("-"))
                    fecha_desde = date(year, month, 1)

                    if month == 12:
                        fecha_hasta = date(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        fecha_hasta = date(year, month + 1, 1) - timedelta(days=1)

                    # Crear nuevo rol de pago
                    rol_pago = RolPago(
                        empleado=result["empleado_codigo"],
                        periodo=result["periodo"],
                        fecha_desde=fecha_desde,
                        fecha_hasta=fecha_hasta
                    )
                    self.session.add(rol_pago)

                # Actualizar campos
                rol_pago.dias_trabajados = int(result["dias_trabajados"])
                rol_pago.sueldo_basico = float(result["sueldo_basico"])
                rol_pago.horas_extras = float(result["total_horas_extras"])
                rol_pago.ingresos_adicionales = float(result["ingresos_adicionales"])
                rol_pago.total_ingresos = float(result["total_ingresos"])
                rol_pago.aporte_iess = float(result["aporte_iess"])
                rol_pago.impuesto_renta = float(result["impuesto_renta"])
                rol_pago.total_descuentos = float(result["total_descuentos"])
                rol_pago.liquido_recibir = float(result["liquido_recibir"])
                rol_pago.decimo_tercero = float(result["decimo_tercero"])
                rol_pago.decimo_cuarto = float(result["decimo_cuarto"])
                rol_pago.vacaciones = float(result["vacaciones"])
                rol_pago.fondos_reserva = float(result["fondos_reserva"])
                rol_pago.aporte_patronal = float(result["aporte_patronal"])
                rol_pago.estado = "CALCULADO"

                if approved_by:
                    rol_pago.aprobado_por = approved_by
                    rol_pago.fecha_aprobacion = datetime.now()

            self.session.commit()
            logger.info(f"Guardados {len(payroll_results)} roles de pago")

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error guardando resultados de nómina: {e}")
            raise

    def get_payroll_summary(self, period_year, period_month):
        """Obtener resumen de nómina del período"""
        try:
            period = f"{period_year:04d}-{period_month:02d}"

            roles = self.session.query(RolPago).filter(
                RolPago.periodo == period
            ).all()

            if not roles:
                return {
                    "total_empleados": 0,
                    "total_ingresos": Decimal("0"),
                    "total_descuentos": Decimal("0"),
                    "liquido_total": Decimal("0"),
                    "aporte_iess_personal": Decimal("0"),
                    "aporte_iess_patronal": Decimal("0"),
                    "impuesto_renta_total": Decimal("0"),
                    "provisiones_total": Decimal("0"),
                    "costo_empresa_total": Decimal("0")
                }

            summary = {
                "total_empleados": len(roles),
                "total_ingresos": sum(Decimal(str(rol.total_ingresos)) for rol in roles),
                "total_descuentos": sum(Decimal(str(rol.total_descuentos)) for rol in roles),
                "liquido_total": sum(Decimal(str(rol.liquido_recibir)) for rol in roles),
                "aporte_iess_personal": sum(Decimal(str(rol.aporte_iess)) for rol in roles),
                "aporte_iess_patronal": sum(Decimal(str(rol.aporte_patronal)) for rol in roles),
                "impuesto_renta_total": sum(Decimal(str(rol.impuesto_renta)) for rol in roles),
                "provisiones_total": sum(
                    Decimal(str(rol.decimo_tercero)) +
                    Decimal(str(rol.decimo_cuarto)) +
                    Decimal(str(rol.vacaciones)) +
                    Decimal(str(rol.fondos_reserva))
                    for rol in roles
                ),
            }

            # Costo total para la empresa
            summary["costo_empresa_total"] = (
                summary["total_ingresos"] +
                summary["aporte_iess_patronal"] +
                summary["provisiones_total"]
            )

            # Redondear todos los valores
            for key in summary:
                if key != "total_empleados" and isinstance(summary[key], Decimal):
                    summary[key] = self.round_currency(summary[key])

            return summary

        except Exception as e:
            logger.error(f"Error obteniendo resumen de nómina: {e}")
            return {}

# Instancia global
payroll_calculator = PayrollCalculator()