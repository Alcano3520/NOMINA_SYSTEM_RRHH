# 🚀 Guía de Configuración Multi-PC para SAI

Esta guía te permitirá configurar el Sistema SAI en múltiples computadoras de manera rápida y eficiente.

## 📋 Índice
1. [Preparación Inicial](#preparación-inicial)
2. [Configuración PC Principal](#configuración-pc-principal)
3. [Clonación a Otras PCs](#clonación-a-otras-pcs)
4. [Guía para Claude AI](#guía-para-claude-ai)
5. [Solución de Problemas](#solución-de-problemas)

---

## 🔧 Preparación Inicial

### Requisitos Mínimos por PC
- **SO**: Windows 10+, Linux Ubuntu 18+, macOS 10.14+
- **Python**: 3.8 o superior
- **RAM**: 4GB mínimo, 8GB recomendado
- **Espacio**: 500MB libre
- **Internet**: Para clonar repositorio y dependencias

### Verificar Python
```bash
# Verificar versión de Python
python --version
# o
python3 --version

# Debe mostrar 3.8.x o superior
```

---

## 🖥️ Configuración PC Principal

### Paso 1: Clonar el Repositorio
```bash
# Crear carpeta de proyectos
mkdir C:\Mis_Proyectos
cd C:\Mis_Proyectos

# Clonar repositorio
git clone https://github.com/tu-usuario/sai-nomina-system.git
cd sai-nomina-system
```

### Paso 2: Configurar Entorno Python
```bash
# Crear entorno virtual
python -m venv sai_env

# Activar entorno (Windows)
sai_env\Scripts\activate

# Activar entorno (Linux/macOS)
source sai_env/bin/activate

# Actualizar pip
pip install --upgrade pip
```

### Paso 3: Instalar Dependencias
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación crítica
pip list | findstr -i "sqlalchemy pandas openpyxl"
```

### Paso 4: Primera Ejecución
```bash
# Ejecutar sistema por primera vez
python main_fixed.py

# Si aparecen errores, usar versión simple
python main_simple.py
```

### Paso 5: Verificar Funcionamiento
✅ **Checklist de Verificación:**
- [ ] Ventana principal se abre
- [ ] Sidebar de navegación visible
- [ ] Módulos de empleados funciona
- [ ] Base de datos se crea (`sai_nomina.db`)
- [ ] No hay errores críticos en consola

---

## 💻 Clonación a Otras PCs

### Opción A: Clonar desde GitHub (Recomendado)

#### PC Destino - Configuración Rápida
```bash
# 1. Abrir terminal/cmd en PC destino
# 2. Crear carpeta de trabajo
mkdir C:\SAI_System
cd C:\SAI_System

# 3. Clonar repositorio
git clone https://github.com/tu-usuario/sai-nomina-system.git
cd sai-nomina-system

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar sistema
python main_fixed.py
```

### Opción B: Transferencia por USB/Red

#### Preparar Paquete Portable
```bash
# En PC principal, crear paquete
# Comprimir toda la carpeta excluyendo:
- __pycache__/
- *.pyc
- sai_env/
- .git/
- logs/
- *.db
```

#### En PC Destino
```bash
# 1. Extraer paquete a C:\SAI_System
# 2. Instalar dependencias
cd C:\SAI_System\sai-nomina-system
pip install -r requirements.txt

# 3. Ejecutar
python main_fixed.py
```

---

## 🤖 Guía para Claude AI

### 🎯 Prompt Inicial Optimizado

**Copiar y pegar este prompt al iniciar chat con Claude:**

```
Hola Claude! Soy desarrollador trabajando con el Sistema SAI de nómina ecuatoriana.

CONTEXTO DEL PROYECTO:
- Nombre: SAI - Sistema Administrativo Integral
- Ubicación: C:\Mis_Proyectos\sai-nomina-system\ (o tu ruta actual)
- Lenguaje: Python 3.8+
- GUI: Tkinter moderno
- BD: SQLite + SQLAlchemy ORM
- Propósito: Sistema de nómina para empresas ecuatorianas

ARQUITECTURA ACTUAL:
```
sai-nomina-system/
├── database/ (modelos SQLAlchemy)
├── gui/ (interfaz Tkinter moderna)
│   ├── components/ (componentes reutilizables)
│   ├── modules/ (empleados, nómina, décimos, etc.)
├── services/ (lógica de negocio)
├── utils/ (cálculos Ecuador, validaciones)
├── main_fixed.py (punto entrada principal)
└── config.py (configuración sistema)
```

CARACTERÍSTICAS CLAVE:
✅ Cálculos nómina ecuatoriana (IESS, décimos, etc.)
✅ Validaciones cédula/RUC Ecuador
✅ 7 módulos: empleados, nómina, décimos, vacaciones, préstamos, dotación, reportes
✅ Importación masiva Excel/CSV
✅ Interface moderna con tarjetas y efectos

TECNOLOGÍAS:
- SQLAlchemy ORM con modelos: Empleado, RolPago, Decimo, Vacacion, Prestamo, etc.
- Tkinter con componentes: StatCard, DataTable, SearchForm, etc.
- Utilidades: calculations.py (fórmulas Ecuador), validators.py (validaciones)

NECESITO AYUDA CON: [Describir tu tarea específica aquí]

Por favor, mantén el estilo de código existente y las convenciones del proyecto.
```

### 🔧 Prompts para Tareas Específicas

#### Para Agregar Nueva Funcionalidad
```
Claude, necesito agregar [funcionalidad] al Sistema SAI.

El sistema ya tiene:
- Módulos existentes en gui/modules/
- Componentes reutilizables en gui/components/
- Modelos de BD en database/models.py
- Servicios en services/

Por favor, crea [descripción específica] siguiendo:
1. Patrón arquitectónico existente
2. Estilo de código del proyecto
3. Validaciones apropiadas para Ecuador
4. Integración con BD existente
```

#### Para Corregir Errores
```
Claude, el Sistema SAI presenta el siguiente error:

ERROR: [copiar error exacto]

Contexto:
- Ocurre en: [módulo/función específica]
- Al hacer: [acción que causa error]
- Sistema operativo: [Windows/Linux/macOS]
- Python version: [versión]

Archivo principal: main_fixed.py
Por favor diagnostica y proporciona solución.
```

#### Para Optimización
```
Claude, necesito optimizar [aspecto específico] del Sistema SAI.

Situación actual:
- [Describir problema de rendimiento/usabilidad]
- Afecta: [módulos afectados]
- Frecuencia: [cuando ocurre]

Objetivos:
- [Resultado esperado]
- Mantener compatibilidad con arquitectura existente
- Preservar funcionalidad ecuatoriana específica
```

### 📚 Información de Contexto para Claude

#### Cálculos Importantes Ecuador
```python
# Rates importantes en config.py
SBU = 460.00                    # Salario Básico Unificado 2024
APORTE_PERSONAL_IESS = 0.0945   # 9.45%
APORTE_PATRONAL_IESS = 0.1115   # 11.15%
FONDOS_RESERVA = 0.0833         # 8.33%
HORAS_EXTRAS_25 = 1.25          # 25% recargo
HORAS_EXTRAS_50 = 1.50          # 50% recargo
HORAS_EXTRAS_100 = 2.00         # 100% recargo
```

#### Modelos Principales
```python
# Modelos clave en database/models.py
- Empleado: datos personales y laborales
- RolPago: roles de nómina procesados
- Decimo: gestión 13° y 14° sueldo
- Vacacion: control vacaciones
- Prestamo: préstamos empleados
- Dotacion: uniformes y EPP
```

#### Módulos GUI
```python
# Módulos en gui/modules/
- empleados.py: CRUD empleados
- nomina.py: procesamiento roles
- decimos.py: gestión décimos
- vacaciones.py: control vacaciones
- prestamos.py: gestión préstamos
- dotacion.py: control dotación
- reportes.py: dashboard y reportes
```

---

## 🔍 Solución de Problemas Comunes

### Error: "Module not found"
```bash
# Solución: Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Error: "Permission denied"
```bash
# Windows: Ejecutar como administrador
# Linux/macOS: Usar sudo si es necesario
sudo python main_fixed.py
```

### Error: "Database is locked"
```bash
# Cerrar todas las instancias del programa
# Eliminar archivo de base de datos
rm sai_nomina.db
# Ejecutar nuevamente
python main_fixed.py
```

### Error: "Invalid color name"
```bash
# Usar versión corregida
python main_fixed.py
# En lugar de
python main.py
```

### Interfaz no se muestra
```bash
# Verificar display (Linux)
echo $DISPLAY

# Probar versión simple
python main_simple.py
```

---

## 📞 Soporte y Contacto

### Recursos de Ayuda
- **README principal**: Documentación completa
- **GitHub Issues**: Reportar problemas
- **Wiki**: Guías adicionales

### Información del Sistema
```bash
# Comando para diagnostico completo
python -c "
import sys, platform, tkinter
print(f'Python: {sys.version}')
print(f'Platform: {platform.system()} {platform.release()}')
print(f'Tkinter: OK')
"
```

---

## ✅ Checklist de Configuración Exitosa

### PC Principal
- [ ] Python 3.8+ instalado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] `python main_fixed.py` ejecuta sin errores
- [ ] Base de datos `sai_nomina.db` se crea
- [ ] Todos los módulos navegan correctamente

### PCs Adicionales
- [ ] Mismos requisitos que PC principal
- [ ] Código transferido/clonado
- [ ] Dependencias instaladas localmente
- [ ] Sistema ejecuta sin problemas
- [ ] Funcionalidad completa verificada

---

**🎉 ¡Configuración completada! El Sistema SAI está listo para usar en múltiples PCs.**