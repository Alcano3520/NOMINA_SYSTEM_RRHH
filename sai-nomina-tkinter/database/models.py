"""Modelos de base de datos con SQLAlchemy"""

from sqlalchemy import (
    Column, String, Integer, Float, Date, DateTime, Boolean,
    ForeignKey, Text, Numeric, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

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

class Departamento(Base):
    """Catálogo de departamentos"""
    __tablename__ = "departamentos"

    codigo = Column(String(3), primary_key=True)
    nombre = Column(String(100), nullable=False)
    responsable = Column(String(6))  # Código empleado
    centro_costo = Column(String(10))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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
        Index('idx_auditoria_usuario_fecha', 'usuario', 'fecha_acceso'),
        Index('idx_auditoria_modulo_accion', 'modulo', 'accion'),
    )