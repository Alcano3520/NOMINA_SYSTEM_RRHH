"""Modelos de base de datos con SQLAlchemy"""

from sqlalchemy import (
    Column, String, Integer, Float, Date, DateTime, Boolean,
    ForeignKey, Text, Numeric, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib
import json

Base = declarative_base()

class Empleado(Base):
    """Modelo principal de empleados - Tabla RPEMPLEA"""
    __tablename__ = "rpemplea"

    # Campos principales
    empleado = Column(String(6), primary_key=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    cedula = Column(String(10), unique=True, nullable=False)
    fecha_nac = Column(Date)
    sexo = Column(String(1))  # M/F
    estado_civil = Column(String(1))  # S/C/D/V/U
    direccion = Column(String(200))
    telefono = Column(String(20))
    celular = Column(String(20))
    email = Column(String(100))

    # Datos laborales
    cargo = Column(String(3))
    depto = Column(String(3))
    seccion = Column(String(3))
    sueldo = Column(Numeric(10, 2), default=460.00)
    fecha_ing = Column(Date, nullable=False)
    fecha_sal = Column(Date)

    # Tipos y estados
    tipo_tra = Column(Integer, default=1)  # 1:Operativo, 2:Admin, 3:Ejecutivo
    tipo_pgo = Column(Integer, default=1)  # 1:Semanal, 2:Quincenal, 3:Mensual
    estado = Column(String(3), default='ACT')  # ACT, VAC, LIC, RET, JUB

    # Campos financieros
    anticipo = Column(Numeric(10, 2), default=0.00)
    dct_extra = Column(Numeric(10, 2), default=0.00)
    ing_extra = Column(Numeric(10, 2), default=0.00)

    # Datos bancarios
    banco = Column(String(3))
    cuenta_banco = Column(String(20))
    tipo_cuenta = Column(String(1))  # A:Ahorros, C:Corriente

    # Campos de vacaciones
    fec_invac = Column(Date)
    vacacion = Column(Integer, default=0)
    saldo_vac = Column(Integer, default=0)

    # Campos décimos
    decimo3 = Column(Numeric(10, 2), default=0.00)
    decimo4 = Column(Numeric(10, 2), default=0.00)
    decimo5 = Column(Numeric(10, 2), default=0.00)

    # Cargas familiares
    cargas = Column(Integer, default=0)

    # Beneficiarios
    beneficiario = Column(String(100))
    parentesco = Column(String(20))
    telefono_beneficiario = Column(String(20))

    # Datos adicionales
    tipo_sangre = Column(String(5))
    contacto_emergencia = Column(String(100))
    telefono_emergencia = Column(String(20))

    # Campos de control
    foto = Column(Text)  # Path o base64 de la foto
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(20))
    updated_by = Column(String(20))

    # Relaciones
    historicos = relationship("Historico", back_populates="empleado_rel", cascade="all, delete-orphan")
    ingresos_descuentos = relationship("IngresoDescuento", back_populates="empleado_rel", cascade="all, delete-orphan")
    vacaciones = relationship("Vacacion", back_populates="empleado_rel", cascade="all, delete-orphan")
    prestamos = relationship("Prestamo", back_populates="empleado_rel", cascade="all, delete-orphan")
    dotaciones = relationship("Dotacion", back_populates="empleado_rel", cascade="all, delete-orphan")

    # Índices
    __table_args__ = (
        Index('idx_empleado_cedula', 'cedula'),
        Index('idx_empleado_depto', 'depto'),
        Index('idx_empleado_estado', 'estado'),
    )

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

class Historico(Base):
    """Histórico de movimientos - Tabla RPHISTOR"""
    __tablename__ = "rphistor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    fecha = Column(Date, nullable=False)
    tipo = Column(String(3))  # ING, EGR, VAC, DEC, LIQ, HEX
    clase = Column(Integer)  # 167 para anticipos décimos, etc.
    concepto = Column(String(100))
    valor = Column(Numeric(10, 2))
    horas = Column(Numeric(5, 2))
    referencia = Column(String(20))
    observacion = Column(Text)
    periodo = Column(String(7))  # YYYY-MM
    procesado = Column(Boolean, default=False)
    usuario = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación
    empleado_rel = relationship("Empleado", back_populates="historicos")

    __table_args__ = (
        Index('idx_historico_empleado_fecha', 'empleado', 'fecha'),
        Index('idx_historico_tipo_clase', 'tipo', 'clase'),
        Index('idx_historico_periodo', 'periodo'),
    )

class IngresoDescuento(Base):
    """Ingresos y descuentos para nómina - Tabla RPINGDES"""
    __tablename__ = "rpingdes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    fecha_desde = Column(Date)
    fecha_hasta = Column(Date)
    tipo = Column(String(1))  # I:Ingreso, D:Descuento
    codigo = Column(String(10))
    concepto = Column(String(100))
    valor = Column(Numeric(10, 2))
    horas = Column(Numeric(5, 2))
    aplica_iess = Column(Boolean, default=True)
    aplica_ir = Column(Boolean, default=True)
    procesado = Column(Boolean, default=False)
    rol_id = Column(Integer)  # Referencia al rol procesado
    usuario = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación
    empleado_rel = relationship("Empleado", back_populates="ingresos_descuentos")

class Cliente(Base):
    """Clientes de la empresa de seguridad"""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10), unique=True, nullable=False)
    ruc = Column(String(13), unique=True)
    razon_social = Column(String(200), nullable=False)
    nombre_comercial = Column(String(200))
    direccion = Column(String(300))
    telefono = Column(String(20))
    email = Column(String(100))
    contacto = Column(String(100))
    telefono_contacto = Column(String(20))
    email_contacto = Column(String(100))
    estado = Column(String(10), default='ACTIVO')  # ACTIVO, INACTIVO, SUSPENDIDO
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    valor_mensual = Column(Numeric(10, 2))
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(20))

    # Relaciones
    departamentos = relationship("Departamento", back_populates="cliente_rel", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_cliente_codigo', 'codigo'),
        Index('idx_cliente_ruc', 'ruc'),
        Index('idx_cliente_estado', 'estado'),
    )

