"""
Solución Ejercicio 02: Transformación y Análisis RFM
====================================================

Este DAG extiende el pipeline de transformaciones para incluir análisis RFM
(Recency, Frequency, Monetary) de clientes. Demuestra:

- Transformaciones avanzadas de datos
- Cálculo de métricas de negocio (RFM)
- Segmentación de clientes usando quintiles
- Validaciones de calidad robustas
- Flujos condicionales con BranchPythonOperator
- Generación de reportes analíticos

El análisis RFM permite segmentar clientes para personalizar estrategias de marketing
y retención basadas en su comportamiento de compra.

Autor: Solución de Referencia - Taller de Apache Airflow
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import BranchPythonOperator
import pandas as pd
import numpy as np
from utils.db_utils import get_postgres_engine, execute_query

# ============================================================================
# CONFIGURACIÓN DEL DAG
# ============================================================================

default_args = {
    'owner': 'estudiante',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='ejercicio_02_transformacion_rfm',
    default_args=default_args,
    description='Pipeline de transformación con análisis RFM de clientes',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ejercicio', 'transformacion', 'rfm', 'analytics'],
    doc_md=__doc__,
}

# ============================================================================
# TAREAS EXISTENTES DEL DAG 02 (simplificadas para el ejercicio)
# ============================================================================

@task(dag=dag)
def extract_raw_data(**context):
    """Extrae datos de la capa raw (versión simplificada)."""
    print("📥 Extrayendo datos de la capa raw...")
    
    transactions_query = "SELECT * FROM raw.transactions"
    df_transactions = execute_query(transactions_query)
    print(f"✓ Transacciones extraídas: {len(df_transactions)} registros")
    
    return {'transactions_count': len(df_transactions)}


@task(dag=dag)
def process_transactions(**context):
    """Procesa transacciones básicas (versión simplificada)."""
    print("🔄 Procesando transacciones...")
    
    # En el DAG real, aquí irían las transformaciones del DAG 02
    # Para este ejercicio, asumimos que ya están procesadas
    
    return {'status': 'processed'}


# ============================================================================
# NUEVAS TAREAS: ANÁLISIS RFM
# ============================================================================

@task(dag=dag)
def calculate_rfm_metrics(**context):
    """
    Calcula las métricas RFM (Recency, Frequency, Monetary) para cada cliente.
    
    RFM es una técnica de segmentación que evalúa:
    - Recency: Días desde la última compra (menor es mejor)
    - Frequency: Número de transacciones (mayor es mejor)
    - Monetary: Total gastado (mayor es mejor)
    
    Cada métrica se convierte en un score de 1-5 usando quintiles,
    y se asigna un segmento de cliente basado en el score RFM combinado.
    
    Returns:
        dict: Estadísticas de las métricas RFM calculadas
    """
    print("📊 Calculando métricas RFM para segmentación de clientes...")
    
    # Fecha de referencia para cálculo de recency (hoy)
    reference_date = datetime.now()
    print(f"📅 Fecha de referencia: {reference_date.date()}")
    
    # Extraer transacciones de la capa processed
    query = """
        SELECT 
            customer_id,
            transaction_date,
            amount
        FROM processed.transactions_clean
        ORDER BY customer_id, transaction_date
    """
    df = execute_query(query)
    
    if df.empty:
        raise ValueError("No hay transacciones para calcular RFM")
    
    print(f"✓ Transacciones cargadas: {len(df)} registros")
    
    # Convertir transaction_date a datetime
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # ========================================================================
    # PASO 1: Calcular métricas base por cliente
    # ========================================================================
    
    print("\n📈 Calculando métricas base...")
    
    rfm = df.groupby('customer_id').agg({
        'transaction_date': lambda x: (reference_date - x.max()).days,  # Recency
        'customer_id': 'count',  # Frequency
        'amount': 'sum'  # Monetary
    }).reset_index()
    
    # Renombrar columnas
    rfm.columns = ['customer_id', 'recency_days', 'frequency', 'monetary']
    
    print(f"✓ Clientes analizados: {len(rfm)}")
    print(f"  • Recency promedio: {rfm['recency_days'].mean():.1f} días")
    print(f"  • Frequency promedio: {rfm['frequency'].mean():.1f} transacciones")
    print(f"  • Monetary promedio: ${rfm['monetary'].mean():,.2f}")
    
    # ========================================================================
    # PASO 2: Calcular scores RFM (1-5) usando quintiles
    # ========================================================================
    
    print("\n🎯 Calculando scores RFM (1-5)...")
    
    # Para Recency: menor es mejor, así que invertimos la escala
    # qcut divide en quintiles y asigna labels 1-5
    rfm['r_score'] = pd.qcut(
        rfm['recency_days'], 
        q=5, 
        labels=[5, 4, 3, 2, 1],  # Invertido: menor recency = mayor score
        duplicates='drop'
    ).astype(int)
    
    # Para Frequency: mayor es mejor
    rfm['f_score'] = pd.qcut(
        rfm['frequency'],
        q=5,
        labels=[1, 2, 3, 4, 5],
        duplicates='drop'
    ).astype(int)
    
    # Para Monetary: mayor es mejor
    rfm['m_score'] = pd.qcut(
        rfm['monetary'],
        q=5,
        labels=[1, 2, 3, 4, 5],
        duplicates='drop'
    ).astype(int)
    
    print("✓ Scores RFM calculados")
    
    # ========================================================================
    # PASO 3: Crear RFM Score combinado (concatenación de R, F, M)
    # ========================================================================
    
    rfm['rfm_score'] = (
        rfm['r_score'].astype(str) + 
        rfm['f_score'].astype(str) + 
        rfm['m_score'].astype(str)
    )
    
    print(f"✓ RFM Score creado (ejemplo: {rfm['rfm_score'].iloc[0]})")
    
    # ========================================================================
    # PASO 4: Asignar segmentos de clientes basados en RFM score
    # ========================================================================
    
    print("\n🏷️  Asignando segmentos de clientes...")
    
    def assign_segment(row):
        """Asigna segmento basado en scores RFM."""
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        avg_score = (r + f + m) / 3
        
        # Lógica de segmentación
        if avg_score >= 4.5:
            return 'Champions'
        elif avg_score >= 3.5:
            return 'Loyal'
        elif avg_score >= 2.5:
            return 'Potential'
        elif avg_score >= 1.5:
            return 'At Risk'
        else:
            return 'Lost'
    
    rfm['segment'] = rfm.apply(assign_segment, axis=1)
    
    # Estadísticas de segmentación
    segment_counts = rfm['segment'].value_counts()
    print("\n📊 Distribución de segmentos:")
    for segment, count in segment_counts.items():
        percentage = (count / len(rfm)) * 100
        print(f"  • {segment}: {count} clientes ({percentage:.1f}%)")
    
    # ========================================================================
    # PASO 5: Guardar resultados en analytics.customer_rfm
    # ========================================================================
    
    print("\n💾 Guardando métricas RFM en base de datos...")
    
    # Crear tabla si no existe
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS analytics.customer_rfm (
        customer_id VARCHAR(50) PRIMARY KEY,
        recency_days INTEGER,
        frequency INTEGER,
        monetary DECIMAL(12,2),
        r_score INTEGER,
        f_score INTEGER,
        m_score INTEGER,
        rfm_score VARCHAR(3),
        segment VARCHAR(50),
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    engine = get_postgres_engine()
    with engine.connect() as conn:
        conn.execute(create_table_sql)
        conn.commit()
    
    # Cargar datos
    rfm.to_sql('customer_rfm', engine, schema='analytics',
               if_exists='replace', index=False)
    
    print(f"✅ Métricas RFM guardadas: {len(rfm)} clientes")
    
    # Preparar metadatos para retornar
    metadata = {
        'customers_analyzed': len(rfm),
        'segments': segment_counts.to_dict(),
        'avg_recency': float(rfm['recency_days'].mean()),
        'avg_frequency': float(rfm['frequency'].mean()),
        'avg_monetary': float(rfm['monetary'].mean()),
        'calculation_timestamp': datetime.now().isoformat()
    }
    
    return metadata


@task(dag=dag)
def validate_rfm_metrics(**context):
    """
    Valida que las métricas RFM calculadas sean correctas.
    
    Validaciones:
    1. Rangos de scores (1-5)
    2. Valores numéricos válidos
    3. Segmentos válidos
    4. Completitud de datos
    
    Returns:
        dict: Resultados de todas las validaciones
    """
    print("🔍 Validando métricas RFM...")
    
    # Extraer métricas RFM
    query = "SELECT * FROM analytics.customer_rfm"
    df = execute_query(query)
    
    if df.empty:
        raise ValueError("No hay métricas RFM para validar")
    
    print(f"📊 Validando {len(df)} registros de clientes...")
    
    validation_results = {}
    all_passed = True
    
    # ========================================================================
    # VALIDACIÓN 1: Rangos de scores (1-5)
    # ========================================================================
    
    print("\n1️⃣  Validando rangos de scores...")
    
    score_columns = ['r_score', 'f_score', 'm_score']
    invalid_scores = {}
    
    for col in score_columns:
        invalid = df[(df[col] < 1) | (df[col] > 5)]
        invalid_scores[col] = len(invalid)
        
        if len(invalid) > 0:
            all_passed = False
            print(f"   ❌ {col}: {len(invalid)} valores fuera de rango [1-5]")
        else:
            print(f"   ✅ {col}: Todos los valores en rango [1-5]")
    
    validation_results['score_ranges'] = {
        'passed': all(count == 0 for count in invalid_scores.values()),
        'invalid_counts': invalid_scores
    }
    
    # Validar formato de rfm_score (3 dígitos)
    invalid_rfm_format = df[df['rfm_score'].str.len() != 3]
    if len(invalid_rfm_format) > 0:
        all_passed = False
        print(f"   ❌ rfm_score: {len(invalid_rfm_format)} valores con formato incorrecto")
    else:
        print(f"   ✅ rfm_score: Todos tienen formato correcto (3 dígitos)")
    
    validation_results['rfm_format'] = {
        'passed': len(invalid_rfm_format) == 0,
        'invalid_count': len(invalid_rfm_format)
    }
    
    # ========================================================================
    # VALIDACIÓN 2: Valores numéricos válidos
    # ========================================================================
    
    print("\n2️⃣  Validando valores numéricos...")
    
    # Recency >= 0
    invalid_recency = df[df['recency_days'] < 0]
    if len(invalid_recency) > 0:
        all_passed = False
        print(f"   ❌ recency_days: {len(invalid_recency)} valores negativos")
    else:
        print(f"   ✅ recency_days: Todos >= 0")
    
    # Frequency >= 1
    invalid_frequency = df[df['frequency'] < 1]
    if len(invalid_frequency) > 0:
        all_passed = False
        print(f"   ❌ frequency: {len(invalid_frequency)} valores < 1")
    else:
        print(f"   ✅ frequency: Todos >= 1")
    
    # Monetary > 0
    invalid_monetary = df[df['monetary'] <= 0]
    if len(invalid_monetary) > 0:
        all_passed = False
        print(f"   ❌ monetary: {len(invalid_monetary)} valores <= 0")
    else:
        print(f"   ✅ monetary: Todos > 0")
    
    validation_results['numeric_values'] = {
        'passed': (len(invalid_recency) == 0 and 
                  len(invalid_frequency) == 0 and 
                  len(invalid_monetary) == 0),
        'invalid_recency': len(invalid_recency),
        'invalid_frequency': len(invalid_frequency),
        'invalid_monetary': len(invalid_monetary)
    }
    
    # ========================================================================
    # VALIDACIÓN 3: Segmentos válidos
    # ========================================================================
    
    print("\n3️⃣  Validando segmentos...")
    
    valid_segments = ['Champions', 'Loyal', 'Potential', 'At Risk', 'Lost']
    invalid_segments = df[~df['segment'].isin(valid_segments)]
    
    if len(invalid_segments) > 0:
        all_passed = False
        print(f"   ❌ segment: {len(invalid_segments)} valores inválidos")
        print(f"      Segmentos inválidos: {invalid_segments['segment'].unique()}")
    else:
        print(f"   ✅ segment: Todos los valores son válidos")
    
    validation_results['segments'] = {
        'passed': len(invalid_segments) == 0,
        'invalid_count': len(invalid_segments),
        'valid_segments': valid_segments
    }
    
    # ========================================================================
    # VALIDACIÓN 4: Completitud de datos
    # ========================================================================
    
    print("\n4️⃣  Validando completitud...")
    
    critical_columns = ['customer_id', 'recency_days', 'frequency', 'monetary',
                       'r_score', 'f_score', 'm_score', 'rfm_score', 'segment']
    
    null_counts = {}
    for col in critical_columns:
        null_count = df[col].isnull().sum()
        null_counts[col] = null_count
        
        if null_count > 0:
            all_passed = False
            print(f"   ❌ {col}: {null_count} valores nulos")
        else:
            print(f"   ✅ {col}: Sin valores nulos")
    
    validation_results['completeness'] = {
        'passed': all(count == 0 for count in null_counts.values()),
        'null_counts': null_counts
    }
    
    # ========================================================================
    # RESUMEN DE VALIDACIÓN
    # ========================================================================
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ TODAS LAS VALIDACIONES PASARON")
    else:
        print("❌ ALGUNAS VALIDACIONES FALLARON")
    print("="*70)
    
    validation_results['all_passed'] = all_passed
    validation_results['records_validated'] = len(df)
    validation_results['validation_timestamp'] = datetime.now().isoformat()
    
    return validation_results


def branch_on_rfm_quality(**context):
    """
    Decide el flujo basado en los resultados de validación RFM.
    
    Returns:
        str: ID de la siguiente tarea a ejecutar
    """
    print("🔀 Evaluando resultados de validación RFM...")
    
    ti = context['ti']
    validation_results = ti.xcom_pull(task_ids='validate_rfm_metrics')
    
    if validation_results['all_passed']:
        print("✅ Todas las validaciones pasaron. Generando reporte RFM.")
        return 'generate_rfm_report'
    else:
        print("❌ Algunas validaciones fallaron. Manejando error.")
        return 'handle_rfm_validation_failure'


@task(dag=dag)
def generate_rfm_report(**context):
    """
    Genera un reporte resumen de la segmentación RFM.
    
    El reporte incluye:
    - Número de clientes por segmento
    - Valor promedio por segmento
    - Frecuencia promedio por segmento
    - Recency promedio por segmento
    - Top 10 clientes
    
    Returns:
        dict: Metadatos del reporte generado
    """
    print("📊 Generando reporte resumen de segmentación RFM...")
    
    # Extraer métricas RFM
    query = "SELECT * FROM analytics.customer_rfm"
    df = execute_query(query)
    
    # ========================================================================
    # Calcular estadísticas por segmento
    # ========================================================================
    
    segment_stats = df.groupby('segment').agg({
        'customer_id': 'count',
        'monetary': 'mean',
        'frequency': 'mean',
        'recency_days': 'mean'
    }).reset_index()
    
    segment_stats.columns = [
        'segment', 'customer_count', 'avg_monetary', 
        'avg_frequency', 'avg_recency'
    ]
    
    # Redondear valores
    segment_stats['avg_monetary'] = segment_stats['avg_monetary'].round(2)
    segment_stats['avg_frequency'] = segment_stats['avg_frequency'].round(1)
    segment_stats['avg_recency'] = segment_stats['avg_recency'].round(1)
    
    # Ordenar por valor (Champions primero)
    segment_order = ['Champions', 'Loyal', 'Potential', 'At Risk', 'Lost']
    segment_stats['segment'] = pd.Categorical(
        segment_stats['segment'], 
        categories=segment_order, 
        ordered=True
    )
    segment_stats = segment_stats.sort_values('segment')
    
    # ========================================================================
    # Identificar top 10 clientes
    # ========================================================================
    
    top_customers = df.nlargest(10, 'monetary')[
        ['customer_id', 'rfm_score', 'segment', 'monetary', 'frequency']
    ]
    
    # ========================================================================
    # Guardar reporte en base de datos
    # ========================================================================
    
    print("\n💾 Guardando reporte en base de datos...")
    
    # Crear tabla si no existe
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS analytics.rfm_summary_report (
        segment VARCHAR(50),
        customer_count INTEGER,
        avg_monetary DECIMAL(12,2),
        avg_frequency DECIMAL(10,1),
        avg_recency DECIMAL(10,1),
        report_date DATE DEFAULT CURRENT_DATE
    );
    """
    
    engine = get_postgres_engine()
    with engine.connect() as conn:
        conn.execute(create_table_sql)
        conn.commit()
    
    # Cargar reporte
    segment_stats.to_sql('rfm_summary_report', engine, schema='analytics',
                        if_exists='replace', index=False)
    
    # ========================================================================
    # Imprimir reporte
    # ========================================================================
    
    print("\n" + "="*70)
    print("📊 REPORTE DE SEGMENTACIÓN RFM")
    print("="*70)
    print("\n📈 Estadísticas por Segmento:")
    print(segment_stats.to_string(index=False))
    
    print("\n🏆 Top 10 Clientes (por valor monetario):")
    print(top_customers.to_string(index=False))
    
    print("\n💡 Insights:")
    champions = segment_stats[segment_stats['segment'] == 'Champions']
    if not champions.empty:
        print(f"  • Champions representan {champions['customer_count'].values[0]} clientes")
        print(f"    con valor promedio de ${champions['avg_monetary'].values[0]:,.2f}")
    
    lost = segment_stats[segment_stats['segment'] == 'Lost']
    if not lost.empty:
        print(f"  • {lost['customer_count'].values[0]} clientes en riesgo de pérdida (Lost)")
        print(f"    con {lost['avg_recency'].values[0]:.0f} días desde última compra")
    
    print("="*70 + "\n")
    
    return {
        'report_generated': True,
        'segments_analyzed': len(segment_stats),
        'top_customers_identified': len(top_customers),
        'report_timestamp': datetime.now().isoformat()
    }


