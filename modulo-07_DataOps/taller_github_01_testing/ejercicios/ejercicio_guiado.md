# Ejercicio Práctico Guiado: Función categorizar_cliente

## 🎯 Objetivo

Crear una función que categoriza clientes según su total de compras y escribir tests completos para ella.

## ⏱️ Tiempo Estimado: 30 minutos

## 📝 Descripción

Vas a implementar una función `categorizar_cliente` que clasifica clientes en 4 categorías según su historial de compras:

| Categoría | Rango de Compras |
|-----------|------------------|
| Bronce    | $0 - $1,000      |
| Plata     | $1,001 - $5,000  |
| Oro       | $5,001 - $10,000 |
| Platino   | Más de $10,000   |

## 📋 Requisitos

La función debe:
1. Recibir un número (float) representando el total de compras
2. Retornar un string con la categoría ('bronce', 'plata', 'oro', 'platino')
3. Lanzar `ValueError` si el total es negativo

## 🚀 Paso a Paso

### Paso 1: Crear la Firma de la Función (5 minutos)

Abre `src/transformations.py` y agrega al final:

```python
def categorizar_cliente(total_compras: float) -> str:
    """
    Categoriza un cliente según su total de compras.
    
    Args:
        total_compras: Total acumulado de compras del cliente (debe ser >= 0)
    
    Returns:
        Categoría: 'bronce', 'plata', 'oro', 'platino'
    
    Raises:
        ValueError: Si total_compras es negativo
    
    Ejemplos:
        >>> categorizar_cliente(500.0)
        'bronce'
        >>> categorizar_cliente(3000.0)
        'plata'
        >>> categorizar_cliente(7500.0)
        'oro'
        >>> categorizar_cliente(15000.0)
        'platino'
    """
    # TODO: Implementa la lógica aquí
    pass
```

**✅ Checkpoint**: La función está definida pero no implementada.

### Paso 2: Crear el Archivo de Tests (5 minutos)

Crea un nuevo archivo `tests/test_ejercicio.py`:

```python
"""
Tests para la función categorizar_cliente
"""
import pytest
from src.transformations import categorizar_cliente


def test_categorizar_cliente_bronce_minimo():
    """Test con el valor mínimo de bronce (0)"""
    resultado = categorizar_cliente(0.0)
    assert resultado == 'bronce'


def test_categorizar_cliente_bronce_maximo():
    """Test con el valor máximo de bronce (1000)"""
    resultado = categorizar_cliente(1000.0)
    assert resultado == 'bronce'


def test_categorizar_cliente_plata_minimo():
    """Test con el valor mínimo de plata (1001)"""
    resultado = categorizar_cliente(1001.0)
    assert resultado == 'plata'


def test_categorizar_cliente_plata_medio():
    """Test con un valor medio de plata"""
    resultado = categorizar_cliente(3000.0)
    assert resultado == 'plata'


def test_categorizar_cliente_plata_maximo():
    """Test con el valor máximo de plata (5000)"""
    resultado = categorizar_cliente(5000.0)
    assert resultado == 'plata'


def test_categorizar_cliente_oro_minimo():
    """Test con el valor mínimo de oro (5001)"""
    resultado = categorizar_cliente(5001.0)
    assert resultado == 'oro'


def test_categorizar_cliente_oro_medio():
    """Test con un valor medio de oro"""
    resultado = categorizar_cliente(7500.0)
    assert resultado == 'oro'


def test_categorizar_cliente_oro_maximo():
    """Test con el valor máximo de oro (10000)"""
    resultado = categorizar_cliente(10000.0)
    assert resultado == 'oro'


def test_categorizar_cliente_platino_minimo():
    """Test con el valor mínimo de platino (10001)"""
    resultado = categorizar_cliente(10001.0)
    assert resultado == 'platino'


def test_categorizar_cliente_platino_alto():
    """Test con un valor alto de platino"""
    resultado = categorizar_cliente(50000.0)
    assert resultado == 'platino'


def test_categorizar_cliente_negativo():
    """Test que verifica rechazo de valores negativos"""
    with pytest.raises(ValueError):
        categorizar_cliente(-100.0)
```

**✅ Checkpoint**: Tienes 11 tests definidos.

### Paso 3: Ejecutar los Tests (Deben Fallar) (2 minutos)

```bash
pytest tests/test_ejercicio.py -v
```

**Output esperado:**
```
FAILED tests/test_ejercicio.py::test_categorizar_cliente_bronce_minimo
FAILED tests/test_ejercicio.py::test_categorizar_cliente_bronce_maximo
... (todos fallan porque la función no está implementada)
```

Esto es normal y esperado. Es parte del proceso TDD (Test-Driven Development):
1. ❌ Escribir tests que fallan
2. ✅ Implementar código para que pasen
3. 🔄 Refactorizar si es necesario

### Paso 4: Implementar la Función (10 minutos)

Ahora implementa la lógica en `src/transformations.py`:

```python
def categorizar_cliente(total_compras: float) -> str:
    """
    Categoriza un cliente según su total de compras.
    
    Args:
        total_compras: Total acumulado de compras del cliente (debe ser >= 0)
    
    Returns:
        Categoría: 'bronce', 'plata', 'oro', 'platino'
    
    Raises:
        ValueError: Si total_compras es negativo
    
    Ejemplos:
        >>> categorizar_cliente(500.0)
        'bronce'
        >>> categorizar_cliente(3000.0)
        'plata'
    """
    # Validar que el total no sea negativo
    if total_compras < 0:
        raise ValueError(f"El total de compras no puede ser negativo: {total_compras}")
    
    # Categorizar según rangos
    if total_compras <= 1000:
        return 'bronce'
    elif total_compras <= 5000:
        return 'plata'
    elif total_compras <= 10000:
        return 'oro'
    else:
        return 'platino'
```

**💡 Explicación del código:**
- Primero validamos que el total no sea negativo
- Usamos if/elif/else para verificar los rangos en orden
- Retornamos el string correspondiente a cada categoría

### Paso 5: Ejecutar los Tests (Deben Pasar) (2 minutos)

```bash
pytest tests/test_ejercicio.py -v
```

**Output esperado:**
```
tests/test_ejercicio.py::test_categorizar_cliente_bronce_minimo PASSED
tests/test_ejercicio.py::test_categorizar_cliente_bronce_maximo PASSED
tests/test_ejercicio.py::test_categorizar_cliente_plata_minimo PASSED
tests/test_ejercicio.py::test_categorizar_cliente_plata_medio PASSED
tests/test_ejercicio.py::test_categorizar_cliente_plata_maximo PASSED
tests/test_ejercicio.py::test_categorizar_cliente_oro_minimo PASSED
tests/test_ejercicio.py::test_categorizar_cliente_oro_medio PASSED
tests/test_ejercicio.py::test_categorizar_cliente_oro_maximo PASSED
tests/test_ejercicio.py::test_categorizar_cliente_platino_minimo PASSED
tests/test_ejercicio.py::test_categorizar_cliente_platino_alto PASSED
tests/test_ejercicio.py::test_categorizar_cliente_negativo PASSED

========================= 11 passed in 0.05s ==========================
```

**✅ Checkpoint**: ¡Todos los tests pasan!

### Paso 6: Ejecutar TODOS los Tests del Proyecto (2 minutos)

```bash
pytest -v
```

Deberías ver que todos los tests del proyecto pasan (los 11 originales + los 11 nuevos = 22 tests).

### Paso 7: Commit y Push a GitHub (4 minutos)

```bash
# Ver qué archivos cambiaron
git status

# Agregar los archivos modificados
git add src/transformations.py tests/test_ejercicio.py

# Hacer commit con mensaje descriptivo
git commit -m "Feat: agregar función categorizar_cliente con tests completos"

# Subir a GitHub
git push
```

### Paso 8: Verificar en GitHub Actions (2 minutos)

1. Ve a tu repositorio en GitHub
2. Click en la pestaña "Actions"
3. Verás un nuevo workflow ejecutándose
4. Espera a que termine (debería mostrar ✅ verde)
5. Click en el workflow para ver los detalles
6. Verás que se ejecutaron 22 tests y todos pasaron

**✅ Checkpoint Final**: Tu código está en GitHub y CI confirma que todo funciona.

## 🎯 Criterios de Auto-Evaluación

Marca cada criterio que cumpliste:

- [ ] La función `categorizar_cliente` está implementada
- [ ] La función valida que el total no sea negativo
- [ ] La función retorna 'bronce' para valores 0-1000
- [ ] La función retorna 'plata' para valores 1001-5000
- [ ] La función retorna 'oro' para valores 5001-10000
- [ ] La función retorna 'platino' para valores > 10000
- [ ] Todos los 11 tests pasan localmente
- [ ] El código está en GitHub
- [ ] GitHub Actions muestra todos los tests en verde

## 🎓 ¿Qué Aprendiste?

- ✅ TDD (Test-Driven Development): escribir tests antes del código
- ✅ Cómo testear casos límite (valores en los bordes de los rangos)
- ✅ Cómo testear múltiples casos para la misma función
- ✅ Cómo usar Git para versionar tu código
- ✅ Cómo CI/CD valida automáticamente tu código

## 🚀 Desafío Extra (Opcional)

Si terminaste antes de tiempo, intenta:

1. **Agregar más tests**: ¿Qué pasa con valores decimales como 1000.50?
2. **Refactorizar**: ¿Puedes hacer la función más eficiente?
3. **Documentación**: Agrega más ejemplos en el docstring
4. **Edge cases**: ¿Qué pasa con valores muy grandes como 1,000,000?

## 💡 Pistas

Si te atascas:

**Pista 1 (Validación):**
```python
if total_compras < 0:
    raise ValueError("mensaje de error")
```

**Pista 2 (Rangos):**
```python
if total_compras <= 1000:
    return 'bronce'
elif total_compras <= 5000:
    return 'plata'
# ... continúa con oro y platino
```

**Pista 3 (Tests de Excepción):**
```python
with pytest.raises(ValueError):
    categorizar_cliente(-100.0)
```

## ✅ Solución Completa

Si necesitas ver la solución completa, revisa el archivo `solucion_ejercicio.py` en este mismo directorio.

---

**¡Felicitaciones por completar el ejercicio!** 🎉

Has aplicado todo lo aprendido en el taller:
- Testing unitario con pytest
- Patrón AAA
- Validación de excepciones
- Git y GitHub
- CI/CD con GitHub Actions