class Departamento(Base):
    """Puestos de trabajo / Departamentos de seguridad"""
    __tablename__ = "departamentos"

    codigo = Column(String(10), primary_key=True)
    nombre_codigo = Column(String(100), nullable=False)  # Ej: "GAMMA 4"
    nombre_real = Column(String(200), nullable=False)    # Ej: "RICOCENTRO NORTE"
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    direccion = Column(String(300))
    sector = Column(String(100))  # Zona de la ciudad
    tipo_puesto = Column(String(50))  # COMERCIAL, RESIDENCIAL, INDUSTRIAL, etc.

    # Configuración del puesto
    guardias_requeridos = Column(Integer, default=1)
    turnos_por_dia = Column(Integer, default=3)  # 3 turnos: mañana, tarde, noche
    horas_por_turno = Column(Integer, default=8)
    sueldo_base = Column(Numeric(10, 2))

    # Información operativa
    responsable = Column(String(6))  # Código empleado supervisor
    telefono = Column(String(20))
    referencia = Column(String(200))  # Referencias para ubicar el lugar
    acceso = Column(Text)  # Instrucciones de acceso

    # Estados
    estado = Column(String(10), default='ACTIVO')  # ACTIVO, INACTIVO, SUSPENDIDO
    permite_franco = Column(Boolean, default=True)  # Si permite guardias de franco
    es_24_horas = Column(Boolean, default=True)

    # Fechas
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

    # Observaciones y notas
    observaciones = Column(Text)
    instrucciones = Column(Text)  # Instrucciones específicas del puesto

    # Control
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(20))

    # Relaciones
    cliente_rel = relationship("Cliente", back_populates="departamentos")
    asignaciones = relationship("AsignacionDepartamento", back_populates="departamento_rel", cascade="all, delete-orphan")
    turnos = relationship("Turno", back_populates="departamento_rel", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_depto_cliente', 'cliente_id'),
        Index('idx_depto_codigo', 'codigo'),
        Index('idx_depto_estado', 'estado'),
    )

class AsignacionDepartamento(Base):
    """Asignación de empleados a departamentos/puestos"""
    __tablename__ = "asignaciones_departamento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'), nullable=False)
    departamento_codigo = Column(String(10), ForeignKey('departamentos.codigo'), nullable=False)
    fecha_desde = Column(Date, nullable=False)
    fecha_hasta = Column(Date)
    tipo_asignacion = Column(String(20), default='FIJO')  # FIJO, FRANCO, TEMPORAL, REEMPLAZO
    turno_id = Column(Integer, ForeignKey('turnos.id'))
    es_responsable = Column(Boolean, default=False)
    estado = Column(String(10), default='ACTIVO')
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))

    # Relaciones
    empleado_rel = relationship("Empleado")
    departamento_rel = relationship("Departamento", back_populates="asignaciones")
    turno_rel = relationship("Turno", back_populates="asignaciones")

    __table_args__ = (
        Index('idx_asignacion_empleado', 'empleado'),
        Index('idx_asignacion_depto', 'departamento_codigo'),
        Index('idx_asignacion_fecha', 'fecha_desde', 'fecha_hasta'),
    )

