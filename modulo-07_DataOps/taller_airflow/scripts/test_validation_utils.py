"""
Script de prueba para validar las funciones de validation_utils.py

Este script ejecuta pruebas básicas de las funciones de validación
para asegurar que funcionan correctamente antes de usarlas en los DAGs.
"""

import sys
import os
import pandas as pd

# Agregar el directorio dags al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dags'))

from utils.validation_utils import validate_nulls, validate_range, validate_uniqueness


def test_validate_nulls():
    """Prueba la función validate_nulls"""
    print("\n=== Test validate_nulls ===")
    
    # Crear DataFrame de prueba
    df = pd.DataFrame({
        'transaction_id': ['T1', 'T2', None, 'T4', 'T5'],
        'amount': [100, 200, 300, 400, 500],
        'customer_id': ['C1', None, 'C3', 'C4', None]
    })
    
    # Ejecutar validación
    results = validate_nulls(df, ['transaction_id', 'customer_id', 'amount'])
    
    # Mostrar resultados
    for col, result in results.items():
        status = "✓ PASS" if result['passed'] else "✗ FAIL"
        print(f"  {col}: {status} - {result['null_count']} nulos")
    
    # Verificar resultados esperados
    assert results['transaction_id']['passed'] == False
    assert results['transaction_id']['null_count'] == 1
    assert results['customer_id']['passed'] == False
    assert results['customer_id']['null_count'] == 2
    assert results['amount']['passed'] == True
    assert results['amount']['null_count'] == 0
    
    print("  ✓ Todas las aserciones pasaron")


def test_validate_range():
    """Prueba la función validate_range"""
    print("\n=== Test validate_range ===")
    
    # Crear DataFrame de prueba
    df = pd.DataFrame({
        'amount': [100, 200, -50, 300, 150000, 5000]
    })
    
    # Ejecutar validación
    result = validate_range(df, 'amount', min_val=0, max_val=100000)
    
    # Mostrar resultados
    status = "✓ PASS" if result['passed'] else "✗ FAIL"
    print(f"  Validación: {status}")
    print(f"  Valores fuera de rango: {result['out_of_range_count']}")
    print(f"  Rango encontrado: [{result['min_value']}, {result['max_value']}]")
    
    # Verificar resultados esperados
    assert result['passed'] == False
    assert result['out_of_range_count'] == 2  # -50 y 150000
    assert result['min_value'] == -50
    assert result['max_value'] == 150000
    
    print("  ✓ Todas las aserciones pasaron")


def test_validate_uniqueness():
    """Prueba la función validate_uniqueness"""
    print("\n=== Test validate_uniqueness ===")
    
    # Crear DataFrame de prueba
    df = pd.DataFrame({
        'transaction_id': ['T1', 'T2', 'T3', 'T2', 'T4', 'T1', 'T5']
    })
    
    # Ejecutar validación
    result = validate_uniqueness(df, 'transaction_id')
    
    # Mostrar resultados
    status = "✓ PASS" if result['passed'] else "✗ FAIL"
    print(f"  Validación: {status}")
    print(f"  Total de registros: {result['total_count']}")
    print(f"  Valores únicos: {result['unique_count']}")
    print(f"  Registros duplicados: {result['duplicate_count']}")
    
    # Verificar resultados esperados
    assert result['passed'] == False
    assert result['total_count'] == 7
    assert result['unique_count'] == 5  # T1, T2, T3, T4, T5
    assert result['duplicate_count'] == 4  # T1(2), T2(2)
    
    print("  ✓ Todas las aserciones pasaron")


def test_edge_cases():
    """Prueba casos extremos"""
    print("\n=== Test casos extremos ===")
    
    # DataFrame vacío
    df_empty = pd.DataFrame({'col': []})
    result = validate_nulls(df_empty, ['col'])
    assert result['col']['passed'] == True
    print("  ✓ DataFrame vacío manejado correctamente")
    
    # DataFrame solo con nulos
    df_all_nulls = pd.DataFrame({'col': [None, None, None]})
    result = validate_nulls(df_all_nulls, ['col'])
    assert result['col']['passed'] == False
    assert result['col']['null_count'] == 3
    print("  ✓ DataFrame con solo nulos manejado correctamente")
    
    # Validación de rango con todos los valores en rango
    df_in_range = pd.DataFrame({'amount': [10, 20, 30, 40, 50]})
    result = validate_range(df_in_range, 'amount', min_val=0, max_val=100)
    assert result['passed'] == True
    print("  ✓ Validación de rango con valores válidos manejada correctamente")
    
    # Validación de unicidad con todos valores únicos
    df_unique = pd.DataFrame({'id': ['A', 'B', 'C', 'D']})
    result = validate_uniqueness(df_unique, 'id')
    assert result['passed'] == True
    assert result['duplicate_count'] == 0
    print("  ✓ Validación de unicidad con valores únicos manejada correctamente")


if __name__ == '__main__':
    print("=" * 60)
    print("Ejecutando pruebas de validation_utils.py")
    print("=" * 60)
    
    try:
        test_validate_nulls()
        test_validate_range()
        test_validate_uniqueness()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ ERROR: Una aserción falló")
        print(f"  {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
