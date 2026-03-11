# Taller de Testing y GitHub Actions - Introducción Práctica


## Duración Total: 2 horas

- **Paso 1**: Setup y Configuración (30 minutos)
- **Paso 2**: Tests Básicos con Pytest (30 minutos)
- **Paso 3**: GitHub Actions y CI (30 minutos)
- **Paso 4**: Ejercicio Práctico (30 minutos)


### Verificar Instalaciones

```bash
# Verificar Python
python --version
# Debe mostrar: Python 3.9.x o superior

# Verificar Git
git --version
# Debe mostrar: git version x.x.x
```

## 📁 Estructura del Proyecto

```
taller_github_01_testing/
├── src/
│   └── transformations.py      # Funciones a testear
├── tests/
│   └── test_basico.py          # Tests unitarios
├── data/
│   ├── transactions.csv        # Datos de ejemplo
│   └── README.md
├── ejercicios/
│   ├── ejercicio_guiado.md     # Ejercicio práctico
│   └── solucion_ejercicio.py   # Solución
├── .github/workflows/
│   └── tests.yml               # Workflow de CI
├── README.md                   # Este archivo
├── requirements.txt            # Dependencias
├── pytest.ini                  # Configuración de pytest
└── .gitignore
```

---

# GUÍA PASO A PASO

## PASO 1: Setup y Configuración 

### 1.1 Clonar o Descargar el Repositorio

Si estás trabajando con un repositorio existente:

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd taller_github_01_testing
```

Si estás empezando desde cero, ya tienes los archivos en tu directorio actual.

### 1.2 Crear y Activar Entorno Virtual

Es una buena práctica usar un entorno virtual para aislar las dependencias:

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu línea de comandos.

### 1.3 Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Output esperado:**
```
Collecting pytest==7.4.0
  Downloading pytest-7.4.0-py3-none-any.whl
Installing collected packages: pytest
Successfully installed pytest-7.4.0
```

### 1.4 Explorar el Código

Abre el archivo `src/transformations.py` y revisa las dos funciones:

1. **calcular_total_venta**: Multiplica precio por cantidad
2. **aplicar_descuento**: Aplica un descuento porcentual

**Ejemplo de uso:**
```python
from src.transformations import calcular_total_venta, aplicar_descuento

# Calcular total de 3 productos de $50
total = calcular_total_venta(50.0, 3)
print(total)  # Output: 150.0

# Aplicar 10% de descuento a $100
con_descuento = aplicar_descuento(100.0, 10.0)
print(con_descuento)  # Output: 90.0
```

### 1.5 Ejecutar tu Primer Test

```bash
pytest
```

**Output esperado:**
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

### ✅ Checkpoint 1

Antes de continuar, verifica que:
- [ ] El entorno virtual está activado
- [ ] pytest está instalado
- [ ] Todos los tests pasan (11 passed)
- [ ] Entiendes qué hacen las funciones en `transformations.py`

### 🎓 ¿Qué acabas de aprender?

- Cómo configurar un entorno de desarrollo Python
- Cómo instalar dependencias con pip
- Cómo ejecutar tests con pytest
- La estructura básica de un proyecto con tests

---

## PASO 2: Tests Básicos con Pytest (30 minutos)

### 2.1 Entender el Patrón AAA (Arrange-Act-Assert)

Abre `tests/test_basico.py` y observa el primer test:

```python
def test_calcular_total_venta_caso_basico():
    # Arrange (preparar): definir los datos de entrada
    precio = 100.0
    cantidad = 2
    
    # Act (actuar): ejecutar la función que queremos testear
    resultado = calcular_total_venta(precio, cantidad)
    
    # Assert (afirmar): verificar que el resultado es el esperado
    assert resultado == 200.0
```

**Patrón AAA:**
1. **Arrange**: Preparar los datos de entrada
2. **Act**: Ejecutar la función a testear
3. **Assert**: Verificar que el resultado es correcto

### 2.2 Tipos de Assertions

Pytest usa assertions simples de Python:

```python
# Igualdad
assert resultado == 200.0

# Desigualdad
assert resultado != 0

# Comparaciones
assert resultado > 0
assert resultado < 1000

# Verificar que algo es True/False
assert es_valido == True
assert es_invalido == False
```

### 2.3 Testear Excepciones

Para verificar que una función lanza una excepción cuando recibe datos inválidos:

```python
import pytest

def test_calcular_total_venta_con_precio_negativo():
    with pytest.raises(ValueError):
        calcular_total_venta(-100.0, 2)
