# Conceptos de Apache Airflow

Esta guía explica los conceptos fundamentales de Apache Airflow, sus componentes principales, mejores prácticas y patrones comunes de uso. Es una referencia esencial para entender cómo funciona Airflow y cómo utilizarlo efectivamente.

---

## 📖 Glosario de Términos

### Conceptos Fundamentales

**Airflow**  
Plataforma de orquestación de workflows de código abierto desarrollada originalmente por Airbnb. Permite programar, monitorear y gestionar pipelines de datos complejos mediante código Python.

**DAG (Directed Acyclic Graph)**  
Grafo dirigido acíclico que representa un workflow en Airflow. Define las tareas y sus dependencias, pero no contiene ciclos (una tarea no puede depender de sí misma directa o indirectamente).

**Task (Tarea)**  
Unidad básica de ejecución en Airflow. Representa una operación específica como ejecutar un script, consultar una base de datos, o enviar un email. Las tareas son nodos en el DAG.

**Operator (Operador)**  
Clase de Airflow que define el tipo de trabajo que realizará una Task. Ejemplos: `PythonOperator`, `BashOperator`, `PostgresOperator`. Los operadores son plantillas reutilizables para tareas comunes.

**Task Instance (Instancia de Tarea)**  
Ejecución específica de una Task para una fecha de ejecución particular. Una Task puede tener múltiples instancias (una por cada ejecución del DAG).

**DAG Run (Ejecución de DAG)**  
Instancia de ejecución de un DAG para una fecha específica. Contiene todas las Task Instances correspondientes a esa ejecución.

### Componentes de Airflow

**Scheduler (Programador)**  
Componente que determina cuándo ejecutar las tareas basándose en:
- Dependencias entre tareas
- Horarios configurados (schedule_interval)
- Disponibilidad de recursos
- Estado de tareas previas

**Webserver (Servidor Web)**  
Interfaz web de Airflow que proporciona:
- Visualización de DAGs y sus estados
- Monitoreo de ejecuciones
- Gestión manual de DAGs (pausar, ejecutar, etc.)
- Acceso a logs de tareas
- Configuración de variables y connections

**Executor (Ejecutor)**  
Mecanismo que determina cómo se ejecutan las tareas. Tipos principales:
- **SequentialExecutor**: Ejecuta tareas una a la vez (solo para desarrollo)
- **LocalExecutor**: Ejecuta tareas en paralelo en la misma máquina
- **CeleryExecutor**: Distribuye tareas entre múltiples workers (usado en este taller)
- **KubernetesExecutor**: Ejecuta cada tarea en un pod de Kubernetes

**Worker (Trabajador)**  
Proceso que ejecuta las tareas asignadas por el Executor. En CeleryExecutor, puede haber múltiples workers distribuidos en diferentes máquinas.

**Metadata Database (Base de Datos de Metadatos)**  
Base de datos (PostgreSQL en este taller) que almacena:
- Definiciones de DAGs
- Estado de ejecuciones
- Historial de tareas
- Variables y connections
- Logs y métricas

**Message Broker (Broker de Mensajes)**  
Sistema de mensajería (Redis en este taller) usado por CeleryExecutor para comunicar el Scheduler con los Workers.

### Conceptos de Ejecución

**execution_date (Fecha de Ejecución)**  
Fecha lógica para la cual se ejecuta un DAG. NO es la fecha actual, sino la fecha del periodo de datos que se está procesando. Por ejemplo, un DAG que corre el 2 de enero a las 00:00 tiene `execution_date` del 1 de enero.

**start_date (Fecha de Inicio)**  
Primera fecha desde la cual el DAG puede ser programado. El Scheduler no ejecutará el DAG para fechas anteriores a esta (a menos que se haga backfill).

**schedule_interval (Intervalo de Programación)**  
Frecuencia con la que se ejecuta el DAG. Puede ser:
- Expresión cron: `'0 0 * * *'` (diario a medianoche)
- Preset: `'@daily'`, `'@hourly'`, `'@weekly'`
- Timedelta: `timedelta(hours=1)`
- `None`: Solo ejecución manual

