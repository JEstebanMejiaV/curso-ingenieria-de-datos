"""
DAG 07: Integración con Great Expectations
===========================================

Este DAG demuestra la integración de Great Expectations para validación avanzada de calidad de datos.
Implementa un pipeline que:
1. Configura el contexto de Great Expectations
2. Ejecuta suites de expectativas sobre los datos
3. Analiza los resultados de validación
4. Usa BranchPythonOperator para decidir el flujo basado en resultados
5. Maneja casos de éxito y fallo de validaciones

Conceptos clave demostrados:
- Integración de Great Expectations con Airflow
- Configuración programática de contexto GE
- Ejecución de expectation suites
- Análisis de validation results
- Flujos condicionales basados en validaciones GE
- Registro de resultados para auditoría

Great Expectations proporciona:
- Validaciones declarativas y expresivas
- Documentación automática de expectativas
- Data Docs para visualización de resultados
- Integración con múltiples fuentes de datos
- Perfilado automático de datos

Caso de uso: Validación avanzada de calidad para datos de ventas e-commerce
usando expectativas predefinidas y generadas automáticamente.

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import BranchPythonOperator
import pandas as pd
import json
from utils.db_utils import get_postgres_engine, execute_query

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
    dag_id='07_dag_great_expectations',
    default_args=default_args,
    description='Validación avanzada de calidad de datos con Great Expectations',
    schedule_interval='@daily',  # Ejecutar diariamente después de las transformaciones
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['great-expectations', 'calidad', 'validacion', 'taller'],
    doc_md=__doc__,
)

# ============================================================================
# TAREAS DEL DAG
# ============================================================================

@task(dag=dag)
def setup_ge_context(**context):
    """
    Configura el contexto de Great Expectations para validación de datos.
    
    Esta tarea:
    - Inicializa Great Expectations en modo programático (sin archivos de configuración)
    - Configura una fuente de datos conectada a PostgreSQL
    - Prepara el entorno para ejecutar expectation suites
    - Valida la conectividad con la base de datos
    
    Great Expectations puede configurarse de dos formas:
    1. File-based: Usando archivos YAML en directorio gx/
    2. Programática: Configurando todo en código (usado aquí para simplicidad)
    
    Returns:
        dict: Metadatos sobre la configuración de GE
    """
    print("🔧 Configurando contexto de Great Expectations...")
    
    try:
        # Nota: En este taller educativo, simulamos la configuración de GE
        # En un entorno real, usarías:
        # import great_expectations as gx
        # context = gx.get_context()
        
        print("✓ Inicializando Great Expectations...")
        
        # Configuración de conexión a PostgreSQL
        db_config = {
            'host': 'postgres',
            'port': 5432,
            'database': 'airflow',
            'username': 'airflow',
            'password': 'airflow'
        }
        
        print(f"✓ Configurando conexión a PostgreSQL: {db_config['host']}:{db_config['port']}")
        
        # Validar conectividad
        engine = get_postgres_engine()
        test_query = "SELECT 1 as test"
        result = execute_query(test_query)
        
        if result.empty:
            raise ValueError("No se pudo conectar a la base de datos")
        
        print("✓ Conexión a base de datos validada")
        
        # En un entorno real, configurarías:
        # - Data Source: Conexión a PostgreSQL
        # - Data Asset: Tabla específica a validar
        # - Expectation Suite: Conjunto de expectativas
        # - Checkpoint: Configuración de validación
        
        print("✓ Contexto de Great Expectations configurado")
        
        metadata = {
            'ge_configured': True,
            'datasource': 'postgresql',
            'database': db_config['database'],
            'configuration_timestamp': datetime.now().isoformat()
        }
        
        print("✅ Configuración de GE completada exitosamente")
        return metadata
        
    except Exception as e:
        print(f"❌ Error configurando Great Expectations: {str(e)}")
        raise


@task(dag=dag)
def run_expectation_suite(**context):
    """
    Ejecuta una suite de expectativas de Great Expectations sobre los datos.
    
    Esta tarea implementa expectativas comunes para validación de datos:
    
    Expectativas implementadas:
    1. expect_table_row_count_to_be_between: Valida cantidad de registros
    2. expect_column_values_to_not_be_null: Valida ausencia de nulos
    3. expect_column_values_to_be_between: Valida rangos numéricos
    4. expect_column_values_to_be_unique: Valida unicidad
    5. expect_column_values_to_be_in_set: Valida valores permitidos
    6. expect_column_mean_to_be_between: Valida estadísticas agregadas
    
    En un entorno real con GE instalado, usarías:
    ```python
    validator = context.get_validator(
        datasource_name="postgres_datasource",
        data_asset_name="transactions_clean"
    )
    validator.expect_column_values_to_not_be_null("transaction_id")
    results = validator.validate()
    ```
    
    Returns:
        dict: Resultados de la validación con expectativas
    """
    print("🔍 Ejecutando suite de expectativas de Great Expectations...")
    
    # Obtener datos a validar
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
    
    print(f"📊 Datos cargados: {len(df)} registros")
    
    # Inicializar resultados
    expectation_results = {
        'success': True,
        'expectations': [],
        'statistics': {
            'evaluated_expectations': 0,
            'successful_expectations': 0,
            'unsuccessful_expectations': 0,
            'success_percent': 0.0
        }
    }
    
    # ========================================================================
    # EXPECTATIVA 1: Cantidad de registros debe estar en rango razonable
    # ========================================================================
    print("\n1️⃣  Expectativa: expect_table_row_count_to_be_between")
    
    row_count = len(df)
    min_rows = 10
    max_rows = 1000000
    
    expectation_1 = {
        'expectation_type': 'expect_table_row_count_to_be_between',
        'kwargs': {'min_value': min_rows, 'max_value': max_rows},
        'success': min_rows <= row_count <= max_rows,
        'result': {
            'observed_value': row_count,
            'element_count': row_count
        }
    }
    
    expectation_results['expectations'].append(expectation_1)
    print(f"   Resultado: {'✅ PASS' if expectation_1['success'] else '❌ FAIL'}")
    print(f"   Registros observados: {row_count} (esperado: {min_rows}-{max_rows})")
    
    # ========================================================================
    # EXPECTATIVA 2: Columnas críticas no deben tener nulos
    # ========================================================================
    print("\n2️⃣  Expectativa: expect_column_values_to_not_be_null")
    
    critical_columns = ['transaction_id', 'customer_id', 'product_id', 'amount']
    
    for column in critical_columns:
        null_count = df[column].isnull().sum()
        success = (null_count == 0)
        
        expectation = {
            'expectation_type': 'expect_column_values_to_not_be_null',
            'kwargs': {'column': column},
            'success': success,
            'result': {
                'element_count': len(df),
                'unexpected_count': int(null_count),
                'unexpected_percent': float(null_count / len(df) * 100) if len(df) > 0 else 0
            }
        }
        
        expectation_results['expectations'].append(expectation)
        print(f"   {column}: {'✅ PASS' if success else '❌ FAIL'} ({null_count} nulos)")
    
    # ========================================================================
    # EXPECTATIVA 3: Valores numéricos deben estar en rangos válidos
    # ========================================================================
    print("\n3️⃣  Expectativa: expect_column_values_to_be_between")
    
    # Validar amount
    amount_min = 0
    amount_max = 100000
    out_of_range_amount = df[(df['amount'] < amount_min) | (df['amount'] > amount_max)]
    
    expectation_3a = {
        'expectation_type': 'expect_column_values_to_be_between',
        'kwargs': {'column': 'amount', 'min_value': amount_min, 'max_value': amount_max},
        'success': len(out_of_range_amount) == 0,
        'result': {
            'element_count': len(df),
            'unexpected_count': len(out_of_range_amount),
            'unexpected_percent': float(len(out_of_range_amount) / len(df) * 100) if len(df) > 0 else 0,
            'observed_min': float(df['amount'].min()),
            'observed_max': float(df['amount'].max())
        }
    }
    
    expectation_results['expectations'].append(expectation_3a)
    print(f"   amount: {'✅ PASS' if expectation_3a['success'] else '❌ FAIL'}")
    print(f"   Rango esperado: [{amount_min}, {amount_max}]")
    print(f"   Rango observado: [{df['amount'].min():.2f}, {df['amount'].max():.2f}]")
    
    # Validar quantity
    quantity_min = 1
    quantity_max = 1000
    out_of_range_quantity = df[(df['quantity'] < quantity_min) | (df['quantity'] > quantity_max)]
    
    expectation_3b = {
        'expectation_type': 'expect_column_values_to_be_between',
        'kwargs': {'column': 'quantity', 'min_value': quantity_min, 'max_value': quantity_max},
        'success': len(out_of_range_quantity) == 0,
        'result': {
            'element_count': len(df),
            'unexpected_count': len(out_of_range_quantity),
            'unexpected_percent': float(len(out_of_range_quantity) / len(df) * 100) if len(df) > 0 else 0,
            'observed_min': int(df['quantity'].min()),
            'observed_max': int(df['quantity'].max())
        }
    }
    
    expectation_results['expectations'].append(expectation_3b)
    print(f"   quantity: {'✅ PASS' if expectation_3b['success'] else '❌ FAIL'}")
    print(f"   Rango esperado: [{quantity_min}, {quantity_max}]")
    print(f"   Rango observado: [{df['quantity'].min()}, {df['quantity'].max()}]")

    
    # ========================================================================
    # EXPECTATIVA 4: transaction_id debe ser único
    # ========================================================================
    print("\n4️⃣  Expectativa: expect_column_values_to_be_unique")
    
    duplicates = df[df.duplicated(subset=['transaction_id'], keep=False)]
    
    expectation_4 = {
        'expectation_type': 'expect_column_values_to_be_unique',
        'kwargs': {'column': 'transaction_id'},
        'success': len(duplicates) == 0,
        'result': {
            'element_count': len(df),
            'unexpected_count': len(duplicates),
            'unexpected_percent': float(len(duplicates) / len(df) * 100) if len(df) > 0 else 0,
            'partial_unexpected_list': duplicates['transaction_id'].head(5).tolist() if len(duplicates) > 0 else []
        }
    }
    
    expectation_results['expectations'].append(expectation_4)
    print(f"   transaction_id: {'✅ PASS' if expectation_4['success'] else '❌ FAIL'}")
    print(f"   Duplicados encontrados: {len(duplicates)}")
    
    # ========================================================================
    # EXPECTATIVA 5: category debe estar en conjunto de valores válidos
    # ========================================================================
    print("\n5️⃣  Expectativa: expect_column_values_to_be_in_set")
    
    # Obtener categorías válidas de la tabla de productos
    valid_categories_query = "SELECT DISTINCT category FROM raw.products"
    valid_categories_df = execute_query(valid_categories_query)
    valid_categories = set(valid_categories_df['category'].tolist())
    
    invalid_categories = df[~df['category'].isin(valid_categories)]
    
    expectation_5 = {
        'expectation_type': 'expect_column_values_to_be_in_set',
        'kwargs': {'column': 'category', 'value_set': list(valid_categories)},
        'success': len(invalid_categories) == 0,
        'result': {
            'element_count': len(df),
            'unexpected_count': len(invalid_categories),
            'unexpected_percent': float(len(invalid_categories) / len(df) * 100) if len(df) > 0 else 0,
            'partial_unexpected_list': invalid_categories['category'].unique().tolist() if len(invalid_categories) > 0 else []
        }
    }
    
    expectation_results['expectations'].append(expectation_5)
    print(f"   category: {'✅ PASS' if expectation_5['success'] else '❌ FAIL'}")
    print(f"   Categorías válidas: {len(valid_categories)}")
    print(f"   Valores inválidos: {len(invalid_categories)}")
    
    # ========================================================================
    # EXPECTATIVA 6: Promedio de amount debe estar en rango razonable
    # ========================================================================
    print("\n6️⃣  Expectativa: expect_column_mean_to_be_between")
    
    mean_amount = float(df['amount'].mean())
    min_mean = 10.0
    max_mean = 10000.0
    
    expectation_6 = {
        'expectation_type': 'expect_column_mean_to_be_between',
        'kwargs': {'column': 'amount', 'min_value': min_mean, 'max_value': max_mean},
        'success': min_mean <= mean_amount <= max_mean,
        'result': {
            'observed_value': mean_amount
        }
    }
    
    expectation_results['expectations'].append(expectation_6)
    print(f"   amount mean: {'✅ PASS' if expectation_6['success'] else '❌ FAIL'}")
    print(f"   Promedio esperado: [{min_mean}, {max_mean}]")
    print(f"   Promedio observado: {mean_amount:.2f}")
    
    # ========================================================================
    # Calcular estadísticas finales
    # ========================================================================
    total_expectations = len(expectation_results['expectations'])
    successful_expectations = sum(1 for exp in expectation_results['expectations'] if exp['success'])
    unsuccessful_expectations = total_expectations - successful_expectations
    success_percent = (successful_expectations / total_expectations * 100) if total_expectations > 0 else 0
    
    expectation_results['statistics'] = {
        'evaluated_expectations': total_expectations,
        'successful_expectations': successful_expectations,
        'unsuccessful_expectations': unsuccessful_expectations,
        'success_percent': success_percent
    }
    
    # Determinar si la validación general fue exitosa
    # Consideramos exitosa si al menos el 80% de las expectativas pasan
    expectation_results['success'] = success_percent >= 80.0
    
    # Imprimir resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE EXPECTATIVAS DE GREAT EXPECTATIONS")
    print("="*70)
    print(f"Total de expectativas evaluadas: {total_expectations}")
    print(f"✅ Expectativas exitosas: {successful_expectations}")
    print(f"❌ Expectativas fallidas: {unsuccessful_expectations}")
    print(f"📈 Porcentaje de éxito: {success_percent:.2f}%")
    print(f"Resultado general: {'✅ PASS' if expectation_results['success'] else '❌ FAIL'}")
    print("="*70 + "\n")
    
    expectation_results['execution_timestamp'] = datetime.now().isoformat()
    
    return expectation_results


@task(dag=dag)
def parse_validation_results(**context):
    """
    Analiza y procesa los resultados de validación de Great Expectations.
    
    Esta tarea:
    - Extrae métricas clave de los resultados de validación
    - Identifica expectativas fallidas y sus detalles
    - Genera un reporte estructurado para toma de decisiones
    - Prepara datos para registro en auditoría
    
    Returns:
        dict: Análisis detallado de los resultados de validación
    """
    print("📊 Analizando resultados de validación de Great Expectations...")
    
    # Obtener resultados de la tarea anterior
    ti = context['ti']
    validation_results = ti.xcom_pull(task_ids='run_expectation_suite')
    
    # Inicializar análisis
    analysis = {
        'overall_success': validation_results['success'],
        'statistics': validation_results['statistics'],
        'failed_expectations': [],
        'passed_expectations': [],
        'critical_issues': [],
        'warnings': [],
        'recommendations': []
    }
    
    print("\n🔍 Analizando expectativas individuales...")
    
    # Analizar cada expectativa
    for expectation in validation_results['expectations']:
        expectation_summary = {
            'type': expectation['expectation_type'],
            'kwargs': expectation['kwargs'],
            'success': expectation['success'],
            'result': expectation['result']
        }
        
        if expectation['success']:
            analysis['passed_expectations'].append(expectation_summary)
        else:
            analysis['failed_expectations'].append(expectation_summary)
            
            # Clasificar severidad del fallo
            unexpected_percent = expectation['result'].get('unexpected_percent', 0)
            
            if unexpected_percent > 10:
                # Más del 10% de registros con problemas = crítico
                analysis['critical_issues'].append({
                    'expectation': expectation['expectation_type'],
                    'severity': 'CRITICAL',
                    'affected_percent': unexpected_percent,
                    'description': f"Más del 10% de registros fallan esta expectativa"
                })
            elif unexpected_percent > 1:
                # Entre 1% y 10% = advertencia
                analysis['warnings'].append({
                    'expectation': expectation['expectation_type'],
                    'severity': 'WARNING',
                    'affected_percent': unexpected_percent,
                    'description': f"Entre 1% y 10% de registros fallan esta expectativa"
                })
    
    # Generar recomendaciones basadas en fallos
    if len(analysis['critical_issues']) > 0:
        analysis['recommendations'].append(
            "🚨 ACCIÓN INMEDIATA: Investigar y corregir problemas críticos de calidad"
        )
        analysis['recommendations'].append(
            "🔒 Bloquear uso de datos en producción hasta resolver problemas"
        )
    
    if len(analysis['warnings']) > 0:
        analysis['recommendations'].append(
            "⚠️  Revisar advertencias y considerar limpieza de datos"
        )
    
    if len(analysis['failed_expectations']) == 0:
        analysis['recommendations'].append(
            "✅ Datos aprobados para uso en producción"
        )
        analysis['recommendations'].append(
            "📊 Actualizar dashboards y reportes con datos validados"
        )
    
    # Imprimir análisis detallado
    print("\n" + "="*70)
    print("📊 ANÁLISIS DE RESULTADOS DE VALIDACIÓN")
    print("="*70)
    
    print(f"\n✅ Expectativas exitosas: {len(analysis['passed_expectations'])}")
    for exp in analysis['passed_expectations']:
        print(f"   • {exp['type']}")
    
    if len(analysis['failed_expectations']) > 0:
        print(f"\n❌ Expectativas fallidas: {len(analysis['failed_expectations'])}")
        for exp in analysis['failed_expectations']:
            print(f"   • {exp['type']}")
            if 'unexpected_percent' in exp['result']:
                print(f"     Registros afectados: {exp['result']['unexpected_percent']:.2f}%")
    
    if len(analysis['critical_issues']) > 0:
        print(f"\n🚨 Problemas críticos: {len(analysis['critical_issues'])}")
        for issue in analysis['critical_issues']:
            print(f"   • {issue['expectation']}: {issue['description']}")
    
    if len(analysis['warnings']) > 0:
        print(f"\n⚠️  Advertencias: {len(analysis['warnings'])}")
        for warning in analysis['warnings']:
            print(f"   • {warning['expectation']}: {warning['description']}")
    
    print(f"\n💡 Recomendaciones:")
    for rec in analysis['recommendations']:
        print(f"   {rec}")
    
    print("="*70 + "\n")
    
    analysis['analysis_timestamp'] = datetime.now().isoformat()
    
    return analysis


def branch_on_validation(**context):
    """
    Decide el flujo del pipeline basado en los resultados de validación de GE.
    
    Esta función es usada por BranchPythonOperator para determinar qué
    tarea ejecutar a continuación basándose en si las validaciones de
    Great Expectations pasaron o fallaron.
    
    Criterios de decisión:
    - Si success_percent >= 80%: Continuar con handle_validation_success
    - Si success_percent < 80%: Ejecutar handle_validation_failure
    
    Returns:
        str: ID de la tarea a ejecutar ('handle_validation_success' o 'handle_validation_failure')
    """
    print("🔀 Evaluando resultados de validación para decidir flujo...")
    
    # Obtener análisis de resultados
    ti = context['ti']
    analysis = ti.xcom_pull(task_ids='parse_validation_results')
    
    overall_success = analysis['overall_success']
    success_percent = analysis['statistics']['success_percent']
    critical_issues = len(analysis['critical_issues'])
    
    print("\n" + "="*70)
    print("🔀 DECISIÓN DE FLUJO DEL PIPELINE")
    print("="*70)
    print(f"Porcentaje de éxito: {success_percent:.2f}%")
    print(f"Problemas críticos: {critical_issues}")
    print(f"Resultado general: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    # Decidir siguiente tarea
    if overall_success and critical_issues == 0:
        print("\n✅ Validación exitosa. Continuando con procesamiento normal.")
        print("   → Ejecutando: handle_validation_success")
        next_task = 'handle_validation_success'
    else:
        print("\n❌ Validación fallida. Ejecutando manejo de errores.")
        print("   → Ejecutando: handle_validation_failure")
        next_task = 'handle_validation_failure'
    
    print("="*70 + "\n")
    
    return next_task


@task(dag=dag)
def handle_validation_success(**context):
    """
    Maneja el caso cuando las validaciones de Great Expectations pasan exitosamente.
    
    En un escenario real, esta tarea podría:
    - Marcar los datos como aprobados para uso en producción
    - Publicar Data Docs de Great Expectations
    - Activar pipelines downstream
    - Enviar notificaciones de éxito al equipo
    - Actualizar dashboards de calidad de datos
    - Registrar métricas de calidad en sistemas de monitoreo
    
    Returns:
        dict: Resumen de acciones tomadas tras validación exitosa
    """
    print("✅ Manejo de validación exitosa de Great Expectations...")
    
    # Obtener análisis de resultados
    ti = context['ti']
    analysis = ti.xcom_pull(task_ids='parse_validation_results')
    
    success_percent = analysis['statistics']['success_percent']
    passed_count = analysis['statistics']['successful_expectations']
    total_count = analysis['statistics']['evaluated_expectations']
    
    print("\n" + "="*70)
    print("✅ VALIDACIÓN EXITOSA - ACCIONES EJECUTADAS")
    print("="*70)
    
    print(f"\n📊 Resumen de validación:")
    print(f"   • Expectativas evaluadas: {total_count}")
    print(f"   • Expectativas exitosas: {passed_count}")
    print(f"   • Porcentaje de éxito: {success_percent:.2f}%")
    
    print(f"\n✅ Acciones ejecutadas:")
    print(f"   • Datos aprobados para uso en producción")
    print(f"   • Data Docs de GE actualizados (simulado)")
    print(f"   • Pipelines downstream pueden proceder")
    print(f"   • Notificación de éxito enviada (simulado)")
    print(f"   • Métricas de calidad registradas")
    
    # En un entorno real, aquí ejecutarías:
    # 1. Publicar Data Docs:
    #    context.build_data_docs()
    #    # Subir a S3, GCS, o servidor web
    #
    # 2. Activar DAGs downstream:
    #    from airflow.operators.trigger_dagrun import TriggerDagRunOperator
    #    trigger_downstream_dag()
    #
    # 3. Enviar notificaciones:
    #    send_slack_notification(f"✅ Validación GE exitosa: {success_percent}%")
    #    send_email_notification(...)
    #
    # 4. Actualizar métricas:
    #    push_metrics_to_datadog(success_percent)
    
    print("\n💡 Recomendaciones:")
    for rec in analysis['recommendations']:
        print(f"   {rec}")
    
    print("="*70 + "\n")
    
    return {
        'status': 'VALIDATION_SUCCESS',
        'success_percent': success_percent,
        'passed_expectations': passed_count,
        'total_expectations': total_count,
        'data_approved_for_production': True,
        'timestamp': datetime.now().isoformat()
    }


@task(dag=dag)
def handle_validation_failure(**context):
    """
    Maneja el caso cuando las validaciones de Great Expectations fallan.
    
    En un escenario real, esta tarea podría:
    - Bloquear el uso de datos en producción
    - Enviar alertas críticas al equipo de datos
    - Crear tickets de investigación automáticamente
    - Activar procesos de corrección de datos
    - Generar reportes detallados de problemas
    - Notificar a stakeholders sobre retrasos
    
    Returns:
        dict: Resumen de acciones tomadas tras validación fallida
    """
    print("❌ Manejo de validación fallida de Great Expectations...")
    
    # Obtener análisis de resultados
    ti = context['ti']
    analysis = ti.xcom_pull(task_ids='parse_validation_results')
    
    success_percent = analysis['statistics']['success_percent']
    failed_count = analysis['statistics']['unsuccessful_expectations']
    total_count = analysis['statistics']['evaluated_expectations']
    critical_issues = len(analysis['critical_issues'])
    warnings = len(analysis['warnings'])
    
    print("\n" + "="*70)
    print("❌ VALIDACIÓN FALLIDA - ACCIONES EJECUTADAS")
    print("="*70)
    
    print(f"\n📊 Resumen de validación:")
    print(f"   • Expectativas evaluadas: {total_count}")
    print(f"   • Expectativas fallidas: {failed_count}")
    print(f"   • Porcentaje de éxito: {success_percent:.2f}%")
    print(f"   • Problemas críticos: {critical_issues}")
    print(f"   • Advertencias: {warnings}")
    
    print(f"\n❌ Expectativas fallidas:")
    for exp in analysis['failed_expectations']:
        print(f"   • {exp['type']}")
        if 'unexpected_percent' in exp['result']:
            print(f"     Registros afectados: {exp['result']['unexpected_percent']:.2f}%")
    
    if critical_issues > 0:
        print(f"\n🚨 Problemas críticos detectados:")
        for issue in analysis['critical_issues']:
            print(f"   • {issue['expectation']}")
            print(f"     Severidad: {issue['severity']}")
            print(f"     Descripción: {issue['description']}")
    
    print(f"\n🚨 Acciones ejecutadas:")
    print(f"   • Datos BLOQUEADOS para uso en producción")
    print(f"   • Alerta crítica enviada al equipo de calidad (simulado)")
    print(f"   • Ticket de investigación creado (simulado)")
    print(f"   • Notificación a stakeholders sobre retraso (simulado)")
    print(f"   • Reporte detallado de problemas generado")
    
    # En un entorno real, aquí ejecutarías:
    # 1. Enviar alertas críticas:
    #    send_pagerduty_alert("Critical data quality issues detected")
    #    send_slack_alert(channel="#data-quality-alerts", ...)
    #
    # 2. Crear tickets:
    #    create_jira_ticket(
    #        project="DATA",
    #        issue_type="Bug",
    #        summary=f"Data quality validation failed: {failed_count} expectations",
    #        description=generate_detailed_report(analysis)
    #    )
    #
    # 3. Bloquear datos:
    #    mark_data_as_quarantined(execution_date)
    #    prevent_downstream_processing()
    #
    # 4. Generar reportes:
    #    generate_failure_report(analysis)
    #    publish_to_s3(report, f"quality-reports/{execution_date}/")
    
    print("\n💡 Recomendaciones:")
    for rec in analysis['recommendations']:
        print(f"   {rec}")
    
    print("="*70 + "\n")
    
    return {
        'status': 'VALIDATION_FAILURE',
        'success_percent': success_percent,
        'failed_expectations': failed_count,
        'total_expectations': total_count,
        'critical_issues': critical_issues,
        'warnings': warnings,
        'data_approved_for_production': False,
        'failed_expectation_details': analysis['failed_expectations'],
        'timestamp': datetime.now().isoformat()
    }


@task(dag=dag, trigger_rule='none_failed_min_one_success')
def log_ge_audit(**context):
    """
    Registra los resultados de validación de Great Expectations en la tabla de auditoría.
    
    Esta tarea se ejecuta siempre (tanto si las validaciones pasan como si fallan)
    para mantener un registro completo de todas las ejecuciones de validación GE.
    
    El trigger_rule 'none_failed_min_one_success' asegura que esta tarea se ejecute
    si al menos una de las tareas anteriores (handle_validation_success o 
    handle_validation_failure) se ejecutó exitosamente.
    
    Returns:
        dict: Confirmación de registro en auditoría
    """
    print("📝 Registrando resultados de Great Expectations en auditoría...")
    
    # Obtener información del contexto
    ti = context['ti']
    execution_date = context['execution_date']
    dag_id = context['dag'].dag_id
    
    # Obtener resultados de validación y análisis
    validation_results = ti.xcom_pull(task_ids='run_expectation_suite')
    analysis = ti.xcom_pull(task_ids='parse_validation_results')
    
    # Determinar qué handler se ejecutó
    success_result = ti.xcom_pull(task_ids='handle_validation_success')
    failure_result = ti.xcom_pull(task_ids='handle_validation_failure')
    
    final_status = 'PASS' if success_result else 'FAIL'
    
    # Preparar registros de auditoría para cada expectativa
    audit_records = []
    
    for expectation in validation_results['expectations']:
        # Extraer información relevante
        exp_type = expectation['expectation_type']
        exp_success = expectation['success']
        exp_result = expectation['result']
        
        # Determinar columna si aplica
        column = expectation['kwargs'].get('column', 'N/A')
        
        # Calcular registros afectados
        records_checked = exp_result.get('element_count', 0)
        records_failed = exp_result.get('unexpected_count', 0)
        
        # Preparar detalles del error si falló
        error_details = None
        if not exp_success:
            error_details = json.dumps({
                'unexpected_percent': exp_result.get('unexpected_percent', 0),
                'partial_unexpected_list': exp_result.get('partial_unexpected_list', []),
                'observed_value': exp_result.get('observed_value'),
                'kwargs': expectation['kwargs']
            })
        
        audit_record = {
            'dag_id': dag_id,
            'execution_date': execution_date,
            'check_name': f"GE: {exp_type} ({column})",
            'check_result': 'PASS' if exp_success else 'FAIL',
            'records_checked': records_checked,
            'records_failed': records_failed,
            'error_details': error_details
        }
        
        audit_records.append(audit_record)
    
    # Agregar registro resumen
    summary_record = {
        'dag_id': dag_id,
        'execution_date': execution_date,
        'check_name': 'GE: Validation Suite Summary',
        'check_result': final_status,
        'records_checked': validation_results['statistics']['evaluated_expectations'],
        'records_failed': validation_results['statistics']['unsuccessful_expectations'],
        'error_details': json.dumps({
            'success_percent': validation_results['statistics']['success_percent'],
            'critical_issues': len(analysis['critical_issues']),
            'warnings': len(analysis['warnings']),
            'recommendations': analysis['recommendations']
        })
    }
    
    audit_records.append(summary_record)
    
    # Crear DataFrame y cargar a tabla de auditoría
    df_audit = pd.DataFrame(audit_records)
    engine = get_postgres_engine()
    df_audit.to_sql('data_quality_checks', engine, schema='audit',
                    if_exists='append', index=False)
    
    print(f"✅ {len(audit_records)} registros de auditoría guardados")
    
    # Imprimir resumen final
    print("\n" + "="*70)
    print("📊 AUDITORÍA DE GREAT EXPECTATIONS COMPLETADA")
    print("="*70)
    print(f"DAG: {dag_id}")
    print(f"Fecha de ejecución: {execution_date}")
    print(f"Resultado final: {final_status}")
    print(f"Expectativas evaluadas: {validation_results['statistics']['evaluated_expectations']}")
    print(f"✅ Exitosas: {validation_results['statistics']['successful_expectations']}")
    print(f"❌ Fallidas: {validation_results['statistics']['unsuccessful_expectations']}")
    print(f"📈 Porcentaje de éxito: {validation_results['statistics']['success_percent']:.2f}%")
    print(f"Registros de auditoría creados: {len(audit_records)}")
    print("="*70 + "\n")
    
    return {
        'audit_records_created': len(audit_records),
        'final_status': final_status,
        'success_percent': validation_results['statistics']['success_percent'],
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ============================================================================

# Crear instancias de las tareas
setup_task = setup_ge_context()
run_suite_task = run_expectation_suite()
parse_task = parse_validation_results()

# BranchPythonOperator para decidir flujo basado en resultados
branch_task = BranchPythonOperator(
    task_id='branch_on_validation',
    python_callable=branch_on_validation,
    provide_context=True,
    dag=dag
)

# Tareas de manejo de resultados
success_task = handle_validation_success()
failure_task = handle_validation_failure()

# Tarea de auditoría (se ejecuta siempre)
audit_task = log_ge_audit()

# Establecer dependencias
# 1. Configurar contexto de GE primero
setup_task >> run_suite_task

# 2. Ejecutar suite de expectativas
run_suite_task >> parse_task

# 3. Analizar resultados antes de la decisión
parse_task >> branch_task

# 4. Branch decide entre success o failure
branch_task >> [success_task, failure_task]

# 5. Ambas rutas llevan a la auditoría
[success_task, failure_task] >> audit_task

# ============================================================================
# DOCUMENTACIÓN ADICIONAL
# ============================================================================

"""
NOTAS SOBRE GREAT EXPECTATIONS EN PRODUCCIÓN
=============================================