class Turno(Base):
    """Turnos de trabajo"""
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)  # Ej: "MAÑANA", "TARDE", "NOCHE"
    codigo = Column(String(10), unique=True, nullable=False)  # Ej: "M", "T", "N"
    hora_inicio = Column(String(5), nullable=False)  # Formato HH:MM
    hora_fin = Column(String(5), nullable=False)    # Formato HH:MM
    horas_duracion = Column(Integer, nullable=False)
    es_nocturno = Column(Boolean, default=False)
    recargo_nocturno = Column(Numeric(5, 2), default=0.00)  # % adicional

    # Configuración por departamento
    departamento_codigo = Column(String(10), ForeignKey('departamentos.codigo'))
    sueldo_adicional = Column(Numeric(10, 2), default=0.00)

    # Días de la semana (1=Lunes, 7=Domingo)
    lunes = Column(Boolean, default=True)
    martes = Column(Boolean, default=True)
    miercoles = Column(Boolean, default=True)
    jueves = Column(Boolean, default=True)
    viernes = Column(Boolean, default=True)
    sabado = Column(Boolean, default=True)
    domingo = Column(Boolean, default=True)

    estado = Column(String(10), default='ACTIVO')
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))

    # Relaciones
    departamento_rel = relationship("Departamento", back_populates="turnos")
    asignaciones = relationship("AsignacionDepartamento", back_populates="turno_rel")

    __table_args__ = (
        Index('idx_turno_codigo', 'codigo'),
        Index('idx_turno_depto', 'departamento_codigo'),
    )

class Equipo(Base):
    """Equipos y herramientas de seguridad"""
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50))  # RADIO, LINTERNA, ARMA, CHALECO, etc.
    marca = Column(String(50))
    modelo = Column(String(50))
    serie = Column(String(100))

    # Estado y ubicación
    estado = Column(String(20), default='DISPONIBLE')  # DISPONIBLE, ASIGNADO, MANTENIMIENTO, DAÑADO, PERDIDO
    departamento_codigo = Column(String(10), ForeignKey('departamentos.codigo'))
    empleado_asignado = Column(String(6), ForeignKey('rpemplea.empleado'))

    # Información del equipo
    fecha_compra = Column(Date)
    valor_compra = Column(Numeric(10, 2))
    proveedor = Column(String(100))
    garantia_hasta = Column(Date)

    # Mantenimiento
    requiere_mantenimiento = Column(Boolean, default=False)
    frecuencia_mantenimiento = Column(Integer)  # días
    ultimo_mantenimiento = Column(Date)
    proximo_mantenimiento = Column(Date)

    # Características
    peso = Column(Numeric(8, 2))
    dimensiones = Column(String(50))
    color = Column(String(30))
    material = Column(String(50))

    # Control
    observaciones = Column(Text)
    foto = Column(Text)  # Path o base64 de la foto
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(20))

    # Relaciones
    departamento_rel = relationship("Departamento")
    empleado_rel = relationship("Empleado")
    historial_equipos = relationship("HistorialEquipo", back_populates="equipo_rel", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_equipo_codigo', 'codigo'),
        Index('idx_equipo_tipo', 'tipo'),
        Index('idx_equipo_estado', 'estado'),
        Index('idx_equipo_depto', 'departamento_codigo'),
    )

class HistorialEquipo(Base):
    """Historial de movimientos de equipos"""
    __tablename__ = "historial_equipos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipo_id = Column(Integer, ForeignKey('equipos.id'), nullable=False)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    departamento_codigo = Column(String(10), ForeignKey('departamentos.codigo'))

    tipo_movimiento = Column(String(20), nullable=False)  # ASIGNACION, DEVOLUCION, MANTENIMIENTO, BAJA
    fecha_movimiento = Column(DateTime, default=datetime.utcnow)
    estado_anterior = Column(String(20))
    estado_nuevo = Column(String(20))

    motivo = Column(String(200))
    observaciones = Column(Text)
    responsable = Column(String(20))  # Usuario que realizó el movimiento
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    equipo_rel = relationship("Equipo", back_populates="historial_equipos")
    empleado_rel = relationship("Empleado")
    departamento_rel = relationship("Departamento")

    __table_args__ = (
        Index('idx_historial_equipo', 'equipo_id'),
        Index('idx_historial_fecha', 'fecha_movimiento'),
    )