@task(dag=dag)
def handle_rfm_validation_failure(**context):
    """
    Maneja el caso cuando las validaciones RFM fallan.
    
    Acciones:
    - Registra detalles de validaciones fallidas
    - Crea registro en tabla de auditoría
    - Imprime mensaje de error detallado
    """
    print("❌ Manejando fallo en validaciones RFM...")
    
    ti = context['ti']
    validation_results = ti.xcom_pull(task_ids='validate_rfm_metrics')
    
    print("\n⚠️  VALIDACIONES FALLIDAS:")
    
    for validation_name, result in validation_results.items():
        if validation_name in ['all_passed', 'records_validated', 'validation_timestamp']:
            continue
        
        if isinstance(result, dict) and not result.get('passed', True):
            print(f"\n❌ {validation_name}:")
            for key, value in result.items():
                if key != 'passed':
                    print(f"   • {key}: {value}")
    
    # Registrar en auditoría
    engine = get_postgres_engine()
    audit_record = pd.DataFrame([{
        'dag_id': context['dag'].dag_id,
        'execution_date': context['execution_date'],
        'status': 'VALIDATION_FAILED',
        'records_processed': validation_results['records_validated'],
        'duration_seconds': None,
        'error_message': f"RFM validation failed: {validation_results}"
    }])
    
    audit_record.to_sql('pipeline_executions', engine, schema='audit',
                       if_exists='append', index=False)
    
    print("\n🚨 ACCIÓN REQUERIDA:")
    print("   • Revisar métricas RFM calculadas")
    print("   • Verificar datos de entrada")
    print("   • Corregir problemas antes de continuar")
    
    return {
        'validation_failed': True,
        'failure_timestamp': datetime.now().isoformat()
    }


