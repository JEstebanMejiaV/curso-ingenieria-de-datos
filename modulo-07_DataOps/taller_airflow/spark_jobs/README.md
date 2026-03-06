# Spark Jobs - Taller de Apache Airflow

Este directorio contiene jobs de Apache Spark que son orquestados por Airflow para realizar procesamiento de datos a gran escala.

## Contenido

- `aggregate_sales.py`: Job principal de agregaciones de ventas
- `test_aggregate_sales.py`: Tests unitarios para el job de agregaciones

## Job: aggregate_sales.py

### Descripción

Job Spark que lee datos de transacciones desde PostgreSQL, realiza agregaciones complejas usando Spark SQL y DataFrames, y escribe los resultados de vuelta a PostgreSQL.

### Funcionalidades

El job calcula tres tipos de métricas:

1. **Métricas Diarias de Ventas** (`daily_sales_metrics`)
   - Total de transacciones por día
   - Revenue total por día
   - Valor promedio de transacción
   - Número de clientes únicos
   - Categoría más vendida del día

2. **Métricas por Cliente** (`customer_metrics`)
   - Número de transacciones por cliente
   - Total gastado por cliente
   - Valor promedio de orden
   - Días desde última compra
   - Frecuencia de compra (días entre compras)

3. **Performance por Categoría** (`category_performance`)
   - Revenue por categoría
   - Número de transacciones por categoría
   - Ticket promedio por categoría
   - Cantidad de productos vendidos
   - Porcentaje del revenue total

### Uso

#### Ejecución Local (sin Airflow)

```bash
# Ejecutar con todos los datos y todas las métricas
spark-submit \
    --master local[*] \
    --packages org.postgresql:postgresql:42.6.0 \
    spark_jobs/aggregate_sales.py

# Ejecutar para una fecha específica
spark-submit \
    --master local[*] \
    --packages org.postgresql:postgresql:42.6.0 \
    spark_jobs/aggregate_sales.py \
    --input-date 2024-01-15

# Calcular solo métricas diarias
spark-submit \
    --master local[*] \
    --packages org.postgresql:postgresql:42.6.0 \
    spark_jobs/aggregate_sales.py \
    --metrics daily

# Calcular solo métricas por cliente
spark-submit \
    --master local[*] \
    --packages org.postgresql:postgresql:42.6.0 \
    spark_jobs/aggregate_sales.py \
    --metrics customer
```

#### Ejecución desde Airflow

El job está diseñado para ser llamado desde el DAG `06_dag_spark_integration.py`:

```python
from airflow.operators.bash import BashOperator

submit_spark_job = BashOperator(
    task_id='submit_spark_job',
    bash_command="""
    spark-submit \
        --master local[*] \
        --packages org.postgresql:postgresql:42.6.0 \
        /opt/airflow/spark_jobs/aggregate_sales.py \
        --input-date {{ ds }}
    """
)
```

### Argumentos de Línea de Comandos

- `--input-date`: Fecha de entrada en formato YYYY-MM-DD (opcional)
  - Si se especifica, procesa solo datos de esa fecha
  - Si se omite, procesa todos los datos disponibles

- `--metrics`: Tipo de métricas a calcular (default: all)
  - `all`: Calcula todas las métricas
  - `daily`: Solo métricas diarias
  - `customer`: Solo métricas por cliente
  - `category`: Solo métricas por categoría

### Requisitos

#### Dependencias Python

```
pyspark==3.5.0
```

#### Driver JDBC

El job requiere el driver JDBC de PostgreSQL. Se descarga automáticamente usando:

```
--packages org.postgresql:postgresql:42.6.0
```

#### Configuración de Base de Datos

El job se conecta a PostgreSQL usando las siguientes credenciales (configuradas en `.env`):

- Host: `postgres`
- Puerto: `5432`
- Base de datos: `airflow`
- Usuario: `airflow`
- Password: `airflow`

### Tablas de Entrada

El job lee datos de:

- `processed.transactions_clean`: Transacciones limpias y enriquecidas

### Tablas de Salida

El job escribe resultados a:

- `analytics.daily_sales_metrics`: Métricas diarias agregadas
- `analytics.customer_metrics`: Métricas por cliente
- `analytics.category_performance`: Performance por categoría

### Optimizaciones

El job incluye varias optimizaciones de Spark:

1. **Adaptive Query Execution**: Habilitado para optimizar planes de ejecución dinámicamente
2. **Coalesce Partitions**: Reduce particiones automáticamente para mejorar performance
3. **Caching**: Cachea el DataFrame de transacciones para reutilización
4. **Window Functions**: Usa funciones de ventana para cálculos eficientes
5. **Batch Inserts**: Escribe a PostgreSQL en lotes para mejor throughput

## Testing

### Ejecutar Tests

```bash
# Instalar pytest si no está instalado
pip install pytest

# Ejecutar todos los tests
pytest spark_jobs/test_aggregate_sales.py -v

# Ejecutar un test específico
pytest spark_jobs/test_aggregate_sales.py::test_daily_sales_metrics_calculation -v
```

### Cobertura de Tests

Los tests cubren:

- ✓ Cálculo de métricas diarias
- ✓ Filtrado por fecha específica
- ✓ Cálculo de métricas por cliente
- ✓ Cálculo de performance por categoría
- ✓ Manejo de DataFrames vacíos

## Troubleshooting

### Error: "No suitable driver found"

**Problema**: Spark no puede encontrar el driver JDBC de PostgreSQL.

**Solución**: Asegúrate de incluir el package en spark-submit:

```bash
--packages org.postgresql:postgresql:42.6.0
```

### Error: "Connection refused"

**Problema**: No se puede conectar a PostgreSQL.

**Solución**: 
1. Verifica que el contenedor de Postgres esté corriendo: `docker ps`
2. Verifica las credenciales en `.env`
3. Si ejecutas fuera de Docker, cambia el host de `postgres` a `localhost`

### Performance Lento

**Problema**: El job tarda mucho en ejecutarse.

**Solución**:
1. Aumenta el número de cores: `--master local[4]`
2. Aumenta la memoria: `--driver-memory 4g --executor-memory 4g`
3. Ajusta el número de particiones: `--conf spark.sql.shuffle.partitions=8`

### Out of Memory

**Problema**: El job falla con errores de memoria.

**Solución**:
1. Aumenta la memoria del driver: `--driver-memory 4g`
2. Procesa datos por fecha en lugar de todos a la vez
3. Reduce el número de particiones si los datos son pequeños

## Mejores Prácticas

1. **Procesamiento Incremental**: Usa `--input-date` para procesar datos por fecha en lugar de reprocesar todo
2. **Monitoreo**: Revisa los logs de Spark para identificar cuellos de botella
3. **Particionamiento**: Para datasets grandes, considera particionar las tablas de salida por fecha
4. **Idempotencia**: El job usa `mode='append'` para métricas diarias/cliente, asegúrate de limpiar datos duplicados si re-ejecutas

## Extensiones Futuras

Ideas para extender el job:

- [ ] Agregar métricas de RFM (Recency, Frequency, Monetary)
- [ ] Implementar detección de anomalías en ventas
- [ ] Agregar análisis de cohortes de clientes
- [ ] Implementar predicción de churn usando ML
- [ ] Agregar análisis de canasta de mercado (market basket analysis)

## Referencias

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [PySpark SQL Functions](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html)
- [Spark JDBC Documentation](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html)