class Cargo(Base):
    """Catálogo de cargos"""
    __tablename__ = "cargos"

    codigo = Column(String(3), primary_key=True)
    nombre = Column(String(100), nullable=False)
    sueldo_base = Column(Numeric(10, 2))
    nivel = Column(Integer)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Control(Base):
    """Parámetros del sistema - Tabla RPCONTRL"""
    __tablename__ = "rpcontrl"

    parametro = Column(String(50), primary_key=True)
    valor = Column(String(200))
    descripcion = Column(String(200))
    tipo = Column(String(10))  # STRING, NUMBER, DATE, BOOLEAN
    categoria = Column(String(50))
    activo = Column(Boolean, default=True)
    editable = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(20))

class Vacacion(Base):
    """Control de vacaciones"""
    __tablename__ = "vacaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    periodo = Column(Integer)  # Año
    dias_derecho = Column(Integer, default=15)
    dias_tomados = Column(Integer, default=0)
    dias_pagados = Column(Integer, default=0)
    dias_saldo = Column(Integer, default=15)
    fecha_desde = Column(Date)
    fecha_hasta = Column(Date)
    fecha_reintegro = Column(Date)
    valor_pagado = Column(Numeric(10, 2))
    estado = Column(String(10))  # PENDIENTE, APROBADA, RECHAZADA, PAGADA
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))

    # Relación
    empleado_rel = relationship("Empleado", back_populates="vacaciones")

    __table_args__ = (
        Index('idx_vacacion_empleado_periodo', 'empleado', 'periodo'),
    )

class Prestamo(Base):
    """Control de préstamos y anticipos"""
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    fecha = Column(Date, nullable=False)
    tipo = Column(String(20))  # ANTICIPO, PRESTAMO, EMERGENCIA
    monto = Column(Numeric(10, 2), nullable=False)
    cuotas = Column(Integer, default=1)
    valor_cuota = Column(Numeric(10, 2))
    cuotas_pagadas = Column(Integer, default=0)
    saldo = Column(Numeric(10, 2))
    interes = Column(Numeric(5, 2), default=0.00)
    estado = Column(String(10))  # ACTIVO, PAGADO, CANCELADO
    motivo = Column(Text)
    aprobado_por = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))

    # Relación
    empleado_rel = relationship("Empleado", back_populates="prestamos")

    __table_args__ = (
        Index('idx_prestamo_empleado_estado', 'empleado', 'estado'),
    )

class Dotacion(Base):
    """Control de dotación y equipos"""
    __tablename__ = "dotaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    fecha_entrega = Column(Date, nullable=False)
    tipo = Column(String(50))  # UNIFORME, EQUIPO, HERRAMIENTA
    descripcion = Column(String(200))
    cantidad = Column(Integer, default=1)
    talla = Column(String(10))
    valor_unitario = Column(Numeric(10, 2))
    valor_total = Column(Numeric(10, 2))
    estado = Column(String(20))  # ENTREGADO, DEVUELTO, PERDIDO, DAÑADO
    fecha_devolucion = Column(Date)
    descuento_aplicado = Column(Boolean, default=False)
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))

    # Relación
    empleado_rel = relationship("Empleado", back_populates="dotaciones")

    __table_args__ = (
        Index('idx_dotacion_empleado_fecha', 'empleado', 'fecha_entrega'),
    )

