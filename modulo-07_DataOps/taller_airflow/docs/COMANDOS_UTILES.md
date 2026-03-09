# Comandos Útiles - Taller de Apache Airflow

Esta guía de referencia rápida contiene los comandos más utilizados para trabajar con el taller de Airflow, incluyendo Docker Compose, CLI de Airflow, queries SQL útiles y soluciones a problemas comunes.

---

## 📦 Comandos Docker Compose

### Iniciar el Entorno

```bash
# Iniciar todos los servicios en segundo plano
docker-compose up -d

# Iniciar y ver logs en tiempo real
docker-compose up

# Iniciar servicios específicos
docker-compose up -d postgres redis
```

### Detener y Limpiar

```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Borra la base de datos)
docker-compose down -v

# Detener y eliminar imágenes
docker-compose down --rmi all
```

### Monitoreo y Logs

```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
docker-compose logs postgres

# Seguir logs en tiempo real
docker-compose logs -f airflow-scheduler

# Ver últimas 100 líneas de logs
docker-compose logs --tail=100 airflow-worker
```

### Gestión de Servicios

```bash
# Ver estado de los servicios
docker-compose ps

# Reiniciar un servicio específico
docker-compose restart airflow-scheduler

# Reiniciar todos los servicios
docker-compose restart

# Reconstruir imágenes (después de cambiar requirements.txt)
docker-compose build

# Reconstruir y reiniciar
docker-compose up -d --build
```

### Acceso a Contenedores

```bash
# Acceder al contenedor del webserver
docker-compose exec airflow-webserver bash

# Acceder al contenedor del scheduler
docker-compose exec airflow-scheduler bash

# Acceder a PostgreSQL
docker-compose exec postgres psql -U airflow -d airflow

# Acceder a Redis CLI
docker-compose exec redis redis-cli
```

---

## 🚀 Comandos CLI de Airflow

### Gestión de DAGs

```bash
# Listar todos los DAGs
docker-compose exec airflow-scheduler airflow dags list

# Ver detalles de un DAG específico
docker-compose exec airflow-scheduler airflow dags show 01_dag_basico_ingesta

# Pausar un DAG
docker-compose exec airflow-scheduler airflow dags pause 01_dag_basico_ingesta

# Despausar un DAG
docker-compose exec airflow-scheduler airflow dags unpause 01_dag_basico_ingesta

# Eliminar un DAG (solo de la base de datos, no el archivo)
docker-compose exec airflow-scheduler airflow dags delete 01_dag_basico_ingesta

# Probar un DAG (validar sintaxis)
docker-compose exec airflow-scheduler airflow dags test 01_dag_basico_ingesta 2024-01-01
```

### Ejecución de Tareas

```bash
# Ejecutar una tarea específica manualmente
docker-compose exec airflow-scheduler airflow tasks test 01_dag_basico_ingesta check_source_files 2024-01-01

# Listar tareas de un DAG
docker-compose exec airflow-scheduler airflow tasks list 01_dag_basico_ingesta

# Ver estado de una tarea
docker-compose exec airflow-scheduler airflow tasks state 01_dag_basico_ingesta check_source_files 2024-01-01

# Limpiar estado de una tarea (para re-ejecutar)
docker-compose exec airflow-scheduler airflow tasks clear 01_dag_basico_ingesta -t check_source_files
```

### Backfill (Reprocesamiento Histórico)

```bash
# Ejecutar backfill para un rango de fechas
docker-compose exec airflow-scheduler airflow dags backfill \
  -s 2024-01-01 \
  -e 2024-01-31 \
  01_dag_basico_ingesta

# Backfill con reintentos
docker-compose exec airflow-scheduler airflow dags backfill \
  -s 2024-01-01 \
  -e 2024-01-31 \
  --rerun-failed-tasks \
  01_dag_basico_ingesta

# Backfill sin dependencias
docker-compose exec airflow-scheduler airflow dags backfill \
  -s 2024-01-01 \
  -e 2024-01-31 \
  --ignore-dependencies \
  01_dag_basico_ingesta
```

### Variables y Connections

```bash
# Listar variables
docker-compose exec airflow-scheduler airflow variables list

# Crear/actualizar variable
docker-compose exec airflow-scheduler airflow variables set my_key my_value

# Obtener valor de variable
docker-compose exec airflow-scheduler airflow variables get my_key

# Eliminar variable
docker-compose exec airflow-scheduler airflow variables delete my_key

# Importar variables desde JSON
docker-compose exec airflow-scheduler airflow variables import /opt/airflow/variables.json

# Listar connections
docker-compose exec airflow-scheduler airflow connections list

# Crear connection
docker-compose exec airflow-scheduler airflow connections add 'my_postgres' \
  --conn-type 'postgres' \
  --conn-host 'postgres' \
  --conn-login 'airflow' \
  --conn-password 'airflow' \
  --conn-port 5432
```

