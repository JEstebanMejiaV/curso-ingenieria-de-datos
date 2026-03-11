"""
Módulo de transformaciones de datos para e-commerce.

Este módulo contiene funciones simples para practicar testing unitario.
"""


def calcular_total_venta(precio: float, cantidad: int) -> float:
    """
    Calcula el total de una venta (precio * cantidad).
    
    Esta es una función simple para practicar tests básicos.
    
    Args:
        precio: Precio unitario del producto (debe ser >= 0)
        cantidad: Cantidad de productos (debe ser >= 1)
    
    Returns:
        Total de la venta
    
    Raises:
        ValueError: Si precio es negativo o cantidad es menor a 1
    
    Ejemplo:
        >>> calcular_total_venta(100.0, 2)
        200.0
    """
    # Validar que el precio no sea negativo
    if precio < 0:
        raise ValueError(f"El precio no puede ser negativo: {precio}")
    
    # Validar que la cantidad sea al menos 1
    if cantidad < 1:
        raise ValueError(f"La cantidad debe ser al menos 1: {cantidad}")
    
    # Calcular y retornar el total
    return precio * cantidad


def aplicar_descuento(monto: float, porcentaje_descuento: float) -> float:
    """
    Aplica un descuento porcentual a un monto.
    
    Args:
        monto: Monto original (debe ser >= 0)
        porcentaje_descuento: Porcentaje de descuento entre 0 y 100
    
    Returns:
        Monto con descuento aplicado
    
    Raises:
        ValueError: Si monto es negativo o descuento fuera de rango 0-100
    
    Ejemplo:
        >>> aplicar_descuento(100.0, 10.0)
        90.0
    """
    # Validar que el monto no sea negativo
    if monto < 0:
        raise ValueError(f"El monto no puede ser negativo: {monto}")
    
    # Validar que el descuento esté entre 0 y 100
    if not 0 <= porcentaje_descuento <= 100:
        raise ValueError(f"El descuento debe estar entre 0 y 100: {porcentaje_descuento}")
    
    # Calcular el monto con descuento
    descuento = monto * (porcentaje_descuento / 100)
    return monto - descuento