**catchup (Alcanzar)**  
Parámetro booleano que determina si Airflow debe ejecutar automáticamente todas las ejecuciones perdidas entre `start_date` y la fecha actual. `catchup=True` ejecuta todas las fechas faltantes, `catchup=False` solo ejecuta desde ahora en adelante.

**Backfill (Reprocesamiento)**  
Ejecución retroactiva de un DAG para procesar datos históricos. Se usa para:
- Reprocesar datos después de corregir un bug
- Procesar datos históricos al crear un nuevo DAG
- Recuperarse de fallos masivos

### Mecanismos de Comunicación

**XCom (Cross-Communication)**  
Mecanismo para compartir datos pequeños entre tareas. Las tareas pueden "push" valores a XCom y otras tareas pueden "pull" esos valores. Limitado a datos pequeños (< 1MB típicamente).

**Variable**  
Valor clave-valor almacenado en la base de datos de Airflow, accesible desde cualquier DAG. Útil para configuración compartida entre DAGs.

**Connection**  
Credenciales y configuración para conectarse a sistemas externos (bases de datos, APIs, servicios cloud). Almacenadas de forma segura en la base de datos de Airflow.

### Tipos de Operadores

**Sensor**  
Tipo especial de Operator que espera a que se cumpla una condición antes de continuar. Ejemplos:
- `FileSensor`: Espera a que exista un archivo
- `ExternalTaskSensor`: Espera a que otra tarea termine
- `TimeSensor`: Espera hasta una hora específica

**BranchOperator**  
Operador que permite flujos condicionales. Decide dinámicamente qué rama del DAG ejecutar basándose en lógica de negocio.

**TaskFlow API**  
API moderna de Airflow (desde versión 2.0) que usa decoradores Python (`@task`) para definir tareas de forma más simple y pythónica.

### Estados de Tareas

- **none**: Tarea creada pero no programada
- **scheduled**: Tarea programada para ejecución
- **queued**: Tarea en cola esperando un worker
- **running**: Tarea ejecutándose actualmente
- **success**: Tarea completada exitosamente
- **failed**: Tarea falló
- **skipped**: Tarea omitida (por branching)
- **upstream_failed**: Tarea no ejecutada porque una dependencia falló
- **up_for_retry**: Tarea falló pero se reintentará
- **up_for_reschedule**: Sensor esperando para verificar condición nuevamente

---

## 🏗️ Componentes de Airflow

### Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                        Airflow UI                           │
│                     (Webserver)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      Scheduler                              │
│  - Lee DAGs desde el directorio                             │
│  - Programa ejecuciones basándose en schedule_interval      │
│  - Envía tareas al Executor                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      Executor                               │
│  - CeleryExecutor: Distribuye tareas vía Redis              │
│  - Gestiona cola de tareas                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
┌─────────────▼──────┐  ┌──────────▼─────────────┐
│    Worker 1        │  │    Worker 2            │
│  - Ejecuta tareas  │  │  - Ejecuta tareas      │
└────────────────────┘  └────────────────────────┘
              │                     │
              └──────────┬──────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Metadata Database (PostgreSQL)                 │
│  - Estado de DAGs y tareas                                  │
│  - Historial de ejecuciones                                 │
│  - Variables, Connections, XComs                            │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Ejecución de un DAG

1. **Parsing**: El Scheduler lee los archivos Python del directorio `dags/` y carga las definiciones de DAGs

2. **Scheduling**: El Scheduler determina qué DAG Runs deben ejecutarse basándose en:
   - `start_date` y `schedule_interval`
   - Estado de ejecuciones previas
   - Configuración de `catchup`

3. **Task Queuing**: Para cada DAG Run, el Scheduler:
   - Identifica tareas listas para ejecutar (dependencias satisfechas)
   - Las envía al Executor
   - El Executor las coloca en la cola (Redis para CeleryExecutor)

4. **Task Execution**: Los Workers:
   - Toman tareas de la cola
   - Ejecutan el código del Operator
   - Actualizan el estado en la base de datos
   - Escriben logs

5. **Dependency Resolution**: El Scheduler:
   - Monitorea el estado de las tareas
   - Cuando una tarea completa, programa las tareas downstream
   - Repite hasta que todas las tareas del DAG Run completen

6. **Completion**: Cuando todas las tareas terminan, el DAG Run se marca como `success` o `failed`

