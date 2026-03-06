# Ejercicio 03: Pipeline Completo End-to-End

## 🎯 Objetivo

Diseñar e implementar un pipeline completo de datos end-to-end que coordine múltiples DAGs, implemente monitoreo robusto, maneje errores apropiadamente y aplique mejores prácticas de DataOps. Este ejercicio integra todos los conceptos aprendidos en el taller.

## 📋 Contexto

Tu empresa necesita un sistema de análisis de datos completo que:
1. Ingeste datos de múltiples fuentes diariamente
2. Transforme y enriquezca los datos
3. Valide la calidad en cada etapa
4. Genere reportes analíticos
5. Monitoree el estado del pipeline
6. Maneje errores y reintentos de manera inteligente
7. Envíe notificaciones sobre el estado de ejecución

Este es un proyecto realista que simula pipelines de producción en empresas de datos.

## 🎓 Conceptos a Aplicar

- Coordinación de múltiples DAGs con ExternalTaskSensor
- Manejo robusto de errores con callbacks
- Configuración de SLAs y alertas
- Uso de Variables y Connections de Airflow
- Logging estructurado
- Monitoreo y observabilidad
- Mejores prácticas de DataOps
- Documentación completa

## 🏗️ Arquitectura del Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE END-TO-END                       │
└─────────────────────────────────────────────────────────────┘

DAG 1: Ingesta Multi-Fuente
├── Ingestar eventos web
├── Ingestar transacciones
├── Ingestar datos de productos
└── Validar ingesta → [Notificar si falla]

                ↓ (ExternalTaskSensor)

DAG 2: Transformación y Enriquecimiento
├── Esperar DAG 1
├── Limpiar datos
├── Enriquecer con dimensiones
├── Calcular métricas
└── Validar transformaciones → [Notificar si falla]

                ↓ (ExternalTaskSensor)

DAG 3: Análisis y Reportes
├── Esperar DAG 2
├── Calcular RFM
├── Generar reportes de negocio
├── Detectar anomalías
└── Publicar resultados → [Notificar éxito]

                ↓

