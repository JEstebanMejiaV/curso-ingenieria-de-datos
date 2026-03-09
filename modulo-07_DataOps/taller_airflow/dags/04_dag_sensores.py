"""
DAG 04: Sensores y Dependencias Externas
=========================================

Este DAG demuestra el uso de sensores en Airflow para coordinar pipelines
con dependencias externas. Los sensores son operadores especiales que esperan
a que se cumpla una condición antes de continuar con la ejecución del pipeline.

Implementa un pipeline que:
1. Espera la llegada de un archivo de datos usando FileSensor
2. Espera la finalización de otro DAG usando ExternalTaskSensor
3. Procesa datos una vez cumplidas ambas condiciones
4. Notifica la finalización del procesamiento

Conceptos clave demostrados:
- FileSensor para esperar archivos en el sistema de archivos
- ExternalTaskSensor para coordinar múltiples DAGs
- Configuración de timeout y poke_interval para sensores
- Diferencia entre modo 'poke' y 'reschedule' para optimización de recursos
- Coordinación de pipelines con dependencias externas

Casos de uso de sensores:
- FileSensor: Esperar archivos de sistemas externos (FTP, SFTP, S3, etc.)
- ExternalTaskSensor: Coordinar DAGs que dependen de otros DAGs
- HttpSensor: Esperar disponibilidad de APIs o servicios web
- SqlSensor: Esperar que aparezcan datos en una base de datos
- TimeSensor: Esperar hasta una hora específica del día

Modos de operación de sensores:
- 'poke': El sensor verifica la condición continuamente sin liberar el worker slot
  * Ventaja: Menor latencia, respuesta inmediata cuando se cumple la condición
  * Desventaja: Ocupa un worker slot durante toda la espera
  * Usar cuando: El tiempo de espera es corto (< 5 minutos)

- 'reschedule': El sensor libera el worker slot entre verificaciones
  * Ventaja: No ocupa recursos mientras espera, mejor para esperas largas
  * Desventaja: Mayor latencia debido a la reprogramación
  * Usar cuando: El tiempo de espera es largo (> 5 minutos)

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
import pandas as pd
from utils.db_utils import get_postgres_engine, execute_query

# ============================================================================
# CONFIGURACIÓN DEL DAG
# ============================================================================

# Argumentos por defecto para todas las tareas del DAG
default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG
dag = DAG(
    dag_id='04_dag_sensores',
    default_args=default_args,
    description='Pipeline con sensores para coordinar dependencias externas',
    schedule_interval='@daily',  # Ejecutar diariamente
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['sensores', 'coordinacion', 'taller'],
    doc_md=__doc__,
)

# ============================================================================
# TAREAS DEL DAG
# ============================================================================

# Sensor 1: FileSensor - Esperar llegada de archivo de datos
# ============================================================================
# FileSensor verifica periódicamente si un archivo existe en el sistema de archivos.
# Es útil para pipelines que dependen de archivos generados por sistemas externos.

wait_for_file = FileSensor(
    task_id='wait_for_file',
    # Ruta del archivo a esperar (puede usar templating con macros de Airflow)
    # {{ ds }} se reemplaza con la fecha de ejecución en formato YYYY-MM-DD
    filepath='/opt/airflow/data/raw/transactions_{{ ds }}.csv',
    
    # Directorio base donde buscar el archivo (fs_conn_id debe apuntar aquí)
    # Por defecto usa el sistema de archivos local
    fs_conn_id='fs_default',
    
    # Intervalo de tiempo (en segundos) entre verificaciones
    # 60 segundos = verificar cada minuto
    poke_interval=60,
    
    # Tiempo máximo de espera (en segundos) antes de marcar la tarea como fallida
    # 3600 segundos = 1 hora
    timeout=3600,
    
    # Modo de operación del sensor:
    # 'reschedule': Libera el worker slot entre verificaciones (recomendado para esperas largas)
    # 'poke': Mantiene el worker slot ocupado durante toda la espera
    mode='reschedule',
    
    # Mensaje descriptivo para logs
    dag=dag
)

# Documentación adicional sobre FileSensor:
# - Útil para esperar archivos de ETL externos, exports de sistemas legacy, etc.
# - Puede verificar archivos en sistemas remotos usando conexiones (SFTP, S3, etc.)
# - El timeout debe ser mayor que el tiempo esperado de llegada del archivo
# - Si el archivo no llega en el timeout, la tarea falla y se puede reintentar


# Sensor 2: ExternalTaskSensor - Esperar finalización de otro DAG
# ============================================================================
# ExternalTaskSensor espera a que una tarea específica de otro DAG se complete.
# Es fundamental para coordinar pipelines que tienen dependencias entre DAGs.

wait_for_upstream_dag = ExternalTaskSensor(
    task_id='wait_for_upstream_dag',
    
    # ID del DAG externo del cual dependemos
    external_dag_id='01_dag_basico_ingesta',
    
    # ID de la tarea específica en el DAG externo que debe completarse
    # None significa esperar a que TODO el DAG se complete
    external_task_id='log_completion',
    
    # Diferencia de tiempo entre la ejecución de este DAG y el DAG externo
    # timedelta(hours=0) significa que esperamos la ejecución del mismo día
    # Si el DAG externo corre 1 hora antes, usaríamos timedelta(hours=-1)
    execution_delta=timedelta(hours=0),
    
    # Intervalo de verificación (en segundos)
    poke_interval=30,
    
    # Timeout (en segundos)
    timeout=1800,  # 30 minutos
    
    # Modo de operación:
    # 'poke': Mantiene el worker ocupado (mejor para esperas cortas)
    # Usamos 'poke' aquí porque esperamos que el DAG upstream termine pronto
    mode='poke',
    
    # Estados permitidos del task externo para considerar la condición cumplida
    # Por defecto: ['success']
    # Otros valores posibles: ['success', 'skipped'] si queremos continuar aunque se saltee
    allowed_states=['success'],
    
    # Si el task externo falla, ¿este sensor debe fallar también?
    # True: Si el task externo falla, este sensor falla
    # False: El sensor sigue esperando incluso si el task externo falla
    failed_states=['failed', 'upstream_failed', 'skipped'],
    
    dag=dag
)

# Documentación adicional sobre ExternalTaskSensor:
# - Esencial para arquitecturas de múltiples DAGs con dependencias
# - Permite desacoplar DAGs grandes en componentes más pequeños y manejables
# - execution_delta es crítico: debe reflejar la diferencia de schedule entre DAGs
# - Ejemplo: Si DAG A corre a las 2 AM y DAG B a las 3 AM, execution_delta=timedelta(hours=-1)


# Tarea 3: Procesar datos una vez cumplidas las condiciones
# ============================================================================

@task(dag=dag)
def process_data(**context):
    """
    Procesa los datos una vez que se cumplen todas las condiciones de los sensores.
    
    Esta tarea se ejecuta solo después de que:
    1. El archivo de datos ha llegado (FileSensor)
    2. El DAG upstream ha completado exitosamente (ExternalTaskSensor)
    
    En un escenario real, esta tarea podría:
    - Leer y validar el archivo recién llegado
    - Combinar datos del archivo con datos del DAG upstream
    - Ejecutar transformaciones complejas
    - Cargar resultados a la capa analytics
    
    Returns:
        dict: Metadatos sobre el procesamiento realizado
    """
    print("🔄 Procesando datos después de cumplir condiciones de sensores...")
    
    # Obtener fecha de ejecución del contexto
    execution_date = context['execution_date']
    ds = context['ds']  # Fecha en formato YYYY-MM-DD
    
    print(f"📅 Fecha de ejecución: {ds}")
    
    # Simular lectura del archivo que esperamos con FileSensor
    file_path = f"/opt/airflow/data/raw/transactions_{ds}.csv"
    print(f"📂 Archivo esperado: {file_path}")
    
    # En un escenario real, aquí leeríamos el archivo:
    # df_new_data = pd.read_csv(file_path)
    
    # Verificar que el DAG upstream completó exitosamente
    # Podemos leer datos que el DAG upstream generó
    try:
        query = """
            SELECT COUNT(*) as count 
            FROM processed.transactions_clean
        """
        result = execute_query(query)
        upstream_records = result['count'][0]
        print(f"✓ DAG upstream procesó {upstream_records} registros")
    except Exception as e:
        print(f"⚠️  No se pudieron leer datos del DAG upstream: {e}")
        upstream_records = 0
    
    # Simular procesamiento de datos
    print("\n" + "="*70)
    print("📊 PROCESAMIENTO DE DATOS CON DEPENDENCIAS EXTERNAS")
    print("="*70)
    print(f"✓ Archivo de datos recibido: {file_path}")
    print(f"✓ DAG upstream completado: 01_dag_basico_ingesta")
    print(f"✓ Registros disponibles del upstream: {upstream_records}")
    print("\n🔄 Ejecutando transformaciones...")
    print("   • Validando integridad del archivo")
    print("   • Combinando con datos del upstream")
    print("   • Aplicando reglas de negocio")
    print("   • Calculando métricas derivadas")
    print("="*70 + "\n")
    
    # En un escenario real, aquí ejecutaríamos el procesamiento:
    # 1. Leer archivo nuevo
    # 2. Leer datos del upstream
    # 3. Combinar y transformar
    # 4. Cargar a tablas finales
    
    # Registrar ejecución en auditoría
    engine = get_postgres_engine()
    audit_record = pd.DataFrame([{
        'dag_id': context['dag'].dag_id,
        'execution_date': execution_date,
        'status': 'SUCCESS',
        'records_processed': upstream_records,
        'duration_seconds': None,
        'error_message': None
    }])
    
    try:
        audit_record.to_sql('pipeline_executions', engine, schema='audit',
                           if_exists='append', index=False)
        print("✅ Ejecución registrada en auditoría")
    except Exception as e:
        print(f"⚠️  No se pudo registrar en auditoría: {e}")
    
    # Preparar metadatos de retorno
    metadata = {
        'execution_date': ds,
        'file_processed': file_path,
        'upstream_dag': '01_dag_basico_ingesta',
        'upstream_records': upstream_records,
        'status': 'SUCCESS',
        'processing_timestamp': datetime.now().isoformat()
    }
    
    print("✅ Procesamiento completado exitosamente!")
    
    return metadata


# Tarea 4: Notificar finalización
# ============================================================================

@task(dag=dag)
def notify_completion(**context):
    """
    Notifica la finalización exitosa del pipeline con sensores.
    
    En un escenario real, esta tarea podría:
    - Enviar emails de notificación
    - Publicar mensajes en Slack/Teams
    - Actualizar dashboards de monitoreo
    - Activar pipelines downstream
    - Registrar métricas en sistemas de observabilidad
    
    Args:
        context: Contexto de Airflow con información de la ejecución
    """
    print("📧 Enviando notificaciones de finalización...")
    
    # Obtener metadatos del procesamiento
    ti = context['ti']
    process_metadata = ti.xcom_pull(task_ids='process_data')
    
    # Preparar mensaje de notificación
    print("\n" + "="*70)
    print("✅ PIPELINE CON SENSORES COMPLETADO EXITOSAMENTE")
    print("="*70)
    print(f"DAG: {context['dag'].dag_id}")
    print(f"Fecha de ejecución: {context['ds']}")
    print(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📊 RESUMEN:")
    print(f"   • Archivo procesado: {process_metadata['file_processed']}")
    print(f"   • DAG upstream: {process_metadata['upstream_dag']}")
    print(f"   • Registros procesados: {process_metadata['upstream_records']}")
    print(f"   • Estado: {process_metadata['status']}")
    print("\n🔔 NOTIFICACIONES:")
    print("   ✓ Email enviado al equipo de datos")
    print("   ✓ Mensaje publicado en Slack #data-pipelines")
    print("   ✓ Dashboard actualizado")
    print("   ✓ Métricas registradas en sistema de monitoreo")
    print("="*70 + "\n")
    
    # En un escenario real, aquí enviaríamos notificaciones:
    # - EmailOperator para enviar emails
    # - SlackWebhookOperator para Slack
    # - HTTP requests a APIs de monitoreo
    
    return {
        'notification_sent': True,
        'notification_timestamp': datetime.now().isoformat(),
        'recipients': ['data-team@company.com'],
        'channels': ['#data-pipelines']
    }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Crear instancias de las tareas decoradas
process_task = process_data()
notify_task = notify_completion()

# Establecer dependencias
# Ambos sensores deben completarse antes de procesar datos
[wait_for_file, wait_for_upstream_dag] >> process_task >> notify_task

# Flujo del DAG:
# 1. wait_for_file y wait_for_upstream_dag se ejecutan en paralelo
#    - wait_for_file espera el archivo de datos
#    - wait_for_upstream_dag espera que el DAG 01 complete
# 2. Una vez AMBOS sensores se completan, se ejecuta process_data
# 3. Después del procesamiento, se ejecuta notify_completion

# ============================================================================
# DOCUMENTACIÓN ADICIONAL: MEJORES PRÁCTICAS CON SENSORES
# ============================================================================

"""
MEJORES PRÁCTICAS PARA USAR SENSORES EN AIRFLOW:

1. ELEGIR EL MODO CORRECTO (poke vs reschedule):
   - Usar 'poke' para esperas cortas (< 5 minutos)
     * Menor latencia
     * Respuesta inmediata
     * Ejemplo: Esperar que un DAG upstream termine (usualmente rápido)
   
   - Usar 'reschedule' para esperas largas (> 5 minutos)
     * Libera recursos del worker
     * Mejor para el cluster
     * Ejemplo: Esperar archivos de sistemas externos (puede tardar horas)

2. CONFIGURAR TIMEOUTS APROPIADOS:
   - El timeout debe ser mayor que el tiempo esperado de espera
   - Considerar SLAs del negocio
   - Ejemplo: Si un archivo llega entre 1-2 horas, usar timeout de 3 horas

3. AJUSTAR POKE_INTERVAL:
   - No verificar muy frecuentemente (desperdicia recursos)
   - No verificar muy espaciado (aumenta latencia)
   - Regla general: poke_interval = 10% del tiempo esperado de espera
   - Ejemplo: Si esperas 10 minutos, usa poke_interval=60 segundos

4. MANEJAR FALLOS DE SENSORES:
   - Configurar retries apropiados en default_args
   - Considerar usar on_failure_callback para alertas
   - Documentar qué hacer cuando un sensor falla (manual intervention?)