### Webserver - Interfaz de Usuario

La UI de Airflow proporciona varias vistas:

**DAGs View (Vista de DAGs)**  
Lista todos los DAGs con información resumida:
- Estado (pausado/activo)
- Última ejecución
- Próxima ejecución programada
- Estadísticas de éxito/fallo

**Graph View (Vista de Grafo)**  
Visualización gráfica del DAG mostrando:
- Tareas como nodos
- Dependencias como flechas
- Estado de cada tarea (colores)

**Tree View (Vista de Árbol)**  
Historial de ejecuciones del DAG:
- Cada columna es una ejecución
- Cada fila es una tarea
- Colores indican estado

**Gantt View (Vista de Gantt)**  
Diagrama de Gantt mostrando:
- Duración de cada tarea
- Paralelismo
- Cuellos de botella

**Task Instance Details (Detalles de Instancia)**  
Información detallada de una tarea específica:
- Logs de ejecución
- Duración
- Intentos
- XCom values

---

## ✅ Mejores Prácticas

### Diseño de DAGs

**1. Idempotencia**  
Las tareas deben producir el mismo resultado si se ejecutan múltiples veces con los mismos inputs.

```python
# ❌ MAL: No idempotente
def load_data():
    df = pd.read_csv('data.csv')
    df.to_sql('table', engine, if_exists='append')  # Duplica datos

# ✅ BIEN: Idempotente
def load_data():
    df = pd.read_csv('data.csv')
    df.to_sql('table', engine, if_exists='replace')  # Reemplaza datos
```

**2. Atomicidad**  
Cada tarea debe ser una unidad atómica de trabajo. Si falla, debe poder reintentarse sin efectos secundarios.

```python
# ❌ MAL: Tarea hace demasiado
@task
def process_everything():
    extract_data()
    transform_data()
    load_data()
    send_email()

# ✅ BIEN: Tareas separadas
@task
def extract_data(): ...

@task
def transform_data(): ...

@task
def load_data(): ...

@task
def send_email(): ...
```

**3. Tareas Pequeñas y Enfocadas**  
Divide el trabajo en tareas pequeñas para:
- Mejor paralelismo
- Reintentos más granulares
- Debugging más fácil

**4. No Usar Variables Globales**  
Los DAGs se parsean frecuentemente. Variables globales pueden causar comportamiento inesperado.

```python
# ❌ MAL: Variable global
current_date = datetime.now()  # Se evalúa al parsear, no al ejecutar

# ✅ BIEN: Usar macros o parámetros
@task
def process_data(**context):
    current_date = context['execution_date']
```

### Configuración de DAGs

**1. Configurar Reintentos**  
Siempre configura reintentos para manejar fallos transitorios.

```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}
```

**2. Configurar Timeouts**  
Evita que tareas cuelguen indefinidamente.

```python
@task(execution_timeout=timedelta(hours=1))
def long_running_task():
    ...
```

**3. Usar catchup Apropiadamente**  
Para desarrollo y la mayoría de casos, usa `catchup=False`.

```python
dag = DAG(
    'my_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,  # No ejecutar fechas históricas
)
```

**4. Configurar SLAs**  
Define SLAs para monitorear performance.

```python
@task(sla=timedelta(hours=2))
def critical_task():
    ...
```

### Manejo de Datos

**1. No Pasar Datos Grandes por XCom**  
XCom es para metadatos pequeños, no para datasets.

```python
# ❌ MAL: Pasar DataFrame por XCom
@task
def extract():
    df = pd.read_csv('large_file.csv')
    return df  # Puede ser muy grande

# ✅ BIEN: Pasar ruta o metadatos
@task
def extract():
    df = pd.read_csv('large_file.csv')
    output_path = '/tmp/processed_data.parquet'
    df.to_parquet(output_path)
    return output_path  # Solo la ruta
```

**2. Usar Almacenamiento Externo**  
Para datos grandes, usa S3, HDFS, o bases de datos.

**3. Particionar Datos por Fecha**  
Facilita backfills y reprocesamiento.

```python
@task
def process_partition(**context):
    partition_date = context['ds']  # YYYY-MM-DD
    df = pd.read_parquet(f's3://bucket/data/date={partition_date}/')
    # Procesar solo esta partición
```