DAG 4: Monitoreo y Auditoría (Independiente)
├── Verificar SLAs
├── Analizar logs de errores
├── Generar dashboard de salud
└── Enviar reporte diario
```

## 📝 Requisitos

### DAG 1: Ingesta Multi-Fuente (`pipeline_01_ingesta_multifuente`)

**Propósito**: Ingestar datos de múltiples fuentes de manera coordinada

**Tareas**:
1. `check_all_sources`: Verificar que todos los archivos fuente existen
2. `ingest_web_events`: Ingestar eventos web (paralelo)
3. `ingest_transactions`: Ingestar transacciones (paralelo)
4. `ingest_products`: Ingestar productos (paralelo)
5. `validate_ingestion`: Validar que todas las ingestas fueron exitosas
6. `log_ingestion_metrics`: Registrar métricas de ingesta

**Configuración especial**:
- `schedule_interval='0 1 * * *'` (1 AM diario)
- `sla=timedelta(hours=1)` (debe completar en 1 hora)
- `on_failure_callback`: Enviar alerta si falla
- `retries=3` con `retry_delay=timedelta(minutes=10)`

**Validaciones**:
- Verificar conteos de registros
- Validar integridad de datos
- Comparar con día anterior (detectar anomalías)

### DAG 2: Transformación (`pipeline_02_transformacion`)

**Propósito**: Transformar y enriquecer datos ingresados

**Tareas**:
1. `wait_for_ingestion`: ExternalTaskSensor esperando DAG 1
2. `extract_raw_data`: Extraer datos de capa raw
3. `clean_and_validate`: Limpiar y validar datos
4. `enrich_data`: Enriquecer con dimensiones
5. `calculate_metrics`: Calcular métricas agregadas
6. `quality_checks`: Ejecutar validaciones de calidad
7. `branch_on_quality`: Decidir flujo basado en calidad
8. `handle_quality_pass`: Continuar si pasa
9. `handle_quality_fail`: Manejar si falla
10. `log_transformation_metrics`: Registrar métricas

**Configuración especial**:
- `schedule_interval='0 2 * * *'` (2 AM diario, después de ingesta)
- `sla=timedelta(hours=2)`
- `depends_on_past=True` (no ejecutar si día anterior falló)
- Usar XCom para compartir resultados de calidad

**Validaciones**:
- Validar nulos en columnas críticas
- Validar rangos de valores
- Validar integridad referencial
- Validar consistencia con día anterior

### DAG 3: Análisis y Reportes (`pipeline_03_analytics`)

**Propósito**: Generar análisis y reportes de negocio

**Tareas**:
1. `wait_for_transformation`: ExternalTaskSensor esperando DAG 2
2. `calculate_rfm`: Calcular métricas RFM
3. `generate_sales_report`: Generar reporte de ventas
4. `generate_customer_report`: Generar reporte de clientes
5. `detect_anomalies`: Detectar anomalías en métricas
6. `generate_executive_summary`: Generar resumen ejecutivo
7. `publish_results`: Publicar resultados (simular envío)
8. `notify_completion`: Notificar finalización exitosa

**Configuración especial**:
- `schedule_interval='0 3 * * *'` (3 AM diario)
- `sla=timedelta(hours=1)`
- Generar archivos de reporte en formato CSV/JSON
- Incluir visualizaciones básicas (opcional)

**Reportes a generar**:
- Reporte de ventas diarias
- Reporte de segmentación RFM
- Reporte de anomalías detectadas
- Dashboard ejecutivo (métricas clave)

### DAG 4: Monitoreo (`pipeline_04_monitoring`)

**Propósito**: Monitorear la salud del pipeline completo

**Tareas**:
1. `check_dag_runs`: Verificar estado de ejecuciones de DAGs 1-3
2. `analyze_sla_misses`: Analizar violaciones de SLA
3. `analyze_task_failures`: Analizar tareas fallidas
4. `calculate_pipeline_health`: Calcular score de salud del pipeline
5. `generate_monitoring_report`: Generar reporte de monitoreo
6. `send_daily_summary`: Enviar resumen diario

**Configuración especial**:
- `schedule_interval='0 9 * * *'` (9 AM diario, después de todos)
- Independiente de otros DAGs (no usa sensores)
- Consulta metadatos de Airflow para análisis

**Métricas a monitorear**:
- Tasa de éxito de DAGs (últimos 7 días)
- Duración promedio de ejecución
- Violaciones de SLA
- Tareas con más fallos
- Tendencias de volumen de datos

## ✅ Criterios de Evaluación

Tu solución será evaluada según los siguientes criterios:

### Arquitectura y Diseño (25 puntos)
- [ ] Coordinación correcta entre DAGs con sensores (10 pts)
- [ ] Flujo lógico y secuencial apropiado (8 pts)
- [ ] Separación de responsabilidades clara (7 pts)

### Implementación (30 puntos)
- [ ] Todos los DAGs se ejecutan correctamente (10 pts)
- [ ] Validaciones de calidad robustas (8 pts)
- [ ] Manejo de errores apropiado (7 pts)
- [ ] Uso correcto de XCom y Variables (5 pts)

### Monitoreo y Observabilidad (20 puntos)
- [ ] SLAs configurados apropiadamente (5 pts)
- [ ] Callbacks de error implementados (5 pts)
- [ ] Logging estructurado y útil (5 pts)
- [ ] DAG de monitoreo funcional (5 pts)

### Mejores Prácticas (15 puntos)
- [ ] Configuración apropiada de reintentos (5 pts)
- [ ] Uso de Variables/Connections (5 pts)
- [ ] Código limpio y mantenible (5 pts)

### Documentación (10 puntos)
- [ ] Docstrings completos en todos los DAGs (5 pts)
- [ ] README explicando el pipeline (3 pts)
- [ ] Diagramas de arquitectura (2 pts)

**Total: 100 puntos**

## 🚀 Pasos para Completar el Ejercicio

### Fase 1: Planificación (30 min)

1. **Diseñar la arquitectura**
   - Dibujar diagrama de flujo de los 4 DAGs
   - Definir dependencias entre DAGs
   - Identificar puntos de validación

2. **Definir configuraciones**
   - Horarios de ejecución
   - SLAs por DAG
   - Estrategias de reintento
   - Variables de Airflow necesarias

### Fase 2: Implementación (3-4 horas)

1. **Crear DAG 1: Ingesta**
   ```bash
   touch dags/pipeline_01_ingesta_multifuente.py
   ```
   - Implementar ingesta de múltiples fuentes
   - Agregar validaciones
   - Configurar callbacks

2. **Crear DAG 2: Transformación**
   ```bash
   touch dags/pipeline_02_transformacion.py
   ```
   - Implementar ExternalTaskSensor
   - Agregar transformaciones
   - Implementar validaciones de calidad

3. **Crear DAG 3: Análisis**
   ```bash
   touch dags/pipeline_03_analytics.py
   ```
   - Implementar análisis RFM
   - Generar reportes
   - Implementar detección de anomalías

4. **Crear DAG 4: Monitoreo**
   ```bash
   touch dags/pipeline_04_monitoring.py
   ```
   - Consultar metadatos de Airflow
   - Calcular métricas de salud
   - Generar reportes de monitoreo

### Fase 3: Configuración (30 min)

1. **Configurar Variables de Airflow**
   ```python
   # Via UI o CLI
   airflow variables set pipeline_sla_hours 2
   airflow variables set alert_email "team@company.com"
   airflow variables set data_quality_threshold 0.95
   ```

2. **Configurar Connections** (si aplica)
   ```bash
   airflow connections add 'postgres_prod' \
       --conn-type 'postgres' \
       --conn-host 'postgres' \
       --conn-login 'airflow' \
       --conn-password 'airflow' \
       --conn-port 5432
   ```

### Fase 4: Testing (1 hora)

1. **Probar cada DAG individualmente**
   - Verificar que se cargan sin errores
   - Ejecutar manualmente cada DAG
   - Revisar logs de todas las tareas

2. **Probar el pipeline completo**
   - Activar todos los DAGs
   - Ejecutar DAG 1 y verificar que dispara los demás
   - Simular fallos y verificar manejo de errores
   - Verificar que las notificaciones funcionan

3. **Validar resultados**
   ```sql
   -- Verificar datos en todas las capas
   SELECT COUNT(*) FROM raw.web_events;
   SELECT COUNT(*) FROM processed.transactions_clean;
   SELECT COUNT(*) FROM analytics.customer_rfm;
   
   -- Verificar auditoría
   SELECT * FROM audit.pipeline_executions 
   WHERE execution_date = CURRENT_DATE
   ORDER BY created_at;
   ```

### Fase 5: Documentación (30 min)

1. **Crear README del pipeline**
   ```bash
   touch ejercicios/PIPELINE_README.md
   ```
   - Explicar arquitectura
   - Documentar configuración
   - Incluir guía de troubleshooting

2. **Documentar decisiones de diseño**
   - ¿Por qué estos horarios?
   - ¿Por qué estos SLAs?
   - ¿Cómo se manejan los errores?

## 💡 Consejos

### Coordinación de DAGs

```python
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_ingestion = ExternalTaskSensor(
    task_id='wait_for_ingestion',
    external_dag_id='pipeline_01_ingesta_multifuente',
    external_task_id='log_ingestion_metrics',
    allowed_states=['success'],
    failed_states=['failed', 'skipped'],
    mode='reschedule',  # Libera worker mientras espera
    timeout=3600,  # 1 hora timeout
    poke_interval=300,  # Verificar cada 5 minutos
)
```

### Callbacks de Error

```python
def notify_failure(context):
    """Callback cuando una tarea falla."""
    dag_id = context['dag'].dag_id
    task_id = context['task_instance'].task_id
    execution_date = context['execution_date']
    
    print(f"🚨 ALERTA: Tarea fallida")
    print(f"   DAG: {dag_id}")
    print(f"   Task: {task_id}")
    print(f"   Fecha: {execution_date}")
    
    # Aquí podrías enviar email, Slack, etc.
    # send_slack_alert(f"DAG {dag_id} falló en tarea {task_id}")

