"""
DAG 05: Backfill y Procesamiento Histórico
===========================================

Este DAG demuestra el procesamiento de datos históricos usando backfill en Airflow.
El backfill permite ejecutar un DAG para fechas pasadas, procesando datos históricos
de manera particionada y controlada.

Implementa un pipeline que:
1. Obtiene la fecha de partición usando macros de Airflow
2. Verifica si la partición ya fue procesada (idempotencia)
3. Procesa datos de la partición específica
4. Marca la partición como completada

Conceptos clave demostrados:
- Uso de macros de Airflow (execution_date, ds, prev_ds, next_ds)
- Configuración de catchup=True para habilitar backfill
- Procesamiento particionado por fecha
- Idempotencia: verificar si una partición ya fue procesada
- Control de paralelismo con max_active_runs
- Templating con Jinja2 para fechas dinámicas

Casos de uso de backfill:
- Reprocesar datos históricos después de correcciones de bugs
- Cargar datos históricos al implementar un nuevo pipeline
- Recalcular métricas con nueva lógica de negocio
- Llenar gaps de datos faltantes

Mejores prácticas de backfill:
- Diseñar tareas idempotentes (pueden ejecutarse múltiples veces sin efectos secundarios)
- Particionar datos por fecha para procesamiento independiente
- Limitar ejecuciones paralelas con max_active_runs
- Verificar si una partición ya fue procesada antes de reprocesar
- Usar depends_on_past=False para permitir procesamiento independiente de particiones

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
import pandas as pd
from utils.db_utils import get_postgres_engine, execute_query

# ============================================================================
# CONFIGURACIÓN DEL DAG
# ============================================================================

# Argumentos por defecto para todas las tareas del DAG
default_args = {
    'owner': 'data_engineering_team',
    # IMPORTANTE: depends_on_past=False permite que cada partición se procese independientemente
    # Si una partición falla, las siguientes pueden continuar
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,  # Reintentar dos veces si falla
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG
dag = DAG(
    dag_id='05_dag_backfill',
    default_args=default_args,
    description='Pipeline de procesamiento histórico con backfill y particionamiento por fecha',
    
    # Ejecutar diariamente a las 2 AM
    schedule_interval='@daily',
    
    # Fecha de inicio: desde aquí se pueden ejecutar backfills
    # Si catchup=True, Airflow ejecutará todas las fechas desde start_date hasta hoy
    start_date=datetime(2024, 1, 1),
    
    # CRÍTICO: catchup=True habilita el backfill
    # Cuando se activa el DAG, Airflow ejecutará todas las fechas faltantes
    catchup=True,
    
    # max_active_runs limita cuántas ejecuciones pueden correr en paralelo
    # Esto previene sobrecargar el sistema al procesar muchas particiones históricas
    # Valor recomendado: 3-5 para backfills, 1 para procesamiento crítico
    max_active_runs=3,
    
    tags=['backfill', 'historico', 'particionado', 'taller'],
    doc_md=__doc__,
)

# ============================================================================
# TAREAS DEL DAG
# ============================================================================

@task(dag=dag)
def get_partition_date(**context):
    """
    Obtiene la fecha de partición usando macros de Airflow.
    
    Airflow proporciona varias macros útiles para trabajar con fechas:
    - execution_date: Fecha/hora lógica de ejecución (datetime object)
    - ds: execution_date en formato YYYY-MM-DD (string)
    - ds_nodash: execution_date en formato YYYYMMDD (string)
    - prev_ds: Fecha anterior en formato YYYY-MM-DD
    - next_ds: Fecha siguiente en formato YYYY-MM-DD
    - yesterday_ds: Ayer en formato YYYY-MM-DD
    - tomorrow_ds: Mañana en formato YYYY-MM-DD
    
    Estas macros son esenciales para procesamiento particionado por fecha.
    
    Returns:
        dict: Información sobre la partición a procesar
    """
    # Obtener macros de fecha del contexto
    execution_date = context['execution_date']  # datetime object
    ds = context['ds']  # YYYY-MM-DD string
    ds_nodash = context['ds_nodash']  # YYYYMMDD string
    prev_ds = context['prev_ds']  # Fecha anterior
    next_ds = context['next_ds']  # Fecha siguiente
    
    print("\n" + "="*70)
    print("📅 INFORMACIÓN DE PARTICIÓN")
    print("="*70)
    print(f"Execution Date (datetime): {execution_date}")
    print(f"Partition Date (ds): {ds}")
    print(f"Partition Date (ds_nodash): {ds_nodash}")
    print(f"Previous Partition: {prev_ds}")
    print(f"Next Partition: {next_ds}")
    print("="*70 + "\n")
    
    # Preparar información de la partición
    partition_info = {
        'partition_date': ds,
        'partition_date_nodash': ds_nodash,
        'execution_date': execution_date.isoformat(),
        'prev_partition': prev_ds,
        'next_partition': next_ds,
        'year': execution_date.year,
        'month': execution_date.month,
        'day': execution_date.day,
        'day_of_week': execution_date.strftime('%A'),
    }
    
    print(f"✅ Partición identificada: {ds}")
    print(f"   Año: {partition_info['year']}")
    print(f"   Mes: {partition_info['month']}")
    print(f"   Día: {partition_info['day']}")
    print(f"   Día de la semana: {partition_info['day_of_week']}")
    
    return partition_info


@task(dag=dag)
def check_partition_exists(**context):
    """
    Verifica si la partición ya fue procesada.
    
    Esta verificación es crucial para la idempotencia del pipeline.
    Permite que el DAG se ejecute múltiples veces sin duplicar datos
    o reprocesar particiones innecesariamente.
    
    Estrategias de verificación:
    1. Tabla de control con particiones procesadas (usado aquí)
    2. Verificar existencia de datos en tabla destino
    3. Verificar archivos de salida en sistema de archivos
    4. Combinar múltiples verificaciones
    
    Returns:
        dict: Estado de la partición (existe o no)
    """
    # Obtener información de la partición
    ti = context['ti']
    partition_info = ti.xcom_pull(task_ids='get_partition_date')
    partition_date = partition_info['partition_date']
    
    print(f"🔍 Verificando si la partición {partition_date} ya fue procesada...")
    
    # Crear tabla de control si no existe
    engine = get_postgres_engine()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS audit.partition_control (
            partition_date DATE PRIMARY KEY,
            dag_id VARCHAR(255),
            status VARCHAR(50),
            records_processed INTEGER,
            processing_started_at TIMESTAMP,
            processing_completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(create_table_query)
            conn.commit()
        print("✓ Tabla de control de particiones verificada")
    except Exception as e:
        print(f"⚠️  Error al crear tabla de control: {e}")
    
    # Verificar si la partición existe
    check_query = f"""
        SELECT 
            partition_date,
            status,
            records_processed,
            processing_completed_at
        FROM audit.partition_control
        WHERE partition_date = '{partition_date}'
        AND status = 'COMPLETED'
    """
    
    try:
        result = execute_query(check_query)
        partition_exists = len(result) > 0
        
        if partition_exists:
            record = result.iloc[0]
            print(f"✓ Partición {partition_date} ya fue procesada:")
            print(f"   • Estado: {record['status']}")
            print(f"   • Registros procesados: {record['records_processed']}")
            print(f"   • Completada: {record['processing_completed_at']}")
            print(f"\n⚠️  NOTA: La partición será reprocesada (comportamiento de backfill)")
        else:
            print(f"✓ Partición {partition_date} no ha sido procesada aún")
    
    except Exception as e:
        print(f"⚠️  Error al verificar partición: {e}")
        partition_exists = False
    
    return {
        'partition_date': partition_date,
        'partition_exists': partition_exists,
        'check_timestamp': datetime.now().isoformat()
    }


@task(dag=dag)
def process_partition(**context):
    """
    Procesa datos de la partición específica usando execution_date.
    
    Esta tarea demuestra cómo procesar datos particionados por fecha:
    1. Filtrar datos por la fecha de partición
    2. Aplicar transformaciones específicas de la partición
    3. Calcular métricas agregadas para la partición
    4. Cargar resultados a tablas particionadas
    
    El uso de execution_date garantiza que cada ejecución del DAG
    procese solo los datos correspondientes a su fecha lógica.
    
    Returns:
        dict: Metadatos del procesamiento de la partición
    """
    # Obtener información de la partición
    ti = context['ti']
    partition_info = ti.xcom_pull(task_ids='get_partition_date')
    partition_date = partition_info['partition_date']
    
    print(f"\n🔄 Procesando partición: {partition_date}")
    print("="*70)
    
    # Registrar inicio del procesamiento
    engine = get_postgres_engine()
    start_time = datetime.now()
    
    # Insertar o actualizar registro de inicio
    start_query = f"""
        INSERT INTO audit.partition_control 
            (partition_date, dag_id, status, processing_started_at)
        VALUES 
            ('{partition_date}', '05_dag_backfill', 'PROCESSING', '{start_time}')
        ON CONFLICT (partition_date) 
        DO UPDATE SET 
            status = 'PROCESSING',
            processing_started_at = '{start_time}',
            updated_at = '{start_time}'
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(start_query)
            conn.commit()
        print(f"✓ Inicio de procesamiento registrado: {start_time}")
    except Exception as e:
        print(f"⚠️  Error al registrar inicio: {e}")
    
    # PROCESAMIENTO DE DATOS PARTICIONADOS
    # =====================================
    
    # 1. Extraer transacciones de la partición específica
    print(f"\n📥 Extrayendo transacciones para {partition_date}...")
    
    transactions_query = f"""
        SELECT 
            transaction_id,
            customer_id,
            product_id,
            transaction_date,
            amount,
            quantity
        FROM raw.transactions
        WHERE DATE(transaction_date) = '{partition_date}'
    """
    
    try:
        df_transactions = execute_query(transactions_query)
        transaction_count = len(df_transactions)
        print(f"✓ Transacciones extraídas: {transaction_count}")
    except Exception as e:
        print(f"⚠️  Error al extraer transacciones: {e}")
        df_transactions = pd.DataFrame()
        transaction_count = 0
    
    if transaction_count == 0:
        print(f"⚠️  No hay transacciones para la partición {partition_date}")
        print("   Esto es normal para backfills de fechas sin datos")
        
        # Marcar partición como completada con 0 registros
        return {
            'partition_date': partition_date,
            'records_processed': 0,
            'status': 'COMPLETED_NO_DATA',
            'processing_time_seconds': 0
        }
    
    # 2. Enriquecer con información de productos
    print("\n🔗 Enriqueciendo con información de productos...")
    
    products_query = "SELECT product_id, product_name, category, price FROM raw.products"
    try:
        df_products = execute_query(products_query)
        df_enriched = df_transactions.merge(df_products, on='product_id', how='left')
        print(f"✓ Transacciones enriquecidas: {len(df_enriched)}")
    except Exception as e:
        print(f"⚠️  Error al enriquecer: {e}")
        df_enriched = df_transactions
    
    # 3. Calcular métricas de la partición
    print(f"\n📊 Calculando métricas para {partition_date}...")
    
    total_revenue = df_enriched['amount'].sum()
    avg_transaction = df_enriched['amount'].mean()
    unique_customers = df_enriched['customer_id'].nunique()
    unique_products = df_enriched['product_id'].nunique()
    
    print(f"   • Total de transacciones: {transaction_count}")
    print(f"   • Ingresos totales: ${total_revenue:,.2f}")
    print(f"   • Valor promedio: ${avg_transaction:,.2f}")
    print(f"   • Clientes únicos: {unique_customers}")
    print(f"   • Productos únicos: {unique_products}")
    
    # 4. Guardar datos procesados de la partición
    print(f"\n💾 Guardando datos procesados de la partición...")
    
    # Agregar columna de partición
    df_enriched['partition_date'] = partition_date
    df_enriched['processed_at'] = datetime.now()
    
    # Guardar en tabla particionada
    # En producción, usarías particionamiento nativo de la base de datos
    table_name = f'transactions_partitioned'
    
    try:
        # Eliminar datos existentes de esta partición (idempotencia)
        delete_query = f"""
            DELETE FROM processed.{table_name}
            WHERE partition_date = '{partition_date}'
        """
        with engine.connect() as conn:
            conn.execute(delete_query)
            conn.commit()
        
        # Insertar datos de la partición
        df_enriched.to_sql(table_name, engine, schema='processed',
                          if_exists='append', index=False)
        print(f"✓ Datos guardados en processed.{table_name}")
    except Exception as e:
        print(f"⚠️  Error al guardar datos: {e}")
        # En producción, aquí lanzarías una excepción para marcar la tarea como fallida
    
    # Calcular tiempo de procesamiento
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    print(f"\n✅ Partición {partition_date} procesada exitosamente")
    print(f"   Tiempo de procesamiento: {processing_time:.2f} segundos")
    print("="*70 + "\n")
    
    # Preparar metadatos
    processing_metadata = {
        'partition_date': partition_date,
        'records_processed': transaction_count,
        'total_revenue': float(total_revenue),
        'avg_transaction': float(avg_transaction),
        'unique_customers': unique_customers,
        'unique_products': unique_products,
        'processing_time_seconds': processing_time,
        'status': 'COMPLETED',
        'processing_started_at': start_time.isoformat(),
        'processing_completed_at': end_time.isoformat()
    }
    
    return processing_metadata


