# Instrucciones para Configurar Git Remoto

## Paso 1: Crear Repositorio en GitHub

1. Ve a https://github.com
2. Inicia sesión o crea una cuenta
3. Haz clic en "New repository" (botón verde)
4. Nombre del repositorio: `NOMINA_SYSTEM_RRHH`
5. Descripción: `Sistema de Nómina SAI - INSEVIG CIA. LTDA - Ecuador Security Sector`
6. Selecciona "Private" (recomendado para código empresarial)
7. NO marques "Initialize this repository with a README"
8. Haz clic en "Create repository"

## Paso 2: Conectar Repositorio Local con GitHub

Ejecutar estos comandos en la terminal desde la carpeta del proyecto:

```bash
# Agregar el repositorio remoto (reemplaza YOUR_USERNAME con tu usuario de GitHub)
git remote add origin https://github.com/YOUR_USERNAME/NOMINA_SYSTEM_RRHH.git

# Configurar tu identidad (solo la primera vez)
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"

# Subir el código al repositorio remoto
git push -u origin master
```

## Paso 3: Para Trabajar desde Otra PC

En la otra computadora, ejecuta:

```bash
# Clonar el repositorio
git clone https://github.com/YOUR_USERNAME/NOMINA_SYSTEM_RRHH.git

# Entrar a la carpeta
cd NOMINA_SYSTEM_RRHH

# Verificar que todo esté correcto
git status
```

## Comandos Útiles para Trabajo Colaborativo

```bash
# Antes de empezar a trabajar, siempre actualiza:
git pull origin master

# Después de hacer cambios:
git add .
git commit -m "Descripción de los cambios"
git push origin master

# Ver el historial de cambios:
git log --oneline

# Ver qué archivos han cambiado:
git status
```

## Archivos Incluidos en el Repositorio

- **sai_sistema_mejorado_completo.html** - Interface principal completa
- **SP_RP_PREPARA_ROL.sql** - Procedimiento principal de nómina
- **SP_RP_DECIMO_CUARTO_QUINTO.sql** - Cálculo de décimos
- **REPORTE_INVESTIGACION_SISTEMAS_NOMINA.md** - Investigación completa
- **REPORTE_MODULO_RRHH_COMPLETO.md** - Análisis del sistema SAI
- Archivos DLL y componentes del sistema PowerBuilder
- Todas las interfaces de prueba y mockups

## Notas Importantes

1. **Seguridad**: El repositorio contiene código empresarial, manténlo privado
2. **Credenciales**: Nunca subas contraseñas o datos sensibles
3. **Sincronización**: Siempre haz `git pull` antes de trabajar
4. **Respaldos**: Git automáticamente respalda tu código en la nube

## Troubleshooting

Si tienes problemas con permisos:
```bash
# Usar autenticación con token personal en lugar de contraseña
# Ve a GitHub → Settings → Developer settings → Personal access tokens
```

Si necesitas cambiar el repositorio remoto:
```bash
git remote set-url origin https://github.com/NUEVO_USUARIO/NOMINA_SYSTEM_RRHH.git
```