### Usuarios y Roles

```bash
# Listar usuarios
docker-compose exec airflow-webserver airflow users list

# Crear usuario admin
docker-compose exec airflow-webserver airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin

# Cambiar contraseña
docker-compose exec airflow-webserver airflow users reset-password \
  --username airflow
```

### Información del Sistema

```bash
# Ver versión de Airflow
docker-compose exec airflow-scheduler airflow version

# Ver configuración
docker-compose exec airflow-scheduler airflow config list

# Ver información de la base de datos
docker-compose exec airflow-scheduler airflow db check

# Inicializar/actualizar base de datos
docker-compose exec airflow-scheduler airflow db init
docker-compose exec airflow-scheduler airflow db upgrade
```

---

## 🗄️ Queries SQL Útiles

### Conectarse a PostgreSQL

```bash
# Desde la línea de comandos
docker-compose exec postgres psql -U airflow -d airflow

# O usando variables de entorno
docker-compose exec postgres psql postgresql://airflow:airflow@localhost:5432/airflow
```

### Consultas de Datos del Taller

```sql
-- Ver todas las transacciones raw
SELECT * FROM raw.transactions LIMIT 10;

-- Contar registros por tabla
SELECT 'raw.transactions' as tabla, COUNT(*) as registros FROM raw.transactions
UNION ALL
SELECT 'raw.products', COUNT(*) FROM raw.products
UNION ALL
SELECT 'raw.customers', COUNT(*) FROM raw.customers
UNION ALL
SELECT 'processed.transactions_clean', COUNT(*) FROM processed.transactions_clean;

-- Ver métricas diarias más recientes
SELECT * FROM analytics.daily_sales_metrics 
ORDER BY metric_date DESC 
LIMIT 7;

-- Ver top 10 clientes por gasto total
SELECT 
    customer_id,
    SUM(total_spent) as total_gastado,
    SUM(transaction_count) as total_transacciones
FROM analytics.customer_metrics
GROUP BY customer_id
ORDER BY total_gastado DESC
LIMIT 10;

-- Ver resultados de validaciones de calidad
SELECT 
    dag_id,
    check_name,
    check_result,
    records_checked,
    records_failed,
    execution_date
FROM audit.data_quality_checks
ORDER BY created_at DESC
LIMIT 20;

-- Ver ejecuciones de pipelines con errores
SELECT 
    dag_id,
    execution_date,
    status,
    error_message,
    duration_seconds
FROM audit.pipeline_executions
WHERE status = 'failed'
ORDER BY created_at DESC;
```

### Consultas de Metadatos de Airflow

```sql
-- Ver todos los DAGs registrados
SELECT dag_id, is_paused, is_active, last_parsed_time 
FROM dag 
ORDER BY dag_id;

-- Ver ejecuciones de DAGs (últimas 20)
SELECT 
    dag_id,
    execution_date,
    state,
    start_date,
    end_date,
    EXTRACT(EPOCH FROM (end_date - start_date)) as duration_seconds
FROM dag_run
ORDER BY execution_date DESC
LIMIT 20;

-- Ver tareas fallidas recientes
SELECT 
    dag_id,
    task_id,
    execution_date,
    state,
    start_date,
    end_date,
    try_number
FROM task_instance
WHERE state = 'failed'
ORDER BY start_date DESC
LIMIT 20;

-- Ver duración promedio de DAGs
SELECT 
    dag_id,
    COUNT(*) as ejecuciones,
    AVG(EXTRACT(EPOCH FROM (end_date - start_date))) as avg_duration_seconds,
    MAX(EXTRACT(EPOCH FROM (end_date - start_date))) as max_duration_seconds
FROM dag_run
WHERE state = 'success' AND end_date IS NOT NULL
GROUP BY dag_id
ORDER BY avg_duration_seconds DESC;

-- Ver tareas más lentas
SELECT 
    dag_id,
    task_id,
    AVG(EXTRACT(EPOCH FROM (end_date - start_date))) as avg_duration_seconds,
    COUNT(*) as ejecuciones
FROM task_instance
WHERE state = 'success' AND end_date IS NOT NULL
GROUP BY dag_id, task_id
ORDER BY avg_duration_seconds DESC
LIMIT 10;

-- Ver XComs recientes
SELECT 
    dag_id,
    task_id,
    execution_date,
    key,
    value,
    timestamp
FROM xcom
ORDER BY timestamp DESC
LIMIT 20;
```

