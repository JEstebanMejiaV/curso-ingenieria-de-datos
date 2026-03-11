"""
SOLUCIÓN COMPLETA DEL EJERCICIO

Este archivo contiene la solución completa del ejercicio práctico.
Incluye tanto la función como los tests.

NO MIRES ESTA SOLUCIÓN hasta que hayas intentado resolver el ejercicio por tu cuenta.
"""

# ============================================================================
# PARTE 1: FUNCIÓN (agregar en src/transformations.py)
# ============================================================================

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
    # Validar que el total no sea negativo
    if total_compras < 0:
        raise ValueError(f"El total de compras no puede ser negativo: {total_compras}")
    
    # Categorizar según rangos
    # Usamos <= para incluir el límite superior en cada categoría
    if total_compras <= 1000:
        return 'bronce'
    elif total_compras <= 5000:
        return 'plata'
    elif total_compras <= 10000:
        return 'oro'
    else:
        return 'platino'


# ============================================================================
# PARTE 2: TESTS (crear archivo tests/test_ejercicio.py)
# ============================================================================

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


# ============================================================================
# EXPLICACIÓN DE LA SOLUCIÓN
# ============================================================================

"""
EXPLICACIÓN DETALLADA:

1. VALIDACIÓN:
   - Primero verificamos que el total no sea negativo
   - Si es negativo, lanzamos ValueError con mensaje descriptivo

2. LÓGICA DE CATEGORIZACIÓN:
   - Usamos if/elif/else para verificar rangos en orden
   - Cada condición usa <= para incluir el límite superior
   - El orden importa: verificamos de menor a mayor
   
3. RANGOS:
   - Bronce: 0 <= total <= 1000
   - Plata: 1001 <= total <= 5000
   - Oro: 5001 <= total <= 10000
   - Platino: total > 10000

4. TESTS:
   - Testeamos los valores límite de cada categoría (importante!)
   - Testeamos valores medios para asegurar que el rango completo funciona
   - Testeamos la validación de valores negativos
   
5. PATRÓN AAA EN LOS TESTS:
   - Arrange: preparar el valor de entrada
   - Act: llamar a la función
   - Assert: verificar el resultado

MEJORES PRÁCTICAS APLICADAS:
✅ Validación de entrada
✅ Mensajes de error descriptivos
✅ Docstring completo con ejemplos
✅ Tests para casos límite
✅ Tests para casos de error
✅ Nombres de tests descriptivos
✅ Comentarios explicativos

COMANDOS PARA EJECUTAR:
1. Agregar la función a src/transformations.py
2. Crear tests/test_ejercicio.py con los tests
3. Ejecutar: pytest tests/test_ejercicio.py -v
4. Commit: git add . && git commit -m "Feat: categorizar_cliente"
5. Push: git push
6. Verificar en GitHub Actions
"""