@task(dag=dag)
def mark_partition_complete(**context):
    """
    Marca la partición como completada en la tabla de control.
    
    Esta tarea actualiza el registro de control con:
    - Estado final (COMPLETED o FAILED)
    - Número de registros procesados
    - Tiempo de procesamiento
    - Timestamp de finalización
    
    Esto permite:
    - Rastrear qué particiones han sido procesadas
    - Auditar el procesamiento histórico
    - Identificar particiones que fallaron
    - Calcular métricas de performance
    """
    # Obtener metadatos del procesamiento
    ti = context['ti']
    processing_metadata = ti.xcom_pull(task_ids='process_partition')
    
    partition_date = processing_metadata['partition_date']
    records_processed = processing_metadata['records_processed']
    status = processing_metadata['status']
    processing_time = processing_metadata['processing_time_seconds']
    
    print(f"✅ Marcando partición {partition_date} como completada...")
    
    # Actualizar registro de control
    engine = get_postgres_engine()
    completed_at = datetime.now()
    
    update_query = f"""
        UPDATE audit.partition_control
        SET 
            status = '{status}',
            records_processed = {records_processed},
            processing_completed_at = '{completed_at}',
            updated_at = '{completed_at}'
        WHERE partition_date = '{partition_date}'
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(update_query)
            conn.commit()
        print(f"✓ Partición marcada como {status}")
    except Exception as e:
        print(f"⚠️  Error al actualizar control: {e}")
    
    # Registrar en tabla de ejecuciones de pipeline
    execution_record = pd.DataFrame([{
        'dag_id': context['dag'].dag_id,
        'execution_date': context['execution_date'],
        'status': status,
        'records_processed': records_processed,
        'duration_seconds': int(processing_time),
        'error_message': None
    }])
    
    try:
        execution_record.to_sql('pipeline_executions', engine, schema='audit',
                               if_exists='append', index=False)
        print("✓ Ejecución registrada en auditoría")
    except Exception as e:
        print(f"⚠️  Error al registrar ejecución: {e}")
    
    # Imprimir resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE PROCESAMIENTO DE PARTICIÓN")
    print("="*70)
    print(f"Partición: {partition_date}")
    print(f"Estado: {status}")
    print(f"Registros procesados: {records_processed}")
    print(f"Tiempo de procesamiento: {processing_time:.2f} segundos")
    
    if status == 'COMPLETED' and records_processed > 0:
        print(f"Ingresos totales: ${processing_metadata['total_revenue']:,.2f}")
        print(f"Valor promedio: ${processing_metadata['avg_transaction']:,.2f}")
        print(f"Clientes únicos: {processing_metadata['unique_customers']}")
        print(f"Productos únicos: {processing_metadata['unique_products']}")
    
    print("="*70 + "\n")
    
    return {
        'partition_date': partition_date,
        'status': status,
        'records_processed': records_processed,
        'marked_complete_at': completed_at.isoformat()
    }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Crear instancias de las tareas
get_partition_task = get_partition_date()
check_partition_task = check_partition_exists()
process_partition_task = process_partition()
mark_complete_task = mark_partition_complete()

# Establecer dependencias lineales
get_partition_task >> check_partition_task >> process_partition_task >> mark_complete_task

# Flujo del DAG:
# 1. get_partition_date: Identifica la fecha de partición a procesar
# 2. check_partition_exists: Verifica si ya fue procesada (idempotencia)
# 3. process_partition: Procesa datos de la partición específica
# 4. mark_partition_complete: Marca la partición como completada

# ============================================================================
# DOCUMENTACIÓN ADICIONAL: BACKFILL Y PROCESAMIENTO HISTÓRICO
# ============================================================================

"""
GUÍA COMPLETA DE BACKFILL EN AIRFLOW