### Limpieza de Datos

```sql
-- Limpiar datos de las capas (¡CUIDADO!)
TRUNCATE TABLE raw.transactions;
TRUNCATE TABLE raw.products;
TRUNCATE TABLE raw.customers;
TRUNCATE TABLE processed.transactions_clean;
TRUNCATE TABLE analytics.daily_sales_metrics;
TRUNCATE TABLE analytics.customer_metrics;

-- Limpiar logs de auditoría
TRUNCATE TABLE audit.data_quality_checks;
TRUNCATE TABLE audit.pipeline_executions;

-- Eliminar ejecuciones antiguas de DAGs (más de 30 días)
DELETE FROM dag_run 
WHERE execution_date < NOW() - INTERVAL '30 days';

-- Eliminar instancias de tareas antiguas
DELETE FROM task_instance 
WHERE execution_date < NOW() - INTERVAL '30 days';
```

---

## 🔧 Troubleshooting Común

### Problema: Los servicios no inician

**Síntomas**: `docker-compose up` falla o los servicios se reinician constantemente

**Soluciones**:

```bash
# 1. Verificar logs para identificar el error
docker-compose logs

# 2. Verificar recursos del sistema (memoria, CPU, disco)
docker stats

# 3. Limpiar y reiniciar desde cero
docker-compose down -v
docker-compose up -d

# 4. En Linux, verificar AIRFLOW_UID
echo "AIRFLOW_UID=$(id -u)" >> .env
docker-compose down -v
docker-compose up -d
```

### Problema: DAGs no aparecen en la UI

**Síntomas**: Los archivos .py están en `dags/` pero no se ven en la interfaz web

**Soluciones**:

```bash
# 1. Verificar que el directorio esté montado correctamente
docker-compose exec airflow-scheduler ls -la /opt/airflow/dags

# 2. Verificar errores de sintaxis en los DAGs
docker-compose exec airflow-scheduler python /opt/airflow/dags/01_dag_basico_ingesta.py

# 3. Verificar logs del scheduler
docker-compose logs airflow-scheduler | grep -i error

# 4. Forzar re-parsing de DAGs
docker-compose restart airflow-scheduler

# 5. Verificar que LOAD_EXAMPLES esté en false
docker-compose exec airflow-scheduler airflow config get-value core load_examples
```

### Problema: Tareas quedan en estado "running" indefinidamente

**Síntomas**: Las tareas no completan ni fallan, quedan "stuck"

**Soluciones**:

```bash
# 1. Verificar logs de la tarea
docker-compose logs airflow-worker

# 2. Marcar tarea como fallida manualmente
docker-compose exec airflow-scheduler airflow tasks clear \
  01_dag_basico_ingesta \
  -t check_source_files \
  -s 2024-01-01 \
  -e 2024-01-01

# 3. Reiniciar el worker
docker-compose restart airflow-worker

# 4. Verificar que el worker esté procesando tareas
docker-compose exec airflow-worker celery -A airflow.executors.celery_executor inspect active
```

### Problema: Error de conexión a PostgreSQL

**Síntomas**: `FATAL: password authentication failed` o `could not connect to server`

**Soluciones**:

```bash
# 1. Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# 2. Verificar credenciales en .env
cat .env | grep POSTGRES

# 3. Probar conexión manualmente
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT 1;"

# 4. Reinicializar base de datos (¡CUIDADO! Borra datos)
docker-compose down -v
docker-compose up -d
```

### Problema: Errores de permisos en volúmenes

**Síntomas**: `Permission denied` al escribir logs o archivos

**Soluciones**:

```bash
# En Linux, configurar AIRFLOW_UID
echo "AIRFLOW_UID=$(id -u)" >> .env

# Cambiar permisos de directorios
sudo chown -R $(id -u):$(id -g) logs/ dags/ plugins/ data/

# O dar permisos amplios (solo para desarrollo local)
chmod -R 777 logs/ dags/ plugins/ data/

# Reiniciar servicios
docker-compose down
docker-compose up -d
```

### Problema: Memoria insuficiente

**Síntomas**: Servicios se reinician, `OOMKilled` en logs

**Soluciones**:

```bash
# 1. Verificar uso de memoria
docker stats

# 2. Aumentar memoria asignada a Docker
# En Docker Desktop: Settings > Resources > Memory (mínimo 4GB)

# 3. Reducir workers de Celery (editar docker-compose.yml)
# Cambiar réplicas de airflow-worker a 1

# 4. Usar LocalExecutor en lugar de CeleryExecutor para desarrollo
# Editar .env:
# AIRFLOW__CORE__EXECUTOR=LocalExecutor
```

### Problema: DAG tarda mucho en ejecutarse