@task(dag=dag, trigger_rule='none_failed_min_one_success')
def log_rfm_completion(**context):
    """
    Registra la finalización del proceso RFM.
    
    Se ejecuta siempre (tanto si las validaciones pasan como si fallan)
    para mantener registro completo de ejecuciones.
    """
    print("📝 Registrando finalización del proceso RFM...")
    
    ti = context['ti']
    rfm_metadata = ti.xcom_pull(task_ids='calculate_rfm_metrics')
    validation_results = ti.xcom_pull(task_ids='validate_rfm_metrics')
    
    print("\n" + "="*70)
    print("📊 RESUMEN DE PROCESO RFM")
    print("="*70)
    print(f"Clientes analizados: {rfm_metadata['customers_analyzed']}")
    print(f"Validación: {'✅ EXITOSA' if validation_results['all_passed'] else '❌ FALLIDA'}")
    print(f"Segmentos identificados: {len(rfm_metadata['segments'])}")
    print("\nDistribución de segmentos:")
    for segment, count in rfm_metadata['segments'].items():
        print(f"  • {segment}: {count} clientes")
    print("="*70 + "\n")
    
    return {
        'rfm_process_completed': True,
        'completion_timestamp': datetime.now().isoformat()
    }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Tareas existentes (simplificadas)
extract_task = extract_raw_data()
process_task = process_transactions()

# Nuevas tareas RFM
calculate_rfm_task = calculate_rfm_metrics()
validate_rfm_task = validate_rfm_metrics()

branch_rfm_task = BranchPythonOperator(
    task_id='branch_on_rfm_quality',
    python_callable=branch_on_rfm_quality,
    provide_context=True,
    dag=dag
)

generate_report_task = generate_rfm_report()
handle_failure_task = handle_rfm_validation_failure()
log_rfm_task = log_rfm_completion()

# Establecer dependencias
extract_task >> process_task >> calculate_rfm_task
calculate_rfm_task >> validate_rfm_task >> branch_rfm_task
branch_rfm_task >> [generate_report_task, handle_failure_task]
[generate_report_task, handle_failure_task] >> log_rfm_task