class RolPago(Base):
    """Roles de pago procesados"""
    __tablename__ = "roles_pago"

    id = Column(Integer, primary_key=True, autoincrement=True)
    periodo = Column(String(7), nullable=False)  # YYYY-MM
    fecha_desde = Column(Date, nullable=False)
    fecha_hasta = Column(Date, nullable=False)
    tipo_nomina = Column(Integer)  # 1:Semanal, 2:Quincenal, 3:Mensual
    empleado = Column(String(6))

    # Datos del período
    dias_trabajados = Column(Integer)
    horas_normales = Column(Numeric(5, 2))
    horas_extras_25 = Column(Numeric(5, 2))
    horas_extras_50 = Column(Numeric(5, 2))
    horas_extras_100 = Column(Numeric(5, 2))

    # Ingresos
    sueldo_basico = Column(Numeric(10, 2))
    horas_extras = Column(Numeric(10, 2))
    comisiones = Column(Numeric(10, 2))
    bonos = Column(Numeric(10, 2))
    otros_ingresos = Column(Numeric(10, 2))
    total_ingresos = Column(Numeric(10, 2))

    # Descuentos
    aporte_iess = Column(Numeric(10, 2))
    impuesto_renta = Column(Numeric(10, 2))
    prestamos = Column(Numeric(10, 2))
    anticipos = Column(Numeric(10, 2))
    otros_descuentos = Column(Numeric(10, 2))
    total_descuentos = Column(Numeric(10, 2))

    # Totales
    neto_pagar = Column(Numeric(10, 2))

    # Estado y control
    estado = Column(String(10))  # BORRADOR, PROCESADO, PAGADO, ANULADO
    fecha_proceso = Column(DateTime)
    fecha_pago = Column(Date)
    procesado_por = Column(String(20))
    observaciones = Column(Text)

    __table_args__ = (
        Index('idx_rol_periodo_empleado', 'periodo', 'empleado'),
        Index('idx_rol_estado', 'estado'),
    )

class DecimoTercer(Base):
    """Control de décimo tercer sueldo"""
    __tablename__ = "decimo_tercer"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    periodo = Column(Integer)  # Año
    mes_desde = Column(Integer, default=12)  # Diciembre año anterior
    mes_hasta = Column(Integer, default=11)  # Noviembre año actual
    total_ingresos = Column(Numeric(10, 2))
    valor_decimo = Column(Numeric(10, 2))
    valor_pagado = Column(Numeric(10, 2), default=0.00)
    saldo_pendiente = Column(Numeric(10, 2))
    fecha_calculo = Column(Date)
    fecha_pago = Column(Date)
    estado = Column(String(10))  # CALCULADO, PAGADO, ANULADO
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))

    __table_args__ = (
        Index('idx_decimo13_empleado_periodo', 'empleado', 'periodo'),
    )

class DecimoCuarto(Base):
    """Control de décimo cuarto sueldo"""
    __tablename__ = "decimo_cuarto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    periodo = Column(Integer)  # Año
    valor_sbu = Column(Numeric(10, 2))  # SBU del año
    dias_trabajados = Column(Integer)
    valor_proporcional = Column(Numeric(10, 2))
    valor_pagado = Column(Numeric(10, 2), default=0.00)
    saldo_pendiente = Column(Numeric(10, 2))
    fecha_calculo = Column(Date)
    fecha_pago = Column(Date)
    estado = Column(String(10))  # CALCULADO, PAGADO, ANULADO
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))

    __table_args__ = (
        Index('idx_decimo14_empleado_periodo', 'empleado', 'periodo'),
    )

class FondosReserva(Base):
    """Control de fondos de reserva"""
    __tablename__ = "fondos_reserva"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    periodo = Column(String(7))  # YYYY-MM
    total_ingresos = Column(Numeric(10, 2))
    porcentaje = Column(Numeric(5, 4), default=0.0833)  # 8.33%
    valor_fondo = Column(Numeric(10, 2))
    acumulado = Column(Numeric(10, 2))
    valor_pagado = Column(Numeric(10, 2), default=0.00)
    fecha_calculo = Column(Date)
    fecha_pago = Column(Date)
    estado = Column(String(10))  # CALCULADO, PAGADO
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_fondos_empleado_periodo', 'empleado', 'periodo'),
    )

class Liquidacion(Base):
    """Control de liquidaciones"""
    __tablename__ = "liquidaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado = Column(String(6), ForeignKey('rpemplea.empleado'))
    fecha_salida = Column(Date, nullable=False)
    motivo_salida = Column(String(50))  # RENUNCIA, DESPIDO, JUBILACION

    # Valores a liquidar
    sueldo_pendiente = Column(Numeric(10, 2))
    vacaciones_pendientes = Column(Numeric(10, 2))
    decimo_tercer = Column(Numeric(10, 2))
    decimo_cuarto = Column(Numeric(10, 2))
    fondos_reserva = Column(Numeric(10, 2))
    indemnizacion = Column(Numeric(10, 2))
    bonificacion = Column(Numeric(10, 2))

    # Descuentos
    prestamos_pendientes = Column(Numeric(10, 2))
    anticipos_pendientes = Column(Numeric(10, 2))
    otros_descuentos = Column(Numeric(10, 2))

    # Totales
    total_ingresos = Column(Numeric(10, 2))
    total_descuentos = Column(Numeric(10, 2))
    neto_liquidacion = Column(Numeric(10, 2))

    # Control
    estado = Column(String(10))  # BORRADOR, APROBADA, PAGADA
    fecha_calculo = Column(Date)
    fecha_pago = Column(Date)
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))

    __table_args__ = (
        Index('idx_liquidacion_empleado_fecha', 'empleado', 'fecha_salida'),
    )

