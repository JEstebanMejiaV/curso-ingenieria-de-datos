"""
Utilidades de Validación de Calidad de Datos para DAGs de Airflow
==================================================================

Este módulo proporciona funciones para validar la calidad de datos en pipelines
de Airflow. Incluye validaciones comunes como:
- Detección de valores nulos en columnas críticas
- Validación de rangos de valores numéricos
- Validación de unicidad de identificadores

Estas funciones están diseñadas para ser usadas en tareas de validación de calidad
dentro de los DAGs, especialmente en el DAG 03 de validación de calidad.

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

import pandas as pd
from typing import List, Dict, Union, Any


def validate_nulls(df: pd.DataFrame, columns: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Valida que las columnas especificadas no contengan valores nulos.
    
    Esta función es útil para verificar la integridad de datos en columnas críticas
    como identificadores, fechas obligatorias, o campos de negocio esenciales.
    
    Args:
        df: DataFrame de pandas a validar
        columns: Lista de nombres de columnas a verificar por valores nulos
    
    Returns:
        Dict[str, Dict[str, Any]]: Diccionario con resultados de validación por columna.
            Cada entrada contiene:
            - 'passed': bool indicando si la validación pasó (sin nulos)
            - 'null_count': int con el número de valores nulos encontrados
            
    Example:
        >>> df = pd.DataFrame({
        ...     'transaction_id': ['T1', 'T2', None, 'T4'],
        ...     'amount': [100, 200, 300, 400],
        ...     'customer_id': ['C1', None, 'C3', 'C4']
        ... })
        >>> results = validate_nulls(df, ['transaction_id', 'customer_id'])
        >>> print(results)
        {
            'transaction_id': {'passed': False, 'null_count': 1},
            'customer_id': {'passed': False, 'null_count': 1}
        }
        
    Note:
        Esta función considera como nulos: None, np.nan, pd.NA, pd.NaT
        
    Raises:
        KeyError: Si alguna columna especificada no existe en el DataFrame
    """
    results = {}
    
    for col in columns:
        # Verificar que la columna existe
        if col not in df.columns:
            raise KeyError(f"La columna '{col}' no existe en el DataFrame")
        
        # Contar valores nulos
        null_count = df[col].isnull().sum()
        
        # Almacenar resultados
        results[col] = {
            'passed': null_count == 0,
            'null_count': int(null_count)
        }
    
    return results


def validate_range(
    df: pd.DataFrame,
    column: str,
    min_val: Union[int, float],
    max_val: Union[int, float]
) -> Dict[str, Any]:
    """
    Valida que los valores de una columna numérica estén dentro de un rango esperado.
    
    Esta función es útil para detectar valores anómalos o errores de entrada de datos
    en columnas numéricas como montos, cantidades, porcentajes, etc.
    
    Args:
        df: DataFrame de pandas a validar
        column: Nombre de la columna numérica a validar
        min_val: Valor mínimo permitido (inclusivo)
        max_val: Valor máximo permitido (inclusivo)
    
    Returns:
        Dict[str, Any]: Diccionario con resultados de validación:
            - 'passed': bool indicando si todos los valores están en rango
            - 'out_of_range_count': int con el número de valores fuera de rango
            - 'min_value': valor mínimo encontrado en los datos
            - 'max_value': valor máximo encontrado en los datos
            
    Example:
        >>> df = pd.DataFrame({
        ...     'amount': [100, 200, -50, 300, 150000]
        ... })
        >>> result = validate_range(df, 'amount', min_val=0, max_val=100000)
        >>> print(result)
        {
            'passed': False,
            'out_of_range_count': 2,
            'min_value': -50,
            'max_value': 150000
        }
        
    Note:
        - Los valores nulos (NaN) son ignorados en la validación
        - Los límites min_val y max_val son inclusivos
        - Si la columna está vacía o solo contiene nulos, passed será True
        
    Raises:
        KeyError: Si la columna especificada no existe en el DataFrame
        TypeError: Si la columna no es de tipo numérico
    """
    # Verificar que la columna existe
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")
    
    # Verificar que la columna es numérica
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise TypeError(f"La columna '{column}' no es de tipo numérico")
    
    # Filtrar valores no nulos para la validación
    non_null_values = df[column].dropna()
    
    # Si no hay valores no nulos, la validación pasa
    if len(non_null_values) == 0:
        return {
            'passed': True,
            'out_of_range_count': 0,
            'min_value': None,
            'max_value': None
        }
    
    # Encontrar valores fuera de rango
    out_of_range = df[(df[column] < min_val) | (df[column] > max_val)]
    
    # Calcular estadísticas
    min_value = float(non_null_values.min())
    max_value = float(non_null_values.max())
    
    return {
        'passed': len(out_of_range) == 0,
        'out_of_range_count': len(out_of_range),
        'min_value': min_value,
        'max_value': max_value
    }


def validate_uniqueness(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Valida que los valores de una columna sean únicos (sin duplicados).
    
    Esta función es esencial para verificar la integridad de identificadores únicos
    como IDs de transacciones, clientes, productos, etc.
    
    Args:
        df: DataFrame de pandas a validar
        column: Nombre de la columna a verificar por unicidad
    
    Returns:
        Dict[str, Any]: Diccionario con resultados de validación:
            - 'passed': bool indicando si todos los valores son únicos
            - 'duplicate_count': int con el número de registros duplicados
            - 'unique_count': int con el número de valores únicos
            - 'total_count': int con el número total de registros (excluyendo nulos)
            
    Example:
        >>> df = pd.DataFrame({
        ...     'transaction_id': ['T1', 'T2', 'T3', 'T2', 'T4', 'T1']
        ... })
        >>> result = validate_uniqueness(df, 'transaction_id')
        >>> print(result)
        {
            'passed': False,
            'duplicate_count': 4,
            'unique_count': 4,
            'total_count': 6
        }
        
    Note:
        - Los valores nulos (NaN) son ignorados en la validación de unicidad
        - duplicate_count incluye TODAS las ocurrencias de valores duplicados,
          no solo las repeticiones adicionales
        - Si hay 2 registros con valor 'A', duplicate_count será 2, no 1
        
    Raises:
        KeyError: Si la columna especificada no existe en el DataFrame
    """
    # Verificar que la columna existe
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")
    
    # Filtrar valores no nulos
    non_null_df = df[df[column].notna()]
    
    # Encontrar duplicados (mantiene todas las ocurrencias de valores duplicados)
    duplicates = non_null_df[non_null_df.duplicated(subset=[column], keep=False)]
    
    # Calcular estadísticas
    unique_count = non_null_df[column].nunique()
    total_count = len(non_null_df)
    duplicate_count = len(duplicates)
    
    return {
        'passed': duplicate_count == 0,
        'duplicate_count': duplicate_count,
        'unique_count': unique_count,
        'total_count': total_count
    }
