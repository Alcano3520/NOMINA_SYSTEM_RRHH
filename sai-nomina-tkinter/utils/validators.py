"""Validaciones para datos ecuatorianos"""

import re
from datetime import datetime, date
from decimal import Decimal
from typing import Union

def validar_cedula(cedula: str) -> bool:
    """Validar cédula ecuatoriana"""
    if not cedula or len(cedula) != 10:
        return False

    if not cedula.isdigit():
        return False

    # Validar provincia (primeros 2 dígitos)
    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
        return False

    # Validar tercer dígito
    tercer_digito = int(cedula[2])
    if tercer_digito > 5:
        return False

    # Algoritmo de validación
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor >= 10:
            valor = valor - 9
        total += valor

    digito_verificador = total % 10
    if digito_verificador != 0:
        digito_verificador = 10 - digito_verificador

    return digito_verificador == int(cedula[9])

def validar_ruc(ruc: str) -> bool:
    """Validar RUC ecuatoriano"""
    if not ruc or len(ruc) != 13:
        return False

    if not ruc.isdigit():
        return False

    # Los primeros 10 dígitos deben ser una cédula válida
    cedula = ruc[:10]
    if not validar_cedula(cedula):
        return False

    # Los últimos 3 dígitos deben ser 001
    return ruc[10:] == "001"

def validar_email(email: str) -> bool:
    """Validar formato de email"""
    if not email:
        return False

    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_telefono(telefono: str) -> bool:
    """Validar formato de teléfono ecuatoriano"""
    if not telefono:
        return True  # Opcional

    # Limpiar caracteres especiales
    telefono_limpio = re.sub(r'[^\d]', '', telefono)

    # Validar longitud y formato
    if len(telefono_limpio) == 9:  # Teléfono fijo
        return telefono_limpio.startswith('0')
    elif len(telefono_limpio) == 10:  # Celular
        return telefono_limpio.startswith('09')

    return False

def validar_fecha(fecha_str: str, formato: str = "%d/%m/%Y") -> bool:
    """Validar formato de fecha"""
    if not fecha_str:
        return False

    try:
        datetime.strptime(fecha_str, formato)
        return True
    except ValueError:
        return False

def validar_numero_positivo(numero: Union[str, int, float, Decimal]) -> bool:
    """Validar que sea un número positivo"""
    try:
        valor = float(numero)
        return valor >= 0
    except (ValueError, TypeError):
        return False

def validar_sueldo(sueldo: Union[str, int, float, Decimal], sbu: float = 460.00) -> bool:
    """Validar que el sueldo sea mayor o igual al SBU"""
    try:
        valor = float(sueldo)
        return valor >= sbu
    except (ValueError, TypeError):
        return False

def validar_porcentaje(porcentaje: Union[str, int, float]) -> bool:
    """Validar que sea un porcentaje válido (0-100)"""
    try:
        valor = float(porcentaje)
        return 0 <= valor <= 100
    except (ValueError, TypeError):
        return False

def validar_codigo_empleado(codigo: str) -> bool:
    """Validar formato de código de empleado"""
    if not codigo:
        return False

    # Debe ser numérico y tener 6 dígitos
    return codigo.isdigit() and len(codigo) == 6

def validar_horas(horas: Union[str, int, float]) -> bool:
    """Validar horas trabajadas"""
    try:
        valor = float(horas)
        return 0 <= valor <= 24  # Máximo 24 horas por día
    except (ValueError, TypeError):
        return False

def validar_edad_laboral(fecha_nacimiento: date) -> bool:
    """Validar que la edad esté en rango laboral"""
    if not fecha_nacimiento:
        return False

    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year

    # Ajustar si aún no cumplió años este año
    if hoy.month < fecha_nacimiento.month or \
       (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
        edad -= 1

    return 18 <= edad <= 70

def validar_cuenta_bancaria(numero_cuenta: str, tipo_cuenta: str) -> bool:
    """Validar número de cuenta bancaria"""
    if not numero_cuenta:
        return True  # Opcional

    # Limpiar espacios y caracteres especiales
    cuenta_limpia = re.sub(r'[^\d]', '', numero_cuenta)

    # Validar longitud según tipo
    if tipo_cuenta == 'A':  # Ahorros
        return 8 <= len(cuenta_limpia) <= 12
    elif tipo_cuenta == 'C':  # Corriente
        return 8 <= len(cuenta_limpia) <= 15

    return False

def validar_dias_vacaciones(dias: int, dias_anuales: int = 15) -> bool:
    """Validar días de vacaciones"""
    return 0 <= dias <= dias_anuales * 2  # Máximo 2 años acumulados

def normalizar_texto(texto: str) -> str:
    """Normalizar texto para almacenamiento"""
    if not texto:
        return ""

    # Convertir a mayúsculas y limpiar espacios
    texto_normalizado = texto.strip().upper()

    # Remover espacios múltiples
    texto_normalizado = re.sub(r'\s+', ' ', texto_normalizado)

    return texto_normalizado

def normalizar_cedula(cedula: str) -> str:
    """Normalizar cédula removiendo caracteres especiales"""
    if not cedula:
        return ""

    return re.sub(r'[^\d]', '', cedula)

def formatear_sueldo(sueldo: Union[str, int, float, Decimal]) -> str:
    """Formatear sueldo para mostrar"""
    try:
        valor = float(sueldo)
        return f"${valor:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def formatear_fecha(fecha: date, formato: str = "%d/%m/%Y") -> str:
    """Formatear fecha para mostrar"""
    if not fecha:
        return ""

    try:
        return fecha.strftime(formato)
    except:
        return ""

class ValidacionError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

def validar_empleado_completo(data: dict) -> list:
    """Validar todos los datos de un empleado"""
    errores = []

    # Campos obligatorios
    if not data.get('cedula'):
        errores.append("Cédula es obligatoria")
    elif not validar_cedula(data['cedula']):
        errores.append("Cédula inválida")

    if not data.get('nombres'):
        errores.append("Nombres son obligatorios")

    if not data.get('apellidos'):
        errores.append("Apellidos son obligatorios")

    if not data.get('fecha_ing'):
        errores.append("Fecha de ingreso es obligatoria")

    # Validaciones opcionales
    if data.get('email') and not validar_email(data['email']):
        errores.append("Email inválido")

    if data.get('telefono') and not validar_telefono(data['telefono']):
        errores.append("Teléfono inválido")

    if data.get('sueldo') and not validar_sueldo(data['sueldo']):
        errores.append("Sueldo debe ser mayor o igual al SBU")

    if data.get('fecha_nac'):
        try:
            fecha_nac = datetime.strptime(data['fecha_nac'], "%d/%m/%Y").date()
            if not validar_edad_laboral(fecha_nac):
                errores.append("Edad debe estar entre 18 y 70 años")
        except ValueError:
            errores.append("Formato de fecha de nacimiento inválido")

    return errores