1. ¿QUÉ ES BACKFILL?
   Backfill es el proceso de ejecutar un DAG para fechas pasadas, permitiendo
   procesar datos históricos de manera retroactiva.

2. ¿CUÁNDO USAR BACKFILL?
   - Cargar datos históricos al implementar un nuevo pipeline
   - Reprocesar datos después de corregir bugs en la lógica
   - Recalcular métricas con nueva lógica de negocio
   - Llenar gaps de datos faltantes
   - Migrar datos de sistemas legacy

3. CONFIGURACIÓN DE BACKFILL:

   a) catchup=True (habilita backfill automático):
      - Cuando se activa el DAG, Airflow ejecuta todas las fechas desde start_date
      - Útil para pipelines nuevos que necesitan procesar historia completa
      - Cuidado: puede generar muchas ejecuciones si start_date es muy antiguo

   b) catchup=False (deshabilita backfill automático):
      - Solo ejecuta para la fecha actual
      - Backfill manual usando CLI: airflow dags backfill
      - Más control sobre cuándo y cómo se procesan datos históricos

4. BACKFILL MANUAL CON CLI:

   # Backfill para un rango de fechas
   airflow dags backfill \
       --start-date 2024-01-01 \
       --end-date 2024-01-31 \
       05_dag_backfill

   # Backfill con opciones adicionales
   airflow dags backfill \
       --start-date 2024-01-01 \
       --end-date 2024-01-31 \
       --reset-dagruns \  # Resetear ejecuciones existentes
       --rerun-failed-tasks \  # Re-ejecutar tareas fallidas
       05_dag_backfill