class AuditoriaAcceso(Base):
    """Auditoría de accesos al sistema"""
    __tablename__ = "auditoria_acceso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario = Column(String(20), nullable=False)
    fecha_acceso = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(15))
    modulo = Column(String(50))
    accion = Column(String(50))  # LOGIN, LOGOUT, CREATE, UPDATE, DELETE
    tabla_afectada = Column(String(50))
    registro_id = Column(String(50))
    detalles = Column(Text)
    exitoso = Column(Boolean, default=True)

    __table_args__ = (
        Index('idx_acceso_usuario_fecha', 'usuario', 'fecha_acceso'),
        Index('idx_acceso_modulo_accion', 'modulo', 'accion'),
    )

class Usuario(Base):
    """Sistema de usuarios para autenticación"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    nombres = Column(String(100))
    apellidos = Column(String(100))

    # Control de acceso
    activo = Column(Boolean, default=True)
    ultimo_acceso = Column(DateTime)
    intentos_fallidos = Column(Integer, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con rol
    rol_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    rol = relationship("Rol", back_populates="usuarios")

    # Relación con empleado (opcional)
    empleado_codigo = Column(String(6), ForeignKey('rpemplea.empleado'))
    empleado_rel = relationship("Empleado")

    __table_args__ = (
        Index('idx_usuario_username', 'username'),
        Index('idx_usuario_activo', 'activo'),
    )

    def set_password(self, password):
        """Establecer contraseña encriptada"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        """Verificar contraseña"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    @property
    def nombre_completo(self):
        if self.nombres and self.apellidos:
            return f"{self.nombres} {self.apellidos}"
        return self.username

class Rol(Base):
    """Roles de usuario para control de permisos"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200))
    permisos = Column(Text)  # JSON con permisos por módulo
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    usuarios = relationship("Usuario", back_populates="rol")

    def get_permisos(self):
        """Obtener permisos como diccionario"""
        if self.permisos:
            try:
                return json.loads(self.permisos)
            except:
                return {}
        return {}

    def set_permisos(self, permisos_dict):
        """Establecer permisos desde diccionario"""
        self.permisos = json.dumps(permisos_dict)

    def tiene_permiso(self, modulo, accion="read"):
        """Verificar si el rol tiene permiso específico"""
        permisos = self.get_permisos()
        modulo_permisos = permisos.get(modulo, {})
        return modulo_permisos.get(accion, False)

class LogAuditoria(Base):
    """Log de auditoría para seguimiento de acciones"""
    __tablename__ = "log_auditoria"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario = Column(String(50), nullable=False)
    accion = Column(String(100), nullable=False)
    modulo = Column(String(50))
    tabla = Column(String(50))
    registro_id = Column(String(50))
    valores_antes = Column(Text)  # JSON
    valores_despues = Column(Text)  # JSON
    ip_address = Column(String(15))
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    exitosa = Column(Boolean, default=True)
    detalles = Column(Text)

    __table_args__ = (
        Index('idx_auditoria_usuario_fecha', 'usuario', 'fecha'),
        Index('idx_auditoria_modulo_tabla', 'modulo', 'tabla'),
        Index('idx_auditoria_fecha', 'fecha'),
    )

class SesionUsuario(Base):
    """Control de sesiones activas"""
    __tablename__ = "sesiones_usuario"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    token_sesion = Column(String(255), unique=True, nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime, nullable=False)
    ip_address = Column(String(15))
    user_agent = Column(String(200))
    activa = Column(Boolean, default=True)

    # Relación con usuario
    usuario = relationship("Usuario")

    __table_args__ = (
        Index('idx_sesion_token', 'token_sesion'),
        Index('idx_sesion_usuario_activa', 'usuario_id', 'activa'),
    )