5. MONITOREAR SENSORES:
   - Los sensores que esperan mucho tiempo pueden indicar problemas upstream
   - Configurar alertas si sensores exceden tiempos esperados
   - Revisar logs regularmente para identificar patrones

6. ALTERNATIVAS A SENSORES:
   - Para dependencias entre DAGs, considerar TriggerDagRunOperator
   - Para archivos, considerar event-driven triggers (Airflow 2.2+)
   - Para APIs, considerar webhooks en lugar de polling

7. CASOS DE USO COMUNES:

   a) Esperar archivos de SFTP/S3:
      - Usar FileSensor con conexión remota
      - Modo: reschedule
      - Timeout: Basado en SLA del proveedor de datos
   
   b) Coordinar múltiples DAGs:
      - Usar ExternalTaskSensor
      - Modo: poke (si el DAG upstream es rápido)
      - Considerar execution_delta cuidadosamente
   
   c) Esperar disponibilidad de API:
      - Usar HttpSensor
      - Modo: reschedule
      - Configurar endpoint y response_check
   
   d) Esperar datos en base de datos:
      - Usar SqlSensor
      - Modo: reschedule
      - Escribir query que retorne True cuando los datos estén listos

8. DEBUGGING DE SENSORES:
   - Revisar logs para ver qué está verificando el sensor
   - Usar airflow tasks test para probar sensores manualmente
   - Verificar que las conexiones (fs_conn_id, etc.) estén configuradas
   - Para ExternalTaskSensor, verificar execution_delta y schedules

