"""
DAG 06: Integración con Apache Spark
=====================================

Este DAG demuestra cómo orquestar jobs de Apache Spark desde Airflow.
Implementa un pipeline que:
1. Prepara el entorno y datos de entrada para el job Spark
2. Ejecuta un job Spark para agregaciones complejas usando BashOperator
3. Valida los resultados generados por Spark
4. Carga y verifica los resultados en PostgreSQL

Conceptos clave demostrados:
- Orquestación de jobs Spark desde Airflow
- Uso de BashOperator para ejecutar spark-submit
- Paso de parámetros a jobs Spark (fechas, configuración)
- Validación de outputs de jobs externos
- Integración entre Spark y PostgreSQL
- Manejo de errores en jobs de larga duración

Caso de uso: Procesamiento de grandes volúmenes de datos de ventas con Spark
para cálculos complejos que requieren procesamiento distribuido.

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
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
    'retries': 2,  # Reintentar dos veces (jobs Spark pueden fallar por recursos)
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG
dag = DAG(
    dag_id='06_dag_spark_integration',
    default_args=default_args,
    description='Orquestación de jobs Spark para agregaciones complejas de datos',
    schedule_interval='@daily',  # Ejecutar diariamente
    start_date=datetime(2024, 1, 1),
    catchup=False,  # No ejecutar para fechas pasadas
    tags=['spark', 'big-data', 'analytics', 'taller'],
    doc_md=__doc__,
)

# ============================================================================
# TAREAS DEL DAG
# ============================================================================

@task(dag=dag)
def prepare_spark_job(**context):
    """
    Prepara el entorno y valida prerequisitos para ejecutar el job Spark.
    
    Esta tarea:
    - Valida que existan datos en la capa processed para procesar
    - Verifica la disponibilidad de la tabla transactions_clean
    - Calcula estadísticas básicas de los datos de entrada
    - Prepara parámetros para el job Spark
    
    Returns:
        dict: Metadatos sobre los datos de entrada y configuración del job
    """
    print("🔧 Preparando job Spark...")
    
    # Obtener fecha de ejecución
    execution_date = context['ds']  # Formato YYYY-MM-DD
    print(f"📅 Fecha de ejecución: {execution_date}")
    
    # Validar que existan datos en processed layer
    query = """
        SELECT 
            COUNT(*) as total_records,
            MIN(transaction_date) as min_date,
            MAX(transaction_date) as max_date,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(DISTINCT product_id) as unique_products,
            SUM(amount) as total_amount
        FROM processed.transactions_clean
    """
    
    try:
        stats = execute_query(query)
        
        if stats.empty or stats['total_records'][0] == 0:
            raise ValueError("No hay datos disponibles en processed.transactions_clean")
        
        total_records = int(stats['total_records'][0])
        min_date = stats['min_date'][0]
        max_date = stats['max_date'][0]
        unique_customers = int(stats['unique_customers'][0])
        unique_products = int(stats['unique_products'][0])
        total_amount = float(stats['total_amount'][0])
        
        print(f"✓ Datos disponibles para procesar:")
        print(f"  • Total de registros: {total_records:,}")
        print(f"  • Rango de fechas: {min_date} a {max_date}")
        print(f"  • Clientes únicos: {unique_customers:,}")
        print(f"  • Productos únicos: {unique_products:,}")
        print(f"  • Monto total: ${total_amount:,.2f}")
        
        # Verificar que hay suficientes datos para procesamiento Spark
        if total_records < 10:
            print("⚠️  Advertencia: Pocos registros para procesamiento Spark")
            print("   Spark es más eficiente con grandes volúmenes de datos")
        
        # Preparar metadatos para el job
        job_metadata = {
            'execution_date': execution_date,
            'input_records': total_records,
            'date_range': f"{min_date} to {max_date}",
            'unique_customers': unique_customers,
            'unique_products': unique_products,
            'total_amount': total_amount,
            'preparation_timestamp': datetime.now().isoformat()
        }
        
        print("✅ Preparación completada exitosamente")
        return job_metadata
        
    except Exception as e:
        print(f"❌ Error preparando job Spark: {str(e)}")
        raise


# Tarea para ejecutar el job Spark usando BashOperator
# BashOperator es ideal para ejecutar comandos externos como spark-submit
submit_spark_job = BashOperator(
    task_id='submit_spark_job',
    bash_command="""
    echo "🚀 Iniciando job Spark..."
    echo "📅 Fecha de procesamiento: {{ ds }}"
    echo "================================================"
    
    # Ejecutar job Spark con spark-submit
    # Nota: En un entorno real, spark-submit estaría disponible en el PATH
    # Para este taller, ejecutamos el script Python directamente
    
    python3 /opt/airflow/spark_jobs/aggregate_sales.py \
        --input-date {{ ds }} \
        --metrics all
    
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "================================================"
        echo "✅ Job Spark completado exitosamente"
    else
        echo "================================================"
        echo "❌ Job Spark falló con código de salida: $exit_code"
        exit $exit_code
    fi
    """,
    dag=dag,
    doc_md="""
    ### Tarea: submit_spark_job
    
    Esta tarea ejecuta el job Spark usando BashOperator con spark-submit.
    
    **Comando ejecutado:**
    ```bash
    spark-submit \\
        --master local[*] \\
        --conf spark.sql.shuffle.partitions=4 \\
        /opt/airflow/spark_jobs/aggregate_sales.py \\
        --input-date {{ ds }} \\
        --metrics all
    ```
    
    **Parámetros:**
    - `--master local[*]`: Ejecuta Spark en modo local usando todos los cores disponibles
    - `--conf spark.sql.shuffle.partitions=4`: Configura 4 particiones para shuffles
    - `--input-date {{ ds }}`: Pasa la fecha de ejecución del DAG al job Spark
    - `--metrics all`: Calcula todas las métricas (daily, customer, category)
    
    **Nota sobre spark-submit:**
    En un entorno de producción, usarías spark-submit para ejecutar el job en un cluster.
    Para este taller educativo, ejecutamos el script Python directamente, pero el job
    usa PySpark y puede escalar a un cluster real sin cambios en el código.
    
    **Configuración recomendada para producción:**
    ```bash
    spark-submit \\
        --master yarn \\
        --deploy-mode cluster \\
        --num-executors 4 \\
        --executor-memory 4G \\
        --executor-cores 2 \\
        --driver-memory 2G \\
        --conf spark.sql.shuffle.partitions=200 \\
        /path/to/aggregate_sales.py \\
        --input-date {{ ds }}
    ```
    """,
)


@task(dag=dag)
def validate_spark_output(**context):
    """
    Valida que el job Spark haya generado los resultados esperados.
    
    Esta tarea verifica:
    - Que las tablas de analytics tengan nuevos registros
    - Que los datos generados sean consistentes
    - Que no haya valores nulos en columnas críticas
    - Que los rangos de valores sean razonables
    
    Returns:
        dict: Resultados de la validación
    """
    print("🔍 Validando resultados del job Spark...")
    
    # Obtener metadatos de preparación
    ti = context['ti']
    prep_metadata = ti.xcom_pull(task_ids='prepare_spark_job')
    input_records = prep_metadata['input_records']
    
    print(f"📥 Registros de entrada procesados: {input_records:,}")
    
    validation_results = {
        'daily_metrics': {},
        'customer_metrics': {},
        'category_performance': {},
        'validation_passed': True,
        'validation_errors': []
    }
    
    # 1. Validar métricas diarias
    print("\n📊 Validando métricas diarias...")
    try:
        daily_query = """
            SELECT 
                COUNT(*) as record_count,
                SUM(total_transactions) as sum_transactions,
                SUM(total_revenue) as sum_revenue,
                MIN(total_revenue) as min_revenue,
                MAX(total_revenue) as max_revenue
            FROM analytics.daily_sales_metrics
        """
        daily_stats = execute_query(daily_query)
        
        if daily_stats.empty or daily_stats['record_count'][0] == 0:
            validation_results['validation_passed'] = False
            validation_results['validation_errors'].append(
                "No se generaron métricas diarias"
            )
        else:
            record_count = int(daily_stats['record_count'][0])
            sum_transactions = int(daily_stats['sum_transactions'][0])
            sum_revenue = float(daily_stats['sum_revenue'][0])
            
            print(f"  ✓ Registros generados: {record_count}")
            print(f"  ✓ Total transacciones: {sum_transactions:,}")
            print(f"  ✓ Revenue total: ${sum_revenue:,.2f}")
            
            validation_results['daily_metrics'] = {
                'record_count': record_count,
                'sum_transactions': sum_transactions,
                'sum_revenue': sum_revenue
            }
            
            # Validar que el revenue sea positivo
            if sum_revenue <= 0:
                validation_results['validation_passed'] = False
                validation_results['validation_errors'].append(
                    f"Revenue total inválido: ${sum_revenue}"
                )
    
    except Exception as e:
        print(f"  ❌ Error validando métricas diarias: {str(e)}")
        validation_results['validation_passed'] = False
        validation_results['validation_errors'].append(
            f"Error en métricas diarias: {str(e)}"
        )
    
    # 2. Validar métricas de clientes
    print("\n👥 Validando métricas de clientes...")
    try:
        customer_query = """
            SELECT 
                COUNT(*) as record_count,
                COUNT(DISTINCT customer_id) as unique_customers,
                SUM(total_spent) as sum_spent,
                AVG(avg_order_value) as avg_aov
            FROM analytics.customer_metrics
        """
        customer_stats = execute_query(customer_query)
        
        if customer_stats.empty or customer_stats['record_count'][0] == 0:
            validation_results['validation_passed'] = False
            validation_results['validation_errors'].append(
                "No se generaron métricas de clientes"
            )
        else:
            record_count = int(customer_stats['record_count'][0])
            unique_customers = int(customer_stats['unique_customers'][0])
            sum_spent = float(customer_stats['sum_spent'][0])
            
            print(f"  ✓ Registros generados: {record_count}")
            print(f"  ✓ Clientes únicos: {unique_customers:,}")
            print(f"  ✓ Total gastado: ${sum_spent:,.2f}")
            
            validation_results['customer_metrics'] = {
                'record_count': record_count,
                'unique_customers': unique_customers,
                'sum_spent': sum_spent
            }
    
    except Exception as e:
        print(f"  ❌ Error validando métricas de clientes: {str(e)}")
        validation_results['validation_passed'] = False
        validation_results['validation_errors'].append(
            f"Error en métricas de clientes: {str(e)}"
        )
    
    # 3. Validar métricas de categorías
    print("\n📦 Validando métricas de categorías...")
    try:
        category_query = """
            SELECT 
                COUNT(*) as record_count,
                SUM(category_revenue) as sum_revenue,
                SUM(revenue_percentage) as sum_percentage
            FROM analytics.category_performance
        """
        category_stats = execute_query(category_query)
        
        if category_stats.empty or category_stats['record_count'][0] == 0:
            print("  ⚠️  No se generaron métricas de categorías (opcional)")
        else:
            record_count = int(category_stats['record_count'][0])
            sum_revenue = float(category_stats['sum_revenue'][0])
            sum_percentage = float(category_stats['sum_percentage'][0])
            
            print(f"  ✓ Categorías procesadas: {record_count}")
            print(f"  ✓ Revenue total: ${sum_revenue:,.2f}")
            print(f"  ✓ Suma de porcentajes: {sum_percentage:.2f}%")
            
            validation_results['category_performance'] = {
                'record_count': record_count,
                'sum_revenue': sum_revenue,
                'sum_percentage': sum_percentage
            }
            
            # Validar que los porcentajes sumen aproximadamente 100%
            if abs(sum_percentage - 100.0) > 1.0:
                print(f"  ⚠️  Advertencia: Porcentajes no suman 100% ({sum_percentage:.2f}%)")
    
    except Exception as e:
        print(f"  ⚠️  Métricas de categorías no disponibles: {str(e)}")
    
    # Resumen de validación
    print("\n" + "="*70)
    if validation_results['validation_passed']:
        print("✅ VALIDACIÓN EXITOSA - Todos los resultados son correctos")
    else:
        print("❌ VALIDACIÓN FALLIDA - Se encontraron errores:")
        for error in validation_results['validation_errors']:
            print(f"   • {error}")
    print("="*70 + "\n")
    
    if not validation_results['validation_passed']:
        raise ValueError(
            f"Validación de resultados Spark falló: {validation_results['validation_errors']}"
        )
    
    validation_results['validation_timestamp'] = datetime.now().isoformat()
    return validation_results


@task(dag=dag)
def load_results(**context):
    """
    Tarea final que registra la ejecución exitosa del pipeline Spark.
    
    Esta tarea:
    - Consolida metadatos de todas las tareas anteriores
    - Registra la ejecución en la tabla de auditoría
    - Genera un resumen completo del procesamiento
    - Calcula métricas de performance del job Spark
    """
    print("📝 Registrando resultados del pipeline Spark...")
    
    # Obtener metadatos de todas las tareas
    ti = context['ti']
    prep_metadata = ti.xcom_pull(task_ids='prepare_spark_job')
    validation_results = ti.xcom_pull(task_ids='validate_spark_output')
    
    # Calcular duración aproximada (desde preparación hasta ahora)
    prep_time = datetime.fromisoformat(prep_metadata['preparation_timestamp'])
    current_time = datetime.now()
    duration_seconds = int((current_time - prep_time).total_seconds())
    
    print("\n" + "="*70)
    print("📊 RESUMEN DE EJECUCIÓN DEL PIPELINE SPARK")
    print("="*70)
    
    print(f"\n📥 DATOS DE ENTRADA:")
    print(f"   • Fecha de ejecución: {prep_metadata['execution_date']}")
    print(f"   • Registros procesados: {prep_metadata['input_records']:,}")
    print(f"   • Rango de fechas: {prep_metadata['date_range']}")
    print(f"   • Clientes únicos: {prep_metadata['unique_customers']:,}")
    print(f"   • Productos únicos: {prep_metadata['unique_products']:,}")
    print(f"   • Monto total: ${prep_metadata['total_amount']:,.2f}")
    
    print(f"\n📊 RESULTADOS GENERADOS:")
    
    if 'daily_metrics' in validation_results and validation_results['daily_metrics']:
        dm = validation_results['daily_metrics']
        print(f"   • Métricas diarias: {dm['record_count']} días")
        print(f"     - Total transacciones: {dm['sum_transactions']:,}")
        print(f"     - Revenue total: ${dm['sum_revenue']:,.2f}")
    
    if 'customer_metrics' in validation_results and validation_results['customer_metrics']:
        cm = validation_results['customer_metrics']
        print(f"   • Métricas de clientes: {cm['record_count']} registros")
        print(f"     - Clientes únicos: {cm['unique_customers']:,}")
        print(f"     - Total gastado: ${cm['sum_spent']:,.2f}")
    
    if 'category_performance' in validation_results and validation_results['category_performance']:
        cp = validation_results['category_performance']
        print(f"   • Performance de categorías: {cp['record_count']} categorías")
        print(f"     - Revenue total: ${cp['sum_revenue']:,.2f}")
    
    print(f"\n⏱️  PERFORMANCE:")
    print(f"   • Duración total: {duration_seconds} segundos")
    print(f"   • Registros/segundo: {prep_metadata['input_records'] / max(duration_seconds, 1):.2f}")
    
    print("="*70 + "\n")
    
    # Registrar en tabla de auditoría
    execution_date = context['execution_date']
    dag_id = context['dag'].dag_id
    
    audit_record = pd.DataFrame([{
        'dag_id': dag_id,
        'execution_date': execution_date,
        'status': 'SUCCESS',
        'records_processed': prep_metadata['input_records'],
        'duration_seconds': duration_seconds,
        'error_message': None
    }])
    
    engine = get_postgres_engine()
    audit_record.to_sql('pipeline_executions', engine, schema='audit',
                       if_exists='append', index=False)
    
    print("✅ Pipeline Spark completado y registrado exitosamente!")
    
    return {
        'status': 'SUCCESS',
        'input_records': prep_metadata['input_records'],
        'duration_seconds': duration_seconds,
        'daily_metrics_count': validation_results['daily_metrics'].get('record_count', 0),
        'customer_metrics_count': validation_results['customer_metrics'].get('record_count', 0),
        'completion_timestamp': datetime.now().isoformat()
    }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Definir el flujo de tareas
# Este pipeline ejecuta las tareas en secuencia:
# 1. Preparar job Spark (validar datos de entrada)
# 2. Ejecutar job Spark (procesamiento con Spark)
# 3. Validar resultados (verificar outputs)
# 4. Cargar y registrar resultados (auditoría)

prepare_task = prepare_spark_job()
validate_task = validate_spark_output()
load_task = load_results()

# Establecer dependencias
prepare_task >> submit_spark_job >> validate_task >> load_task

# Notas sobre el pipeline:
# 
# 1. prepare_spark_job valida que haya datos disponibles antes de ejecutar Spark
# 2. submit_spark_job ejecuta el job Spark usando BashOperator
# 3. validate_spark_output verifica que los resultados sean correctos
# 4. load_results registra la ejecución en auditoría
#
# Ventajas de usar Spark desde Airflow:
# - Airflow orquesta el workflow pero Spark hace el procesamiento pesado
# - Spark puede escalar horizontalmente para grandes volúmenes de datos
# - Separación de responsabilidades: orquestación vs procesamiento
# - Fácil monitoreo y retry de jobs Spark desde Airflow UI
#
# Consideraciones para producción:
# - Usar SparkSubmitOperator en lugar de BashOperator para mejor integración
# - Configurar cluster Spark (YARN, Kubernetes, Standalone)
# - Ajustar recursos (executors, memory, cores) según volumen de datos
# - Implementar checkpointing para jobs de larga duración
# - Configurar alertas para fallos de jobs Spark
# - Monitorear métricas de Spark (shuffle, spill, GC)

