# Guía de Testing - Taller de Apache Airflow

Esta guía proporciona instrucciones para probar los DAGs del taller antes de ejecutarlos en el entorno completo de Airflow.

## Tabla de Contenidos

1. [Validación de Sintaxis](#validación-de-sintaxis)
2. [Testing de Utilidades](#testing-de-utilidades)
3. [Validación de Estructura de DAGs](#validación-de-estructura-de-dags)
4. [Testing con Docker](#testing-con-docker)
5. [Troubleshooting](#troubleshooting)

---

## Validación de Sintaxis

### Verificar sintaxis de Python

```bash
# Validar todos los DAGs
python -m py_compile dags/01_dag_basico_ingesta.py
python -m py_compile dags/02_dag_transformaciones.py
python -m py_compile dags/03_dag_calidad.py
python -m py_compile dags/04_dag_sensores.py
python -m py_compile dags/05_dag_backfill.py

# Validar utilidades
python -m py_compile dags/utils/db_utils.py
python -m py_compile dags/utils/validation_utils.py
```

### Verificar imports

```bash
# Desde el directorio del taller
cd modulo-07_DataOps/taller_airflow

# Verificar que los módulos se puedan importar
python -c "import sys; sys.path.insert(0, 'dags'); from utils import db_utils, validation_utils; print('✅ Imports OK')"
```

---

## Testing de Utilidades

### Test de validation_utils

```bash
# Ejecutar tests unitarios de las funciones de validación
python scripts/test_validation_utils.py
```

Esto validará:
- `validate_nulls()`: Detección de valores nulos
- `validate_range()`: Validación de rangos numéricos
- `validate_uniqueness()`: Verificación de unicidad

### Test de db_utils (requiere base de datos)

```bash
# Primero, iniciar solo el servicio de Postgres
docker-compose up -d postgres

# Esperar a que Postgres esté listo
sleep 10

# Probar conexión a la base de datos
python -c "
import sys
sys.path.insert(0, 'dags')
from utils.db_utils import get_postgres_engine
try:
    engine = get_postgres_engine()
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('✅ Conexión a Postgres exitosa')
except Exception as e:
    print(f'❌ Error de conexión: {e}')
"
```

---

## Validación de Estructura de DAGs

### Usando el script de validación

```bash
# Ejecutar el script de validación de DAGs
python scripts/test_dags.py
```

Este script verifica:
- Que los DAGs se puedan importar sin errores
- Que tengan un objeto `dag` definido
- Que tengan las propiedades básicas (dag_id, schedule_interval, tasks)

### Validación manual de un DAG específico

```python
# Validar DAG 01
python -c "
import sys
sys.path.insert(0, 'dags')

# Importar el DAG
from dag_01_basico_ingesta import dag

# Verificar propiedades
print(f'DAG ID: {dag.dag_id}')
print(f'Schedule: {dag.schedule_interval}')
print(f'Catchup: {dag.catchup}')
print(f'Tasks: {[task.task_id for task in dag.tasks]}')
print(f'Total tasks: {len(dag.tasks)}')
"
```

---

## Testing con Docker

### 1. Iniciar el entorno completo

```bash
# Desde el directorio del taller
cd modulo-07_DataOps/taller_airflow

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 2. Verificar que los servicios estén corriendo

```bash
# Verificar estado de los contenedores
docker-compose ps

# Deberías ver:
# - postgres (puerto 5432)
# - redis (puerto 6379)
# - airflow-webserver (puerto 8080)
# - airflow-scheduler
# - airflow-worker
```

### 3. Acceder a la UI de Airflow

1. Abrir navegador en: http://localhost:8080
2. Usuario: `airflow`
3. Contraseña: `airflow`

### 4. Verificar que los DAGs aparezcan

En la UI de Airflow, deberías ver:
- `01_dag_basico_ingesta`
- `02_dag_transformaciones`
- `03_dag_calidad`
- `04_dag_sensores`
- `05_dag_backfill`

### 5. Inicializar la base de datos

```bash
# Ejecutar script de inicialización
docker-compose exec postgres psql -U airflow -d airflow -f /docker-entrypoint-initdb.d/init_db.sql

# O manualmente:
docker-compose exec postgres psql -U airflow -d airflow
```

```sql
-- Verificar que los schemas existan
\dn

-- Deberías ver: raw, processed, analytics, audit
```

### 6. Generar datos de prueba

```bash
# Ejecutar script de generación de datos
docker-compose exec airflow-webserver python /opt/airflow/scripts/generate_sample_data.py

# Verificar que los archivos CSV se hayan creado
docker-compose exec airflow-webserver ls -lh /opt/airflow/data/raw/
```

### 7. Probar DAG 01 manualmente

```bash
# Ejecutar una tarea específica en modo test
docker-compose exec airflow-webserver airflow tasks test 01_dag_basico_ingesta check_transactions_file 2024-01-01

# Ejecutar todo el DAG para una fecha específica
docker-compose exec airflow-webserver airflow dags test 01_dag_basico_ingesta 2024-01-01
```

### 8. Activar y ejecutar DAGs desde la UI

1. En la UI, activar el DAG 01 (toggle a ON)
2. Click en "Trigger DAG" (botón de play)
3. Monitorear la ejecución en la vista de Grid
4. Revisar logs de cada tarea

---

## Troubleshooting

### Problema: DAGs no aparecen en la UI

**Solución:**
```bash
# Verificar logs del scheduler
docker-compose logs airflow-scheduler

# Verificar que los archivos de DAGs estén en el volumen
docker-compose exec airflow-webserver ls -la /opt/airflow/dags/

# Refrescar DAGs manualmente
docker-compose exec airflow-webserver airflow dags list
```

### Problema: Error de conexión a Postgres

**Solución:**
```bash
# Verificar que Postgres esté corriendo
docker-compose ps postgres

# Verificar variables de entorno
docker-compose exec airflow-webserver env | grep POSTGRES

# Probar conexión manualmente
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT 1"
```

### Problema: Import errors en DAGs

**Solución:**
```bash
# Verificar que las utilidades estén en el path correcto
docker-compose exec airflow-webserver ls -la /opt/airflow/dags/utils/

# Verificar imports desde el contenedor
docker-compose exec airflow-webserver python -c "
import sys
sys.path.insert(0, '/opt/airflow/dags')
from utils import db_utils, validation_utils
print('✅ Imports OK')
"
```

### Problema: FileSensor no encuentra archivos

**Solución:**
```bash
# Verificar que los archivos existan en el volumen
docker-compose exec airflow-webserver ls -la /opt/airflow/data/raw/

# Verificar permisos
docker-compose exec airflow-webserver ls -la /opt/airflow/data/

# Generar archivos de prueba si no existen
docker-compose exec airflow-webserver python /opt/airflow/scripts/generate_sample_data.py
```

### Problema: ExternalTaskSensor timeout

**Solución:**
- Asegurar que el DAG upstream (01_dag_basico_ingesta) se haya ejecutado primero
- Verificar que las fechas de ejecución coincidan
- Revisar el `execution_delta` en el sensor
- Ejecutar el DAG upstream manualmente si es necesario

### Problema: Tareas fallan con "No module named 'utils'"

**Solución:**
```bash
# Verificar estructura de directorios
docker-compose exec airflow-webserver tree /opt/airflow/dags/

# Asegurar que utils/ tenga __init__.py
docker-compose exec airflow-webserver touch /opt/airflow/dags/utils/__init__.py

# Reiniciar scheduler
docker-compose restart airflow-scheduler
```

---

## Checklist de Validación Completa

Antes de considerar el taller listo para uso:

### ✅ Validaciones de Código
- [ ] Todos los DAGs pasan validación de sintaxis
- [ ] Todos los DAGs se pueden importar sin errores
- [ ] Tests unitarios de utilidades pasan
- [ ] No hay errores de linting críticos

### ✅ Validaciones de Infraestructura
- [ ] Docker Compose inicia todos los servicios
- [ ] Postgres está accesible y tiene los schemas
- [ ] Redis está corriendo
- [ ] Airflow webserver responde en puerto 8080
- [ ] Airflow scheduler está procesando DAGs

### ✅ Validaciones de DAGs
- [ ] Todos los DAGs aparecen en la UI
- [ ] DAG 01 se ejecuta exitosamente
- [ ] DAG 02 se ejecuta exitosamente
- [ ] DAG 03 se ejecuta exitosamente
- [ ] DAG 04 sensores funcionan correctamente
- [ ] DAG 05 procesa particiones correctamente

### ✅ Validaciones de Datos
- [ ] Script de generación de datos funciona
- [ ] Datos se cargan a raw layer
- [ ] Transformaciones producen datos en processed layer
- [ ] Métricas se calculan en analytics layer
- [ ] Auditoría registra ejecuciones

### ✅ Validaciones de Documentación
- [ ] README.md tiene instrucciones claras
- [ ] Cada DAG tiene documentación inline
- [ ] Ejemplos de uso están documentados
- [ ] Troubleshooting común está documentado

---

## Comandos Útiles para Testing

```bash
# Ver logs en tiempo real
docker-compose logs -f airflow-scheduler

# Ejecutar comando en el contenedor
docker-compose exec airflow-webserver bash

# Listar DAGs
docker-compose exec airflow-webserver airflow dags list

# Ver tareas de un DAG
docker-compose exec airflow-webserver airflow tasks list 01_dag_basico_ingesta

# Probar una tarea específica
docker-compose exec airflow-webserver airflow tasks test 01_dag_basico_ingesta load_transactions 2024-01-01

# Ver estado de las conexiones
docker-compose exec airflow-webserver airflow connections list

# Ver variables
docker-compose exec airflow-webserver airflow variables list

# Limpiar metadata de un DAG
docker-compose exec airflow-webserver airflow dags delete 01_dag_basico_ingesta

# Pausar/despausar DAG
docker-compose exec airflow-webserver airflow dags pause 01_dag_basico_ingesta
docker-compose exec airflow-webserver airflow dags unpause 01_dag_basico_ingesta
```

---

## Próximos Pasos

Una vez que todas las validaciones pasen:

1. ✅ Continuar con la implementación de DAGs avanzados (06-08)
2. ✅ Crear documentación de referencia
3. ✅ Crear ejercicios prácticos
4. ✅ Validación final del taller completo

---

**Nota:** Este documento se actualizará a medida que se implementen más componentes del taller.
