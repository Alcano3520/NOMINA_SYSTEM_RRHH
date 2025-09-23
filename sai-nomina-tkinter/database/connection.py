"""Conexión y sesión de base de datos"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
import logging

from config import Config

logger = logging.getLogger(__name__)

# Crear engine
engine = create_engine(
    Config.DATABASE_URL,
    echo=False,  # Cambiar a True para debug SQL
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    }
)

# Crear session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Session con scope para thread safety
Session = scoped_session(SessionLocal)

def get_session():
    """Obtener sesión de base de datos"""
    return Session()

def close_session():
    """Cerrar sesión"""
    Session.remove()

def get_engine():
    """Obtener engine de base de datos"""
    return engine

class DatabaseManager:
    """Manejador de base de datos"""

    def __init__(self):
        self.engine = engine
        self.session = Session

    def create_tables(self):
        """Crear todas las tablas"""
        from database.models import Base
        Base.metadata.create_all(bind=self.engine)
        logger.info("Tablas creadas correctamente")

    def drop_tables(self):
        """Eliminar todas las tablas"""
        from database.models import Base
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Tablas eliminadas correctamente")

    def backup_database(self, backup_path: str):
        """Crear respaldo de la base de datos"""
        import shutil
        try:
            shutil.copy2(Config.DATABASE_PATH, backup_path)
            logger.info(f"Respaldo creado en: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error al crear respaldo: {e}")
            return False

    def restore_database(self, backup_path: str):
        """Restaurar base de datos desde respaldo"""
        import shutil
        try:
            # Cerrar conexiones
            self.session.remove()
            self.engine.dispose()

            # Restaurar archivo
            shutil.copy2(backup_path, Config.DATABASE_PATH)

            # Recrear engine
            global engine
            engine = create_engine(
                Config.DATABASE_URL,
                echo=False,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                }
            )

            self.engine = engine
            logger.info(f"Base de datos restaurada desde: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error al restaurar: {e}")
            return False

    def execute_sql(self, sql: str, params: dict = None):
        """Ejecutar SQL personalizado"""
        try:
            session = self.session()
            if params:
                result = session.execute(sql, params)
            else:
                result = session.execute(sql)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Error ejecutando SQL: {e}")
            raise
        finally:
            session.close()

    def get_table_count(self, table_name: str) -> int:
        """Obtener conteo de registros de una tabla"""
        try:
            session = self.session()
            result = session.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = result.scalar()
            return count
        except Exception as e:
            logger.error(f"Error obteniendo conteo de {table_name}: {e}")
            return 0
        finally:
            session.close()

    def get_database_info(self) -> dict:
        """Obtener información de la base de datos"""
        try:
            from database.models import (
                Empleado, Departamento, Cargo, RolPago,
                Vacacion, Prestamo, Dotacion
            )

            session = self.session()

            info = {
                'empleados_activos': session.query(Empleado).filter(
                    Empleado.activo == True
                ).count(),
                'empleados_total': session.query(Empleado).count(),
                'departamentos': session.query(Departamento).count(),
                'cargos': session.query(Cargo).count(),
                'roles_procesados': session.query(RolPago).count(),
                'vacaciones_pendientes': session.query(Vacacion).filter(
                    Vacacion.estado == 'PENDIENTE'
                ).count(),
                'prestamos_activos': session.query(Prestamo).filter(
                    Prestamo.estado == 'ACTIVO'
                ).count(),
                'dotaciones': session.query(Dotacion).count()
            }

            return info
        except Exception as e:
            logger.error(f"Error obteniendo info de BD: {e}")
            return {}
        finally:
            session.close()