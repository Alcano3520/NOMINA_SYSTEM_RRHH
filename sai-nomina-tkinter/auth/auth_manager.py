#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AuthManager - Sistema SAI
Gestión completa de autenticación de usuarios
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import hashlib
import logging

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_session
from database.models import Usuario, Rol, LogAuditoria, SesionUsuario

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Excepción personalizada para errores de autenticación"""
    pass

class AuthManager:
    """Gestor principal de autenticación"""

    def __init__(self):
        self.session = get_session()
        self.current_user = None
        self.current_session = None

    def authenticate(self, username, password):
        """
        Autenticar usuario con credenciales

        Args:
            username (str): Nombre de usuario
            password (str): Contraseña

        Returns:
            Usuario: Usuario autenticado o None si falló

        Raises:
            AuthenticationError: Si hay problemas de autenticación
        """
        try:
            # Buscar usuario activo
            usuario = self.session.query(Usuario).filter_by(
                username=username,
                activo=True
            ).first()

            if not usuario:
                logger.warning(f"Intento de login con usuario inexistente: {username}")
                raise AuthenticationError("Usuario o contraseña incorrectos")

            # Verificar si está bloqueado por intentos fallidos
            if usuario.intentos_fallidos >= 3:
                logger.warning(f"Usuario bloqueado por intentos fallidos: {username}")
                raise AuthenticationError("Usuario bloqueado por múltiples intentos fallidos")

            # Verificar contraseña
            if not usuario.check_password(password):
                # Incrementar intentos fallidos
                usuario.intentos_fallidos += 1
                self.session.commit()

                logger.warning(f"Contraseña incorrecta para usuario: {username}")
                raise AuthenticationError("Usuario o contraseña incorrectos")

            # Login exitoso - resetear intentos fallidos
            usuario.intentos_fallidos = 0
            usuario.ultimo_acceso = datetime.utcnow()
            self.session.commit()

            # Crear sesión
            session_token = self.create_session(usuario)

            # Log de auditoría
            self.log_action(
                usuario=username,
                accion="LOGIN_SUCCESS",
                modulo="AUTH",
                detalles="Login exitoso"
            )

            self.current_user = usuario
            logger.info(f"Usuario autenticado exitosamente: {username}")
            return usuario

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            raise AuthenticationError("Error interno del sistema")

    def create_session(self, usuario):
        """Crear sesión de usuario"""
        try:
            # Cerrar sesiones anteriores
            self.session.query(SesionUsuario).filter_by(
                usuario_id=usuario.id,
                activa=True
            ).update({'activa': False})

            # Crear nueva sesión
            token = str(uuid.uuid4())
            expiracion = datetime.utcnow() + timedelta(hours=8)  # 8 horas de sesión

            sesion = SesionUsuario(
                usuario_id=usuario.id,
                token_sesion=token,
                fecha_expiracion=expiracion,
                ip_address="127.0.0.1",  # Para aplicación desktop
                user_agent="SAI Desktop App",
                activa=True
            )

            self.session.add(sesion)
            self.session.commit()

            self.current_session = sesion
            return token

        except Exception as e:
            logger.error(f"Error creando sesión: {str(e)}")
            return None

    def logout(self):
        """Cerrar sesión del usuario actual"""
        try:
            if self.current_user and self.current_session:
                # Cerrar sesión
                self.current_session.activa = False
                self.session.commit()

                # Log de auditoría
                self.log_action(
                    usuario=self.current_user.username,
                    accion="LOGOUT",
                    modulo="AUTH",
                    detalles="Logout exitoso"
                )

                logger.info(f"Usuario deslogueado: {self.current_user.username}")

            self.current_user = None
            self.current_session = None
            return True

        except Exception as e:
            logger.error(f"Error en logout: {str(e)}")
            return False

    def is_authenticated(self):
        """Verificar si hay usuario autenticado"""
        return self.current_user is not None

    def get_current_user(self):
        """Obtener usuario actual"""
        return self.current_user

    def has_permission(self, modulo, accion="read"):
        """Verificar permisos del usuario actual"""
        if not self.current_user:
            return False

        try:
            rol = self.current_user.rol
            return rol.tiene_permiso(modulo, accion)
        except:
            return False

    def require_permission(self, modulo, accion="read"):
        """Decorador para requerir permisos"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.has_permission(modulo, accion):
                    raise AuthenticationError(f"Sin permisos para {modulo}:{accion}")
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def create_user(self, username, password, email, nombres, apellidos, rol_id):
        """Crear nuevo usuario"""
        try:
            # Verificar que no existe
            if self.session.query(Usuario).filter_by(username=username).first():
                raise AuthenticationError("El usuario ya existe")

            # Crear usuario
            usuario = Usuario(
                username=username,
                email=email,
                nombres=nombres,
                apellidos=apellidos,
                rol_id=rol_id,
                activo=True
            )
            usuario.set_password(password)

            self.session.add(usuario)
            self.session.commit()

            # Log de auditoría
            self.log_action(
                usuario=self.current_user.username if self.current_user else "SYSTEM",
                accion="CREATE_USER",
                modulo="AUTH",
                registro_id=str(usuario.id),
                detalles=f"Usuario creado: {username}"
            )

            logger.info(f"Usuario creado: {username}")
            return usuario

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error creando usuario: {str(e)}")
            raise AuthenticationError("Error creando usuario")

    def reset_password(self, username, new_password):
        """Resetear contraseña de usuario"""
        try:
            usuario = self.session.query(Usuario).filter_by(username=username).first()
            if not usuario:
                raise AuthenticationError("Usuario no encontrado")

            usuario.set_password(new_password)
            usuario.intentos_fallidos = 0  # Resetear intentos fallidos
            self.session.commit()

            # Log de auditoría
            self.log_action(
                usuario=self.current_user.username if self.current_user else "SYSTEM",
                accion="RESET_PASSWORD",
                modulo="AUTH",
                registro_id=str(usuario.id),
                detalles=f"Password reseteado para: {username}"
            )

            logger.info(f"Password reseteado para usuario: {username}")
            return True

        except Exception as e:
            logger.error(f"Error reseteando password: {str(e)}")
            return False

    def unlock_user(self, username):
        """Desbloquear usuario"""
        try:
            usuario = self.session.query(Usuario).filter_by(username=username).first()
            if not usuario:
                raise AuthenticationError("Usuario no encontrado")

            usuario.intentos_fallidos = 0
            self.session.commit()

            logger.info(f"Usuario desbloqueado: {username}")
            return True

        except Exception as e:
            logger.error(f"Error desbloqueando usuario: {str(e)}")
            return False

    def log_action(self, usuario, accion, modulo=None, tabla=None, registro_id=None,
                   valores_antes=None, valores_despues=None, detalles=None):
        """Registrar acción en auditoría"""
        try:
            log = LogAuditoria(
                usuario=usuario,
                accion=accion,
                modulo=modulo,
                tabla=tabla,
                registro_id=registro_id,
                valores_antes=str(valores_antes) if valores_antes else None,
                valores_despues=str(valores_despues) if valores_despues else None,
                detalles=detalles,
                exitosa=True
            )

            self.session.add(log)
            self.session.commit()

        except Exception as e:
            logger.error(f"Error registrando auditoría: {str(e)}")

    def get_default_permissions(self):
        """Obtener permisos por defecto para roles"""
        return {
            "ADMINISTRADOR": {
                "empleados": {"read": True, "write": True, "delete": True, "admin": True},
                "nomina": {"read": True, "write": True, "delete": True, "process": True},
                "decimos": {"read": True, "write": True, "delete": True, "calculate": True},
                "vacaciones": {"read": True, "write": True, "delete": True, "approve": True},
                "liquidaciones": {"read": True, "write": True, "delete": True, "calculate": True},
                "prestamos": {"read": True, "write": True, "delete": True, "approve": True},
                "reportes": {"read": True, "write": True, "export": True, "all": True},
                "configuracion": {"read": True, "write": True, "delete": True, "admin": True},
                "usuarios": {"read": True, "write": True, "delete": True, "admin": True}
            },
            "RRHH": {
                "empleados": {"read": True, "write": True, "delete": False, "admin": False},
                "nomina": {"read": True, "write": True, "delete": False, "process": True},
                "decimos": {"read": True, "write": True, "delete": False, "calculate": True},
                "vacaciones": {"read": True, "write": True, "delete": False, "approve": True},
                "liquidaciones": {"read": True, "write": True, "delete": False, "calculate": True},
                "prestamos": {"read": True, "write": True, "delete": False, "approve": False},
                "reportes": {"read": True, "write": False, "export": True, "all": False},
                "configuracion": {"read": True, "write": False, "delete": False, "admin": False}
            },
            "EMPLEADO": {
                "empleados": {"read": True, "write": False, "delete": False, "admin": False},
                "nomina": {"read": True, "write": False, "delete": False, "process": False},
                "vacaciones": {"read": True, "write": True, "delete": False, "approve": False},
                "reportes": {"read": True, "write": False, "export": False, "all": False}
            },
            "SOLO_LECTURA": {
                "empleados": {"read": True, "write": False, "delete": False, "admin": False},
                "nomina": {"read": True, "write": False, "delete": False, "process": False},
                "decimos": {"read": True, "write": False, "delete": False, "calculate": False},
                "vacaciones": {"read": True, "write": False, "delete": False, "approve": False},
                "reportes": {"read": True, "write": False, "export": False, "all": False}
            }
        }

    def initialize_system(self):
        """Inicializar sistema con datos por defecto"""
        try:
            # Crear roles por defecto si no existen
            permisos_default = self.get_default_permissions()

            for rol_nombre, permisos in permisos_default.items():
                rol_existente = self.session.query(Rol).filter_by(nombre=rol_nombre).first()

                if not rol_existente:
                    rol = Rol(
                        nombre=rol_nombre,
                        descripcion=f"Rol {rol_nombre}",
                        activo=True
                    )
                    rol.set_permisos(permisos)
                    self.session.add(rol)

            # Commit roles before creating admin user
            self.session.commit()

            # Crear usuario administrador por defecto si no existe
            admin_user = self.session.query(Usuario).filter_by(username="admin").first()

            if not admin_user:
                rol_admin = self.session.query(Rol).filter_by(nombre="ADMINISTRADOR").first()

                if not rol_admin:
                    raise ValueError("No se pudo crear el rol ADMINISTRADOR")

                admin = Usuario(
                    username="admin",
                    email="admin@empresa.com",
                    nombres="Administrador",
                    apellidos="Sistema",
                    rol_id=rol_admin.id,
                    activo=True
                )
                admin.set_password("admin123")  # Contraseña por defecto
                self.session.add(admin)

            self.session.commit()
            logger.info("Sistema de autenticación inicializado correctamente")

        except Exception as e:
            logger.error(f"Error inicializando sistema: {str(e)}")
            self.session.rollback()
            raise

# Instancia global del administrador de autenticación
auth_manager = AuthManager()