#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PermissionManager - Sistema SGN
Control granular de permisos por usuario y módulo
"""

import sys
from pathlib import Path
import json
import logging
from functools import wraps

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_session
from database.models import Usuario, Rol, LogAuditoria

logger = logging.getLogger(__name__)

class PermissionDeniedError(Exception):
    """Excepción para permisos denegados"""
    pass

class PermissionManager:
    """Gestor de permisos del sistema"""

    # Definición de módulos y acciones disponibles
    MODULES = {
        'empleados': {
            'name': 'Gestión de Empleados',
            'actions': {
                'read': 'Ver empleados',
                'write': 'Crear/Editar empleados',
                'delete': 'Eliminar empleados',
                'import': 'Importar empleados',
                'export': 'Exportar empleados',
                'admin': 'Administrar empleados'
            }
        },
        'nomina': {
            'name': 'Procesamiento de Nómina',
            'actions': {
                'read': 'Ver nóminas',
                'write': 'Crear/Editar nóminas',
                'delete': 'Eliminar nóminas',
                'process': 'Procesar nóminas',
                'approve': 'Aprobar nóminas',
                'close': 'Cerrar períodos'
            }
        },
        'decimos': {
            'name': 'Gestión de Décimos',
            'actions': {
                'read': 'Ver décimos',
                'write': 'Crear/Editar décimos',
                'delete': 'Eliminar décimos',
                'calculate': 'Calcular décimos',
                'approve': 'Aprobar décimos',
                'pay': 'Procesar pagos'
            }
        },
        'vacaciones': {
            'name': 'Control de Vacaciones',
            'actions': {
                'read': 'Ver vacaciones',
                'write': 'Crear/Editar solicitudes',
                'delete': 'Eliminar solicitudes',
                'approve': 'Aprobar vacaciones',
                'calculate': 'Calcular saldos'
            }
        },
        'liquidaciones': {
            'name': 'Liquidaciones',
            'actions': {
                'read': 'Ver liquidaciones',
                'write': 'Crear/Editar liquidaciones',
                'delete': 'Eliminar liquidaciones',
                'calculate': 'Calcular liquidaciones',
                'approve': 'Aprobar liquidaciones',
                'pay': 'Procesar pagos'
            }
        },
        'prestamos': {
            'name': 'Préstamos y Anticipos',
            'actions': {
                'read': 'Ver préstamos',
                'write': 'Crear/Editar préstamos',
                'delete': 'Eliminar préstamos',
                'approve': 'Aprobar préstamos',
                'calculate': 'Calcular intereses'
            }
        },
        'reportes': {
            'name': 'Reportes y Estadísticas',
            'actions': {
                'read': 'Ver reportes',
                'write': 'Crear reportes',
                'export': 'Exportar reportes',
                'sri': 'Reportes SRI',
                'iess': 'Reportes IESS',
                'all': 'Todos los reportes'
            }
        },
        'departamentos': {
            'name': 'Departamentos',
            'actions': {
                'read': 'Ver departamentos',
                'write': 'Crear/Editar departamentos',
                'delete': 'Eliminar departamentos',
                'assign': 'Asignar empleados'
            }
        },
        'configuracion': {
            'name': 'Configuración Sistema',
            'actions': {
                'read': 'Ver configuración',
                'write': 'Modificar configuración',
                'backup': 'Crear respaldos',
                'restore': 'Restaurar datos',
                'admin': 'Administración total'
            }
        },
        'usuarios': {
            'name': 'Gestión de Usuarios',
            'actions': {
                'read': 'Ver usuarios',
                'write': 'Crear/Editar usuarios',
                'delete': 'Eliminar usuarios',
                'permissions': 'Gestionar permisos',
                'roles': 'Gestionar roles',
                'admin': 'Administración usuarios'
            }
        },
        'auditoria': {
            'name': 'Auditoría Sistema',
            'actions': {
                'read': 'Ver logs auditoría',
                'export': 'Exportar logs',
                'admin': 'Administrar auditoría'
            }
        }
    }

    def __init__(self):
        self.session = get_session()

    def check_permission(self, user, module, action="read"):
        """
        Verificar permiso específico de usuario

        Args:
            user (Usuario): Usuario a verificar
            module (str): Módulo del sistema
            action (str): Acción solicitada

        Returns:
            bool: True si tiene permiso, False caso contrario
        """
        try:
            if not user or not user.activo:
                return False

            # Super admin siempre tiene acceso
            if user.rol.nombre == "ADMINISTRADOR":
                return True

            # Verificar permiso específico
            return user.rol.tiene_permiso(module, action)

        except Exception as e:
            logger.error(f"Error verificando permisos: {str(e)}")
            return False

    def require_permission(self, module, action="read"):
        """
        Decorador para requerir permisos en funciones

        Args:
            module (str): Módulo requerido
            action (str): Acción requerida

        Returns:
            decorator: Decorador de función
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Obtener usuario actual del auth_manager
                from auth.auth_manager import auth_manager

                current_user = auth_manager.get_current_user()
                if not current_user:
                    raise PermissionDeniedError("Usuario no autenticado")

                if not self.check_permission(current_user, module, action):
                    # Log intento de acceso denegado
                    self.log_permission_denied(current_user, module, action)
                    raise PermissionDeniedError(
                        f"Sin permisos para {self.MODULES.get(module, {}).get('name', module)}: "
                        f"{self.MODULES.get(module, {}).get('actions', {}).get(action, action)}"
                    )

                return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_user_permissions(self, user):
        """Obtener todos los permisos de un usuario"""
        try:
            if not user:
                return {}

            return user.rol.get_permisos()

        except Exception as e:
            logger.error(f"Error obteniendo permisos de usuario: {str(e)}")
            return {}

    def get_user_modules(self, user):
        """Obtener módulos accesibles para un usuario"""
        try:
            if not user:
                return []

            permisos = self.get_user_permissions(user)
            modules_accesibles = []

            for module, actions in permisos.items():
                if any(actions.values()):  # Si tiene algún permiso en el módulo
                    module_info = self.MODULES.get(module, {})
                    if module_info:
                        modules_accesibles.append({
                            'code': module,
                            'name': module_info['name'],
                            'permissions': actions
                        })

            return modules_accesibles

        except Exception as e:
            logger.error(f"Error obteniendo módulos de usuario: {str(e)}")
            return []

    def create_role(self, nombre, descripcion, permisos_dict):
        """Crear nuevo rol con permisos"""
        try:
            # Verificar que no existe
            if self.session.query(Rol).filter_by(nombre=nombre).first():
                raise ValueError(f"El rol {nombre} ya existe")

            # Crear rol
            rol = Rol(
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            rol.set_permisos(permisos_dict)

            self.session.add(rol)
            self.session.commit()

            logger.info(f"Rol creado: {nombre}")
            return rol

        except Exception as e:
            logger.error(f"Error creando rol: {str(e)}")
            self.session.rollback()
            raise

    def update_role_permissions(self, rol_id, permisos_dict):
        """Actualizar permisos de un rol"""
        try:
            rol = self.session.query(Rol).filter_by(id=rol_id).first()
            if not rol:
                raise ValueError("Rol no encontrado")

            old_permisos = rol.get_permisos()
            rol.set_permisos(permisos_dict)

            self.session.commit()

            # Log de auditoría
            self.log_permission_change(rol.nombre, old_permisos, permisos_dict)

            logger.info(f"Permisos actualizados para rol: {rol.nombre}")
            return True

        except Exception as e:
            logger.error(f"Error actualizando permisos: {str(e)}")
            self.session.rollback()
            raise

    def validate_permissions_dict(self, permisos_dict):
        """Validar estructura de permisos"""
        try:
            for module, actions in permisos_dict.items():
                if module not in self.MODULES:
                    raise ValueError(f"Módulo inválido: {module}")

                if not isinstance(actions, dict):
                    raise ValueError(f"Acciones deben ser diccionario para módulo: {module}")

                valid_actions = self.MODULES[module]['actions'].keys()
                for action in actions.keys():
                    if action not in valid_actions:
                        raise ValueError(f"Acción inválida '{action}' para módulo '{module}'")

            return True

        except Exception as e:
            logger.error(f"Error validando permisos: {str(e)}")
            raise

    def get_permission_matrix(self):
        """Obtener matriz completa de permisos disponibles"""
        return self.MODULES

    def get_role_permissions_readable(self, rol):
        """Obtener permisos de rol en formato legible"""
        try:
            permisos = rol.get_permisos()
            readable = {}

            for module, actions in permisos.items():
                module_info = self.MODULES.get(module, {})
                module_name = module_info.get('name', module)
                actions_info = module_info.get('actions', {})

                readable[module_name] = {}
                for action, granted in actions.items():
                    action_name = actions_info.get(action, action)
                    readable[module_name][action_name] = granted

            return readable

        except Exception as e:
            logger.error(f"Error obteniendo permisos legibles: {str(e)}")
            return {}

    def log_permission_denied(self, user, module, action):
        """Registrar intento de acceso denegado"""
        try:
            log = LogAuditoria(
                usuario=user.username,
                accion="PERMISSION_DENIED",
                modulo=module,
                detalles=f"Acceso denegado a {module}:{action}",
                exitosa=False
            )

            self.session.add(log)
            self.session.commit()

        except Exception as e:
            logger.error(f"Error registrando acceso denegado: {str(e)}")

    def log_permission_change(self, rol_nombre, old_permisos, new_permisos):
        """Registrar cambio de permisos"""
        try:
            from auth.auth_manager import auth_manager

            current_user = auth_manager.get_current_user()
            usuario = current_user.username if current_user else "SYSTEM"

            log = LogAuditoria(
                usuario=usuario,
                accion="UPDATE_PERMISSIONS",
                modulo="usuarios",
                tabla="roles",
                registro_id=rol_nombre,
                valores_antes=json.dumps(old_permisos),
                valores_despues=json.dumps(new_permisos),
                detalles=f"Permisos actualizados para rol: {rol_nombre}",
                exitosa=True
            )

            self.session.add(log)
            self.session.commit()

        except Exception as e:
            logger.error(f"Error registrando cambio de permisos: {str(e)}")

# Instancia global del gestor de permisos
permission_manager = PermissionManager()

# Decoradores de conveniencia
def require_admin(func):
    """Decorador que requiere rol administrador"""
    return permission_manager.require_permission("usuarios", "admin")(func)

def require_rrhh(func):
    """Decorador que requiere permisos de RRHH"""
    return permission_manager.require_permission("empleados", "write")(func)

def require_read(module):
    """Decorador que requiere permiso de lectura"""
    return permission_manager.require_permission(module, "read")

def require_write(module):
    """Decorador que requiere permiso de escritura"""
    return permission_manager.require_permission(module, "write")