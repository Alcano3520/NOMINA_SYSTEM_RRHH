"""Servicio de importación y exportación masiva para todos los módulos"""

import pandas as pd
from datetime import datetime, date
from decimal import Decimal
import logging
from typing import Dict, List, Callable, Optional
import time

from database.connection import get_session
from database.models import (
    Empleado, Historico, IngresoDescuento, Vacacion,
    Prestamo, Dotacion, Departamento, Cargo
)
from utils.validators import (
    validar_cedula, validar_email, validar_fecha,
    validar_numero_positivo
)

logger = logging.getLogger(__name__)

class ImportExportService:
    """Servicio para carga masiva de datos"""

    def __init__(self):
        self.session = get_session()

    def import_employees(self, filename: str,
                        progress_callback: Optional[Callable] = None) -> Dict:
        """Importar empleados desde Excel/CSV"""
        start_time = time.time()
        
        try:
            # Leer archivo
            if filename.endswith('.csv'):
                df = pd.read_csv(filename)
            else:
                df = pd.read_excel(filename)

            total_rows = len(df)
            imported = 0
            updated = 0
            errors = 0
            error_details = []

            # Validar columnas obligatorias
            required_columns = ['CEDULA', 'NOMBRES', 'APELLIDOS']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return {
                    'success': False,
                    'message': f"Columnas faltantes: {', '.join(missing_columns)}"
                }

            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    if progress_callback:
                        progress_callback(
                            index + 1,
                            total_rows,
                            f"Procesando {row['CEDULA']}..."
                        )

                    # Validar cédula
                    if not validar_cedula(str(row['CEDULA'])):
                        errors += 1
                        error_details.append(f"Fila {index + 2}: Cédula inválida")
                        continue

                    # Buscar si existe
                    empleado = self.session.query(Empleado).filter(
                        Empleado.cedula == str(row['CEDULA'])
                    ).first()

                    if empleado:
                        # Actualizar existente
                        self._update_employee_from_row(empleado, row)
                        updated += 1
                    else:
                        # Crear nuevo
                        empleado = self._create_employee_from_row(row)
                        self.session.add(empleado)
                        imported += 1

                    # Commit cada 100 registros
                    if (index + 1) % 100 == 0:
                        self.session.commit()

                except Exception as e:
                    errors += 1
                    error_details.append(f"Fila {index + 2}: {str(e)}")
                    logger.error(f"Error en fila {index + 2}: {e}")

            # Commit final
            self.session.commit()
            
            elapsed_time = time.time() - start_time

            return {
                'success': True,
                'imported': imported,
                'updated': updated,
                'errors': errors,
                'error_details': error_details[:10],  # Primeros 10 errores
                'time': elapsed_time
            }

        except Exception as e:
            logger.error(f"Error en importación: {e}")
            self.session.rollback()
            return {
                'success': False,
                'message': str(e)
            }

    def _create_employee_from_row(self, row) -> Empleado:
        """Crear empleado desde fila de DataFrame"""
        # Generar código de empleado
        last_employee = self.session.query(Empleado).order_by(
            Empleado.empleado.desc()
        ).first()

        if last_employee:
            last_code = int(last_employee.empleado)
            new_code = str(last_code + 1).zfill(6)
        else:
            new_code = "001001"

        empleado = Empleado(
            empleado=new_code,
            cedula=str(row['CEDULA']),
            nombres=str(row['NOMBRES']).upper(),
            apellidos=str(row['APELLIDOS']).upper()
        )

        # Campos opcionales
        if 'FECHA_NAC' in row and pd.notna(row['FECHA_NAC']):
            empleado.fecha_nac = pd.to_datetime(row['FECHA_NAC']).date()

        if 'SEXO' in row and pd.notna(row['SEXO']):
            empleado.sexo = str(row['SEXO']).upper()[:1]

        if 'DIRECCION' in row and pd.notna(row['DIRECCION']):
            empleado.direccion = str(row['DIRECCION'])[:200]

        if 'TELEFONO' in row and pd.notna(row['TELEFONO']):
            empleado.telefono = str(row['TELEFONO'])[:20]

        if 'EMAIL' in row and pd.notna(row['EMAIL']):
            if validar_email(str(row['EMAIL'])):
                empleado.email = str(row['EMAIL']).lower()

        if 'CARGO' in row and pd.notna(row['CARGO']):
            empleado.cargo = str(row['CARGO'])[:3]

        if 'DEPTO' in row and pd.notna(row['DEPTO']):
            empleado.depto = str(row['DEPTO'])[:3]

        if 'SUELDO' in row and pd.notna(row['SUELDO']):
            empleado.sueldo = Decimal(str(row['SUELDO']))

        if 'FECHA_ING' in row and pd.notna(row['FECHA_ING']):
            empleado.fecha_ing = pd.to_datetime(row['FECHA_ING']).date()
        else:
            empleado.fecha_ing = date.today()

        empleado.estado = 'ACT'
        empleado.created_by = 'IMPORT'

        return empleado

    def _update_employee_from_row(self, empleado: Empleado, row):
        """Actualizar empleado desde fila de DataFrame"""
        # Solo actualizar campos que vienen en el archivo
        if 'NOMBRES' in row and pd.notna(row['NOMBRES']):
            empleado.nombres = str(row['NOMBRES']).upper()

        if 'APELLIDOS' in row and pd.notna(row['APELLIDOS']):
            empleado.apellidos = str(row['APELLIDOS']).upper()

        if 'DIRECCION' in row and pd.notna(row['DIRECCION']):
            empleado.direccion = str(row['DIRECCION'])[:200]

        if 'TELEFONO' in row and pd.notna(row['TELEFONO']):
            empleado.telefono = str(row['TELEFONO'])[:20]

        if 'EMAIL' in row and pd.notna(row['EMAIL']):
            if validar_email(str(row['EMAIL'])):
                empleado.email = str(row['EMAIL']).lower()

        if 'SUELDO' in row and pd.notna(row['SUELDO']):
            empleado.sueldo = Decimal(str(row['SUELDO']))

        empleado.updated_by = 'IMPORT'

    def import_payroll_data(self, filename: str,
                           progress_callback: Optional[Callable] = None) -> Dict:
        """Importar datos de nómina (ingresos y descuentos)"""
        try:
            # Leer archivo
            if filename.endswith('.csv'):
                df = pd.read_csv(filename)
            else:
                df = pd.read_excel(filename)

            total_rows = len(df)
            imported = 0
            errors = 0

            for index, row in df.iterrows():
                try:
                    if progress_callback:
                        progress_callback(
                            index + 1,
                            total_rows,
                            f"Procesando concepto {row['CONCEPTO']}..."
                        )

                    # Buscar empleado
                    empleado_ref = str(row['EMPLEADO'])
                    empleado = self.session.query(Empleado).filter(
                        (Empleado.empleado == empleado_ref) |
                        (Empleado.cedula == empleado_ref)
                    ).first()

                    if not empleado:
                        errors += 1
                        continue

                    # Crear registro
                    ingreso_descuento = IngresoDescuento(
                        empleado=empleado.empleado,
                        fecha_desde=pd.to_datetime(row['FECHA_DESDE']).date(),
                        fecha_hasta=pd.to_datetime(row['FECHA_HASTA']).date(),
                        tipo=str(row['TIPO']).upper()[:1],
                        codigo=str(row.get('CODIGO', ''))[:10],
                        concepto=str(row['CONCEPTO'])[:100],
                        valor=Decimal(str(row['VALOR'])),
                        horas=Decimal(str(row.get('HORAS', 0))),
                        usuario='IMPORT'
                    )

                    self.session.add(ingreso_descuento)
                    imported += 1

                    if (index + 1) % 100 == 0:
                        self.session.commit()

                except Exception as e:
                    errors += 1
                    logger.error(f"Error en fila {index + 2}: {e}")

            self.session.commit()

            return {
                'success': True,
                'imported': imported,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"Error en importación de nómina: {e}")
            self.session.rollback()
            return {
                'success': False,
                'message': str(e)
            }

    def generate_import_template(self, template_type: str) -> str:
        """Generar plantilla Excel para importación"""
        
        templates = {
            'empleados': {
                'columns': [
                    'CEDULA', 'NOMBRES', 'APELLIDOS', 'FECHA_NAC', 'SEXO',
                    'ESTADO_CIVIL', 'DIRECCION', 'TELEFONO', 'CELULAR', 'EMAIL',
                    'CARGO', 'DEPTO', 'SECCION', 'SUELDO', 'FECHA_ING',
                    'TIPO_TRA', 'TIPO_PGO', 'BANCO', 'CUENTA_BANCO', 'TIPO_CUENTA'
                ],
                'sample_data': [{
                    'CEDULA': '1234567890',
                    'NOMBRES': 'JUAN CARLOS',
                    'APELLIDOS': 'PEREZ GARCIA',
                    'FECHA_NAC': '15/03/1985',
                    'SEXO': 'M',
                    'ESTADO_CIVIL': 'C',
                    'DIRECCION': 'Av. Principal 123',
                    'TELEFONO': '022345678',
                    'CELULAR': '0987654321',
                    'EMAIL': 'juan.perez@email.com',
                    'CARGO': 'GUA',
                    'DEPTO': '001',
                    'SECCION': 'GUA',
                    'SUELDO': 460,
                    'FECHA_ING': '01/01/2023',
                    'TIPO_TRA': 1,
                    'TIPO_PGO': 1,
                    'BANCO': '001',
                    'CUENTA_BANCO': '1234567890',
                    'TIPO_CUENTA': 'A'
                }]
            },
            'nomina': {
                'columns': [
                    'EMPLEADO', 'FECHA_DESDE', 'FECHA_HASTA', 'TIPO',
                    'CODIGO', 'CONCEPTO', 'VALOR', 'HORAS'
                ],
                'sample_data': [{
                    'EMPLEADO': '001001',
                    'FECHA_DESDE': '01/12/2024',
                    'FECHA_HASTA': '07/12/2024',
                    'TIPO': 'I',
                    'CODIGO': 'HE50',
                    'CONCEPTO': 'HORAS EXTRAS 50%',
                    'VALOR': 50.00,
                    'HORAS': 8
                }]
            }
        }

        if template_type not in templates:
            raise ValueError(f"Tipo de plantilla no válido: {template_type}")

        # Crear DataFrame con columnas y datos de ejemplo
        template = templates[template_type]
        df = pd.DataFrame(template['sample_data'], columns=template['columns'])

        # Guardar en archivo temporal
        filename = f"plantilla_{template_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = f"assets/templates/{filename}"

        # Crear Excel con formato
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Datos', index=False)

            # Agregar hoja de instrucciones
            instructions = pd.DataFrame({
                'INSTRUCCIONES': [
                    f'Plantilla para importación de {template_type}',
                    '',
                    'IMPORTANTE:',
                    '1. No modifique los nombres de las columnas',
                    '2. Respete el formato de fecha: DD/MM/YYYY',
                    '3. La primera fila contiene un ejemplo',
                    '4. Elimine la fila de ejemplo antes de importar',
                    '',
                    'COLUMNAS OBLIGATORIAS:',
                    '- ' + ', '.join(template['columns'][:3]),
                    '',
                    'VALORES PERMITIDOS:',
                    '- SEXO: M (Masculino), F (Femenino)',
                    '- ESTADO_CIVIL: S (Soltero), C (Casado), D (Divorciado), V (Viudo), U (Unión libre)',
                    '- TIPO_TRA: 1 (Operativo), 2 (Administrativo), 3 (Ejecutivo)',
                    '- TIPO_PGO: 1 (Semanal), 2 (Quincenal), 3 (Mensual)',
                    '- TIPO_CUENTA: A (Ahorros), C (Corriente)'
                ]
            })
            instructions.to_excel(writer, sheet_name='Instrucciones', index=False)

        return filepath

class ExportService:
    """Servicio para exportación de datos"""
    
    def __init__(self):
        self.session = get_session()
    
    def export_employees_excel(self, filters=None) -> str:
        """Exportar empleados a Excel"""
        try:
            query = self.session.query(Empleado).filter(Empleado.activo == True)
            
            if filters:
                # Aplicar filtros si existen
                pass
            
            empleados = query.all()
            
            # Convertir a DataFrame
            data = []
            for emp in empleados:
                data.append({
                    'EMPLEADO': emp.empleado,
                    'CEDULA': emp.cedula,
                    'NOMBRES': emp.nombres,
                    'APELLIDOS': emp.apellidos,
                    'CARGO': emp.cargo,
                    'DEPARTAMENTO': emp.depto,
                    'SUELDO': float(emp.sueldo),
                    'FECHA_INGRESO': emp.fecha_ing,
                    'ESTADO': emp.estado,
                    'TELEFONO': emp.telefono,
                    'EMAIL': emp.email
                })
            
            df = pd.DataFrame(data)
            
            # Generar archivo
            filename = f"empleados_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = f"reports/{filename}"
            
            df.to_excel(filepath, index=False, sheet_name='Empleados')
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error exportando empleados: {e}")
            raise
