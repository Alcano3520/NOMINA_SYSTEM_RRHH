# SAI - Sistema Administrativo Integral

![SAI Logo](https://img.shields.io/badge/SAI-Sistema%20Administrativo%20Integral-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## 📋 Descripción

**SAI (Sistema Administrativo Integral)** es un sistema completo de nómina y recursos humanos diseñado específicamente para empresas ecuatorianas. Desarrollado con Python y Tkinter, ofrece una interfaz moderna y funcionalidades completas para la gestión de personal y procesos de nómina según la legislación laboral ecuatoriana.

### 🎯 Desarrollado para INSEVIG CIA. LTDA
Sistema profesional de nómina para empresas de seguridad física en Ecuador.

## ✨ Características Principales

### 📊 Módulos Completos
- **👥 Gestión de Empleados**: CRUD completo con validaciones ecuatorianas
- **💰 Procesamiento de Nómina**: Cálculos automáticos según legislación
- **🎁 Décimos**: Gestión de 13° y 14° sueldo
- **🏖️ Vacaciones**: Control de solicitudes y saldos
- **💳 Préstamos**: Sistema financiero completo
- **👔 Dotación**: Control de uniformes y EPP
- **📊 Reportes**: Dashboard ejecutivo y análisis

### 🇪🇨 Específico para Ecuador
- ✅ Validación de cédula ecuatoriana
- ✅ Validación de RUC
- ✅ Cálculos IESS (9.45% personal, 11.15% patronal)
- ✅ Fondos de reserva (8.33%)
- ✅ Décimo tercero y cuarto sueldo
- ✅ Horas extras (25%, 50%, 100%)
- ✅ SBU actualizado ($460.00)

### 🚀 Tecnología Moderna
- **Interfaz gráfica moderna** con Tkinter
- **Base de datos SQLite** con SQLAlchemy ORM
- **Importación masiva** Excel/CSV
- **Reportes PDF** profesionales
- **Arquitectura modular** escalable
- **Sistema de validaciones** robusto

## 🛠️ Instalación

### Requisitos del Sistema
- **Python 3.8 o superior**
- **Windows, Linux o macOS**
- **4GB RAM mínimo**
- **100MB espacio en disco**

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/sai-nomina-system.git
cd sai-nomina-system
```

### 2. Crear Entorno Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar el Sistema
```bash
# Versión completa
python main.py

# Versión corregida (recomendada)
python main_fixed.py
```

## 📁 Estructura del Proyecto

```
sai-nomina-system/
├── 📂 database/              # Modelos y conexión BD
│   ├── models.py             # Modelos SQLAlchemy
│   ├── connection.py         # Gestión de conexiones
│   └── initialize.py         # Datos iniciales
├── 📂 gui/                   # Interfaz gráfica
│   ├── 📂 components/        # Componentes reutilizables
│   ├── 📂 dialogs/          # Ventanas de diálogo
│   ├── 📂 modules/          # Módulos principales
│   ├── main_window.py       # Ventana principal
│   └── styles.py            # Estilos y temas
├── 📂 services/             # Servicios del sistema
│   └── import_export.py     # Importación masiva
├── 📂 utils/                # Utilidades
│   ├── calculations.py      # Cálculos de nómina
│   └── validators.py        # Validaciones Ecuador
├── 📂 logs/                 # Archivos de log
├── 📂 reports/              # Reportes generados
├── 📂 backups/              # Respaldos
├── config.py                # Configuración global
├── main.py                  # Punto de entrada
├── main_fixed.py            # Versión optimizada
└── requirements.txt         # Dependencias Python
```

## 🚀 Uso del Sistema

### Inicio Rápido
1. **Ejecutar**: `python main_fixed.py`
2. **Navegar**: Usar sidebar para acceder a módulos
3. **Gestionar**: Empleados, nómina, décimos, etc.
4. **Reportar**: Generar análisis y reportes

### Módulos Principales

#### 👥 Empleados
- Registro completo de personal
- Validación de cédula ecuatoriana
- Gestión de cargos y departamentos
- Importación masiva desde Excel/CSV

#### 💰 Nómina
- Procesamiento automático de roles
- Cálculos según legislación ecuatoriana
- Horas extras y bonificaciones
- Descuentos IESS e impuesto renta

#### 📊 Reportes
- Dashboard ejecutivo en tiempo real
- Reportes de nómina detallada
- Estados financieros
- Análisis de cumplimiento legal

## 🔧 Configuración

### Variables de Entorno
```python
# config.py - Principales configuraciones
SBU = 460.00                    # Salario Básico Unificado
APORTE_PERSONAL_IESS = 0.0945   # 9.45%
APORTE_PATRONAL_IESS = 0.1115   # 11.15%
FONDOS_RESERVA = 0.0833         # 8.33%
```

### Base de Datos
- **SQLite** por defecto (archivo: `sai_nomina.db`)
- **Migrable** a PostgreSQL/MySQL
- **Backup automático** en carpeta `backups/`

## 📚 Documentación para Desarrolladores

### Arquitectura MVC
```
Model (database/models.py) ←→ View (gui/modules/) ←→ Controller (services/)
```

### Agregar Nuevo Módulo
1. Crear archivo en `gui/modules/mi_modulo.py`
2. Implementar clase heredando de `tk.Frame`
3. Agregar importación en `main_window.py`
4. Incluir en sidebar navigation

### Cálculos de Nómina
```python
from utils.calculations import calcular_rol_individual

# Ejemplo de uso
empleado_data = {...}
periodo_data = {...}
resultado = calcular_rol_individual(empleado_data, periodo_data)
```

## 🤖 Guía para Claude (IA)

### Prompt Inicial Recomendado
```
Soy el desarrollador del Sistema SAI de nómina para Ecuador. El proyecto está en:
[ruta del proyecto]

Características del sistema:
- Python + Tkinter GUI moderna
- SQLAlchemy + SQLite
- Cálculos específicos para Ecuador (IESS, décimos, etc.)
- Módulos: empleados, nómina, décimos, vacaciones, préstamos, dotación, reportes
- Importación masiva Excel/CSV
- Validaciones ecuatorianas (cédula, RUC)

Necesito ayuda con: [describir tarea específica]
```

### Tareas Comunes para Claude
1. **Agregar nueva funcionalidad**
2. **Corregir errores específicos**
3. **Optimizar rendimiento**
4. **Agregar validaciones**
5. **Crear nuevos reportes**
6. **Mejorar interfaz**

### Contexto Importante
- **Legislación ecuatoriana** aplicable
- **Arquitectura modular** existente
- **Patrones de código** establecidos
- **Convenciones de naming** del proyecto

## 🐛 Solución de Problemas

### Problemas Comunes

#### Error: "invalid color name"
```bash
# Solución: Usar main_fixed.py en lugar de main.py
python main_fixed.py
```

#### Error: "Module not found"
```bash
# Instalar dependencias faltantes
pip install -r requirements.txt
```

#### Error: "Database locked"
```bash
# Cerrar todas las instancias del programa
# Eliminar archivo sai_nomina.db si es necesario
```

#### Recursión infinita en módulos
```bash
# Usar versión corregida
python main_fixed.py
```

## 📄 Licencia

MIT License - Ver archivo [LICENSE](LICENSE) para detalles.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Soporte

- **Documentación**: [Wiki del proyecto](../../wiki)
- **Issues**: [GitHub Issues](../../issues)
- **Discusiones**: [GitHub Discussions](../../discussions)

## 🏢 Desarrollado por

**Para INSEVIG CIA. LTDA**
Sistema de nómina empresarial ecuatoriano

---

## 📈 Roadmap

### Versión 1.1 (Próxima)
- [ ] Módulo de reportes avanzados
- [ ] Dashboard interactivo
- [ ] Notificaciones por email
- [ ] Backup automático en la nube

### Versión 1.2 (Futuro)
- [ ] API REST
- [ ] Aplicación móvil
- [ ] Integración bancaria
- [ ] Multi-empresa

---

**⚡ SAI - Automatizando la gestión de RRHH en Ecuador**