"""
Solución Ejercicio 01: DAG de Ingesta de Eventos Web
=====================================================

Este DAG implementa un pipeline completo de ingesta de eventos web desde archivos CSV
a PostgreSQL. Demuestra los conceptos fundamentales de Airflow:

- Configuración básica de DAGs
- Uso de TaskFlow API con decoradores @task
- Encadenamiento de tareas con dependencias
- Lectura y validación de archivos CSV
- Carga de datos a PostgreSQL
- Manejo de errores y logging
- Registro de auditoría

Caso de uso: Ingesta diaria de eventos de navegación web para análisis de comportamiento
de usuarios en plataforma e-commerce.

Autor: Solución de Referencia - Taller de Apache Airflow
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
import pandas as pd
import os
from utils.db_utils import get_postgres_engine, execute_query

# ============================================================================
# CONFIGURACIÓN DEL DAG
# ============================================================================

# Argumentos por defecto para todas las tareas
default_args = {
    'owner': 'estudiante',  # Cambiar por tu nombre
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,  # Reintentar 2 veces si falla
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG
dag = DAG(
    dag_id='ejercicio_01_ingesta_eventos_web',
    default_args=default_args,
    description='Pipeline de ingesta de eventos web desde CSV a PostgreSQL',
    schedule_interval='@daily',  # Ejecutar diariamente
    start_date=datetime(2024, 1, 1),
    catchup=False,  # No ejecutar para fechas pasadas
    tags=['ejercicio', 'ingesta', 'eventos_web'],
    doc_md=__doc__,
)

# ============================================================================
# TAREAS DEL DAG
# ============================================================================

@task(dag=dag)
def check_source_file(**context):
    """
    Verifica que el archivo CSV de eventos web existe y es accesible.
    
    Esta tarea valida:
    - Existencia del archivo
    - Permisos de lectura
    - Tamaño del archivo (no vacío)
    
    Returns:
        dict: Información sobre el archivo (ruta, tamaño, etc.)
    
    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    print("🔍 Verificando existencia del archivo de eventos web...")
    
    # Definir ruta del archivo
    file_path = '/opt/airflow/data/raw/web_events.csv'
    
    # Verificar existencia
    if not os.path.exists(file_path):
        error_msg = f"❌ ERROR: Archivo no encontrado en {file_path}"
        print(error_msg)
        raise FileNotFoundError(error_msg)
    
    # Verificar que no esté vacío
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        error_msg = f"❌ ERROR: Archivo está vacío: {file_path}"
        print(error_msg)
        raise ValueError(error_msg)
    
    # Información del archivo
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Archivo encontrado: {file_path}")
    print(f"📊 Tamaño del archivo: {file_size_mb:.2f} MB ({file_size:,} bytes)")
    
    # Retornar información del archivo
    return {
        'file_path': file_path,
        'file_size_bytes': file_size,
        'file_size_mb': round(file_size_mb, 2),
        'check_timestamp': datetime.now().isoformat()
    }