```

Esto verifica que la función rechaza precios negativos lanzando un `ValueError`.

### 2.4 Ejecutar Tests Específicos

```bash
# Ejecutar un test específico
pytest tests/test_basico.py::test_calcular_total_venta_caso_basico

# Ejecutar tests que contengan "descuento" en el nombre
pytest -k descuento

# Ejecutar con más detalle
pytest -v

# Ejecutar y mostrar prints
pytest -s
```

### 2.5 Ejercicio Práctico: Escribir tu Primer Test

Vamos a agregar un nuevo test. Crea un archivo `tests/test_mi_primer_test.py`:

```python
"""
Mi primer test - Ejercicio práctico
"""
from src.transformations import aplicar_descuento


def test_aplicar_descuento_50_porciento():
    """
    EJERCICIO: Completa este test.
    
    Debe verificar que aplicar 50% de descuento a $200 da $100.
    """
    # Arrange: preparar los datos
    monto = 200.0
    descuento = 50.0
    
    # Act: ejecutar la función
    resultado = aplicar_descuento(monto, descuento)
    
    # Assert: verificar el resultado
    assert resultado == 100.0
```

Ejecuta tu nuevo test:

```bash
pytest tests/test_mi_primer_test.py -v
```

**Output esperado:**
```
tests/test_mi_primer_test.py::test_aplicar_descuento_50_porciento PASSED
```

### ✅ Checkpoint 2

Antes de continuar, verifica que:
- [ ] Entiendes el patrón AAA (Arrange-Act-Assert)
- [ ] Sabes usar assertions básicas (==, !=, <, >)
- [ ] Sabes testear excepciones con pytest.raises
- [ ] Creaste y ejecutaste tu primer test exitosamente

### 🎓 ¿Qué acabas de aprender?

- El patrón AAA para estructurar tests
- Cómo usar assertions para verificar resultados
- Cómo testear que una función lanza excepciones
- Cómo ejecutar tests específicos
- Cómo escribir tu propio test desde cero

---

## PASO 3: GitHub Actions y CI (30 minutos)

### 3.1 ¿Qué es CI/CD?

**CI (Continuous Integration)**: Integración Continua
- Ejecutar tests automáticamente cada vez que haces cambios
- Detectar errores temprano
- Asegurar que el código siempre funciona

**CD (Continuous Deployment)**: Despliegue Continuo
- Desplegar automáticamente cuando los tests pasan
- (No lo cubriremos en este taller básico)

### 3.2 ¿Qué es GitHub Actions?

GitHub Actions es una herramienta de CI/CD integrada en GitHub que:
- Ejecuta código automáticamente cuando ocurren eventos (push, pull request, etc.)
- Usa archivos YAML para definir qué hacer
- Es gratis para repositorios públicos

### 3.3 Entender el Workflow

Abre `.github/workflows/tests.yml` y revisa el contenido:

```yaml
name: Tests

# Cuándo se ejecuta
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest -v
```

**Componentes clave:**
- **name**: Nombre del workflow
- **on**: Cuándo se ejecuta (push, pull_request)
- **jobs**: Trabajos a ejecutar
- **steps**: Pasos dentro de cada trabajo

### 3.4 Configurar GitHub Actions (Paso a Paso en GitHub)

#### 3.4.1 Crear un Repositorio en GitHub

1. Ve a https://github.com
2. Click en el botón "+" arriba a la derecha
3. Selecciona "New repository"
4. Nombre: `taller-testing-ci`
5. Descripción: "Taller de Testing y GitHub Actions"
6. Selecciona "Public"
7. NO marques "Initialize with README" (ya tenemos archivos)
8. Click "Create repository"

#### 3.4.2 Subir tu Código a GitHub

En tu terminal, dentro del directorio del taller:

```bash
# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Initial commit: Taller de testing"

# Conectar con GitHub (reemplaza con tu URL)
git remote add origin https://github.com/TU-USUARIO/taller-testing-ci.git

# Subir a GitHub
git branch -M main
git push -u origin main
```

#### 3.4.3 Ver el Workflow en Acción

1. Ve a tu repositorio en GitHub
2. Click en la pestaña "Actions" (arriba)
3. Deberías ver tu workflow "Tests" ejecutándose
4. Click en el workflow para ver los detalles
5. Observa cómo se ejecutan los pasos:
   - Checkout código
   - Configurar Python
   - Instalar dependencias
   - Ejecutar tests

**Captura de pantalla esperada:**
```
✓ Checkout código
✓ Configurar Python 3.9
✓ Instalar dependencias
✓ Ejecutar tests
  11 passed in 0.05s