default_args = {
    'on_failure_callback': notify_failure,
    'on_retry_callback': lambda context: print("⚠️  Reintentando tarea..."),
}
```

### SLA Callbacks

```python
def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Callback cuando se viola un SLA."""
    print(f"⏰ SLA VIOLADO")
    print(f"   DAG: {dag.dag_id}")
    print(f"   Tareas: {[t.task_id for t in task_list]}")
    # Enviar alerta

dag = DAG(
    dag_id='pipeline_01_ingesta_multifuente',
    sla_miss_callback=sla_miss_callback,
    default_args={'sla': timedelta(hours=1)},
)
```

### Uso de Variables

```python
from airflow.models import Variable

# Obtener variables
sla_hours = Variable.get('pipeline_sla_hours', default_var=2)
alert_email = Variable.get('alert_email')
quality_threshold = float(Variable.get('data_quality_threshold', default_var=0.95))

# Usar en lógica
if quality_score < quality_threshold:
    send_alert(f"Calidad por debajo del umbral: {quality_score}")
```

### Detección de Anomalías Simple

```python
def detect_anomalies(**context):
    """Detecta anomalías comparando con promedio histórico."""
    
    # Obtener métricas de hoy
    today_query = """
        SELECT COUNT(*) as count, SUM(amount) as total
        FROM processed.transactions_clean
        WHERE DATE(transaction_date) = CURRENT_DATE
    """
    today_metrics = execute_query(today_query)
    
    # Obtener promedio de últimos 7 días
    avg_query = """
        SELECT AVG(count) as avg_count, AVG(total) as avg_total
        FROM (
            SELECT DATE(transaction_date) as date,
                   COUNT(*) as count,
                   SUM(amount) as total
            FROM processed.transactions_clean
            WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(transaction_date)
        ) daily_stats
    """
    avg_metrics = execute_query(avg_query)
    
    # Detectar anomalías (variación > 30%)
    anomalies = []
    
    count_diff = abs(today_metrics['count'][0] - avg_metrics['avg_count'][0])
    count_pct = (count_diff / avg_metrics['avg_count'][0]) * 100
    
    if count_pct > 30:
        anomalies.append({
            'metric': 'transaction_count',
            'today': today_metrics['count'][0],
            'avg': avg_metrics['avg_count'][0],
            'deviation_pct': count_pct
        })
    
    return anomalies
```

## 🔍 Preguntas de Reflexión

Después de completar el ejercicio, reflexiona sobre:

1. **Diseño**: ¿Por qué dividiste el pipeline en estos DAGs específicos? ¿Podrías haberlo hecho diferente?

2. **Horarios**: ¿Son apropiados los horarios de ejecución? ¿Qué consideraciones tuviste?

3. **SLAs**: ¿Cómo determinaste los SLAs? ¿Son realistas para producción?

4. **Errores**: ¿Qué tipos de errores puede tener el pipeline? ¿Cómo los manejas?

5. **Escalabilidad**: ¿Cómo escalaría este pipeline con 10x más datos?

6. **Monitoreo**: ¿Qué otras métricas deberías monitorear?

7. **Mejoras**: ¿Qué mejorarías si tuvieras más tiempo?

## 📚 Recursos Adicionales

- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [ExternalTaskSensor Documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/external_task_sensor.html)
- [Airflow Variables](https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html)
- [Airflow Callbacks](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/callbacks.html)
- Todos los DAGs del taller (01-08) como referencia

## ✨ Bonus (Opcional)

Si terminas el ejercicio básico, intenta agregar:

1. **Integración con Spark**: Agregar DAG que procese datos con Spark
2. **Great Expectations**: Integrar validaciones con GE
3. **Alertas reales**: Implementar notificaciones por Slack/Email
4. **Dashboard**: Crear dashboard de monitoreo con Grafana
5. **Tests**: Escribir tests unitarios para las tareas
6. **CI/CD**: Configurar pipeline de CI/CD para los DAGs
7. **Backfill**: Implementar estrategia de backfill para datos históricos

## 📊 Entregables

1. **Código**:
   - `pipeline_01_ingesta_multifuente.py`
   - `pipeline_02_transformacion.py`
   - `pipeline_03_analytics.py`
   - `pipeline_04_monitoring.py`

2. **Documentación**:
   - `PIPELINE_README.md` con arquitectura y guía
   - Docstrings completos en todos los DAGs
   - Comentarios explicativos en código complejo

3. **Configuración**:
   - Lista de Variables de Airflow necesarias
   - Lista de Connections necesarias
   - Configuración de SLAs y alertas

4. **Evidencia** (screenshots o logs):
   - Graph view de cada DAG
   - Ejecución exitosa del pipeline completo
   - Ejemplo de manejo de error
   - Reporte de monitoreo generado

---

**¡Éxito en tu pipeline! 🚀**

Este es el ejercicio más completo del taller. Tómate tu tiempo, planifica bien, y no dudes en consultar la solución de referencia en `ejercicios/soluciones/ejercicio_03_solucion.py` si te atascas.

**Recuerda**: En producción, los pipelines de datos son sistemas complejos que requieren diseño cuidadoso, monitoreo constante y mantenimiento continuo. Este ejercicio te da una probada de esa realidad.
