"""
Utilidades de Base de Datos para DAGs de Airflow
=================================================

Este módulo proporciona funciones helper para interactuar con PostgreSQL
desde los DAGs de Airflow. Incluye funcionalidades para:
- Crear conexiones a la base de datos usando SQLAlchemy
- Cargar archivos CSV a tablas de Postgres
- Ejecutar queries SQL y retornar resultados como DataFrames

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from typing import Optional, Union


def get_postgres_engine() -> Engine:
    """
    Crea y retorna un engine de SQLAlchemy para conectarse a PostgreSQL.
    
    La función lee las credenciales de conexión desde variables de entorno
    configuradas en el archivo .env del proyecto. Estas variables son:
    - POSTGRES_USER: Usuario de la base de datos
    - POSTGRES_PASSWORD: Contraseña del usuario
    - POSTGRES_HOST: Host del servidor PostgreSQL
    - POSTGRES_PORT: Puerto del servidor PostgreSQL
    - POSTGRES_DB: Nombre de la base de datos
    
    Returns:
        Engine: Engine de SQLAlchemy configurado para PostgreSQL
        
    Example:
        >>> engine = get_postgres_engine()
        >>> with engine.connect() as conn:
        ...     result = conn.execute("SELECT 1")
        
    Raises:
        ValueError: Si alguna variable de entorno requerida no está configurada
    """
    # Leer credenciales desde variables de entorno
    user = os.getenv('POSTGRES_USER', 'airflow')
    password = os.getenv('POSTGRES_PASSWORD', 'airflow')
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = os.getenv('POSTGRES_PORT', '5432')
    database = os.getenv('POSTGRES_DB', 'airflow')
    
    # Construir string de conexión
    conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    
    # Crear y retornar engine
    engine = create_engine(conn_string)
    
    return engine


def load_csv_to_postgres(
    csv_path: str,
    table_name: str,
    schema: str = 'raw',
    if_exists: str = 'append'
) -> int:
    """
    Carga datos desde un archivo CSV a una tabla de PostgreSQL.
    
    Esta función lee un archivo CSV usando pandas y lo carga a una tabla
    de PostgreSQL usando SQLAlchemy. Es útil para tareas de ingesta de datos
    en los DAGs de Airflow.
    
    Args:
        csv_path: Ruta al archivo CSV a cargar
        table_name: Nombre de la tabla destino en PostgreSQL
        schema: Schema de la base de datos donde crear/insertar la tabla (default: 'raw')
        if_exists: Comportamiento si la tabla ya existe:
                   - 'fail': Lanza error si la tabla existe
                   - 'replace': Elimina la tabla existente y crea una nueva
                   - 'append': Inserta datos a la tabla existente (default)
    
    Returns:
        int: Número de registros cargados exitosamente
        
    Example:
        >>> records_loaded = load_csv_to_postgres(
        ...     csv_path='/opt/airflow/data/raw/transactions.csv',
        ...     table_name='transactions',
        ...     schema='raw',
        ...     if_exists='append'
        ... )
        >>> print(f"Cargados {records_loaded} registros")
        
    Raises:
        FileNotFoundError: Si el archivo CSV no existe
        ValueError: Si el archivo CSV está vacío o mal formado
        SQLAlchemyError: Si hay errores al insertar en la base de datos
    """
    # Validar que el archivo existe
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"El archivo CSV no existe: {csv_path}")
    
    # Leer CSV usando pandas
    df = pd.read_csv(csv_path)
    
    # Validar que el DataFrame no esté vacío
    if df.empty:
        raise ValueError(f"El archivo CSV está vacío: {csv_path}")
    
    # Obtener engine de conexión
    engine = get_postgres_engine()
    
    # Cargar datos a PostgreSQL
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=False,
        method='multi'  # Inserciones por lotes para mejor performance
    )
    
    # Retornar número de registros cargados
    return len(df)


def execute_query(
    query: str,
    params: Optional[dict] = None
) -> pd.DataFrame:
    """
    Ejecuta una query SQL y retorna los resultados como un DataFrame de pandas.
    
    Esta función es útil para extraer datos desde PostgreSQL en tareas de
    transformación y análisis dentro de los DAGs de Airflow.
    
    Args:
        query: Query SQL a ejecutar (puede incluir placeholders para parámetros)
        params: Diccionario opcional con parámetros para la query (default: None)
                Los parámetros se usan para prevenir SQL injection
    
    Returns:
        pd.DataFrame: DataFrame con los resultados de la query
        
    Example:
        >>> # Query simple sin parámetros
        >>> df = execute_query("SELECT * FROM raw.transactions LIMIT 10")
        
        >>> # Query con parámetros (recomendado para valores dinámicos)
        >>> df = execute_query(
        ...     "SELECT * FROM raw.transactions WHERE transaction_date = %(date)s",
        ...     params={'date': '2024-01-01'}
        ... )
        
    Raises:
        SQLAlchemyError: Si hay errores al ejecutar la query
        
    Note:
        Para queries de INSERT, UPDATE o DELETE que no retornan resultados,
        esta función retornará un DataFrame vacío. Para esos casos, considera
        usar directamente el engine con execute().
    """
    # Obtener engine de conexión
    engine = get_postgres_engine()
    
    # Ejecutar query y retornar resultados como DataFrame
    df = pd.read_sql(query, con=engine, params=params)
    
    return df