```

### 3.5 Hacer un Cambio y Ver CI en Acción

Vamos a hacer un cambio intencional para ver cómo funciona CI:

#### 3.5.1 Modificar un Test

Edita `tests/test_basico.py` y cambia temporalmente un test para que falle:

```python
def test_calcular_total_venta_caso_basico():
    precio = 100.0
    cantidad = 2
    resultado = calcular_total_venta(precio, cantidad)
    assert resultado == 999.0  # ❌ Esto fallará (antes era 200.0)
```

#### 3.5.2 Commit y Push

```bash
git add tests/test_basico.py
git commit -m "Test: cambio intencional para ver CI fallar"
git push
```

#### 3.5.3 Ver el Fallo en GitHub

1. Ve a la pestaña "Actions" en GitHub
2. Verás un workflow con una ❌ roja
3. Click en el workflow
4. Verás el error:
   ```
   AssertionError: assert 200.0 == 999.0
   ```

#### 3.5.4 Corregir el Test

Vuelve a cambiar el test al valor correcto:

```python
assert resultado == 200.0  # ✅ Correcto
```

```bash
git add tests/test_basico.py
git commit -m "Fix: corregir test"
git push
```

Ahora verás un ✅ verde en GitHub Actions.

### ✅ Checkpoint 3

Antes de continuar, verifica que:
- [ ] Entiendes qué es CI/CD
- [ ] Creaste un repositorio en GitHub
- [ ] Subiste tu código a GitHub
- [ ] Viste el workflow ejecutarse en GitHub Actions
- [ ] Hiciste un cambio y viste cómo CI detecta errores

### 🎓 ¿Qué acabas de aprender?

- Qué es CI/CD y por qué es importante
- Cómo funciona GitHub Actions
- Cómo crear y configurar un workflow
- Cómo ver los resultados de CI en GitHub
- Cómo CI detecta errores automáticamente

---

## PASO 4: Ejercicio Práctico (30 minutos)

### 4.1 Objetivo del Ejercicio

Vas a crear una nueva función y sus tests desde cero, siguiendo todo lo que aprendiste.

### 4.2 Descripción del Ejercicio

**Crear una función `categorizar_cliente`** que clasifica clientes según su total de compras:

- Bronce: $0 - $1,000
- Plata: $1,001 - $5,000
- Oro: $5,001 - $10,000
- Platino: Más de $10,000

### 4.3 Paso a Paso del Ejercicio

#### Paso 4.3.1: Crear la Función

Agrega esta función en `src/transformations.py`:

```python
def categorizar_cliente(total_compras: float) -> str:
    """
    Categoriza un cliente según su total de compras.
    
    Args:
        total_compras: Total acumulado de compras del cliente
    
    Returns:
        Categoría: 'bronce', 'plata', 'oro', 'platino'
    
    Raises:
        ValueError: Si total_compras es negativo
    
    Ejemplo:
        >>> categorizar_cliente(500.0)
        'bronce'
        >>> categorizar_cliente(3000.0)
        'plata'
    """
    # TODO: Implementa esta función
    pass
```

**Pista**: Usa if/elif/else para verificar los rangos.

#### Paso 4.3.2: Crear los Tests

Crea un archivo `tests/test_ejercicio.py` con estos tests:

```python
"""
Tests para la función categorizar_cliente
"""
import pytest
from src.transformations import categorizar_cliente


def test_categorizar_cliente_bronce():
    """Test para categoría bronce (0 - 1000)"""
    # TODO: Completa este test
    pass


def test_categorizar_cliente_plata():
    """Test para categoría plata (1001 - 5000)"""
    # TODO: Completa este test
    pass


def test_categorizar_cliente_oro():
    """Test para categoría oro (5001 - 10000)"""
    # TODO: Completa este test
    pass


def test_categorizar_cliente_platino():
    """Test para categoría platino (> 10000)"""
    # TODO: Completa este test
    pass


def test_categorizar_cliente_negativo():
    """Test que verifica rechazo de valores negativos"""
    # TODO: Completa este test usando pytest.raises
    pass