5. CONTROL DE PARALELISMO:

   a) max_active_runs:
      - Limita cuántas ejecuciones del DAG pueden correr simultáneamente
      - Previene sobrecargar el sistema durante backfills masivos
      - Valores recomendados:
        * 1: Procesamiento secuencial (más seguro, más lento)
        * 3-5: Balance entre velocidad y recursos
        * 10+: Procesamiento rápido (requiere recursos suficientes)

   b) depends_on_past:
      - False: Cada partición se procesa independientemente (recomendado)
      - True: Una partición solo se procesa si la anterior tuvo éxito
      - Usar True solo si hay dependencias reales entre particiones

6. DISEÑO PARA BACKFILL - MEJORES PRÁCTICAS:

   a) IDEMPOTENCIA:
      - Las tareas deben poder ejecutarse múltiples veces sin efectos secundarios
      - Usar UPSERT o DELETE + INSERT en lugar de solo INSERT
      - Verificar si los datos ya existen antes de procesar
      - Ejemplo: DELETE WHERE partition_date = X antes de INSERT

   b) PARTICIONAMIENTO:
      - Particionar datos por fecha para procesamiento independiente
      - Usar execution_date para filtrar datos de cada partición
      - Almacenar datos en tablas particionadas o con columna de partición
      - Permite reprocesar particiones específicas sin afectar otras

   c) TABLA DE CONTROL:
      - Mantener registro de qué particiones han sido procesadas
      - Incluir: fecha, estado, registros procesados, timestamps
      - Permite auditar el progreso del backfill
      - Facilita identificar y reprocesar particiones fallidas

   d) MANEJO DE DATOS FALTANTES:
      - No fallar si una partición no tiene datos
      - Registrar particiones vacías en la tabla de control
      - Distinguir entre "sin datos" y "error de procesamiento"

