"""
Paquete de Utilidades para DAGs de Airflow
==========================================

Este paquete contiene módulos helper con funciones reutilizables
para los DAGs del taller de Apache Airflow.

Módulos disponibles:
- db_utils: Funciones para interactuar con PostgreSQL
- validation_utils: Funciones para validación de calidad de datos
"""

from .db_utils import (
    get_postgres_engine,
    load_csv_to_postgres,
    execute_query
)

__all__ = [
    'get_postgres_engine',
    'load_csv_to_postgres',
    'execute_query'
]