9. PERFORMANCE:
   - Demasiados sensores en modo 'poke' pueden saturar workers
   - Preferir 'reschedule' para sensores de larga duración
   - Considerar aumentar workers si hay muchos sensores
   - Monitorear métricas de scheduler y workers

10. TESTING:
    - Crear archivos/datos de prueba para validar sensores
    - Usar fechas pasadas para testing (catchup=True temporalmente)
    - Verificar comportamiento de timeout
    - Probar escenarios de fallo (archivo nunca llega, DAG upstream falla)
"""

# ============================================================================
# EJEMPLOS DE OTROS TIPOS DE SENSORES
# ============================================================================

"""
OTROS SENSORES ÚTILES EN AIRFLOW:

1. HttpSensor - Esperar disponibilidad de API:
   from airflow.sensors.http_sensor import HttpSensor
   
   wait_for_api = HttpSensor(
       task_id='wait_for_api',
       http_conn_id='my_api_connection',
       endpoint='api/v1/status',
       request_params={'check': 'ready'},
       response_check=lambda response: response.json()['status'] == 'ready',
       poke_interval=60,
       timeout=3600,
       mode='reschedule'
   )

2. SqlSensor - Esperar datos en base de datos:
   from airflow.sensors.sql import SqlSensor
   
   wait_for_data = SqlSensor(
       task_id='wait_for_data',
       conn_id='postgres_default',
       sql="SELECT COUNT(*) FROM raw.transactions WHERE DATE(loaded_at) = '{{ ds }}'",
       # La query debe retornar un valor truthy cuando la condición se cumple
       poke_interval=120,
       timeout=7200,
       mode='reschedule'
   )

3. TimeSensor - Esperar hasta una hora específica:
   from airflow.sensors.time_sensor import TimeSensor
   
   wait_until_9am = TimeSensor(
       task_id='wait_until_9am',
       target_time=time(9, 0, 0),  # 9:00 AM
       poke_interval=60,
       mode='reschedule'
   )

4. S3KeySensor - Esperar archivo en S3:
   from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
   
   wait_for_s3_file = S3KeySensor(
       task_id='wait_for_s3_file',
       bucket_name='my-data-bucket',
       bucket_key='data/transactions/{{ ds }}/data.csv',
       aws_conn_id='aws_default',
       poke_interval=300,
       timeout=7200,
       mode='reschedule'
   )

5. DateTimeSensor - Esperar hasta una fecha/hora específica:
   from airflow.sensors.date_time import DateTimeSensor
   
   wait_until_datetime = DateTimeSensor(
       task_id='wait_until_datetime',
       target_time="{{ execution_date.replace(hour=10, minute=0) }}",
       poke_interval=60,
       mode='reschedule'
   )
"""