@task(dag=dag)
def create_table(**context):
    """
    Crea la tabla raw.web_events en PostgreSQL si no existe.
    
    La tabla almacena eventos de navegación web con la siguiente estructura:
    - event_id: Identificador único del evento (PK)
    - user_id: Identificador del usuario
    - event_type: Tipo de evento (page_view, add_to_cart, purchase, etc.)
    - page_url: URL de la página
    - timestamp: Fecha y hora del evento
    - session_id: Identificador de sesión
    - loaded_at: Timestamp de carga a la base de datos
    
    Returns:
        dict: Información sobre la creación de la tabla
    """
    print("🗄️  Creando tabla raw.web_events si no existe...")
    
    # SQL para crear la tabla
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS raw.web_events (
        event_id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50),
        event_type VARCHAR(50),
        page_url VARCHAR(500),
        timestamp TIMESTAMP,
        session_id VARCHAR(50),
        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        # Ejecutar creación de tabla
        engine = get_postgres_engine()
        with engine.connect() as conn:
            conn.execute(create_table_sql)
            conn.commit()
        
        print("✅ Tabla raw.web_events creada/verificada exitosamente")
        
        # Verificar si la tabla tiene datos previos
        count_query = "SELECT COUNT(*) as count FROM raw.web_events"
        result = execute_query(count_query)
        existing_records = result['count'][0]
        
        if existing_records > 0:
            print(f"ℹ️  La tabla ya contiene {existing_records} registros")
        else:
            print("ℹ️  La tabla está vacía, lista para carga inicial")
        
        return {
            'table_created': True,
            'existing_records': existing_records,
            'creation_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"❌ Error al crear tabla: {str(e)}"
        print(error_msg)
        raise


@task(dag=dag)
def load_events(**context):
    """
    Lee el archivo CSV de eventos web y carga los datos a PostgreSQL.
    
    Esta tarea:
    - Lee el archivo CSV
    - Valida que no esté vacío
    - Valida que tenga las columnas esperadas
    - Carga los datos a la tabla raw.web_events
    - Maneja duplicados (reemplaza si existen)
    
    Returns:
        dict: Información sobre la carga (registros cargados, etc.)
    """
    print("📥 Cargando eventos web desde CSV a PostgreSQL...")
    
    # Obtener información del archivo de la tarea anterior
    ti = context['ti']
    file_info = ti.xcom_pull(task_ids='check_source_file')
    file_path = file_info['file_path']
    
    try:
        # Leer archivo CSV
        print(f"📖 Leyendo archivo: {file_path}")
        df = pd.read_csv(file_path)
        
        # Validar que no esté vacío
        if df.empty:
            raise ValueError("El archivo CSV está vacío (sin registros)")
        
        print(f"✓ Registros leídos del CSV: {len(df)}")
        
        # Validar columnas esperadas
        expected_columns = ['event_id', 'user_id', 'event_type', 'page_url', 'timestamp', 'session_id']
        missing_columns = set(expected_columns) - set(df.columns)
        
        if missing_columns:
            raise ValueError(f"Columnas faltantes en el CSV: {missing_columns}")
        
        print(f"✓ Columnas validadas: {list(df.columns)}")
        
        # Convertir timestamp a datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Validar que no haya event_id nulos
        null_event_ids = df['event_id'].isnull().sum()
        if null_event_ids > 0:
            print(f"⚠️  Advertencia: {null_event_ids} registros con event_id nulo serán omitidos")
            df = df.dropna(subset=['event_id'])
        
        # Cargar a PostgreSQL
        engine = get_postgres_engine()
        
        # Usar replace para manejar duplicados (sobrescribe si existen)
        df.to_sql(
            'web_events',
            engine,
            schema='raw',
            if_exists='replace',  # Reemplazar tabla completa
            index=False,
            method='multi',  # Carga por lotes para mejor performance
            chunksize=1000
        )
        
        records_loaded = len(df)
        print(f"✅ Eventos cargados exitosamente: {records_loaded} registros")
        
        # Estadísticas de los datos cargados
        event_types = df['event_type'].value_counts().to_dict()
        unique_users = df['user_id'].nunique()
        unique_sessions = df['session_id'].nunique()
        
        print(f"\n📊 Estadísticas de carga:")
        print(f"   • Total de eventos: {records_loaded}")
        print(f"   • Usuarios únicos: {unique_users}")
        print(f"   • Sesiones únicas: {unique_sessions}")
        print(f"   • Tipos de eventos:")
        for event_type, count in event_types.items():
            print(f"     - {event_type}: {count}")
        
        return {
            'records_loaded': records_loaded,
            'unique_users': unique_users,
            'unique_sessions': unique_sessions,
            'event_types': event_types,
            'load_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"❌ Error al cargar eventos: {str(e)}"
        print(error_msg)
        raise


@task(dag=dag)
def validate_load(**context):
    """
    Valida que los datos se cargaron correctamente a PostgreSQL.
    
    Esta tarea:
    - Cuenta registros en la tabla raw.web_events
    - Compara con el número de registros del CSV
    - Verifica integridad de datos básica
    - Genera resumen de validación
    
    Returns:
        dict: Resultados de la validación
    """
    print("✅ Validando carga de datos...")
    
    # Obtener información de la carga
    ti = context['ti']
    load_info = ti.xcom_pull(task_ids='load_events')
    expected_records = load_info['records_loaded']
    
    try:
        # Contar registros en la tabla
        count_query = "SELECT COUNT(*) as count FROM raw.web_events"
        result = execute_query(count_query)
        actual_records = result['count'][0]
        
        print(f"📊 Registros esperados: {expected_records}")
        print(f"📊 Registros en tabla: {actual_records}")
        
        # Validar que coincidan
        if actual_records != expected_records:
            error_msg = f"❌ Discrepancia en conteo: esperados {expected_records}, encontrados {actual_records}"
            print(error_msg)
            raise ValueError(error_msg)
        
        print("✅ Validación de conteo: EXITOSA")
        
        # Validaciones adicionales
        validations = {}
        
        # 1. Verificar que no haya event_id nulos
        null_check_query = "SELECT COUNT(*) as count FROM raw.web_events WHERE event_id IS NULL"
        null_result = execute_query(null_check_query)
        null_count = null_result['count'][0]
        validations['null_event_ids'] = null_count
        
        if null_count > 0:
            print(f"⚠️  Advertencia: {null_count} registros con event_id nulo")
        else:
            print("✅ Validación de nulos: EXITOSA")
        
        # 2. Verificar que haya eventos de diferentes tipos
        types_query = "SELECT DISTINCT event_type FROM raw.web_events"
        types_result = execute_query(types_query)
        event_types = types_result['event_type'].tolist()
        validations['event_types_found'] = event_types
        
        print(f"✅ Tipos de eventos encontrados: {len(event_types)}")
        for event_type in event_types:
            print(f"   • {event_type}")
        
        # 3. Verificar rango de fechas
        date_range_query = """
            SELECT 
                MIN(timestamp) as min_date,
                MAX(timestamp) as max_date
            FROM raw.web_events
        """
        date_result = execute_query(date_range_query)
        min_date = date_result['min_date'][0]
        max_date = date_result['max_date'][0]
        validations['date_range'] = {
            'min_date': str(min_date),
            'max_date': str(max_date)
        }
        
        print(f"✅ Rango de fechas: {min_date} a {max_date}")
        
        print("\n" + "="*60)
        print("✅ VALIDACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        
        return {
            'validation_passed': True,
            'records_validated': actual_records,
            'validations': validations,
            'validation_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"❌ Error en validación: {str(e)}"
        print(error_msg)
        raise


@task(dag=dag)
def log_completion(**context):
    """
    Registra la ejecución exitosa del DAG en la tabla de auditoría.
    
    Esta tarea:
    - Registra información de la ejecución en audit.pipeline_executions
    - Incluye métricas de la ejecución (registros procesados, duración, etc.)
    - Genera resumen final de la ejecución
    
    Returns:
        dict: Información del registro de auditoría
    """
    print("📝 Registrando ejecución en tabla de auditoría...")
    
    # Obtener información del contexto
    ti = context['ti']
    execution_date = context['execution_date']
    dag_id = context['dag'].dag_id
    
    # Obtener información de tareas anteriores
    load_info = ti.xcom_pull(task_ids='load_events')
    validation_info = ti.xcom_pull(task_ids='validate_load')
    
    try:
        # Preparar registro de auditoría
        audit_record = pd.DataFrame([{
            'dag_id': dag_id,
            'execution_date': execution_date,
            'status': 'SUCCESS',
            'records_processed': load_info['records_loaded'],
            'duration_seconds': None,  # Se puede calcular si se guarda start_time
            'error_message': None
        }])
        
        # Cargar a tabla de auditoría
        engine = get_postgres_engine()
        audit_record.to_sql(
            'pipeline_executions',
            engine,
            schema='audit',
            if_exists='append',
            index=False
        )
        
        print("✅ Registro de auditoría creado exitosamente")
        
        # Imprimir resumen final
        print("\n" + "="*70)
        print("🎉 EJECUCIÓN DEL DAG COMPLETADA EXITOSAMENTE")
        print("="*70)
        print(f"DAG: {dag_id}")
        print(f"Fecha de ejecución: {execution_date}")
        print(f"Registros procesados: {load_info['records_loaded']}")
        print(f"Usuarios únicos: {load_info['unique_users']}")
        print(f"Sesiones únicas: {load_info['unique_sessions']}")
        print(f"Validación: {'✅ EXITOSA' if validation_info['validation_passed'] else '❌ FALLIDA'}")
        print("="*70 + "\n")
        
        return {
            'audit_logged': True,
            'completion_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"❌ Error al registrar auditoría: {str(e)}"
        print(error_msg)
        # No fallar el DAG si solo falla el logging de auditoría
        print("⚠️  Continuando a pesar del error en auditoría")
        return {
            'audit_logged': False,
            'error': str(e)
        }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Crear instancias de las tareas
check_file_task = check_source_file()
create_table_task = create_table()
load_events_task = load_events()
validate_load_task = validate_load()
log_completion_task = log_completion()

# Establecer dependencias: cada tarea depende de la anterior
check_file_task >> create_table_task >> load_events_task >> validate_load_task >> log_completion_task

# Flujo del DAG:
# 1. check_source_file: Verifica que el archivo CSV existe
# 2. create_table: Crea la tabla en PostgreSQL si no existe
# 3. load_events: Carga los datos del CSV a la tabla
# 4. validate_load: Valida que la carga fue exitosa
# 5. log_completion: Registra la ejecución en auditoría