Este DAG demuestra la integración de Great Expectations con Airflow de forma
educativa. En un entorno de producción real, considerarías:

1. INSTALACIÓN DE GREAT EXPECTATIONS:
   ```bash
   pip install great_expectations
   ```

2. INICIALIZACIÓN DE CONTEXTO:
   ```python
   import great_expectations as gx
   context = gx.get_context()
   ```

3. CONFIGURACIÓN DE DATA SOURCE:
   ```python
   datasource = context.sources.add_postgres(
       name="postgres_datasource",
       connection_string="postgresql://user:pass@host:port/db"
   )
   ```

4. CREACIÓN DE EXPECTATION SUITE:
   ```python
   suite = context.add_expectation_suite("transactions_suite")
   validator = context.get_validator(
       batch_request=batch_request,
       expectation_suite_name="transactions_suite"
   )
   ```

5. EJECUCIÓN DE CHECKPOINT:
   ```python
   checkpoint = context.add_checkpoint(
       name="transactions_checkpoint",
       validations=[{
           "batch_request": batch_request,
           "expectation_suite_name": "transactions_suite"
       }]
   )
   results = checkpoint.run()
   ```

6. PUBLICACIÓN DE DATA DOCS:
   ```python
   context.build_data_docs()
   # Los Data Docs se generan en gx/uncommitted/data_docs/
   # Puedes subirlos a S3, GCS, o un servidor web
   ```

VENTAJAS DE GREAT EXPECTATIONS:
- Validaciones declarativas y expresivas
- Documentación automática (Data Docs)
- Perfilado automático de datos
- Integración con múltiples fuentes de datos
- Versionado de expectation suites
- Métricas y alertas integradas

INTEGRACIÓN CON AIRFLOW:
- Usar GreatExpectationsOperator (requiere airflow-provider-great-expectations)
- O implementar tareas personalizadas como en este DAG
- Configurar callbacks para alertas
- Integrar con sistemas de monitoreo

MEJORES PRÁCTICAS:
- Versionar expectation suites en Git
- Mantener Data Docs actualizados
- Configurar alertas para fallos críticos
- Revisar y actualizar expectativas regularmente
- Usar perfilado automático para nuevos datasets
- Documentar el significado de negocio de cada expectativa

Para más información:
https://docs.greatexpectations.io/
"""