7. MACROS DE AIRFLOW PARA BACKFILL:

   Disponibles en el contexto de las tareas:
   
   - execution_date: Fecha lógica de ejecución (datetime)
   - ds: execution_date en formato YYYY-MM-DD
   - ds_nodash: execution_date en formato YYYYMMDD
   - prev_ds: Fecha de la partición anterior
   - next_ds: Fecha de la partición siguiente
   - yesterday_ds: Ayer
   - tomorrow_ds: Mañana
   
   Uso en queries SQL con templating:
   ```sql
   SELECT * FROM transactions
   WHERE DATE(transaction_date) = '{{ ds }}'
   ```

8. MONITOREO DE BACKFILL:

   a) En la UI de Airflow:
      - Ver todas las ejecuciones en la vista de Grid
      - Identificar particiones fallidas (color rojo)
      - Revisar logs de tareas específicas
      - Monitorear progreso del backfill

   b) Queries de auditoría:
      ```sql
      -- Ver estado de todas las particiones
      SELECT 
          partition_date,
          status,
          records_processed,
          processing_completed_at
      FROM audit.partition_control
      ORDER BY partition_date;

      -- Identificar particiones fallidas
      SELECT partition_date
      FROM audit.partition_control
      WHERE status != 'COMPLETED'
      ORDER BY partition_date;

      -- Calcular progreso del backfill
      SELECT 
          COUNT(*) as total_partitions,
          SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
          SUM(records_processed) as total_records
      FROM audit.partition_control;
      ```