**Síntomas**: Las tareas tardan más de lo esperado

**Soluciones**:

```sql
-- 1. Identificar tareas lentas
SELECT 
    task_id,
    AVG(EXTRACT(EPOCH FROM (end_date - start_date))) as avg_seconds
FROM task_instance
WHERE dag_id = '01_dag_basico_ingesta' AND state = 'success'
GROUP BY task_id
ORDER BY avg_seconds DESC;

-- 2. Verificar si hay tareas bloqueadas
SELECT task_id, state, start_date 
FROM task_instance 
WHERE dag_id = '01_dag_basico_ingesta' 
  AND execution_date = '2024-01-01'
ORDER BY start_date;
```

```bash
# 3. Aumentar paralelismo (editar airflow.cfg o variables de entorno)
# AIRFLOW__CORE__PARALLELISM=32
# AIRFLOW__CORE__DAG_CONCURRENCY=16

# 4. Verificar logs para identificar cuellos de botella
docker-compose logs airflow-worker | grep "01_dag_basico_ingesta"
```

### Problema: Importar módulos personalizados falla

**Síntomas**: `ModuleNotFoundError` al importar desde `utils/`

**Soluciones**:

```bash
# 1. Verificar estructura de directorios
docker-compose exec airflow-scheduler ls -la /opt/airflow/dags/utils/

# 2. Asegurar que utils/ tenga __init__.py
touch dags/utils/__init__.py

# 3. Verificar PYTHONPATH
docker-compose exec airflow-scheduler python -c "import sys; print(sys.path)"

# 4. Reiniciar scheduler después de cambios
docker-compose restart airflow-scheduler
```

### Problema: Cambios en DAGs no se reflejan

**Síntomas**: Modificaciones en archivos .py no aparecen en la UI

**Soluciones**:

```bash
# 1. Verificar que el archivo se guardó correctamente
docker-compose exec airflow-scheduler cat /opt/airflow/dags/01_dag_basico_ingesta.py | head -20

# 2. Esperar el intervalo de parsing (por defecto 30 segundos)
# O forzar refresh en la UI (botón de refresh en la lista de DAGs)

# 3. Reiniciar scheduler si es necesario
docker-compose restart airflow-scheduler

# 4. Verificar errores de sintaxis
docker-compose exec airflow-scheduler python /opt/airflow/dags/01_dag_basico_ingesta.py
```

---

## 📚 Recursos Adicionales

### Acceso a la UI Web

- **URL**: http://localhost:8080
- **Usuario**: airflow
- **Contraseña**: airflow

### Acceso a PostgreSQL

```bash
# Desde host (si tienes psql instalado)
psql postgresql://airflow:airflow@localhost:5432/airflow

# Desde contenedor
docker-compose exec postgres psql -U airflow -d airflow
```

### Archivos de Configuración Importantes

- `docker-compose.yml`: Configuración de servicios
- `.env`: Variables de entorno
- `dags/`: Directorio de DAGs
- `logs/`: Logs de ejecución
- `data/`: Datos del taller
- `scripts/init_db.sql`: Inicialización de base de datos

### Comandos Rápidos de Desarrollo

```bash
# Reinicio rápido después de cambios en código
docker-compose restart airflow-scheduler airflow-worker

# Ver logs en tiempo real de scheduler y worker
docker-compose logs -f airflow-scheduler airflow-worker

# Ejecutar tests de DAGs
docker-compose exec airflow-scheduler python -m pytest /opt/airflow/scripts/test_dags.py

# Validar todos los DAGs
docker-compose exec airflow-scheduler airflow dags list-import-errors
```

---

## 💡 Tips y Mejores Prácticas

1. **Desarrollo iterativo**: Usa `airflow tasks test` para probar tareas individuales antes de ejecutar el DAG completo

2. **Logs detallados**: Agrega logging en tus tareas para facilitar debugging:
   ```python
   from airflow.utils.log.logging_mixin import LoggingMixin
   log = LoggingMixin().log
   log.info("Mensaje informativo")
   ```

3. **Validación de DAGs**: Antes de hacer commit, valida sintaxis:
   ```bash
   python dags/mi_dag.py
   ```

4. **Limpieza periódica**: Limpia ejecuciones antiguas para mantener la base de datos ligera

5. **Monitoreo**: Revisa regularmente la tabla `audit.pipeline_executions` para identificar problemas

6. **Backups**: Antes de hacer cambios importantes, respalda la base de datos:
   ```bash
   docker-compose exec postgres pg_dump -U airflow airflow > backup.sql
   ```

---

**Última actualización**: Enero 2024  
**Versión de Airflow**: 2.7.3
