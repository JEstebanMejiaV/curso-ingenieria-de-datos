"""
DAG 02: Transformaciones de Datos
==================================

Este DAG demuestra el encadenamiento de tareas de transformación de datos en Airflow.
Implementa un pipeline completo que:
1. Extrae datos de la capa raw
2. Limpia y normaliza transacciones
3. Enriquece con información de productos
4. Calcula métricas agregadas (diarias y por cliente)
5. Carga resultados a la capa processed y analytics

Conceptos clave demostrados:
- Encadenamiento de tareas con dependencias explícitas usando >>
- Uso de XCom para compartir metadatos entre tareas
- TaskFlow API con decoradores @task
- Transformaciones de datos con pandas
- Agregaciones y cálculos de métricas de negocio

Caso de uso: Pipeline de transformación para análisis de ventas e-commerce

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
    'depends_on_past': False,  # No depende de ejecuciones anteriores
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,  # Reintentar una vez si falla
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG
dag = DAG(
    dag_id='02_dag_transformaciones',
    default_args=default_args,
    description='Pipeline de transformación de datos con limpieza, enriquecimiento y cálculo de métricas',
    schedule_interval='@daily',  # Ejecutar diariamente
    start_date=datetime(2024, 1, 1),
    catchup=False,  # No ejecutar para fechas pasadas
    tags=['transformacion', 'analytics', 'taller'],
    doc_md=__doc__,  # Usar el docstring del módulo como documentación
)

# ============================================================================
# TAREAS DEL DAG
# ============================================================================

@task(dag=dag)
def extract_raw_data(**context):
    """
    Extrae datos de la capa raw en PostgreSQL.
    
    Esta tarea lee las transacciones, productos y clientes desde las tablas
    raw y retorna conteos de registros que serán compartidos con otras tareas
    usando XCom.
    
    Returns:
        dict: Diccionario con conteos de registros por tabla
    """
    print("📥 Extrayendo datos de la capa raw...")
    
    # Extraer transacciones
    transactions_query = "SELECT * FROM raw.transactions"
    df_transactions = execute_query(transactions_query)
    print(f"✓ Transacciones extraídas: {len(df_transactions)} registros")
    
    # Extraer productos
    products_query = "SELECT * FROM raw.products"
    df_products = execute_query(products_query)
    print(f"✓ Productos extraídos: {len(df_products)} registros")
    
    # Extraer clientes
    customers_query = "SELECT * FROM raw.customers"
    df_customers = execute_query(customers_query)
    print(f"✓ Clientes extraídos: {len(df_customers)} registros")
    
    # Preparar metadatos para compartir via XCom
    metadata = {
        'transactions_count': len(df_transactions),
        'products_count': len(df_products),
        'customers_count': len(df_customers),
        'extraction_timestamp': datetime.now().isoformat()
    }
    
    print(f"📊 Metadatos de extracción: {metadata}")
    
    # Retornar metadatos (se almacenan automáticamente en XCom)
    return metadata


@task(dag=dag)
def clean_transactions(**context):
    """
    Limpia y normaliza las transacciones.
    
    Operaciones de limpieza:
    - Eliminar duplicados basados en transaction_id
    - Eliminar registros con valores nulos en campos críticos
    - Normalizar formatos de fechas
    - Validar rangos de valores numéricos (amount > 0, quantity > 0)
    - Convertir tipos de datos apropiadamente
    
    Returns:
        dict: Metadatos sobre el proceso de limpieza
    """
    print("🧹 Limpiando transacciones...")
    
    # Obtener metadatos de la tarea anterior via XCom
    ti = context['ti']
    extraction_metadata = ti.xcom_pull(task_ids='extract_raw_data')
    print(f"📥 Registros originales: {extraction_metadata['transactions_count']}")
    
    # Extraer transacciones
    query = "SELECT * FROM raw.transactions"
    df = execute_query(query)
    initial_count = len(df)
    
    # 1. Eliminar duplicados
    df_before_dedup = len(df)
    df = df.drop_duplicates(subset=['transaction_id'], keep='first')
    duplicates_removed = df_before_dedup - len(df)
    print(f"✓ Duplicados eliminados: {duplicates_removed}")
    
    # 2. Eliminar registros con nulos en campos críticos
    critical_columns = ['transaction_id', 'customer_id', 'product_id', 'transaction_date', 'amount', 'quantity']
    df_before_nulls = len(df)
    df = df.dropna(subset=critical_columns)
    nulls_removed = df_before_nulls - len(df)
    print(f"✓ Registros con nulos eliminados: {nulls_removed}")
    
    # 3. Validar rangos de valores numéricos
    df_before_validation = len(df)
    df = df[(df['amount'] > 0) & (df['quantity'] > 0)]
    invalid_removed = df_before_validation - len(df)
    print(f"✓ Registros con valores inválidos eliminados: {invalid_removed}")
    
    # 4. Normalizar tipos de datos
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['amount'] = df['amount'].astype(float)
    df['quantity'] = df['quantity'].astype(int)
    
    # 5. Guardar transacciones limpias en una tabla temporal
    # (En la siguiente tarea se enriquecerán con información de productos)
    engine = get_postgres_engine()
    df.to_sql('transactions_temp_clean', engine, schema='processed', 
              if_exists='replace', index=False)
    
    final_count = len(df)
    print(f"✅ Limpieza completada: {final_count} registros limpios")
    
    # Preparar metadatos
    cleaning_metadata = {
        'initial_count': initial_count,
        'final_count': final_count,
        'duplicates_removed': duplicates_removed,
        'nulls_removed': nulls_removed,
        'invalid_removed': invalid_removed,
        'total_removed': initial_count - final_count,
        'cleaning_timestamp': datetime.now().isoformat()
    }
    
    return cleaning_metadata


@task(dag=dag)
def enrich_with_product_info(**context):
    """
    Enriquece las transacciones con información de productos.
    
    Realiza un JOIN entre transacciones limpias y productos para agregar:
    - Nombre del producto
    - Categoría del producto
    - Precio del producto (para validaciones futuras)
    
    Returns:
        dict: Metadatos sobre el enriquecimiento
    """
    print("🔗 Enriqueciendo transacciones con información de productos...")
    
    # Obtener metadatos de limpieza
    ti = context['ti']
    cleaning_metadata = ti.xcom_pull(task_ids='clean_transactions')
    print(f"📥 Transacciones limpias: {cleaning_metadata['final_count']}")
    
    # Extraer transacciones limpias
    transactions_query = "SELECT * FROM processed.transactions_temp_clean"
    df_transactions = execute_query(transactions_query)
    
    # Extraer productos
    products_query = "SELECT product_id, product_name, category, price FROM raw.products"
    df_products = execute_query(products_query)
    
    # Realizar JOIN (left join para mantener todas las transacciones)
    df_enriched = df_transactions.merge(
        df_products,
        on='product_id',
        how='left'
    )
    
    # Contar transacciones sin información de producto
    missing_product_info = df_enriched['product_name'].isnull().sum()
    if missing_product_info > 0:
        print(f"⚠️  Advertencia: {missing_product_info} transacciones sin información de producto")
    
    # Guardar transacciones enriquecidas en processed layer
    engine = get_postgres_engine()
    
    # Seleccionar columnas finales
    final_columns = [
        'transaction_id', 'customer_id', 'product_id', 'transaction_date',
        'amount', 'quantity', 'product_name', 'category'
    ]
    df_final = df_enriched[final_columns]
    
    # Cargar a tabla final
    df_final.to_sql('transactions_clean', engine, schema='processed',
                    if_exists='replace', index=False)
    
    print(f"✅ Enriquecimiento completado: {len(df_final)} transacciones enriquecidas")
    
    # Preparar metadatos
    enrichment_metadata = {
        'enriched_count': len(df_final),
        'missing_product_info': int(missing_product_info),
        'enrichment_timestamp': datetime.now().isoformat()
    }
    
    return enrichment_metadata


@task(dag=dag)
def calculate_daily_metrics(**context):
    """
    Calcula métricas agregadas diarias de ventas.
    
    Métricas calculadas:
    - Total de transacciones por día
    - Ingresos totales por día
    - Valor promedio de transacción
    - Número de clientes únicos por día
    - Categoría más vendida por día
    
    Returns:
        dict: Metadatos sobre las métricas calculadas
    """
    print("📊 Calculando métricas diarias de ventas...")
    
    # Extraer transacciones enriquecidas
    query = """
        SELECT 
            DATE(transaction_date) as metric_date,
            transaction_id,
            customer_id,
            amount,
            category
        FROM processed.transactions_clean
    """
    df = execute_query(query)
    
    if df.empty:
        print("⚠️  No hay datos para calcular métricas")
        return {'metrics_calculated': 0}
    
    # Calcular métricas agregadas por día
    daily_metrics = df.groupby('metric_date').agg({
        'transaction_id': 'count',  # Total de transacciones
        'amount': ['sum', 'mean'],  # Ingresos totales y promedio
        'customer_id': 'nunique'    # Clientes únicos
    }).reset_index()
    
    # Aplanar nombres de columnas
    daily_metrics.columns = [
        'metric_date', 'total_transactions', 'total_revenue', 
        'avg_transaction_value', 'unique_customers'
    ]
    
    # Calcular categoría más vendida por día
    top_category_by_day = df.groupby(['metric_date', 'category']).size().reset_index(name='count')
    top_category_by_day = top_category_by_day.loc[
        top_category_by_day.groupby('metric_date')['count'].idxmax()
    ][['metric_date', 'category']]
    top_category_by_day.columns = ['metric_date', 'top_category']
    
    # Combinar con métricas principales
    daily_metrics = daily_metrics.merge(top_category_by_day, on='metric_date', how='left')
    
    # Redondear valores numéricos
    daily_metrics['total_revenue'] = daily_metrics['total_revenue'].round(2)
    daily_metrics['avg_transaction_value'] = daily_metrics['avg_transaction_value'].round(2)
    
    # Cargar a analytics layer
    engine = get_postgres_engine()
    daily_metrics.to_sql('daily_sales_metrics', engine, schema='analytics',
                         if_exists='replace', index=False)
    
    print(f"✅ Métricas diarias calculadas: {len(daily_metrics)} días procesados")
    print(f"📈 Ingresos totales: ${daily_metrics['total_revenue'].sum():,.2f}")
    print(f"📈 Promedio de transacciones por día: {daily_metrics['total_transactions'].mean():.0f}")
    
    # Preparar metadatos
    metrics_metadata = {
        'days_processed': len(daily_metrics),
        'total_revenue': float(daily_metrics['total_revenue'].sum()),
        'avg_daily_transactions': float(daily_metrics['total_transactions'].mean()),
        'calculation_timestamp': datetime.now().isoformat()
    }
    
    return metrics_metadata


@task(dag=dag)
def calculate_customer_metrics(**context):
    """
    Calcula métricas por cliente.
    
    Métricas calculadas por cliente y fecha:
    - Número de transacciones
    - Total gastado
    - Valor promedio de orden
    - Días desde la última compra
    
    Returns:
        dict: Metadatos sobre las métricas de clientes
    """
    print("👥 Calculando métricas por cliente...")
    
    # Extraer transacciones enriquecidas
    query = """
        SELECT 
            customer_id,
            DATE(transaction_date) as metric_date,
            transaction_date,
            amount
        FROM processed.transactions_clean
        ORDER BY customer_id, transaction_date
    """
    df = execute_query(query)
    
    if df.empty:
        print("⚠️  No hay datos para calcular métricas de clientes")
        return {'customers_processed': 0}
    
    # Convertir a datetime
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['metric_date'] = pd.to_datetime(df['metric_date'])
    
    # Calcular métricas agregadas por cliente y fecha
    customer_metrics = df.groupby(['customer_id', 'metric_date']).agg({
        'amount': ['count', 'sum', 'mean']
    }).reset_index()
    
    # Aplanar nombres de columnas
    customer_metrics.columns = [
        'customer_id', 'metric_date', 'transaction_count', 
        'total_spent', 'avg_order_value'
    ]
    
    # Calcular días desde la última compra para cada cliente
    # (Para cada fecha, calcular días desde la compra anterior del mismo cliente)
    df_sorted = df.sort_values(['customer_id', 'transaction_date'])
    df_sorted['prev_purchase_date'] = df_sorted.groupby('customer_id')['transaction_date'].shift(1)
    df_sorted['days_since_last_purchase'] = (
        df_sorted['transaction_date'] - df_sorted['prev_purchase_date']
    ).dt.days
    
    # Para la primera compra de cada cliente, usar 0 días
    df_sorted['days_since_last_purchase'] = df_sorted['days_since_last_purchase'].fillna(0).astype(int)
    
    # Agregar a nivel de fecha (tomar el mínimo de días para cada día)
    days_since_purchase = df_sorted.groupby(['customer_id', 'metric_date'])['days_since_last_purchase'].min().reset_index()
    
    # Combinar con métricas principales
    customer_metrics = customer_metrics.merge(
        days_since_purchase, 
        on=['customer_id', 'metric_date'], 
        how='left'
    )
    
    # Redondear valores numéricos
    customer_metrics['total_spent'] = customer_metrics['total_spent'].round(2)
    customer_metrics['avg_order_value'] = customer_metrics['avg_order_value'].round(2)
    
    # Cargar a analytics layer
    engine = get_postgres_engine()
    customer_metrics.to_sql('customer_metrics', engine, schema='analytics',
                           if_exists='replace', index=False)
    
    unique_customers = customer_metrics['customer_id'].nunique()
    print(f"✅ Métricas de clientes calculadas: {unique_customers} clientes procesados")
    print(f"📊 Total de registros de métricas: {len(customer_metrics)}")
    
    # Preparar metadatos
    metrics_metadata = {
        'unique_customers': unique_customers,
        'total_metric_records': len(customer_metrics),
        'avg_transactions_per_customer': float(customer_metrics['transaction_count'].mean()),
        'calculation_timestamp': datetime.now().isoformat()
    }
    
    return metrics_metadata


@task(dag=dag)
def load_to_processed(**context):
    """
    Tarea final que valida y registra la carga exitosa a las capas processed y analytics.
    
    Esta tarea:
    - Valida que los datos se hayan cargado correctamente
    - Registra métricas de la ejecución en la tabla de auditoría
    - Imprime resumen de la ejecución del pipeline
    """
    print("✅ Validando carga a capas processed y analytics...")
    
    # Obtener todos los metadatos de tareas anteriores via XCom
    ti = context['ti']
    extraction_metadata = ti.xcom_pull(task_ids='extract_raw_data')
    cleaning_metadata = ti.xcom_pull(task_ids='clean_transactions')
    enrichment_metadata = ti.xcom_pull(task_ids='enrich_with_product_info')
    daily_metrics_metadata = ti.xcom_pull(task_ids='calculate_daily_metrics')
    customer_metrics_metadata = ti.xcom_pull(task_ids='calculate_customer_metrics')
    
    # Validar conteos en tablas finales
    engine = get_postgres_engine()
    
    # Contar registros en processed layer
    processed_count_query = "SELECT COUNT(*) as count FROM processed.transactions_clean"
    processed_count = execute_query(processed_count_query)['count'][0]
    
    # Contar registros en analytics layer
    daily_metrics_count_query = "SELECT COUNT(*) as count FROM analytics.daily_sales_metrics"
    daily_metrics_count = execute_query(daily_metrics_count_query)['count'][0]
    
    customer_metrics_count_query = "SELECT COUNT(*) as count FROM analytics.customer_metrics"
    customer_metrics_count = execute_query(customer_metrics_count_query)['count'][0]
    
    print("\n" + "="*70)
    print("📊 RESUMEN DE EJECUCIÓN DEL PIPELINE DE TRANSFORMACIÓN")
    print("="*70)
    print(f"\n📥 EXTRACCIÓN:")
    print(f"   • Transacciones extraídas: {extraction_metadata['transactions_count']}")
    print(f"   • Productos extraídos: {extraction_metadata['products_count']}")
    print(f"   • Clientes extraídos: {extraction_metadata['customers_count']}")
    
    print(f"\n🧹 LIMPIEZA:")
    print(f"   • Registros iniciales: {cleaning_metadata['initial_count']}")
    print(f"   • Duplicados eliminados: {cleaning_metadata['duplicates_removed']}")
    print(f"   • Nulos eliminados: {cleaning_metadata['nulls_removed']}")
    print(f"   • Inválidos eliminados: {cleaning_metadata['invalid_removed']}")
    print(f"   • Registros finales: {cleaning_metadata['final_count']}")
    
    print(f"\n🔗 ENRIQUECIMIENTO:")
    print(f"   • Transacciones enriquecidas: {enrichment_metadata['enriched_count']}")
    print(f"   • Sin info de producto: {enrichment_metadata['missing_product_info']}")
    
    print(f"\n📊 MÉTRICAS DIARIAS:")
    print(f"   • Días procesados: {daily_metrics_metadata['days_processed']}")
    print(f"   • Ingresos totales: ${daily_metrics_metadata['total_revenue']:,.2f}")
    print(f"   • Promedio transacciones/día: {daily_metrics_metadata['avg_daily_transactions']:.0f}")
    
    print(f"\n👥 MÉTRICAS DE CLIENTES:")
    print(f"   • Clientes únicos: {customer_metrics_metadata['unique_customers']}")
    print(f"   • Registros de métricas: {customer_metrics_metadata['total_metric_records']}")
    print(f"   • Promedio transacciones/cliente: {customer_metrics_metadata['avg_transactions_per_customer']:.2f}")
    
    print(f"\n✅ VALIDACIÓN DE CARGA:")
    print(f"   • Processed layer: {processed_count} registros")
    print(f"   • Daily metrics: {daily_metrics_count} registros")
    print(f"   • Customer metrics: {customer_metrics_count} registros")
    print("="*70 + "\n")
    
    # Registrar ejecución en tabla de auditoría
    execution_date = context['execution_date']
    dag_id = context['dag'].dag_id
    
    audit_record = pd.DataFrame([{
        'dag_id': dag_id,
        'execution_date': execution_date,
        'status': 'SUCCESS',
        'records_processed': processed_count,
        'duration_seconds': None,  # Se puede calcular si se guarda start_time
        'error_message': None
    }])
    
    audit_record.to_sql('pipeline_executions', engine, schema='audit',
                       if_exists='append', index=False)
    
    print("✅ Pipeline de transformación completado exitosamente!")
    
    return {
        'status': 'SUCCESS',
        'processed_records': processed_count,
        'daily_metrics_records': daily_metrics_count,
        'customer_metrics_records': customer_metrics_count
    }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Definir el flujo de tareas usando el operador >>
# Este operador establece dependencias: tarea_anterior >> tarea_siguiente

# Flujo principal:
# 1. Extraer datos raw
# 2. Limpiar transacciones
# 3. Enriquecer con información de productos
# 4. Calcular métricas en paralelo (diarias y por cliente)
# 5. Validar y registrar carga

extract_task = extract_raw_data()
clean_task = clean_transactions()
enrich_task = enrich_with_product_info()
daily_metrics_task = calculate_daily_metrics()
customer_metrics_task = calculate_customer_metrics()
load_task = load_to_processed()

# Establecer dependencias
extract_task >> clean_task >> enrich_task
enrich_task >> [daily_metrics_task, customer_metrics_task]
[daily_metrics_task, customer_metrics_task] >> load_task

# Nota sobre dependencias:
# - extract_task debe completarse antes de clean_task
# - clean_task debe completarse antes de enrich_task
# - enrich_task debe completarse antes de calcular métricas
# - daily_metrics_task y customer_metrics_task se ejecutan en paralelo
# - load_task espera a que ambas tareas de métricas se completen