### Seguridad y Credenciales

**1. Usar Connections**  
Nunca hardcodear credenciales en el código.

```python
# ❌ MAL: Credenciales en código
conn_string = "postgresql://user:password@host:5432/db"

# ✅ BIEN: Usar Connection
from airflow.hooks.postgres_hook import PostgresHook
hook = PostgresHook(postgres_conn_id='my_postgres')
```

**2. Usar Variables para Configuración**  
Centraliza configuración en Variables de Airflow.

```python
from airflow.models import Variable

bucket_name = Variable.get('s3_bucket_name')
api_key = Variable.get('api_key', default_var='default_key')
```

**3. Usar Fernet Key**  
Asegura que `AIRFLOW__CORE__FERNET_KEY` esté configurado para encriptar secretos.

### Performance y Recursos

**1. Configurar Paralelismo**  
Ajusta según recursos disponibles.

```python
dag = DAG(
    'my_dag',
    max_active_runs=3,  # Máximo 3 DAG runs simultáneos
    max_active_tasks=10,  # Máximo 10 tareas simultáneas por DAG run
)
```

**2. Usar Pools**  
Limita concurrencia de tareas que usan el mismo recurso.

```python
@task(pool='database_pool', pool_slots=2)
def query_database():
    ...
```

**3. Optimizar Sensores**  
Usa modo `reschedule` para liberar worker slots.

```python
FileSensor(
    task_id='wait_for_file',
    filepath='/path/to/file',
    mode='reschedule',  # Libera worker mientras espera
    poke_interval=60,
)
```

### Logging y Monitoreo

**1. Logging Estructurado**  
Usa logging apropiadamente para debugging.

```python
from airflow.utils.log.logging_mixin import LoggingMixin

@task
def my_task():
    log = LoggingMixin().log
    log.info("Iniciando procesamiento")
    log.warning("Advertencia: datos incompletos")
    log.error("Error al procesar")
```

**2. Callbacks para Alertas**  
Configura callbacks para notificaciones.

```python
def on_failure_callback(context):
    # Enviar email, Slack, etc.
    pass

dag = DAG(
    'my_dag',
    default_args={
        'on_failure_callback': on_failure_callback,
    }
)
```

**3. Métricas Personalizadas**  
Registra métricas en tablas de auditoría.

```python
@task
def log_metrics(**context):
    execution_date = context['execution_date']
    # Guardar métricas en audit.pipeline_executions
```

---

## 🎯 Patrones Comunes

### Patrón 1: ETL Básico

Extracción, Transformación y Carga de datos.

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,
)
def etl_pipeline():
    
    @task
    def extract():
        # Extraer datos de fuente
        data = fetch_from_api()
        return data
    
    @task
    def transform(data):
        # Transformar datos
        cleaned_data = clean_and_transform(data)
        return cleaned_data
    
    @task
    def load(data):
        # Cargar a destino
        save_to_database(data)
    
    # Definir flujo
    data = extract()
    transformed = transform(data)
    load(transformed)

etl_pipeline()
```

### Patrón 2: Branching Condicional

Ejecutar diferentes ramas basándose en condiciones.

```python
from airflow.operators.python import BranchPythonOperator

def decide_branch(**context):
    # Lógica de decisión
    if condition:
        return 'process_large_dataset'
    else:
        return 'process_small_dataset'

branch_task = BranchPythonOperator(
    task_id='branch_decision',
    python_callable=decide_branch,
)

process_large = PythonOperator(
    task_id='process_large_dataset',
    python_callable=process_large_data,
)

process_small = PythonOperator(
    task_id='process_small_dataset',
    python_callable=process_small_data,
)

branch_task >> [process_large, process_small]
```

### Patrón 3: Sensor + Procesamiento

Esperar condición externa antes de procesar.

```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id='wait_for_data',
    filepath='/data/input/{{ ds }}.csv',
    poke_interval=60,
    timeout=3600,
    mode='reschedule',
)

process_file = PythonOperator(
    task_id='process_data',
    python_callable=process_csv,
)

wait_for_file >> process_file
```

### Patrón 4: Procesamiento Paralelo

Procesar múltiples items en paralelo.

```python
from airflow.decorators import task