9. REPROCESAR PARTICIONES FALLIDAS:

   a) Identificar particiones fallidas:
      - Revisar tabla de control
      - Revisar logs en UI de Airflow
      - Queries SQL de auditoría

   b) Reprocesar con CLI:
      ```bash
      # Reprocesar una fecha específica
      airflow dags backfill \
          --start-date 2024-01-15 \
          --end-date 2024-01-15 \
          --reset-dagruns \
          05_dag_backfill

      # Reprocesar múltiples fechas fallidas
      airflow dags backfill \
          --start-date 2024-01-10 \
          --end-date 2024-01-20 \
          --rerun-failed-tasks \
          05_dag_backfill
      ```

   c) Reprocesar desde UI:
      - Navegar a la ejecución fallida
      - Click en "Clear" para resetear tareas
      - La ejecución se reprogramará automáticamente

10. CONSIDERACIONES DE PERFORMANCE:

    a) Tamaño de particiones:
       - Particiones muy pequeñas: Overhead de orquestación
       - Particiones muy grandes: Procesamiento lento, difícil de paralelizar
       - Recomendación: Particiones diarias o horarias según volumen

    b) Recursos del cluster:
       - Ajustar max_active_runs según capacidad del cluster
       - Monitorear uso de CPU, memoria y I/O durante backfill
       - Considerar ejecutar backfills en horarios de baja demanda

    c) Optimización de queries:
       - Usar índices en columnas de fecha
       - Particionar tablas en la base de datos
       - Limitar cantidad de datos leídos por partición

11. TESTING DE BACKFILL:

    a) Antes de ejecutar backfill completo:
       - Probar con una sola fecha: airflow tasks test
       - Probar con rango pequeño (1 semana)
       - Verificar idempotencia ejecutando dos veces
       - Validar resultados en tablas destino

    b) Validaciones:
       - Comparar conteos de registros esperados vs procesados
       - Verificar que no haya duplicados
       - Validar métricas calculadas
       - Revisar logs para warnings o errores

12. EJEMPLO DE WORKFLOW DE BACKFILL:

    Escenario: Implementar nuevo pipeline para procesar 6 meses de historia

    Paso 1: Configurar DAG
    - start_date = 6 meses atrás
    - catchup = False (control manual)
    - max_active_runs = 3

    Paso 2: Testing
    - Probar con 1 día: airflow tasks test
    - Probar con 1 semana: airflow dags backfill
    - Validar resultados

    Paso 3: Backfill por fases
    - Fase 1: Primer mes (30 días)
    - Validar resultados
    - Fase 2: Segundo mes
    - Continuar hasta completar

    Paso 4: Monitoreo
    - Revisar tabla de control diariamente
    - Reprocesar particiones fallidas
    - Ajustar max_active_runs según performance

    Paso 5: Activación
    - Una vez completado el backfill histórico
    - Cambiar catchup = True o schedule para procesamiento diario
    - Monitorear ejecuciones regulares

13. ERRORES COMUNES Y SOLUCIONES:

    a) "Too many active runs":
       - Reducir max_active_runs
       - Esperar a que completen ejecuciones actuales

    b) "Task instance did not exist":
       - Verificar que start_date sea correcto
       - Asegurar que el DAG esté activado

    c) Duplicación de datos:
       - Implementar DELETE antes de INSERT
       - Usar UPSERT con ON CONFLICT
       - Verificar idempotencia

    d) Particiones sin datos:
       - No fallar la tarea, registrar como "sin datos"
       - Distinguir entre error y ausencia de datos

    e) Timeout en particiones grandes:
       - Aumentar timeout de tareas
       - Reducir tamaño de particiones
       - Optimizar queries

14. ALTERNATIVAS A BACKFILL:

    a) Procesamiento incremental:
       - Procesar solo datos nuevos desde última ejecución
       - Usar watermarks o timestamps
       - Más eficiente que reprocesar todo

    b) Snapshots:
       - Tomar snapshots de datos en puntos específicos
       - Procesar snapshots en lugar de datos raw
       - Útil para datos que cambian frecuentemente

    c) Event-driven processing:
       - Procesar datos cuando llegan (no por schedule)
       - Usar triggers o sensores
       - Más reactivo que batch processing

CONCLUSIÓN:
El backfill es una herramienta poderosa para procesar datos históricos,
pero requiere diseño cuidadoso para idempotencia, particionamiento y
control de recursos. Seguir estas mejores prácticas garantiza backfills
exitosos y mantenibles.
"""
