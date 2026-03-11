# Guía Paso a Paso para GitHub y GitHub Actions

Esta guía te muestra exactamente qué hacer en GitHub para configurar CI/CD.

## 📋 Tabla de Contenidos

1. [Crear Repositorio en GitHub](#1-crear-repositorio-en-github)
2. [Subir Código a GitHub](#2-subir-código-a-github)
3. [Ver GitHub Actions](#3-ver-github-actions)
4. [Entender los Resultados](#4-entender-los-resultados)
5. [Hacer Cambios y Ver CI](#5-hacer-cambios-y-ver-ci)
6. [Solucionar Problemas](#6-solucionar-problemas)

---

## 1. Crear Repositorio en GitHub

### Paso 1.1: Ir a GitHub

1. Abre tu navegador
2. Ve a https://github.com
3. Inicia sesión con tu cuenta

### Paso 1.2: Crear Nuevo Repositorio

1. Click en el botón **"+"** en la esquina superior derecha
2. Selecciona **"New repository"**

![Crear repositorio](https://docs.github.com/assets/cb-11427/images/help/repository/repo-create.png)

### Paso 1.3: Configurar el Repositorio

Completa el formulario:

- **Repository name**: `taller-testing-ci`
- **Description**: "Taller de Testing y GitHub Actions - Curso de Ingeniería de Datos"
- **Visibility**: Selecciona **Public** (para que GitHub Actions sea gratis)
- **NO marques** "Initialize this repository with:"
  - ❌ NO marques "Add a README file"
  - ❌ NO marques "Add .gitignore"
  - ❌ NO marques "Choose a license"
  
  (Ya tenemos estos archivos localmente)

### Paso 1.4: Crear el Repositorio

1. Click en el botón verde **"Create repository"**
2. Verás una página con instrucciones para subir código

**✅ Checkpoint**: Tienes un repositorio vacío en GitHub.

---

## 2. Subir Código a GitHub

### Paso 2.1: Abrir Terminal

Abre tu terminal en el directorio del taller:

```bash
cd modulo-07_DataOps/taller_github_01_testing
```

### Paso 2.2: Verificar que Git está Inicializado

```bash
git status
```

**Si ves un error** "not a git repository":
```bash
git init
```

### Paso 2.3: Agregar Todos los Archivos

```bash
git add .
```

Este comando agrega todos los archivos al staging area.

### Paso 2.4: Hacer el Primer Commit

```bash
git commit -m "Initial commit: Taller de testing y CI/CD"
```

**Output esperado:**
```
[main (root-commit) abc1234] Initial commit: Taller de testing y CI/CD
 12 files changed, 500 insertions(+)
 create mode 100644 README.md
 create mode 100644 src/transformations.py
 ...
```

### Paso 2.5: Conectar con GitHub

Copia la URL de tu repositorio de GitHub (la verás en la página después de crear el repo).

```bash
# Reemplaza con TU URL
git remote add origin https://github.com/TU-USUARIO/taller-testing-ci.git
```

### Paso 2.6: Renombrar la Rama a 'main'

```bash
git branch -M main
```

### Paso 2.7: Subir el Código

```bash
git push -u origin main
```

**Si es la primera vez**, Git te pedirá autenticación:
- **Opción 1**: Usar GitHub CLI (recomendado)
- **Opción 2**: Usar Personal Access Token
- **Opción 3**: Usar SSH keys

**Output esperado:**
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
Delta compression using up to 8 threads
Compressing objects: 100% (12/12), done.
Writing objects: 100% (15/15), 8.50 KiB | 2.83 MiB/s, done.
Total 15 (delta 2), reused 0 (delta 0), pack-reused 0
To https://github.com/TU-USUARIO/taller-testing-ci.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

**✅ Checkpoint**: Tu código está en GitHub. Refresca la página del repositorio y verás todos tus archivos.

---

## 3. Ver GitHub Actions

### Paso 3.1: Ir a la Pestaña Actions

1. En tu repositorio de GitHub, click en la pestaña **"Actions"** (arriba)
2. Verás tu workflow "Tests" ejecutándose o ya completado

![GitHub Actions Tab](https://docs.github.com/assets/cb-33882/images/help/repository/actions-tab.png)

### Paso 3.2: Ver el Workflow en Ejecución

1. Click en el workflow "Tests"
2. Verás el job "Ejecutar Tests con Pytest"
3. Click en el job para ver los detalles

### Paso 3.3: Ver los Pasos

Verás cada paso ejecutándose:

```
✓ Checkout código
✓ Configurar Python 3.9
✓ Instalar dependencias
✓ Ejecutar tests
```

### Paso 3.4: Ver los Resultados de los Tests

Click en "Ejecutar tests" para expandir y ver:

```
========================= test session starts =========================
collected 11 items

tests/test_basico.py::test_calcular_total_venta_caso_basico PASSED
tests/test_basico.py::test_calcular_total_venta_con_un_producto PASSED
tests/test_basico.py::test_calcular_total_venta_con_decimales PASSED
tests/test_basico.py::test_calcular_total_venta_con_precio_negativo PASSED
tests/test_basico.py::test_calcular_total_venta_con_cantidad_cero PASSED
tests/test_basico.py::test_aplicar_descuento_10_porciento PASSED
tests/test_basico.py::test_aplicar_descuento_sin_descuento PASSED
tests/test_basico.py::test_aplicar_descuento_completo PASSED
tests/test_basico.py::test_aplicar_descuento_con_monto_negativo PASSED
tests/test_basico.py::test_aplicar_descuento_fuera_de_rango PASSED

========================= 11 passed in 0.05s ==========================
```

**✅ Checkpoint**: Ves un ✅ verde indicando que todos los tests pasaron.

---

## 4. Entender los Resultados

### 4.1: Indicadores Visuales

En la pestaña Actions verás:

- **✅ Verde**: Todos los tests pasaron
- **❌ Rojo**: Algún test falló
- **🟡 Amarillo**: El workflow está en ejecución
- **⚪ Gris**: El workflow fue cancelado

### 4.2: Badge de Estado

Puedes agregar un badge a tu README para mostrar el estado:

1. En la pestaña Actions, click en tu workflow
2. Click en el botón "..." (tres puntos)
3. Selecciona "Create status badge"
4. Copia el markdown
5. Pégalo en tu README.md

Ejemplo:
```markdown
![Tests](https://github.com/TU-USUARIO/taller-testing-ci/workflows/Tests/badge.svg)
```

### 4.3: Historial de Ejecuciones

En la pestaña Actions verás todas las ejecuciones pasadas:
- Cuándo se ejecutó
- Quién hizo el commit
- Cuánto tiempo tomó
- Si pasó o falló

**✅ Checkpoint**: Entiendes cómo leer los resultados de CI.

---

## 5. Hacer Cambios y Ver CI

### Paso 5.1: Hacer un Cambio Intencional

Vamos a hacer un cambio para ver cómo CI detecta errores.

Edita `tests/test_basico.py` y cambia un test:

```python
def test_calcular_total_venta_caso_basico():
    precio = 100.0
    cantidad = 2
    resultado = calcular_total_venta(precio, cantidad)
    assert resultado == 999.0  # ❌ Cambio intencional (antes era 200.0)
```

### Paso 5.2: Commit y Push

```bash
git add tests/test_basico.py
git commit -m "Test: cambio intencional para ver CI fallar"
git push
```

### Paso 5.3: Ver el Fallo en GitHub

1. Ve a la pestaña Actions
2. Verás un nuevo workflow ejecutándose
3. Espera a que termine
4. Verás un ❌ rojo

### Paso 5.4: Ver el Error Detallado

1. Click en el workflow que falló
2. Click en "Ejecutar tests"
3. Verás el error:

```
FAILED tests/test_basico.py::test_calcular_total_venta_caso_basico

def test_calcular_total_venta_caso_basico():
    precio = 100.0
    cantidad = 2
    resultado = calcular_total_venta(precio, cantidad)
>   assert resultado == 999.0
E   AssertionError: assert 200.0 == 999.0

tests/test_basico.py:25: AssertionError
```

### Paso 5.5: Corregir el Error

Vuelve a cambiar el test al valor correcto:

```python
assert resultado == 200.0  # ✅ Correcto
```

```bash
git add tests/test_basico.py
git commit -m "Fix: corregir test"
git push
```

### Paso 5.6: Verificar que Ahora Pasa

1. Ve a Actions
2. Verás un nuevo workflow ejecutándose
3. Ahora debería mostrar ✅ verde

**✅ Checkpoint**: Viste cómo CI detecta errores automáticamente.

---

## 6. Solucionar Problemas

### Problema 1: No Veo la Pestaña Actions

**Causa**: Actions puede estar deshabilitado.

**Solución**:
1. Ve a Settings (en tu repositorio)
2. Click en "Actions" en el menú izquierdo
3. Selecciona "Allow all actions and reusable workflows"
4. Click "Save"

### Problema 2: El Workflow No Se Ejecuta

**Causa**: El archivo YAML puede tener errores de sintaxis.

**Solución**:
1. Verifica que el archivo está en `.github/workflows/tests.yml`
2. Verifica la indentación (YAML es sensible a espacios)
3. Usa un validador YAML online: https://www.yamllint.com/

### Problema 3: Error "Permission Denied"

**Causa**: No tienes permisos para hacer push.

**Solución**:
1. Verifica que eres el dueño del repositorio
2. Configura autenticación:
   ```bash
   # Opción 1: GitHub CLI
   gh auth login
   
   # Opción 2: Personal Access Token
   # Ve a Settings > Developer settings > Personal access tokens
   # Genera un token y úsalo como contraseña
   ```

### Problema 4: Tests Pasan Localmente pero Fallan en CI

**Causas posibles**:
- Diferencias de ambiente (Python version, dependencias)
- Paths relativos vs absolutos
- Datos de test no están en el repositorio

**Solución**:
1. Verifica que todos los archivos necesarios están en Git
2. Verifica la versión de Python en el workflow
3. Ejecuta tests localmente con la misma versión de Python

### Problema 5: El Workflow Toma Mucho Tiempo

**Causa**: Instalación de dependencias puede ser lenta.

**Solución** (avanzado):
Agregar caching al workflow:

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)

### Tutoriales

- [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)
- [Understanding GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions)

### Ejemplos de Workflows

- [Python Application](https://github.com/actions/starter-workflows/blob/main/ci/python-app.yml)
- [Python Package](https://github.com/actions/starter-workflows/blob/main/ci/python-package.yml)

---

## 🎯 Checklist Final

Marca cada item que completaste:

- [ ] Creé un repositorio en GitHub
- [ ] Subí mi código a GitHub
- [ ] Vi mi primer workflow ejecutarse
- [ ] Entiendo los indicadores visuales (✅❌🟡)
- [ ] Hice un cambio y vi CI detectar un error
- [ ] Corregí el error y vi CI pasar
- [ ] Sé dónde buscar ayuda si tengo problemas

---

## 🎉 ¡Felicitaciones!

Ahora sabes cómo usar GitHub y GitHub Actions para CI/CD. Esto es una habilidad esencial para cualquier desarrollador moderno.

**Próximos pasos:**
- Explora otros workflows en GitHub Marketplace
- Aprende sobre deployment automatizado
- Investiga sobre code coverage y quality gates

---

**¿Preguntas?** Consulta la documentación oficial o pregunta al instructor del curso.