@task
def get_items():
    return ['item1', 'item2', 'item3', 'item4']

@task
def process_item(item):
    # Procesar item individual
    result = heavy_processing(item)
    return result

@task
def aggregate_results(results):
    # Combinar resultados
    final_result = combine(results)
    return final_result

# Usar expand para procesamiento paralelo
items = get_items()
results = process_item.expand(item=items)
aggregate_results(results)
```

### Patrón 5: Validación de Calidad

Validar datos antes de continuar pipeline.

```python
@task
def validate_data(data):
    validations = {
        'no_nulls': check_nulls(data),
        'valid_ranges': check_ranges(data),
        'unique_ids': check_uniqueness(data),
    }
    
    if not all(validations.values()):
        raise ValueError(f"Validación falló: {validations}")
    
    return data

@task
def process_validated_data(data):
    # Procesar solo si validación pasó
    ...

data = extract_data()
validated = validate_data(data)
process_validated_data(validated)
```

### Patrón 6: Coordinación de DAGs

Coordinar múltiples DAGs con ExternalTaskSensor.

```python
# DAG downstream
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_upstream = ExternalTaskSensor(
    task_id='wait_for_ingestion',
    external_dag_id='01_dag_basico_ingesta',
    external_task_id='log_completion',
    mode='poke',
)

process_data = PythonOperator(
    task_id='process',
    python_callable=process,
)

wait_for_upstream >> process_data
```

### Patrón 7: Manejo de Errores Robusto

Implementar manejo de errores y recuperación.

```python
@task(retries=3, retry_delay=timedelta(minutes=5))
def resilient_task():
    try:
        result = risky_operation()
        return result
    except TemporaryError as e:
        # Log y reintenta
        log.warning(f"Error temporal: {e}")
        raise  # Airflow reintentará
    except PermanentError as e:
        # Log y falla
        log.error(f"Error permanente: {e}")
        send_alert(e)
        raise

@task
def cleanup_on_failure(**context):
    # Tarea de limpieza si algo falla
    if context['task_instance'].state == 'failed':
        cleanup_resources()

resilient_task() >> cleanup_on_failure()
```

### Patrón 8: Procesamiento Incremental

Procesar solo datos nuevos desde última ejecución.

```python
@task
def get_last_processed_timestamp(**context):
    # Obtener timestamp de última ejecución exitosa
    prev_execution = context['prev_execution_date']
    return prev_execution

@task
def extract_incremental(last_timestamp):
    # Extraer solo datos nuevos
    query = f"""
        SELECT * FROM source_table
        WHERE updated_at > '{last_timestamp}'
    """
    return execute_query(query)

last_ts = get_last_processed_timestamp()
new_data = extract_incremental(last_ts)
```

---

## 🔍 Debugging y Troubleshooting

### Estrategias de Debugging

**1. Usar `airflow tasks test`**  
Ejecuta una tarea sin dependencias ni estado.

```bash
airflow tasks test dag_id task_id 2024-01-01
```

**2. Revisar Logs**  
Los logs son tu mejor amigo. Accede desde:
- UI: Task Instance > Log
- Filesystem: `logs/dag_id/task_id/execution_date/`

**3. Usar Python Debugger**  
Para debugging local:

```python
@task
def debug_task():
    import pdb; pdb.set_trace()
    # Tu código aquí
```

**4. Validar DAG Localmente**  
Ejecuta el archivo Python directamente:

```bash
python dags/my_dag.py
```

### Problemas Comunes

**DAG no aparece en UI**  
- Verificar errores de sintaxis
- Revisar logs del scheduler
- Asegurar que el archivo esté en `dags/`

**Tareas quedan en "running"**  
- Verificar logs del worker
- Revisar timeouts
- Verificar que el worker esté activo

**Errores de importación**  
- Verificar que módulos estén instalados
- Revisar PYTHONPATH
- Asegurar que `__init__.py` exista en directorios

---

## 📚 Recursos Adicionales

- **Documentación Oficial**: https://airflow.apache.org/docs/
- **Guía de Mejores Prácticas**: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html
- **Repositorio GitHub**: https://github.com/apache/airflow

---

**Última actualización**: Enero 2024  
**Versión de Airflow**: 2.7.3