```

#### Paso 4.3.3: Ejecutar los Tests

```bash
pytest tests/test_ejercicio.py -v
```

Inicialmente fallarán porque la función no está implementada.

#### Paso 4.3.4: Implementar la Función

Completa la función `categorizar_cliente` para que los tests pasen.

#### Paso 4.3.5: Subir a GitHub

```bash
git add src/transformations.py tests/test_ejercicio.py
git commit -m "Feat: agregar función categorizar_cliente con tests"
git push
```

Ve a GitHub Actions y verifica que todos los tests pasan.

### 4.4 Solución del Ejercicio

Si te atascas, aquí está la solución completa:

**Función (src/transformations.py):**
```python
def categorizar_cliente(total_compras: float) -> str:
    if total_compras < 0:
        raise ValueError(f"El total de compras no puede ser negativo: {total_compras}")
    
    if total_compras <= 1000:
        return 'bronce'
    elif total_compras <= 5000:
        return 'plata'
    elif total_compras <= 10000:
        return 'oro'
    else:
        return 'platino'
```

**Tests (tests/test_ejercicio.py):**
```python
def test_categorizar_cliente_bronce():
    assert categorizar_cliente(500.0) == 'bronce'
    assert categorizar_cliente(1000.0) == 'bronce'

def test_categorizar_cliente_plata():
    assert categorizar_cliente(1001.0) == 'plata'
    assert categorizar_cliente(3000.0) == 'plata'
    assert categorizar_cliente(5000.0) == 'plata'

def test_categorizar_cliente_oro():
    assert categorizar_cliente(5001.0) == 'oro'
    assert categorizar_cliente(7500.0) == 'oro'
    assert categorizar_cliente(10000.0) == 'oro'

def test_categorizar_cliente_platino():
    assert categorizar_cliente(10001.0) == 'platino'
    assert categorizar_cliente(50000.0) == 'platino'

def test_categorizar_cliente_negativo():
    with pytest.raises(ValueError):
        categorizar_cliente(-100.0)
```

### ✅ Checkpoint 4 (Final)

Verifica que completaste:
- [ ] Implementaste la función `categorizar_cliente`
- [ ] Creaste tests para todos los casos
- [ ] Todos los tests pasan localmente
- [ ] Subiste el código a GitHub
- [ ] GitHub Actions muestra todos los tests en verde

### 🎓 ¿Qué acabas de aprender?

- Cómo crear una función desde cero con TDD (Test-Driven Development)
- Cómo escribir tests completos para diferentes casos
- Cómo usar Git y GitHub para colaborar
- Cómo CI/CD te ayuda a mantener código de calidad

---

## 🎉 ¡Felicitaciones!

Has completado el taller de Testing y GitHub Actions. Ahora sabes:

✅ Configurar un proyecto Python con tests  
✅ Escribir tests unitarios con pytest  
✅ Usar el patrón AAA (Arrange-Act-Assert)  
✅ Testear excepciones  
✅ Configurar GitHub Actions para CI  
✅ Ver y entender resultados de CI en GitHub  
✅ Aplicar todo en un ejercicio práctico  

## 📚 Próximos Pasos

### Para Profundizar

1. **Fixtures de Pytest**: Reutilizar datos entre tests
2. **Parametrización**: Ejecutar el mismo test con diferentes datos
3. **Mocking**: Simular dependencias externas
4. **Coverage**: Medir qué porcentaje del código está testeado
5. **Tests de Integración**: Testear múltiples componentes juntos

### Recursos Recomendados

- [Documentación oficial de Pytest](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Real Python - Testing](https://realpython.com/pytest-python-testing/)
- [Test-Driven Development (TDD)](https://testdriven.io/)

### Taller Avanzado

Si quieres continuar aprendiendo, consulta el **Taller 2: CI/CD Avanzado y Deployment** que cubre:
- Pipelines multi-etapa
- Deployment automatizado
- Docker y containerización
- Tests de integración
- Validación de calidad de datos

## 🆘 Troubleshooting

### Problema: pytest no se encuentra

```bash
# Solución: Asegúrate de que el entorno virtual está activado
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstala pytest
pip install pytest
```

### Problema: Tests fallan con "ModuleNotFoundError"

```bash
# Solución: Ejecuta pytest desde el directorio raíz del proyecto
cd taller_github_01_testing
pytest
```

### Problema: GitHub Actions no se ejecuta

1. Verifica que el archivo está en `.github/workflows/tests.yml`
2. Verifica que hiciste push a la rama `main`
3. Ve a Settings > Actions y asegúrate de que Actions está habilitado

### Problema: Git push falla

```bash
# Si es la primera vez, configura tu identidad
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Si hay conflictos, pull primero
git pull origin main
```

## 📞 Soporte

Si tienes preguntas o problemas:
1. Revisa la sección de Troubleshooting
2. Consulta la documentación oficial de pytest
3. Pregunta al instructor del curso

---

**¡Gracias por participar en este taller!** 🚀

Recuerda: El testing no es opcional, es una habilidad esencial para cualquier desarrollador profesional.
