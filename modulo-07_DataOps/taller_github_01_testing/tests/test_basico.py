"""
Tests básicos para funciones de transformación.

Este archivo contiene tests simples para aprender pytest.
Cada test está bien comentado para explicar qué hace.
"""
import pytest
from src.transformations import calcular_total_venta, aplicar_descuento


# ============================================================================
# PASO 1: Test más simple posible
# ============================================================================

def test_calcular_total_venta_caso_basico():
    """
    Test básico: verifica que 2 productos de $100 cuestan $200.
    
    Este es el test más simple. Solo verifica un caso de éxito.
    Usamos el patrón AAA (Arrange-Act-Assert):
    - Arrange: preparar los datos
    - Act: ejecutar la función
    - Assert: verificar el resultado
    """
    # Arrange (preparar): definir los datos de entrada
    precio = 100.0
    cantidad = 2
    
    # Act (actuar): ejecutar la función que queremos testear
    resultado = calcular_total_venta(precio, cantidad)
    
    # Assert (afirmar): verificar que el resultado es el esperado
    assert resultado == 200.0


# ============================================================================
# PASO 2: Test con diferentes valores
# ============================================================================

def test_calcular_total_venta_con_un_producto():
    """
    Test con cantidad = 1.
    
    Verifica que la función funciona con un solo producto.
    Este test es importante para verificar el caso límite de cantidad mínima.
    """
    resultado = calcular_total_venta(50.0, 1)
    assert resultado == 50.0


def test_calcular_total_venta_con_decimales():
    """
    Test con precios decimales.
    
    Verifica que la función maneja correctamente precios con decimales.
    """
    resultado = calcular_total_venta(19.99, 3)
    assert resultado == 59.97


# ============================================================================
# PASO 3: Test de validación de errores
# ============================================================================

def test_calcular_total_venta_con_precio_negativo():
    """
    Test que verifica que la función rechaza precios negativos.
    
    Usamos pytest.raises para verificar que se lanza una excepción.
    Esto es importante para asegurar que la función valida sus entradas.
    """
    with pytest.raises(ValueError):
        calcular_total_venta(-100.0, 2)


def test_calcular_total_venta_con_cantidad_cero():
    """
    Test que verifica que la función rechaza cantidad = 0.
    
    La cantidad debe ser al menos 1.
    """
    with pytest.raises(ValueError):
        calcular_total_venta(100.0, 0)


# ============================================================================
# PASO 4: Tests para la función aplicar_descuento
# ============================================================================

def test_aplicar_descuento_10_porciento():
    """
    Test de descuento del 10%.
    
    Verifica que aplicar 10% de descuento a $100 da $90.
    """
    resultado = aplicar_descuento(100.0, 10.0)
    assert resultado == 90.0


def test_aplicar_descuento_sin_descuento():
    """
    Test con descuento de 0%.
    
    Verifica que con 0% de descuento, el monto no cambia.
    """
    resultado = aplicar_descuento(100.0, 0.0)
    assert resultado == 100.0


def test_aplicar_descuento_completo():
    """
    Test con descuento del 100%.
    
    Verifica que con 100% de descuento, el resultado es 0.
    """
    resultado = aplicar_descuento(100.0, 100.0)
    assert resultado == 0.0


def test_aplicar_descuento_con_monto_negativo():
    """
    Test que verifica que la función rechaza montos negativos.
    """
    with pytest.raises(ValueError):
        aplicar_descuento(-100.0, 10.0)


def test_aplicar_descuento_fuera_de_rango():
    """
    Test que verifica que la función rechaza descuentos > 100%.
    """
    with pytest.raises(ValueError):
        aplicar_descuento(100.0, 150.0)
