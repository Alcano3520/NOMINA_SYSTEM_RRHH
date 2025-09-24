#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SessionManager - Sistema SAI
Gestión de sesiones de usuario y timeout automático
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
import logging

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_session
from database.models import SesionUsuario, Usuario

logger = logging.getLogger(__name__)

class SessionManager:
    """Gestor de sesiones de usuario"""

    def __init__(self, session_timeout_minutes=480):  # 8 horas por defecto
        self.session = get_session()
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.cleanup_thread = None
        self.running = False

        # Iniciar limpieza automática
        self.start_cleanup_thread()

    def start_cleanup_thread(self):
        """Iniciar hilo de limpieza de sesiones expiradas"""
        if not self.cleanup_thread or not self.cleanup_thread.is_alive():
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions)
            self.cleanup_thread.daemon = True
            self.cleanup_thread.start()
            logger.info("Hilo de limpieza de sesiones iniciado")

    def stop_cleanup_thread(self):
        """Detener hilo de limpieza"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)

    def _cleanup_expired_sessions(self):
        """Limpiar sesiones expiradas (ejecuta en hilo separado)"""
        while self.running:
            try:
                now = datetime.utcnow()

                # Marcar como inactivas las sesiones expiradas
                expired_count = self.session.query(SesionUsuario).filter(
                    SesionUsuario.fecha_expiracion < now,
                    SesionUsuario.activa == True
                ).update({'activa': False})

                if expired_count > 0:
                    self.session.commit()
                    logger.info(f"Sesiones expiradas limpiadas: {expired_count}")

                # Esperar 5 minutos antes de la próxima limpieza
                for _ in range(300):  # 5 minutos = 300 segundos
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error en limpieza de sesiones: {str(e)}")
                time.sleep(60)  # Esperar 1 minuto en caso de error

    def is_session_valid(self, token_sesion):
        """Verificar si una sesión es válida"""
        try:
            now = datetime.utcnow()

            sesion = self.session.query(SesionUsuario).filter_by(
                token_sesion=token_sesion,
                activa=True
            ).first()

            if not sesion:
                return False

            # Verificar si no ha expirado
            if sesion.fecha_expiracion < now:
                # Marcar como inactiva
                sesion.activa = False
                self.session.commit()
                return False

            return True

        except Exception as e:
            logger.error(f"Error verificando sesión: {str(e)}")
            return False

    def extend_session(self, token_sesion, extension_minutes=None):
        """Extender tiempo de sesión"""
        try:
            if extension_minutes is None:
                extension_minutes = self.session_timeout.total_seconds() / 60

            sesion = self.session.query(SesionUsuario).filter_by(
                token_sesion=token_sesion,
                activa=True
            ).first()

            if sesion:
                # Extender fecha de expiración
                sesion.fecha_expiracion = datetime.utcnow() + timedelta(minutes=extension_minutes)
                self.session.commit()
                return True

            return False

        except Exception as e:
            logger.error(f"Error extendiendo sesión: {str(e)}")
            return False

    def get_session_info(self, token_sesion):
        """Obtener información de sesión"""
        try:
            sesion = self.session.query(SesionUsuario).filter_by(
                token_sesion=token_sesion,
                activa=True
            ).first()

            if not sesion:
                return None

            # Calcular tiempo restante
            now = datetime.utcnow()
            tiempo_restante = sesion.fecha_expiracion - now

            return {
                'usuario_id': sesion.usuario_id,
                'usuario': sesion.usuario.username if sesion.usuario else None,
                'fecha_inicio': sesion.fecha_inicio,
                'fecha_expiracion': sesion.fecha_expiracion,
                'tiempo_restante_segundos': int(tiempo_restante.total_seconds()),
                'tiempo_restante_minutos': int(tiempo_restante.total_seconds() / 60),
                'ip_address': sesion.ip_address,
                'activa': sesion.activa
            }

        except Exception as e:
            logger.error(f"Error obteniendo info de sesión: {str(e)}")
            return None

    def invalidate_session(self, token_sesion):
        """Invalidar sesión específica"""
        try:
            result = self.session.query(SesionUsuario).filter_by(
                token_sesion=token_sesion
            ).update({'activa': False})

            self.session.commit()
            return result > 0

        except Exception as e:
            logger.error(f"Error invalidando sesión: {str(e)}")
            return False

    def invalidate_user_sessions(self, usuario_id):
        """Invalidar todas las sesiones de un usuario"""
        try:
            result = self.session.query(SesionUsuario).filter_by(
                usuario_id=usuario_id
            ).update({'activa': False})

            self.session.commit()
            logger.info(f"Sesiones invalidadas para usuario {usuario_id}: {result}")
            return result

        except Exception as e:
            logger.error(f"Error invalidando sesiones de usuario: {str(e)}")
            return 0

    def get_active_sessions(self):
        """Obtener todas las sesiones activas"""
        try:
            now = datetime.utcnow()

            sesiones = self.session.query(SesionUsuario).join(Usuario).filter(
                SesionUsuario.activa == True,
                SesionUsuario.fecha_expiracion > now
            ).all()

            result = []
            for sesion in sesiones:
                tiempo_restante = sesion.fecha_expiracion - now
                result.append({
                    'id': sesion.id,
                    'usuario': sesion.usuario.username,
                    'usuario_completo': sesion.usuario.nombre_completo,
                    'fecha_inicio': sesion.fecha_inicio,
                    'fecha_expiracion': sesion.fecha_expiracion,
                    'tiempo_restante_minutos': int(tiempo_restante.total_seconds() / 60),
                    'ip_address': sesion.ip_address,
                    'user_agent': sesion.user_agent
                })

            return result

        except Exception as e:
            logger.error(f"Error obteniendo sesiones activas: {str(e)}")
            return []

    def get_user_session_history(self, usuario_id, limit=50):
        """Obtener historial de sesiones de un usuario"""
        try:
            sesiones = self.session.query(SesionUsuario).filter_by(
                usuario_id=usuario_id
            ).order_by(SesionUsuario.fecha_inicio.desc()).limit(limit).all()

            result = []
            for sesion in sesiones:
                # Calcular duración de la sesión
                if sesion.activa:
                    duracion = datetime.utcnow() - sesion.fecha_inicio
                else:
                    # Para sesiones cerradas, usar la fecha de expiración o fecha actual
                    fin_sesion = min(sesion.fecha_expiracion, datetime.utcnow())
                    duracion = fin_sesion - sesion.fecha_inicio

                result.append({
                    'fecha_inicio': sesion.fecha_inicio,
                    'fecha_expiracion': sesion.fecha_expiracion,
                    'duracion_minutos': int(duracion.total_seconds() / 60),
                    'ip_address': sesion.ip_address,
                    'activa': sesion.activa,
                    'user_agent': sesion.user_agent
                })

            return result

        except Exception as e:
            logger.error(f"Error obteniendo historial de sesiones: {str(e)}")
            return []

    def force_logout_user(self, usuario_id, reason="Forzado por administrador"):
        """Forzar logout de un usuario"""
        try:
            # Invalidar todas las sesiones del usuario
            count = self.invalidate_user_sessions(usuario_id)

            if count > 0:
                # Log de auditoría
                usuario = self.session.query(Usuario).get(usuario_id)
                if usuario:
                    from auth.auth_manager import auth_manager
                    auth_manager.log_action(
                        usuario=usuario.username,
                        accion="FORCE_LOGOUT",
                        modulo="AUTH",
                        detalles=reason
                    )

                logger.info(f"Logout forzado para usuario {usuario_id}: {reason}")

            return count > 0

        except Exception as e:
            logger.error(f"Error en logout forzado: {str(e)}")
            return False

    def get_session_statistics(self):
        """Obtener estadísticas de sesiones"""
        try:
            now = datetime.utcnow()
            today = now.date()

            stats = {
                'sesiones_activas': self.session.query(SesionUsuario).filter(
                    SesionUsuario.activa == True,
                    SesionUsuario.fecha_expiracion > now
                ).count(),

                'sesiones_hoy': self.session.query(SesionUsuario).filter(
                    SesionUsuario.fecha_inicio >= today
                ).count(),

                'usuarios_unicos_hoy': self.session.query(SesionUsuario.usuario_id).filter(
                    SesionUsuario.fecha_inicio >= today
                ).distinct().count(),

                'sesiones_expiradas_hoy': self.session.query(SesionUsuario).filter(
                    SesionUsuario.fecha_inicio >= today,
                    SesionUsuario.fecha_expiracion < now,
                    SesionUsuario.activa == False
                ).count()
            }

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}

    def cleanup_old_sessions(self, days_old=30):
        """Limpiar sesiones antiguas de la base de datos"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            # Eliminar sesiones antiguas
            deleted = self.session.query(SesionUsuario).filter(
                SesionUsuario.fecha_inicio < cutoff_date
            ).delete()

            self.session.commit()

            logger.info(f"Sesiones antiguas eliminadas: {deleted}")
            return deleted

        except Exception as e:
            logger.error(f"Error limpiando sesiones antiguas: {str(e)}")
            return 0

    def __del__(self):
        """Destructor - detener hilo de limpieza"""
        self.stop_cleanup_thread()

# Instancia global del gestor de sesiones
session_manager = SessionManager()