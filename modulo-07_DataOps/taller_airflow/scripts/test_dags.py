#!/usr/bin/env python3
"""
Script de prueba para validar la estructura de los DAGs de Airflow.
Este script verifica que los DAGs se puedan importar correctamente
y que tengan la estructura esperada.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio de DAGs al path
dags_dir = Path(__file__).parent.parent / 'dags'
sys.path.insert(0, str(dags_dir))

def test_dag_import(dag_file):
    """Intenta importar un DAG y verifica su estructura básica."""
    try:
        # Importar el módulo
        module_name = dag_file.stem
        spec = __import__(module_name)
        
        # Verificar que tenga un objeto 'dag'
        if hasattr(spec, 'dag'):
            dag = spec.dag
            print(f"✅ {dag_file.name}")
            print(f"   DAG ID: {dag.dag_id}")
            print(f"   Schedule: {dag.schedule_interval}")
            print(f"   Tasks: {len(dag.tasks)}")
            return True
        else:
            print(f"❌ {dag_file.name} - No se encontró objeto 'dag'")
            return False
            
    except Exception as e:
        print(f"❌ {dag_file.name} - Error: {str(e)}")
        return False

def main():
    """Ejecuta las pruebas de todos los DAGs."""
    print("="*70)
    print("VALIDACIÓN DE DAGS DE AIRFLOW")
    print("="*70)
    print()
    
    # Listar todos los archivos de DAGs
    dag_files = sorted(dags_dir.glob('0*_dag_*.py'))
    
    if not dag_files:
        print("⚠️  No se encontraron archivos de DAGs")
        return 1
    
    print(f"Encontrados {len(dag_files)} DAGs para validar:\n")
    
    # Probar cada DAG
    results = []
    for dag_file in dag_files:
        result = test_dag_import(dag_file)
        results.append(result)
        print()
    
    # Resumen
    print("="*70)
    print("RESUMEN")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"✅ Exitosos: {passed}/{total}")
    
    if passed < total:
        print(f"❌ Fallidos: {total - passed}/{total}")
        return 1
    else:
        print("\n🎉 Todos los DAGs son válidos!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
