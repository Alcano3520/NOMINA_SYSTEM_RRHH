"""Cálculos y fórmulas para nómina ecuatoriana"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta
from typing import Dict, List
import calendar

from config import Config

def calcular_aporte_iess_personal(sueldo: Decimal) -> Decimal:
    """Calcular aporte personal al IESS (9.45%)"""
    return (sueldo * Decimal(str(Config.APORTE_PERSONAL_IESS))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_aporte_iess_patronal(sueldo: Decimal) -> Decimal:
    """Calcular aporte patronal al IESS (11.15%)"""
    return (sueldo * Decimal(str(Config.APORTE_PATRONAL_IESS))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_fondos_reserva(sueldo: Decimal) -> Decimal:
    """Calcular fondos de reserva (8.33%)"""
    return (sueldo * Decimal(str(Config.FONDOS_RESERVA))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_valor_hora(sueldo_mensual: Decimal, jornada_semanal: int = 40) -> Decimal:
    """Calcular valor hora basado en sueldo mensual"""
    # Horas mensuales = jornada semanal * 4.33 semanas promedio
    horas_mensuales = Decimal(str(jornada_semanal * 4.33))
    return (sueldo_mensual / horas_mensuales).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_horas_extras(valor_hora: Decimal, horas: Decimal, tipo_recargo: str) -> Decimal:
    """Calcular valor de horas extras"""
    recargos = {
        '25': Decimal(str(Config.HORAS_EXTRAS_25)),
        '50': Decimal(str(Config.HORAS_EXTRAS_50)),
        '100': Decimal(str(Config.HORAS_EXTRAS_100))
    }

    recargo = recargos.get(tipo_recargo, Decimal('1.0'))
    return (valor_hora * horas * recargo).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_decimo_tercer_sueldo(ingresos_anuales: Decimal) -> Decimal:
    """Calcular décimo tercer sueldo"""
    return (ingresos_anuales / Decimal('12')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_decimo_cuarto_sueldo(dias_trabajados: int, sbu: Decimal = None) -> Decimal:
    """Calcular décimo cuarto sueldo proporcional"""
    if sbu is None:
        sbu = Decimal(str(Config.SBU))

    # Proporcional según días trabajados en el año
    return (sbu * Decimal(str(dias_trabajados)) / Decimal('360')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_vacaciones(sueldo: Decimal, dias_vacaciones: int = 15) -> Decimal:
    """Calcular valor de vacaciones"""
    # Vacaciones = sueldo * días / 360 (año comercial)
    return (sueldo * Decimal(str(dias_vacaciones)) / Decimal('360')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_dias_trabajados(fecha_inicio: date, fecha_fin: date) -> int:
    """Calcular días trabajados entre fechas"""
    if fecha_inicio > fecha_fin:
        return 0

    delta = fecha_fin - fecha_inicio
    return delta.days + 1

def calcular_dias_laborables(fecha_inicio: date, fecha_fin: date) -> int:
    """Calcular días laborables (lunes a viernes)"""
    dias_laborables = 0
    fecha_actual = fecha_inicio

    while fecha_actual <= fecha_fin:
        # 0 = lunes, 6 = domingo
        if fecha_actual.weekday() < 5:  # Lunes a viernes
            dias_laborables += 1
        fecha_actual += timedelta(days=1)

    return dias_laborables

def calcular_sueldo_proporcional(sueldo_mensual: Decimal, dias_trabajados: int,
                                dias_mes: int) -> Decimal:
    """Calcular sueldo proporcional"""
    return (sueldo_mensual * Decimal(str(dias_trabajados)) /
            Decimal(str(dias_mes))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

def calcular_impuesto_renta(ingreso_gravable: Decimal, tabla_ir: List[Dict] = None) -> Decimal:
    """Calcular impuesto a la renta"""
    # Tabla simplificada del impuesto a la renta 2024
    if tabla_ir is None:
        tabla_ir = [
            {'desde': 0, 'hasta': 11212, 'porcentaje': 0, 'base': 0},
            {'desde': 11212, 'hasta': 14285, 'porcentaje': 5, 'base': 0},
            {'desde': 14285, 'hasta': 17854, 'porcentaje': 10, 'base': 153.65},
            {'desde': 17854, 'hasta': 21442, 'porcentaje': 12, 'base': 510.55},
            {'desde': 21442, 'hasta': 42998, 'porcentaje': 15, 'base': 941.11},
            {'desde': 42998, 'hasta': 64507, 'porcentaje': 20, 'base': 4174.51},
            {'desde': 64507, 'hasta': 86010, 'porcentaje': 25, 'base': 8476.31},
            {'desde': 86010, 'hasta': 114938, 'porcentaje': 30, 'base': 13851.81},
            {'desde': 114938, 'hasta': float('inf'), 'porcentaje': 35, 'base': 22529.21}
        ]

    ingreso_anual = float(ingreso_gravable * 12)  # Convertir a anual

    for tramo in tabla_ir:
        if tramo['desde'] <= ingreso_anual <= tramo['hasta']:
            exceso = ingreso_anual - tramo['desde']
            impuesto_anual = tramo['base'] + (exceso * tramo['porcentaje'] / 100)
            return Decimal(str(impuesto_anual / 12)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

    return Decimal('0.00')

def calcular_liquidacion(empleado_data: Dict) -> Dict:
    """Calcular liquidación completa de empleado"""
    sueldo = Decimal(str(empleado_data.get('sueldo', 0)))
    fecha_ingreso = empleado_data.get('fecha_ingreso')
    fecha_salida = empleado_data.get('fecha_salida', date.today())

    # Calcular tiempo trabajado
    dias_trabajados = calcular_dias_trabajados(fecha_ingreso, fecha_salida)
    años_trabajados = dias_trabajados / 365

    # Sueldo pendiente (proporcional del mes)
    dias_mes = calendar.monthrange(fecha_salida.year, fecha_salida.month)[1]
    dia_mes_salida = fecha_salida.day
    sueldo_pendiente = calcular_sueldo_proporcional(sueldo, dia_mes_salida, dias_mes)

    # Vacaciones no gozadas
    dias_vacaciones_derecho = int(años_trabajados * 15)
    dias_vacaciones_tomadas = empleado_data.get('dias_vacaciones_tomadas', 0)
    dias_vacaciones_pendientes = max(0, dias_vacaciones_derecho - dias_vacaciones_tomadas)
    vacaciones_pendientes = calcular_vacaciones(sueldo, dias_vacaciones_pendientes)

    # Décimo tercer sueldo proporcional
    meses_trabajados_año = fecha_salida.month
    if fecha_ingreso.year == fecha_salida.year:
        meses_trabajados_año = fecha_salida.month - fecha_ingreso.month + 1

    decimo_tercer = (sueldo * Decimal(str(meses_trabajados_año)) / Decimal('12')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    # Décimo cuarto sueldo proporcional
    decimo_cuarto = calcular_decimo_cuarto_sueldo(dias_trabajados)

    # Fondos de reserva (si aplica - después del primer año)
    fondos_reserva = Decimal('0.00')
    if años_trabajados >= 1:
        fondos_reserva = calcular_fondos_reserva(sueldo) * Decimal(str(meses_trabajados_año))

    # Indemnización (según motivo de salida)
    indemnizacion = Decimal('0.00')
    motivo_salida = empleado_data.get('motivo_salida', 'RENUNCIA')

    if motivo_salida == 'DESPIDO_INTEMPESTIVO' and años_trabajados >= 1:
        # 3 meses de sueldo
        indemnizacion = sueldo * Decimal('3')
    elif motivo_salida == 'DESPIDO_JUSTIFICADO':
        # 25% de la última remuneración por cada año
        indemnizacion = sueldo * Decimal('0.25') * Decimal(str(int(años_trabajados)))

    # Totales
    total_ingresos = (sueldo_pendiente + vacaciones_pendientes + decimo_tercer +
                     decimo_cuarto + fondos_reserva + indemnizacion)

    # Descuentos
    prestamos_pendientes = Decimal(str(empleado_data.get('prestamos_pendientes', 0)))
    anticipos_pendientes = Decimal(str(empleado_data.get('anticipos_pendientes', 0)))
    otros_descuentos = Decimal(str(empleado_data.get('otros_descuentos', 0)))

    total_descuentos = prestamos_pendientes + anticipos_pendientes + otros_descuentos

    neto_liquidacion = total_ingresos - total_descuentos

    return {
        'sueldo_pendiente': sueldo_pendiente,
        'vacaciones_pendientes': vacaciones_pendientes,
        'decimo_tercer': decimo_tercer,
        'decimo_cuarto': decimo_cuarto,
        'fondos_reserva': fondos_reserva,
        'indemnizacion': indemnizacion,
        'total_ingresos': total_ingresos,
        'prestamos_pendientes': prestamos_pendientes,
        'anticipos_pendientes': anticipos_pendientes,
        'otros_descuentos': otros_descuentos,
        'total_descuentos': total_descuentos,
        'neto_liquidacion': neto_liquidacion,
        'dias_trabajados': dias_trabajados,
        'años_trabajados': años_trabajados,
        'dias_vacaciones_pendientes': dias_vacaciones_pendientes
    }

def calcular_rol_individual(empleado_data: Dict, periodo_data: Dict) -> Dict:
    """Calcular rol individual de empleado"""
    sueldo_base = Decimal(str(empleado_data.get('sueldo', 0)))
    dias_trabajados = periodo_data.get('dias_trabajados', 30)
    horas_extras_25 = Decimal(str(periodo_data.get('horas_extras_25', 0)))
    horas_extras_50 = Decimal(str(periodo_data.get('horas_extras_50', 0)))
    horas_extras_100 = Decimal(str(periodo_data.get('horas_extras_100', 0)))

    # Sueldo proporcional
    sueldo_proporcional = calcular_sueldo_proporcional(sueldo_base, dias_trabajados, 30)

    # Valor hora
    valor_hora = calcular_valor_hora(sueldo_base)

    # Horas extras
    valor_he_25 = calcular_horas_extras(valor_hora, horas_extras_25, '25')
    valor_he_50 = calcular_horas_extras(valor_hora, horas_extras_50, '50')
    valor_he_100 = calcular_horas_extras(valor_hora, horas_extras_100, '100')

    # Otros ingresos
    comisiones = Decimal(str(periodo_data.get('comisiones', 0)))
    bonos = Decimal(str(periodo_data.get('bonos', 0)))
    otros_ingresos = Decimal(str(periodo_data.get('otros_ingresos', 0)))

    # Total ingresos
    total_ingresos = (sueldo_proporcional + valor_he_25 + valor_he_50 +
                     valor_he_100 + comisiones + bonos + otros_ingresos)

    # Descuentos
    aporte_iess = calcular_aporte_iess_personal(total_ingresos)
    impuesto_renta = calcular_impuesto_renta(total_ingresos)

    prestamos = Decimal(str(periodo_data.get('prestamos', 0)))
    anticipos = Decimal(str(periodo_data.get('anticipos', 0)))
    otros_descuentos = Decimal(str(periodo_data.get('otros_descuentos', 0)))

    total_descuentos = (aporte_iess + impuesto_renta + prestamos +
                       anticipos + otros_descuentos)

    # Neto a pagar
    neto_pagar = total_ingresos - total_descuentos

    return {
        'sueldo_base': sueldo_base,
        'sueldo_proporcional': sueldo_proporcional,
        'valor_hora': valor_hora,
        'horas_extras_25': valor_he_25,
        'horas_extras_50': valor_he_50,
        'horas_extras_100': valor_he_100,
        'comisiones': comisiones,
        'bonos': bonos,
        'otros_ingresos': otros_ingresos,
        'total_ingresos': total_ingresos,
        'aporte_iess': aporte_iess,
        'impuesto_renta': impuesto_renta,
        'prestamos': prestamos,
        'anticipos': anticipos,
        'otros_descuentos': otros_descuentos,
        'total_descuentos': total_descuentos,
        'neto_pagar': neto_pagar,
        'aporte_patronal': calcular_aporte_iess_patronal(total_ingresos),
        'fondos_reserva': calcular_fondos_reserva(total_ingresos)
    }

def validar_calculo_nomina(calculo: Dict) -> List[str]:
    """Validar que los cálculos de nómina sean correctos"""
    errores = []

    # Validar que el neto no sea negativo
    if calculo.get('neto_pagar', 0) < 0:
        errores.append("El neto a pagar no puede ser negativo")

    # Validar que los aportes no excedan límites
    total_ingresos = calculo.get('total_ingresos', 0)
    aporte_iess = calculo.get('aporte_iess', 0)

    if aporte_iess > total_ingresos * Decimal('0.15'):  # Máximo 15%
        errores.append("Aporte IESS excede el límite permitido")

    # Validar coherencia de totales
    suma_ingresos = (calculo.get('sueldo_proporcional', 0) +
                    calculo.get('horas_extras_25', 0) +
                    calculo.get('horas_extras_50', 0) +
                    calculo.get('horas_extras_100', 0) +
                    calculo.get('comisiones', 0) +
                    calculo.get('bonos', 0) +
                    calculo.get('otros_ingresos', 0))

    if abs(suma_ingresos - total_ingresos) > Decimal('0.02'):
        errores.append("Error en la suma de ingresos")

    return errores