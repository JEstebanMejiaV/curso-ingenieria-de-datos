"""
Solución Ejercicio 03: Pipeline Completo End-to-End
===================================================

Este archivo contiene la implementación de referencia del DAG 1 (Ingesta Multi-Fuente)
del pipeline completo. Los otros DAGs (2, 3, 4) seguirían patrones similares.

NOTA: Esta es una solución de referencia que demuestra:
- Coordinación de múltiples tareas de ingesta en paralelo
- Validaciones robustas de datos
- Manejo de errores con callbacks
- Configuración de SLAs
- Logging estructurado
- Uso de Variables de Airflow
- Mejores prácticas de DataOps

Para una implementación completa, se necesitarían crear los 4 DAGs del pipeline.
Este archivo muestra el DAG 1 como ejemplo completo.

Autor: Solución de Referencia - Taller de Apache Airflow
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.python import BranchPythonOperator
import pandas as pd
import os
from utils.db_utils import get_postgres_engine, execute_query

# ============================================================================
# CALLBACKS GLOBALES
# ============================================================================

def notify_failure(context):
    """
    Callback ejecutado cuando una tarea falla.
    
    En producción, esto enviaría alertas por email, Slack, PagerDuty, etc.
    """
    dag_id = context['dag'].dag_id
    task_id = context['task_instance'].task_id
    execution_date = context['execution_date']
    exception = context.get('exception')
    
    print("\n" + "="*70)
    print("🚨 ALERTA: TAREA FALLIDA")
    print("="*70)
    print(f"DAG: {dag_id}")
    print(f"Tarea: {task_id}")
    print(f"Fecha de ejecución: {execution_date}")
    print(f"Error: {exception}")
    print("="*70 + "\n")
    
    # En producción, aquí enviarías notificaciones:
    # send_slack_alert(f"🚨 DAG {dag_id} falló en tarea {task_id}")
    # send_email_alert(alert_email, subject, body)
    
    # Registrar en tabla de alertas
    try:
        engine = get_postgres_engine()
        alert_record = pd.DataFrame([{
            'dag_id': dag_id,
            'task_id': task_id,
            'execution_date': execution_date,
            'alert_type': 'TASK_FAILURE',
            'message': str(exception),
            'created_at': datetime.now()
        }])
        alert_record.to_sql('pipeline_alerts', engine, schema='audit',
                           if_exists='append', index=False)
    except Exception as e:
        print(f"⚠️  No se pudo registrar alerta: {e}")


def notify_retry(context):
    """Callback ejecutado cuando una tarea se reintenta."""
    task_id = context['task_instance'].task_id
    try_number = context['task_instance'].try_number
    
    print(f"⚠️  REINTENTO: Tarea {task_id} (intento {try_number})")


def notify_success(context):
    """Callback ejecutado cuando una tarea tiene éxito."""
    task_id = context['task_instance'].task_id
    print(f"✅ ÉXITO: Tarea {task_id} completada")


def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """
    Callback ejecutado cuando se viola un SLA.
    
    Args:
        dag: El DAG donde ocurrió la violación
        task_list: Lista de tareas que violaron SLA
        blocking_task_list: Lista de tareas que bloquearon
        slas: Lista de SLAs violados
        blocking_tis: TaskInstances que bloquearon
    """
    print("\n" + "="*70)
    print("⏰ ALERTA: SLA VIOLADO")
    print("="*70)
    print(f"DAG: {dag.dag_id}")
    print(f"Tareas con SLA violado: {[t.task_id for t in task_list]}")
    print(f"Tareas bloqueantes: {[t.task_id for t in blocking_task_list]}")
    print("="*70 + "\n")
    
    # En producción, enviar alerta de alta prioridad
    # send_pagerduty_alert(f"SLA violado en {dag.dag_id}")


# ============================================================================
# CONFIGURACIÓN DEL DAG
# ============================================================================

# Obtener configuración de Variables de Airflow
try:
    sla_hours = int(Variable.get('pipeline_sla_hours', default_var='1'))
    alert_email = Variable.get('alert_email', default_var='team@company.com')
    data_quality_threshold = float(Variable.get('data_quality_threshold', default_var='0.95'))
except Exception as e:
    print(f"⚠️  Error al obtener variables: {e}. Usando valores por defecto.")
    sla_hours = 1
    alert_email = 'team@company.com'
    data_quality_threshold = 0.95

# Argumentos por defecto con callbacks
default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email': [alert_email],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,  # Reintentar hasta 3 veces
    'retry_delay': timedelta(minutes=10),
    'retry_exponential_backoff': True,  # Backoff exponencial
    'max_retry_delay': timedelta(minutes=30),
    'on_failure_callback': notify_failure,
    'on_retry_callback': notify_retry,
    'on_success_callback': notify_success,
    'sla': timedelta(hours=sla_hours),  # SLA de 1 hora por defecto
}

# Definición del DAG
dag = DAG(
    dag_id='pipeline_01_ingesta_multifuente',
    default_args=default_args,
    description='Pipeline de ingesta multi-fuente con validaciones y monitoreo',
    schedule_interval='0 1 * * *',  # 1 AM diario
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,  # Solo una ejecución a la vez
    tags=['pipeline', 'ingesta', 'produccion'],
    doc_md=__doc__,
    sla_miss_callback=sla_miss_callback,
)

# ============================================================================
# TAREAS DEL DAG
# ============================================================================

@task(dag=dag)
def check_all_sources(**context):
    """
    Verifica que todos los archivos fuente existen antes de comenzar la ingesta.
    
    Esta tarea actúa como gate keeper: si algún archivo falta, el DAG falla
    inmediatamente sin intentar ingestar datos parciales.
    
    Returns:
        dict: Información sobre los archivos encontrados
    
    Raises:
        FileNotFoundError: Si algún archivo fuente no existe
    """
    print("🔍 Verificando existencia de todos los archivos fuente...")
    
    # Definir archivos fuente esperados
    source_files = {
        'web_events': '/opt/airflow/data/raw/web_events.csv',
        'transactions': '/opt/airflow/data/raw/transactions.csv',
        'products': '/opt/airflow/data/raw/products.csv'
    }
    
    files_info = {}
    missing_files = []
    
    for source_name, file_path in source_files.items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            files_info[source_name] = {
                'path': file_path,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'exists': True
            }
            print(f"✅ {source_name}: {file_size:,} bytes")
        else:
            missing_files.append(source_name)
            files_info[source_name] = {
                'path': file_path,
                'exists': False
            }
            print(f"❌ {source_name}: ARCHIVO NO ENCONTRADO")
    
    # Si hay archivos faltantes, fallar
    if missing_files:
        error_msg = f"Archivos fuente faltantes: {', '.join(missing_files)}"
        print(f"\n🚨 ERROR: {error_msg}")
        raise FileNotFoundError(error_msg)
    
    print(f"\n✅ Todos los archivos fuente encontrados ({len(source_files)} archivos)")
    
    return {
        'files_checked': len(source_files),
        'files_info': files_info,
        'check_timestamp': datetime.now().isoformat()
    }


@task(dag=dag)
def ingest_web_events(**context):
    """
    Ingesta eventos web desde CSV a PostgreSQL.
    
    Esta tarea se ejecuta en paralelo con otras ingestas.
    """
    print("📥 Ingiriendo eventos web...")
    
    file_path = '/opt/airflow/data/raw/web_events.csv'
    
    try:
        # Leer CSV
        df = pd.read_csv(file_path)
        print(f"✓ Registros leídos: {len(df)}")
        
        # Validaciones básicas
        if df.empty:
            raise ValueError("Archivo de eventos web está vacío")
        
        expected_columns = ['event_id', 'user_id', 'event_type', 'page_url', 'timestamp', 'session_id']
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Columnas faltantes: {missing_cols}")
        
        # Convertir tipos
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Cargar a PostgreSQL
        engine = get_postgres_engine()
        df.to_sql('web_events', engine, schema='raw',
                 if_exists='replace', index=False, method='multi', chunksize=1000)
        
        print(f"✅ Eventos web ingresados: {len(df)} registros")
        
        return {
            'source': 'web_events',
            'records_loaded': len(df),
            'load_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error al ingerir eventos web: {e}")
        raise


@task(dag=dag)
def ingest_transactions(**context):
    """
    Ingesta transacciones desde CSV a PostgreSQL.
    
    Esta tarea se ejecuta en paralelo con otras ingestas.
    """
    print("📥 Ingiriendo transacciones...")
    
    file_path = '/opt/airflow/data/raw/transactions.csv'
    
    try:
        df = pd.read_csv(file_path)
        print(f"✓ Registros leídos: {len(df)}")
        
        if df.empty:
            raise ValueError("Archivo de transacciones está vacío")
        
        # Convertir tipos
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Cargar a PostgreSQL
        engine = get_postgres_engine()
        df.to_sql('transactions', engine, schema='raw',
                 if_exists='replace', index=False, method='multi', chunksize=1000)
        
        print(f"✅ Transacciones ingresadas: {len(df)} registros")
        
        return {
            'source': 'transactions',
            'records_loaded': len(df),
            'load_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error al ingerir transacciones: {e}")
        raise


@task(dag=dag)
def ingest_products(**context):
    """
    Ingesta productos desde CSV a PostgreSQL.
    
    Esta tarea se ejecuta en paralelo con otras ingestas.
    """
    print("📥 Ingiriendo productos...")
    
    file_path = '/opt/airflow/data/raw/products.csv'
    
    try:
        df = pd.read_csv(file_path)
        print(f"✓ Registros leídos: {len(df)}")
        
        if df.empty:
            raise ValueError("Archivo de productos está vacío")
        
        # Cargar a PostgreSQL
        engine = get_postgres_engine()
        df.to_sql('products', engine, schema='raw',
                 if_exists='replace', index=False, method='multi', chunksize=1000)
        
        print(f"✅ Productos ingresados: {len(df)} registros")
        
        return {
            'source': 'products',
            'records_loaded': len(df),
            'load_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error al ingerir productos: {e}")
        raise


@task(dag=dag)
def validate_ingestion(**context):
    """
    Valida que todas las ingestas fueron exitosas.
    
    Validaciones:
    1. Verificar conteos de registros
    2. Validar integridad de datos
    3. Comparar con día anterior (detectar anomalías)
    4. Calcular score de calidad
    
    Returns:
        dict: Resultados de validación
    """
    print("🔍 Validando ingesta de datos...")
    
    ti = context['ti']
    
    # Obtener resultados de ingestas
    web_events_info = ti.xcom_pull(task_ids='ingest_web_events')
    transactions_info = ti.xcom_pull(task_ids='ingest_transactions')
    products_info = ti.xcom_pull(task_ids='ingest_products')
    
    validation_results = {
        'validations': {},
        'all_passed': True,
        'quality_score': 1.0
    }
    
    # ========================================================================
    # VALIDACIÓN 1: Verificar conteos mínimos
    # ========================================================================
    
    print("\n1️⃣  Validando conteos de registros...")
    
    min_records = {
        'web_events': 100,
        'transactions': 50,
        'products': 10
    }
    
    sources_info = {
        'web_events': web_events_info,
        'transactions': transactions_info,
        'products': products_info
    }
    
    for source, info in sources_info.items():
        records = info['records_loaded']
        min_required = min_records[source]
        
        if records < min_required:
            validation_results['all_passed'] = False
            validation_results['quality_score'] -= 0.2
            print(f"   ❌ {source}: {records} registros (mínimo: {min_required})")
        else:
            print(f"   ✅ {source}: {records} registros")
        
        validation_results['validations'][f'{source}_count'] = {
            'passed': records >= min_required,
            'actual': records,
            'expected_min': min_required
        }
    
    # ========================================================================
    # VALIDACIÓN 2: Comparar con día anterior (detección de anomalías)
    # ========================================================================
    
    print("\n2️⃣  Detectando anomalías vs día anterior...")
    
    try:
        # Obtener conteos de ayer desde auditoría
        yesterday_query = """
            SELECT records_processed
            FROM audit.pipeline_executions
            WHERE dag_id = 'pipeline_01_ingesta_multifuente'
            AND execution_date = CURRENT_DATE - INTERVAL '1 day'
            ORDER BY created_at DESC
            LIMIT 1
        """
        yesterday_result = execute_query(yesterday_query)
        
        if not yesterday_result.empty:
            yesterday_count = yesterday_result['records_processed'][0]
            today_count = sum(info['records_loaded'] for info in sources_info.values())
            
            # Calcular variación porcentual
            variation_pct = abs(today_count - yesterday_count) / yesterday_count * 100
            
            # Anomalía si variación > 50%
            if variation_pct > 50:
                validation_results['all_passed'] = False
                validation_results['quality_score'] -= 0.1
                print(f"   ⚠️  ANOMALÍA: Variación de {variation_pct:.1f}% vs ayer")
                print(f"      Ayer: {yesterday_count}, Hoy: {today_count}")
            else:
                print(f"   ✅ Variación normal: {variation_pct:.1f}% vs ayer")
            
            validation_results['validations']['anomaly_detection'] = {
                'passed': variation_pct <= 50,
                'variation_pct': variation_pct,
                'yesterday_count': yesterday_count,
                'today_count': today_count
            }
        else:
            print("   ℹ️  No hay datos de ayer para comparar")
            
    except Exception as e:
        print(f"   ⚠️  No se pudo comparar con día anterior: {e}")
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    
    print("\n" + "="*70)
    if validation_results['all_passed']:
        print("✅ VALIDACIÓN EXITOSA")
    else:
        print("❌ VALIDACIÓN FALLIDA")
    print(f"Score de calidad: {validation_results['quality_score']:.2f}")
    print("="*70 + "\n")
    
    # Verificar umbral de calidad
    if validation_results['quality_score'] < data_quality_threshold:
        raise ValueError(
            f"Score de calidad ({validation_results['quality_score']:.2f}) "
            f"por debajo del umbral ({data_quality_threshold})"
        )
    
    return validation_results


@task(dag=dag)
def log_ingestion_metrics(**context):
    """
    Registra métricas de la ingesta en la tabla de auditoría.
    
    Esta tarea siempre se ejecuta al final para mantener registro
    de todas las ejecuciones (exitosas o fallidas).
    """
    print("📝 Registrando métricas de ingesta...")
    
    ti = context['ti']
    execution_date = context['execution_date']
    dag_id = context['dag'].dag_id
    
    # Obtener información de todas las tareas
    web_events_info = ti.xcom_pull(task_ids='ingest_web_events')
    transactions_info = ti.xcom_pull(task_ids='ingest_transactions')
    products_info = ti.xcom_pull(task_ids='ingest_products')
    validation_results = ti.xcom_pull(task_ids='validate_ingestion')
    
    # Calcular totales
    total_records = (
        web_events_info['records_loaded'] +
        transactions_info['records_loaded'] +
        products_info['records_loaded']
    )
    
    # Registrar en auditoría
    try:
        engine = get_postgres_engine()
        audit_record = pd.DataFrame([{
            'dag_id': dag_id,
            'execution_date': execution_date,
            'status': 'SUCCESS' if validation_results['all_passed'] else 'QUALITY_WARNING',
            'records_processed': total_records,
            'duration_seconds': None,
            'error_message': None if validation_results['all_passed'] else 'Quality issues detected'
        }])
        
        audit_record.to_sql('pipeline_executions', engine, schema='audit',
                           if_exists='append', index=False)
        
        print("✅ Métricas registradas en auditoría")
        
    except Exception as e:
        print(f"⚠️  Error al registrar auditoría: {e}")
    
    # Imprimir resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE INGESTA")
    print("="*70)
    print(f"DAG: {dag_id}")
    print(f"Fecha: {execution_date}")
    print(f"\nRegistros ingresados:")
    print(f"  • Eventos web: {web_events_info['records_loaded']:,}")
    print(f"  • Transacciones: {transactions_info['records_loaded']:,}")
    print(f"  • Productos: {products_info['records_loaded']:,}")
    print(f"  • TOTAL: {total_records:,}")
    print(f"\nCalidad: {validation_results['quality_score']:.2%}")
    print(f"Estado: {'✅ EXITOSO' if validation_results['all_passed'] else '⚠️  CON ADVERTENCIAS'}")
    print("="*70 + "\n")
    
    return {
        'total_records': total_records,
        'quality_score': validation_results['quality_score'],
        'completion_timestamp': datetime.now().isoformat()
    }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Crear instancias de tareas
check_sources_task = check_all_sources()

# Tareas de ingesta (se ejecutan en paralelo)
ingest_web_task = ingest_web_events()
ingest_trans_task = ingest_transactions()
ingest_prod_task = ingest_products()

# Tareas de validación y logging
validate_task = validate_ingestion()
log_metrics_task = log_ingestion_metrics()

# Establecer dependencias
check_sources_task >> [ingest_web_task, ingest_trans_task, ingest_prod_task]
[ingest_web_task, ingest_trans_task, ingest_prod_task] >> validate_task
validate_task >> log_metrics_task

# Flujo del DAG:
# 1. check_all_sources: Verifica que todos los archivos existen
# 2. [ingest_*]: Tres ingestas en paralelo
# 3. validate_ingestion: Valida todas las ingestas
# 4. log_ingestion_metrics: Registra métricas finales

# ============================================================================
# NOTAS PARA IMPLEMENTACIÓN COMPLETA
# ============================================================================

"""
Para completar el pipeline, necesitarías crear:

1. pipeline_02_transformacion.py:
   - ExternalTaskSensor esperando este DAG
   - Transformaciones de datos
   - Validaciones de calidad
   - Manejo de errores similar

2. pipeline_03_analytics.py:
   - ExternalTaskSensor esperando DAG 2
   - Cálculos RFM
   - Generación de reportes
   - Detección de anomalías

3. pipeline_04_monitoring.py:
   - Consultas a metadatos de Airflow
   - Análisis de SLAs
   - Generación de dashboard de salud
   - Envío de resumen diario

Todos seguirían patrones similares a este DAG con:
- Callbacks configurados
- SLAs apropiados
- Validaciones robustas
- Logging estructurado
- Manejo de errores
"""

