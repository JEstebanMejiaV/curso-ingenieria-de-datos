"""
DAG 03: Validación de Calidad de Datos
=======================================

Este DAG demuestra la implementación de validaciones de calidad de datos en Airflow.
Implementa un pipeline completo de validación que:
1. Extrae datos a validar desde la capa processed
2. Ejecuta múltiples validaciones de calidad (nulos, rangos, unicidad, integridad referencial)
3. Usa BranchPythonOperator para decidir el flujo basado en resultados de validación
4. Maneja casos de éxito y fallo de validaciones
5. Registra todos los resultados en una tabla de auditoría

Conceptos clave demostrados:
- Validaciones de calidad de datos usando funciones de validation_utils
- Flujos condicionales con BranchPythonOperator
- Manejo de resultados de validación y decisiones de pipeline
- Registro de auditoría para trazabilidad
- Uso de XCom para compartir resultados entre tareas

Caso de uso: Validación de calidad para datos de ventas e-commerce

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import BranchPythonOperator
import pandas as pd
from utils.db_utils import get_postgres_engine, execute_query
from utils.validation_utils import validate_nulls, validate_range, validate_uniqueness

# ============================================================================
# CONFIGURACIÓN DEL DAG
# ============================================================================

# Argumentos por defecto para todas las tareas del DAG
default_args = {
    'owner': 'data_quality_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG
dag = DAG(
    dag_id='03_dag_calidad',
    default_args=default_args,
    description='Pipeline de validación de calidad de datos con flujos condicionales',
    schedule_interval='@daily',  # Ejecutar diariamente después de las transformaciones
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['calidad', 'validacion', 'taller'],
    doc_md=__doc__,
)

# ============================================================================
# TAREAS DEL DAG
# ============================================================================

@task(dag=dag)
def extract_data(**context):
    """
    Extrae datos de la capa processed para validar.
    
    Esta tarea lee las transacciones limpias y enriquecidas desde la capa
    processed y las prepara para las validaciones de calidad.
    
    Returns:
        dict: Metadatos sobre los datos extraídos
    """
    print("📥 Extrayendo datos para validación de calidad...")
    
    # Extraer transacciones de la capa processed
    query = """
        SELECT 
            transaction_id,
            customer_id,
            product_id,
            transaction_date,
            amount,
            quantity,
            product_name,
            category
        FROM processed.transactions_clean
    """
    df = execute_query(query)
    
    print(f"✓ Datos extraídos: {len(df)} registros")
    
    # Guardar en tabla temporal para que otras tareas puedan acceder
    engine = get_postgres_engine()
    df.to_sql('transactions_to_validate', engine, schema='processed',
              if_exists='replace', index=False)
    
    # Preparar metadatos
    metadata = {
        'records_count': len(df),
        'extraction_timestamp': datetime.now().isoformat()
    }
    
    return metadata


@task(dag=dag)
def validate_nulls_task(**context):
    """
    Valida que no existan valores nulos en columnas críticas.
    
    Columnas críticas validadas:
    - transaction_id: Identificador único de transacción
    - customer_id: Identificador de cliente
    - product_id: Identificador de producto
    - transaction_date: Fecha de la transacción
    - amount: Monto de la transacción
    - quantity: Cantidad de productos
    
    Returns:
        dict: Resultados de la validación de nulos
    """
    print("🔍 Validando ausencia de valores nulos en columnas críticas...")
    
    # Extraer datos a validar
    query = "SELECT * FROM processed.transactions_to_validate"
    df = execute_query(query)
    
    # Definir columnas críticas
    critical_columns = [
        'transaction_id',
        'customer_id',
        'product_id',
        'transaction_date',
        'amount',
        'quantity'
    ]
    
    # Ejecutar validación usando validation_utils
    validation_results = validate_nulls(df, critical_columns)
    
    # Analizar resultados
    all_passed = all(result['passed'] for result in validation_results.values())
    total_nulls = sum(result['null_count'] for result in validation_results.values())
    
    # Imprimir resultados detallados
    print("\n" + "="*60)
    print("📊 RESULTADOS DE VALIDACIÓN DE NULOS")
    print("="*60)
    for column, result in validation_results.items():
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status} | {column}: {result['null_count']} nulos")
    print("="*60 + "\n")
    
    # Preparar resumen
    summary = {
        'check_name': 'validate_nulls',
        'check_result': 'PASS' if all_passed else 'FAIL',
        'records_checked': len(df),
        'records_failed': total_nulls,
        'details': validation_results,
        'timestamp': datetime.now().isoformat()
    }
    
    if all_passed:
        print("✅ Validación de nulos: EXITOSA")
    else:
        print(f"❌ Validación de nulos: FALLIDA ({total_nulls} valores nulos encontrados)")
    
    return summary


@task(dag=dag)
def validate_ranges_task(**context):
    """
    Valida que los valores numéricos estén dentro de rangos esperados.
    
    Validaciones de rangos:
    - amount: Debe estar entre 0 y 100,000 (transacciones razonables)
    - quantity: Debe estar entre 1 y 1,000 (cantidades razonables)
    
    Returns:
        dict: Resultados de la validación de rangos
    """
    print("🔍 Validando rangos de valores numéricos...")
    
    # Extraer datos a validar
    query = "SELECT * FROM processed.transactions_to_validate"
    df = execute_query(query)
    
    # Validar rango de amount
    amount_validation = validate_range(df, 'amount', min_val=0, max_val=100000)
    print(f"💰 Amount: {amount_validation['out_of_range_count']} valores fuera de rango [0, 100000]")
    print(f"   Rango encontrado: [{amount_validation['min_value']}, {amount_validation['max_value']}]")
    
    # Validar rango de quantity
    quantity_validation = validate_range(df, 'quantity', min_val=1, max_val=1000)
    print(f"📦 Quantity: {quantity_validation['out_of_range_count']} valores fuera de rango [1, 1000]")
    print(f"   Rango encontrado: [{quantity_validation['min_value']}, {quantity_validation['max_value']}]")
    
    # Analizar resultados
    all_passed = amount_validation['passed'] and quantity_validation['passed']
    total_out_of_range = (
        amount_validation['out_of_range_count'] + 
        quantity_validation['out_of_range_count']
    )
    
    # Preparar resumen
    summary = {
        'check_name': 'validate_ranges',
        'check_result': 'PASS' if all_passed else 'FAIL',
        'records_checked': len(df),
        'records_failed': total_out_of_range,
        'details': {
            'amount': amount_validation,
            'quantity': quantity_validation
        },
        'timestamp': datetime.now().isoformat()
    }
    
    if all_passed:
        print("✅ Validación de rangos: EXITOSA")
    else:
        print(f"❌ Validación de rangos: FALLIDA ({total_out_of_range} valores fuera de rango)")
    
    return summary


@task(dag=dag)
def validate_uniqueness_task(**context):
    """
    Valida que los identificadores sean únicos.
    
    Validaciones de unicidad:
    - transaction_id: Debe ser único (no duplicados)
    
    Returns:
        dict: Resultados de la validación de unicidad
    """
    print("🔍 Validando unicidad de identificadores...")
    
    # Extraer datos a validar
    query = "SELECT * FROM processed.transactions_to_validate"
    df = execute_query(query)
    
    # Validar unicidad de transaction_id
    uniqueness_validation = validate_uniqueness(df, 'transaction_id')
    
    print(f"🔑 Transaction ID:")
    print(f"   Total registros: {uniqueness_validation['total_count']}")
    print(f"   Valores únicos: {uniqueness_validation['unique_count']}")
    print(f"   Duplicados: {uniqueness_validation['duplicate_count']}")
    
    # Analizar resultados
    all_passed = uniqueness_validation['passed']
    
    # Preparar resumen
    summary = {
        'check_name': 'validate_uniqueness',
        'check_result': 'PASS' if all_passed else 'FAIL',
        'records_checked': uniqueness_validation['total_count'],
        'records_failed': uniqueness_validation['duplicate_count'],
        'details': uniqueness_validation,
        'timestamp': datetime.now().isoformat()
    }
    
    if all_passed:
        print("✅ Validación de unicidad: EXITOSA")
    else:
        print(f"❌ Validación de unicidad: FALLIDA ({uniqueness_validation['duplicate_count']} duplicados)")
    
    return summary


@task(dag=dag)
def validate_referential_integrity_task(**context):
    """
    Valida la integridad referencial entre tablas.
    
    Validaciones de integridad referencial:
    - Todos los customer_id en transacciones deben existir en la tabla de clientes
    - Todos los product_id en transacciones deben existir en la tabla de productos
    
    Returns:
        dict: Resultados de la validación de integridad referencial
    """
    print("🔍 Validando integridad referencial...")
    
    # Extraer transacciones
    transactions_query = "SELECT customer_id, product_id FROM processed.transactions_to_validate"
    df_transactions = execute_query(transactions_query)
    
    # Extraer clientes
    customers_query = "SELECT DISTINCT customer_id FROM raw.customers"
    df_customers = execute_query(customers_query)
    valid_customer_ids = set(df_customers['customer_id'])
    
    # Extraer productos
    products_query = "SELECT DISTINCT product_id FROM raw.products"
    df_products = execute_query(products_query)
    valid_product_ids = set(df_products['product_id'])
    
    # Validar customer_id
    invalid_customers = df_transactions[
        ~df_transactions['customer_id'].isin(valid_customer_ids)
    ]
    invalid_customer_count = len(invalid_customers)
    
    print(f"👥 Customer ID: {invalid_customer_count} referencias inválidas")
    
    # Validar product_id
    invalid_products = df_transactions[
        ~df_transactions['product_id'].isin(valid_product_ids)
    ]
    invalid_product_count = len(invalid_products)
    
    print(f"📦 Product ID: {invalid_product_count} referencias inválidas")
    
    # Analizar resultados
    all_passed = (invalid_customer_count == 0) and (invalid_product_count == 0)
    total_invalid = invalid_customer_count + invalid_product_count
    
    # Preparar resumen
    summary = {
        'check_name': 'validate_referential_integrity',
        'check_result': 'PASS' if all_passed else 'FAIL',
        'records_checked': len(df_transactions),
        'records_failed': total_invalid,
        'details': {
            'invalid_customer_ids': invalid_customer_count,
            'invalid_product_ids': invalid_product_count
        },
        'timestamp': datetime.now().isoformat()
    }
    
    if all_passed:
        print("✅ Validación de integridad referencial: EXITOSA")
    else:
        print(f"❌ Validación de integridad referencial: FALLIDA ({total_invalid} referencias inválidas)")
    
    return summary


def branch_on_quality(**context):
    """
    Decide el flujo del pipeline basado en los resultados de validación.
    
    Esta función es usada por BranchPythonOperator para determinar qué
    tarea ejecutar a continuación basándose en si todas las validaciones
    pasaron o si alguna falló.
    
    Returns:
        str: ID de la tarea a ejecutar ('handle_quality_pass' o 'handle_quality_fail')
    """
    print("🔀 Evaluando resultados de validaciones de calidad...")
    
    # Obtener resultados de todas las validaciones via XCom
    ti = context['ti']
    nulls_result = ti.xcom_pull(task_ids='validate_nulls_task')
    ranges_result = ti.xcom_pull(task_ids='validate_ranges_task')
    uniqueness_result = ti.xcom_pull(task_ids='validate_uniqueness_task')
    integrity_result = ti.xcom_pull(task_ids='validate_referential_integrity_task')
    
    # Verificar si todas las validaciones pasaron
    all_validations = [
        nulls_result,
        ranges_result,
        uniqueness_result,
        integrity_result
    ]
    
    all_passed = all(
        validation['check_result'] == 'PASS' 
        for validation in all_validations
    )
    
    # Imprimir resumen de validaciones
    print("\n" + "="*70)
    print("📊 RESUMEN DE VALIDACIONES DE CALIDAD")
    print("="*70)
    for validation in all_validations:
        status = "✅" if validation['check_result'] == 'PASS' else "❌"
        print(f"{status} {validation['check_name']}: {validation['check_result']}")
        print(f"   Registros verificados: {validation['records_checked']}")
        print(f"   Registros fallidos: {validation['records_failed']}")
    print("="*70 + "\n")
    
    # Decidir siguiente tarea
    if all_passed:
        print("✅ Todas las validaciones pasaron. Continuando con procesamiento normal.")
        return 'handle_quality_pass'
    else:
        print("❌ Algunas validaciones fallaron. Ejecutando manejo de errores.")
        return 'handle_quality_fail'


@task(dag=dag)
def handle_quality_pass(**context):
    """
    Maneja el caso cuando todas las validaciones de calidad pasan.
    
    En un escenario real, esta tarea podría:
    - Marcar los datos como aprobados para uso en producción
    - Activar pipelines downstream
    - Enviar notificaciones de éxito
    - Actualizar dashboards de calidad
    """
    print("✅ Manejo de validaciones exitosas...")
    
    # Obtener metadatos de extracción
    ti = context['ti']
    extraction_metadata = ti.xcom_pull(task_ids='extract_data')
    
    print(f"✓ {extraction_metadata['records_count']} registros validados exitosamente")
    print("✓ Datos aprobados para uso en producción")
    print("✓ Pipelines downstream pueden proceder")
    
    return {
        'status': 'QUALITY_PASS',
        'records_validated': extraction_metadata['records_count'],
        'timestamp': datetime.now().isoformat()
    }


@task(dag=dag)
def handle_quality_fail(**context):
    """
    Maneja el caso cuando alguna validación de calidad falla.
    
    En un escenario real, esta tarea podría:
    - Bloquear el uso de datos en producción
    - Enviar alertas al equipo de datos
    - Crear tickets de investigación
    - Activar procesos de corrección de datos
    """
    print("❌ Manejo de validaciones fallidas...")
    
    # Obtener resultados de validaciones
    ti = context['ti']
    nulls_result = ti.xcom_pull(task_ids='validate_nulls_task')
    ranges_result = ti.xcom_pull(task_ids='validate_ranges_task')
    uniqueness_result = ti.xcom_pull(task_ids='validate_uniqueness_task')
    integrity_result = ti.xcom_pull(task_ids='validate_referential_integrity_task')
    
    # Identificar validaciones fallidas
    failed_checks = []
    for result in [nulls_result, ranges_result, uniqueness_result, integrity_result]:
        if result['check_result'] == 'FAIL':
            failed_checks.append({
                'check_name': result['check_name'],
                'records_failed': result['records_failed']
            })
    
    print("\n⚠️  VALIDACIONES FALLIDAS:")
    for check in failed_checks:
        print(f"   • {check['check_name']}: {check['records_failed']} registros con problemas")
    
    print("\n🚨 ACCIONES REQUERIDAS:")
    print("   • Datos bloqueados para uso en producción")
    print("   • Alerta enviada al equipo de calidad de datos")
    print("   • Investigación requerida antes de continuar")
    
    return {
        'status': 'QUALITY_FAIL',
        'failed_checks': failed_checks,
        'timestamp': datetime.now().isoformat()
    }


@task(dag=dag, trigger_rule='none_failed_min_one_success')
def log_audit(**context):
    """
    Registra todos los resultados de validación en la tabla de auditoría.
    
    Esta tarea se ejecuta siempre (tanto si las validaciones pasan como si fallan)
    para mantener un registro completo de todas las ejecuciones de validación.
    
    El trigger_rule 'none_failed_min_one_success' asegura que esta tarea se ejecute
    si al menos una de las tareas anteriores (handle_quality_pass o handle_quality_fail)
    se ejecutó exitosamente.
    """
    print("📝 Registrando resultados de validación en tabla de auditoría...")
    
    # Obtener información del contexto
    ti = context['ti']
    execution_date = context['execution_date']
    dag_id = context['dag'].dag_id
    
    # Obtener resultados de todas las validaciones
    nulls_result = ti.xcom_pull(task_ids='validate_nulls_task')
    ranges_result = ti.xcom_pull(task_ids='validate_ranges_task')
    uniqueness_result = ti.xcom_pull(task_ids='validate_uniqueness_task')
    integrity_result = ti.xcom_pull(task_ids='validate_referential_integrity_task')
    
    # Preparar registros de auditoría
    audit_records = []
    
    for result in [nulls_result, ranges_result, uniqueness_result, integrity_result]:
        audit_record = {
            'dag_id': dag_id,
            'execution_date': execution_date,
            'check_name': result['check_name'],
            'check_result': result['check_result'],
            'records_checked': result['records_checked'],
            'records_failed': result['records_failed'],
            'error_details': str(result['details']) if result['check_result'] == 'FAIL' else None
        }
        audit_records.append(audit_record)
    
    # Crear DataFrame y cargar a tabla de auditoría
    df_audit = pd.DataFrame(audit_records)
    engine = get_postgres_engine()
    df_audit.to_sql('data_quality_checks', engine, schema='audit',
                    if_exists='append', index=False)
    
    print(f"✅ {len(audit_records)} registros de auditoría guardados")
    
    # Imprimir resumen final
    print("\n" + "="*70)
    print("📊 AUDITORÍA DE CALIDAD COMPLETADA")
    print("="*70)
    print(f"DAG: {dag_id}")
    print(f"Fecha de ejecución: {execution_date}")
    print(f"Validaciones registradas: {len(audit_records)}")
    
    passed_count = sum(1 for r in audit_records if r['check_result'] == 'PASS')
    failed_count = sum(1 for r in audit_records if r['check_result'] == 'FAIL')
    
    print(f"✅ Validaciones exitosas: {passed_count}")
    print(f"❌ Validaciones fallidas: {failed_count}")
    print("="*70 + "\n")
    
    return {
        'audit_records_created': len(audit_records),
        'passed_checks': passed_count,
        'failed_checks': failed_count
    }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Crear instancias de las tareas
extract_task = extract_data()
validate_nulls = validate_nulls_task()
validate_ranges = validate_ranges_task()
validate_uniqueness = validate_uniqueness_task()
validate_integrity = validate_referential_integrity_task()

# BranchPythonOperator para decidir flujo basado en resultados
branch_task = BranchPythonOperator(
    task_id='branch_on_quality',
    python_callable=branch_on_quality,
    provide_context=True,
    dag=dag
)

# Tareas de manejo de resultados
quality_pass_task = handle_quality_pass()
quality_fail_task = handle_quality_fail()

# Tarea de auditoría (se ejecuta siempre)
audit_task = log_audit()

# Establecer dependencias
# 1. Extraer datos primero
extract_task >> [validate_nulls, validate_ranges, validate_uniqueness, validate_integrity]

# 2. Todas las validaciones deben completarse antes de la decisión
[validate_nulls, validate_ranges, validate_uniqueness, validate_integrity] >> branch_task

# 3. Branch decide entre pass o fail
branch_task >> [quality_pass_task, quality_fail_task]

# 4. Ambas rutas llevan a la auditoría
[quality_pass_task, quality_fail_task] >> audit_task

# Nota sobre el flujo:
# - extract_task se ejecuta primero y prepara los datos
# - Las 4 validaciones se ejecutan en paralelo
# - branch_task evalúa todos los resultados y decide el flujo
# - Se ejecuta quality_pass_task O quality_fail_task (no ambas)
# - audit_task se ejecuta siempre al final para registrar resultados
