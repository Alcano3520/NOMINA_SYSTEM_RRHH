# 🤖 Guía Completa para Trabajar con Claude AI - Sistema SAI

Esta guía te ayudará a trabajar eficientemente con Claude AI en futuras mejoras del Sistema SAI.

## 📋 Índice
1. [Prompt Inicial Optimizado](#prompt-inicial-optimizado)
2. [Prompts por Tipo de Tarea](#prompts-por-tipo-de-tarea)
3. [Contexto Técnico del Proyecto](#contexto-técnico-del-proyecto)
4. [Ejemplos Prácticos](#ejemplos-prácticos)
5. [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Prompt Inicial Optimizado

### Copiar y Pegar al Iniciar Nuevo Chat

```
¡Hola Claude! Necesito tu ayuda con el Sistema SAI de nómina ecuatoriana.

📊 INFORMACIÓN DEL PROYECTO:
Nombre: SAI - Sistema Administrativo Integral
Repositorio: https://github.com/[TU-USUARIO]/sai-nomina-system
Ubicación local: C:\[TU-RUTA]\sai-nomina-system\

🏗️ ARQUITECTURA TÉCNICA:
- Lenguaje: Python 3.8+
- GUI: Tkinter moderno con componentes personalizados
- Base de datos: SQLite + SQLAlchemy ORM
- Propósito: Sistema de nómina para empresas ecuatorianas
- Empresa: INSEVIG CIA. LTDA (seguridad física)

📁 ESTRUCTURA DEL PROYECTO:
```
sai-nomina-system/
├── 📂 database/              # Modelos y conexión BD
│   ├── models.py            # SQLAlchemy models
│   ├── connection.py        # DB connection management
│   └── initialize.py        # Datos iniciales
├── 📂 gui/                  # Interfaz gráfica moderna
│   ├── 📂 components/       # Componentes reutilizables
│   │   ├── stat_card.py     # Tarjetas estadísticas
│   │   ├── data_table.py    # Tablas de datos
│   │   ├── sidebar.py       # Navegación lateral
│   │   └── header.py        # Encabezado
│   ├── 📂 modules/          # Módulos principales
│   │   ├── empleados.py     # Gestión empleados
│   │   ├── nomina.py        # Procesamiento nómina
│   │   ├── decimos.py       # 13° y 14° sueldo
│   │   ├── vacaciones.py    # Control vacaciones
│   │   ├── prestamos.py     # Gestión préstamos
│   │   ├── dotacion.py      # Uniformes y EPP
│   │   └── reportes.py      # Dashboard y análisis
│   ├── main_window.py       # Ventana principal
│   └── styles.py            # Estilos y temas
├── 📂 services/             # Lógica de negocio
│   └── import_export.py     # Importación masiva
├── 📂 utils/                # Utilidades Ecuador
│   ├── calculations.py      # Fórmulas nómina EC
│   └── validators.py        # Validaciones EC
├── config.py                # Configuración global
├── main_fixed.py            # Punto entrada principal
└── requirements.txt         # Dependencias
```

🇪🇨 CARACTERÍSTICAS ESPECÍFICAS ECUADOR:
✅ Validación cédula ecuatoriana (algoritmo oficial)
✅ Validación RUC empresarial
✅ Cálculos IESS: 9.45% personal, 11.15% patronal
✅ Fondos de reserva: 8.33%
✅ Décimo tercero (13° sueldo): ingresos anuales / 12
✅ Décimo cuarto (14° sueldo): SBU proporcional
✅ SBU actual: $460.00 (2024)
✅ Horas extras: 25%, 50%, 100% recargo
✅ Vacaciones: 15 días anuales
✅ Impuesto a la renta: tabla ecuatoriana

🛠️ TECNOLOGÍAS CLAVE:
- SQLAlchemy: Empleado, RolPago, Decimo, Vacacion, Prestamo, Dotacion
- Tkinter: StatCard, DataTable, SearchForm, ModernButton
- Pandas: Importación masiva Excel/CSV
- ReportLab: Generación reportes PDF
- Python-dateutil: Manejo fechas Ecuador

🎯 PATRONES DE CÓDIGO:
- Módulos heredan de tk.Frame
- Componentes reutilizables en gui/components/
- Servicios independientes en services/
- Validaciones centralizadas en utils/
- Configuración unificada en config.py

NECESITO AYUDA CON: [Describe tu tarea específica aquí]

Por favor mantén el estilo arquitectónico y las convenciones del proyecto.
```

---

## 🔧 Prompts por Tipo de Tarea

### 🆕 Agregar Nueva Funcionalidad

```
Claude, necesito agregar [FUNCIONALIDAD] al Sistema SAI.

🎯 REQUERIMIENTO:
[Descripción detallada de lo que necesitas]

📋 CONTEXTO ACTUAL:
- El sistema tiene 7 módulos principales funcionando
- Arquitectura modular con gui/modules/[modulo].py
- Componentes reutilizables en gui/components/
- Modelos de BD en database/models.py
- Servicios en services/

🔧 ESPECIFICACIONES:
- Integrar con: [módulo existente / nuevo]
- Validaciones Ecuador: [sí/no y cuáles]
- Base de datos: [nuevas tablas / modificar existentes]
- Interfaz: [tipo de componentes necesarios]

📊 DATOS DE ENTRADA:
[Formato y origen de los datos]

📈 RESULTADO ESPERADO:
[Qué debe hacer exactamente]

Por favor sigue:
1. Patrón arquitectónico existente
2. Estilo de código del proyecto
3. Validaciones apropiadas para Ecuador
4. Integración con componentes existentes
```

### 🐛 Corregir Errores

```
Claude, el Sistema SAI presenta el siguiente error:

❌ ERROR ENCONTRADO:
```
[Copiar error exacto aquí]
```

📍 CONTEXTO DEL ERROR:
- Archivo: [archivo específico]
- Línea: [número de línea si conoces]
- Función: [función donde ocurre]
- Acción que lo causa: [qué estabas haciendo]

🖥️ ENTORNO:
- SO: [Windows/Linux/macOS]
- Python: [versión]
- Módulo afectado: [empleados/nomina/etc.]

📁 ARCHIVOS RELACIONADOS:
[Lista de archivos que podrían estar involucrados]

🎯 COMPORTAMIENTO ESPERADO:
[Qué debería pasar en lugar del error]

Por favor diagnostica y proporciona:
1. Causa raíz del problema
2. Solución específica
3. Código corregido
4. Forma de prevenir en el futuro
```

### ⚡ Optimizar Rendimiento

```
Claude, necesito optimizar [ASPECTO] del Sistema SAI.

🐌 PROBLEMA ACTUAL:
[Descripción del problema de rendimiento]

📊 SÍNTOMAS:
- Tiempo de respuesta: [lento/muy lento]
- Uso de memoria: [alto/normal]
- CPU: [alto/normal]
- Frecuencia: [siempre/a veces/con datos grandes]

🎯 MÓDULOS AFECTADOS:
[Lista de módulos con problemas]

📈 OBJETIVO:
- Mejorar tiempo de respuesta en: [%]
- Reducir uso de memoria: [sí/no]
- Manejar más datos: [cantidad]

🔧 RESTRICCIONES:
- Mantener compatibilidad con arquitectura existente
- Preservar funcionalidad ecuatoriana específica
- No romper interfaz de usuario actual

Por favor proporciona:
1. Análisis del cuello de botella
2. Estrategia de optimización
3. Código mejorado
4. Métricas de mejora esperadas
```

### 🎨 Mejorar Interfaz

```
Claude, quiero mejorar la interfaz del Sistema SAI.

🖼️ MEJORA DESEADA:
[Descripción específica de la mejora visual]

📍 UBICACIÓN:
- Módulo: [empleados/nomina/etc.]
- Componente: [tabla/formulario/botón/etc.]
- Archivo: [archivo específico]

🎯 OBJETIVO:
- Usabilidad: [más fácil/más intuitivo]
- Estética: [más moderno/más profesional]
- Funcionalidad: [agregar feature/mejorar existente]

🎨 ESTILO ACTUAL:
- Colores: Config.COLORS (azul profesional)
- Fuentes: Config.FONTS (Segoe UI)
- Componentes: StatCard, DataTable, ModernButton

💡 INSPIRACIÓN:
[Describe el look que quieres o adjunta imagen]

🔧 RESTRICCIONES:
- Mantener coherencia con diseño actual
- Compatible con Tkinter
- Responsive dentro de ventana principal

Por favor proporciona:
1. Mockup o descripción visual
2. Código de implementación
3. Integración con estilos existentes
4. Mejoras de UX adicionales
```

### 📊 Crear Nuevos Reportes

```
Claude, necesito crear un nuevo reporte para el Sistema SAI.

📈 TIPO DE REPORTE:
[Dashboard/PDF/Excel/Gráfico]

📊 DATOS A MOSTRAR:
- Fuente: [tabla/cálculo/combinación]
- Período: [mensual/anual/rango]
- Filtros: [empleado/departamento/fecha/etc.]
- Métricas: [lista de métricas específicas]

🇪🇨 CÁLCULOS ECUADOR:
- IESS: [sí/no]
- Décimos: [sí/no]
- Impuesto renta: [sí/no]
- Provisiones: [sí/no]

📄 FORMATO DE SALIDA:
- Interfaz: [dashboard en módulo reportes]
- Export: [PDF/Excel/ambos]
- Layout: [tabla/gráfico/mixto]

🎯 USUARIOS OBJETIVO:
[Administrador/Contador/RRHH/Gerencia]

📋 REQUERIMIENTOS LEGALES:
[Cumplimiento específico Ecuador si aplica]

Por favor proporciona:
1. Diseño del reporte
2. Código de implementación
3. Integración con módulo reportes
4. Función de exportación
5. Validaciones de datos
```

---

## 🔍 Contexto Técnico del Proyecto

### 📊 Modelos de Base de Datos Principales

```python
# database/models.py - Modelos clave

Empleado:
- empleado (PK): código 6 dígitos
- cedula: validación ecuatoriana
- nombres, apellidos: texto
- fecha_ing, fecha_nac: fechas
- sueldo: decimal para cálculos
- departamento, cargo: FKs
- activo, estado: control

RolPago:
- empleado: FK a Empleado
- periodo: YYYY-MM
- dias_trabajados: entero
- total_ingresos, total_descuentos: decimal
- neto_pagar: decimal calculado
- estado: BORRADOR/PROCESADO/PAGADO

Decimo:
- empleado: FK a Empleado
- tipo_decimo: 13 o 14
- periodo: año fiscal
- monto: decimal calculado
- fecha_pago: fecha
- estado: PENDIENTE/PAGADO

Vacacion:
- empleado: FK a Empleado
- fecha_inicio, fecha_fin: período
- dias_solicitados: entero
- estado: PENDIENTE/APROBADA/RECHAZADA

Prestamo:
- empleado: FK a Empleado
- monto_original, saldo_pendiente: decimal
- cuota_mensual: decimal
- fecha_inicio, fecha_fin: período
- tipo_prestamo: QUIROGRAFARIO/HIPOTECARIO/etc.

Dotacion:
- empleado: FK a Empleado
- tipo_articulo: UNIFORME/CALZADO/EPP
- descripcion, talla: texto
- valor_unitario, cantidad: números
- fecha_entrega: fecha
```

### 🎨 Componentes GUI Reutilizables

```python
# gui/components/ - Componentes principales

StatCard:
- Tarjetas de estadísticas con métricas
- Props: title, value, subtitle, color
- Efectos hover y responsive

DataTable:
- Tablas de datos con acciones
- Props: columns, data, actions, filters
- Sorting, pagination, búsqueda

SearchForm:
- Formularios de búsqueda reutilizables
- Props: fields, validators, on_search
- Validaciones en tiempo real

ModernButton:
- Botones con estilos modernos
- Props: text, command, style, icon
- Estados: normal, hover, disabled
```

### ⚙️ Utilidades Ecuador

```python
# utils/calculations.py - Fórmulas específicas

calcular_aporte_iess_personal(sueldo): 9.45%
calcular_aporte_iess_patronal(sueldo): 11.15%
calcular_fondos_reserva(sueldo): 8.33%
calcular_decimo_tercer_sueldo(ingresos_anuales): / 12
calcular_decimo_cuarto_sueldo(dias, sbu): proporcional
calcular_horas_extras(valor_hora, horas, tipo): 25/50/100%
calcular_impuesto_renta(ingreso, tabla_ir): tabla Ecuador
calcular_vacaciones(sueldo, dias): proporcional

# utils/validators.py - Validaciones específicas

validar_cedula(cedula): algoritmo oficial Ecuador
validar_ruc(ruc): validación empresarial
validar_email(email): formato estándar
validar_telefono(telefono): formato Ecuador
validar_sueldo(sueldo, sbu): >= SBU
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Agregar Validación Nueva

```
Claude, necesito agregar validación de IESS al Sistema SAI.

🎯 REQUERIMIENTO:
Validar que el número de afiliado IESS sea correcto antes de guardar empleado.

📋 CONTEXTO:
- Los empleados se gestionan en gui/modules/empleados.py
- Las validaciones están en utils/validators.py
- El modelo Empleado está en database/models.py

🔧 ESPECIFICACIONES:
- Campo: numero_iess (11 dígitos)
- Validación: formato específico Ecuador
- Integrar en: formulario de empleados
- Error: mensaje claro al usuario

📊 DATOS:
- Input: string de 11 dígitos
- Formato: XXXXXXXXXXX (solo números)
- Validación: algoritmo específico si existe

Por favor proporciona:
1. Función de validación en validators.py
2. Integración en formulario empleados
3. Mensaje de error apropiado
4. Tests básicos de la función
```

### Ejemplo 2: Optimizar Carga de Datos

```
Claude, la carga de empleados en el Sistema SAI es lenta.

🐌 PROBLEMA:
La tabla de empleados tarda 3-5 segundos en cargar con 500 empleados.

📊 CONTEXTO TÉCNICO:
- Método: load_data() en gui/modules/empleados.py línea 245
- Query: session.query(Empleado).order_by(...).all()
- Procesamiento: bucle for para formatear datos
- Tabla: DataTable con 500 filas

🎯 SÍNTOMAS:
- Carga inicial: 5 segundos
- Cambio de filtros: 3 segundos
- UI se congela durante carga

📈 OBJETIVO:
- Reducir tiempo a menos de 1 segundo
- Mantener toda la funcionalidad actual
- No afectar otras partes del sistema

Por favor analiza y optimiza considerando:
1. Lazy loading o paginación
2. Optimización de queries
3. Cache de datos
4. Threading para UI responsiva
```

---

## ✅ Mejores Prácticas

### 🎯 Para Obtener Mejores Resultados

1. **Sé Específico**: En lugar de "mejorar empleados", di "agregar validación de email en formulario de empleados"

2. **Proporciona Contexto**: Siempre menciona archivos específicos y líneas de código si las conoces

3. **Incluye Errores Completos**: Copia el traceback completo, no solo el mensaje

4. **Define Objetivos Claros**: "Reducir tiempo de carga de 5s a 1s" vs "hacer más rápido"

5. **Menciona Restricciones**: "Sin cambiar la base de datos" o "mantener compatibilidad con Windows"

### 📋 Información Útil para Claude

- **Archivo de entrada**: main_fixed.py
- **Configuración principal**: config.py
- **Estilo de código**: PEP 8, docstrings en español
- **Convenciones**: nombres en español para UI, inglés para código
- **Base datos**: SQLite, migraciones manuales
- **Testing**: Manual, sin framework específico

### 🚫 Evitar en Prompts

- Prompts vagos: "mejora el sistema"
- Sin contexto: "da error" (¿cuál error?)
- Cambios drásticos: "cambiar a Django" (mantener Tkinter)
- Sin restricciones: especificar limitaciones siempre

---

## 🎉 ¡Listo para Trabajar con Claude!

Con esta guía podrás:
- ✅ Obtener ayuda específica y útil
- ✅ Mantener consistencia en el proyecto
- ✅ Resolver problemas eficientemente
- ✅ Agregar funcionalidades nuevas
- ✅ Optimizar el sistema existente

**💡 Recuerda**: Mientras más específico y detallado sea tu prompt, mejores serán los resultados de Claude AI.

---

**🤖 ¡Feliz desarrollo con Claude AI en tu Sistema SAI!**