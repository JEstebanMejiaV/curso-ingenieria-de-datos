# Arquitectura del ETL - LogiData Spark

## Visión General

El ETL de KPIs de LogiData es una solución PySpark modular diseñada para transformar datos transaccionales de pedidos y entregas en métricas de negocio accionables.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         FUENTES DE DATOS                         │
├─────────────────────────────────────────────────────────────────┤
│  S3 Raw Zone                                                     │
│  ├── pedidos/event_date=YYYY-MM-DD/                            │
│  ├── entregas/event_date=YYYY-MM-DD/                           │
│  ├── clientes/                                                  │
│  └── catalogo/                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ETL PYSPARK (HU7)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Readers    │→ │   Cleaners   │→ │ Transformers │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                              │                                   │
│                              ▼                                   │
│                    ┌──────────────┐                             │
│                    │ KPI Calculator│                             │
│                    └──────────────┘                             │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Validators  │← │   Writers    │← │  Aggregators │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPAS DE SALIDA                             │
├─────────────────────────────────────────────────────────────────┤
│  S3 Curated Zone                                                 │
│  ├── orders_enriched/event_date=YYYY-MM-DD/                    │
│  └── deliveries_enriched/event_date=YYYY-MM-DD/                │
│                                                                  │
│  S3 Mart Zone                                                    │
│  ├── kpis_delivery_daily/event_date=YYYY-MM-DD/                │
│  ├── kpis_by_store/event_date=YYYY-MM-DD/                      │
│  └── kpis_by_driver/event_date=YYYY-MM-DD/                     │
│                                                                  │
│  Redshift (Opcional)                                             │
│  └── mart.kpis_delivery_daily                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. Readers (src/readers.py)

**Responsabilidad**: Lectura de datos desde S3 o archivos locales

**Funciones**:
- `read_orders()`: Lee pedidos con schema definido
- `read_deliveries()`: Lee entregas con schema definido
- `read_customers()`: Lee clientes (tabla maestra)
- `read_catalog()`: Lee catálogo de productos (tabla maestra)

**Características**:
- Schemas explícitos para validación temprana
- Soporte para lectura incremental (por partición)
- Soporte para lectura full (todo el histórico)
- Modo local para desarrollo

**Ejemplo**:
```python
reader = DataReader(spark, config, use_local=False)
df_orders = reader.read_orders(run_date="2025-01-15", mode="incremental")
```

---

### 2. Cleaners (src/cleaners.py)

**Responsabilidad**: Limpieza y normalización de datos

**Funciones**:
- `clean_orders()`: Limpia pedidos
- `clean_deliveries()`: Limpia entregas
- `clean_customers()`: Limpia clientes
- `clean_catalog()`: Limpia catálogo

**Operaciones**:
- Trimming de strings
- Normalización de mayúsculas/minúsculas
- Validación de estados contra listas permitidas
- Deduplicación por ID
- Filtrado de registros con IDs nulos
- Validación de coherencia temporal
- Cálculo de campos derivados (ej: monto_total)

**Ejemplo**:
```python
cleaner = DataCleaner(config)
df_orders_clean = cleaner.clean_orders(df_orders)
```

---

### 3. Transformers (src/transformers.py)

**Responsabilidad**: Enriquecimiento y transformaciones complejas

**Funciones**:
- `enrich_orders()`: Enriquece pedidos con clientes y catálogo
- `enrich_deliveries()`: Enriquece entregas con pedidos

**Operaciones**:
- Joins con tablas maestras
- Broadcast joins para tablas pequeñas
- Validación de cardinalidad (evitar multiplicación)
- Detección de registros huérfanos
- Selección y renombrado de columnas

**Ejemplo**:
```python
transformer = DataTransformer(config)
df_orders_enriched = transformer.enrich_orders(
    df_orders_clean, df_customers_clean, df_catalog_clean
)
```

---

### 4. KPI Calculator (src/kpis.py)

**Responsabilidad**: Cálculo de KPIs de negocio

**Funciones**:
- `calculate_daily_kpis()`: KPIs agregados por día
- `calculate_kpis_by_store()`: KPIs por zona/tienda
- `calculate_kpis_by_driver()`: KPIs por conductor
- `_add_calculated_metrics()`: Agrega métricas calculadas

**KPIs Calculados**:
- **OTD Rate**: Tasa de entregas a tiempo
- **Lead Time**: Tiempo total de pedido a entrega
- **Pickup Time**: Tiempo de asignación a recogida
- **First Attempt Rate**: Tasa de éxito en primer intento
- **Deliveries per Hour**: Eficiencia por conductor

**Ejemplo**:
```python
calculator = KPICalculator(config)
df_kpis_daily = calculator.calculate_daily_kpis(df_deliveries_enriched)
```

---

### 5. Writers (src/writers.py)

**Responsabilidad**: Escritura de resultados a destinos

**Funciones**:
- `write_curated()`: Escribe a capa curated
- `write_mart()`: Escribe a capa mart
- `write_to_redshift()`: Escribe a Redshift (opcional)

**Características**:
- Particionado por event_date
- Formato Parquet con compresión Snappy
- Modo overwrite por partición
- Soporte para escritura local (desarrollo)

**Ejemplo**:
```python
writer = DataWriter(spark, config, use_local=False)
writer.write_mart(df_kpis_daily, "kpis_daily", run_date)
```

---

### 6. Validators (quality/validations.py)

**Responsabilidad**: Validaciones de calidad de datos

**Funciones**:
- `validate_schema()`: Valida schema esperado
- `validate_data_quality()`: Valida calidad (nulos, duplicados)
- `validate_kpis()`: Valida rangos de KPIs

**Validaciones**:
- Existencia de columnas críticas
- Tasa de nulos < umbral configurado
- Tasa de duplicados < umbral configurado
- KPIs en rangos esperados (0-1 para tasas)
- Lead time no negativo
- OTD por encima de umbral mínimo

**Ejemplo**:
```python
validator = DataValidator(config)
validator.validate_data_quality(df_orders, "orders")
validator.validate_kpis(df_kpis_daily)
```

---

## Flujo de Datos

### Etapa 1: Lectura (Read)

```
S3 Raw → Readers → DataFrames con schema
```

**Inputs**:
- `s3://logidata-raw/pedidos/event_date=2025-01-15/`
- `s3://logidata-raw/entregas/event_date=2025-01-15/`
- `s3://logidata-raw/clientes/`
- `s3://logidata-raw/catalogo/`

**Outputs**:
- `df_pedidos` (DataFrame)
- `df_entregas` (DataFrame)
- `df_clientes` (DataFrame)
- `df_catalogo` (DataFrame)

---

### Etapa 2: Validación de Entrada (Validate Input)

```
DataFrames → Validators → Validación OK / Error
```

**Validaciones**:
- Schema correcto
- Columnas críticas presentes
- Tasa de nulos aceptable

---

### Etapa 3: Limpieza (Clean)

```
DataFrames → Cleaners → DataFrames limpios
```

**Operaciones**:
- Normalización de strings
- Validación de estados
- Deduplicación
- Filtrado de nulos
- Cálculo de campos derivados

---

### Etapa 4: Enriquecimiento (Transform)

```
DataFrames limpios → Transformers → DataFrames enriquecidos
```

**Operaciones**:
- Join pedidos + clientes + catálogo
- Join entregas + pedidos enriquecidos
- Validación de cardinalidad

---

### Etapa 5: Cálculo de KPIs (Calculate)

```
DataFrames enriquecidos → KPI Calculator → DataFrames de KPIs
```

**Operaciones**:
- Agregar métricas calculadas (lead_time, is_on_time, etc.)
- Agregaciones por dimensiones (día, zona, conductor)
- Cálculo de tasas y promedios

---

### Etapa 6: Validación de Salida (Validate Output)

```
DataFrames de KPIs → Validators → Validación OK / Error
```

**Validaciones**:
- KPIs en rangos esperados
- No hay valores negativos
- OTD por encima de umbral

---

### Etapa 7: Escritura (Write)

```
DataFrames validados → Writers → S3 Curated/Mart
```

**Outputs**:
- `s3://logidata-curated/orders_enriched/event_date=2025-01-15/`
- `s3://logidata-curated/deliveries_enriched/event_date=2025-01-15/`
- `s3://logidata-mart/kpis_delivery_daily/event_date=2025-01-15/`
- `s3://logidata-mart/kpis_by_store/event_date=2025-01-15/`
- `s3://logidata-mart/kpis_by_driver/event_date=2025-01-15/`

---

## Configuración

### Archivos de Configuración

```
config/
├── dev.yaml    # Configuración de desarrollo
└── prod.yaml   # Configuración de producción
```

### Parámetros Clave

| Parámetro | Descripción | Dev | Prod |
|-----------|-------------|-----|------|
| `spark.sql.shuffle.partitions` | Particiones para shuffle | 50 | 200 |
| `max_null_rate` | Tasa máxima de nulos | 5% | 2% |
| `min_otd_threshold` | OTD mínimo esperado | 70% | 85% |
| `enable_broadcast_join` | Habilitar broadcast | true | true |

---

## Modos de Ejecución

### Incremental (Recomendado)

```python
etl = ETLKPIsDelivery(
    env="prod",
    run_date="2025-01-15",
    mode="incremental"
)
```

**Características**:
- Procesa solo la fecha especificada
- Lee partición específica de S3
- Sobrescribe solo esa partición en salida

---

### Full

```python
etl = ETLKPIsDelivery(
    env="prod",
    run_date="2025-01-15",
    mode="full"
)
```

**Características**:
- Procesa todo el histórico
- Lee todas las particiones
- Sobrescribe todas las particiones en salida

---

### Backfill

```bash
python jobs/etl_kpis_delivery.py \
  --env prod \
  --mode backfill \
  --start-date 2025-01-01 \
  --end-date 2025-01-15
```

**Características**:
- Procesa rango de fechas
- Ejecuta incremental por cada fecha
- Útil para recuperar datos faltantes

---

## Optimizaciones de Performance

### 1. Broadcast Joins

```python
# Tablas pequeñas (clientes, catálogo) se hacen broadcast
df_enriched = df_orders.join(
    broadcast(df_customers),
    on="id_cliente"
)
```

**Beneficio**: Evita shuffle costoso para tablas pequeñas

---

### 2. Particionado

```python
# Escritura particionada por fecha
df.write.partitionBy("event_date").parquet(path)
```

**Beneficio**: Lectura incremental más rápida

---

### 3. Cache

```python
# Cache de DataFrames reutilizados
df_orders_enriched.cache()
```

**Beneficio**: Evita recalcular transformaciones

---

### 4. Adaptive Query Execution (AQE)

```yaml
spark.sql.adaptive.enabled: true
spark.sql.adaptive.coalescePartitions.enabled: true
spark.sql.adaptive.skewJoin.enabled: true
```

**Beneficio**: Spark optimiza automáticamente en runtime

---

## Monitoreo y Observabilidad

### Logs Estructurados

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "batch_id": "2025-01-15_20250115103000",
  "stage": "read",
  "metrics": {
    "pedidos_count": 1500,
    "entregas_count": 1450,
    "duration_seconds": 12.5
  }
}
```

### Métricas Clave

- `records_read`: Registros leídos por fuente
- `records_written`: Registros escritos
- `records_rejected`: Registros rechazados
- `duration_seconds`: Duración por etapa
- `otd_rate`: Tasa OTD calculada
- `avg_lead_time_hours`: Lead time promedio

---

## Escalabilidad

### Dimensionamiento

| Volumen Diario | Executors | Cores | Memory | Tiempo Estimado |
|----------------|-----------|-------|--------|-----------------|
| < 10K pedidos  | 2         | 4     | 8GB    | 5-10 min        |
| 10K-100K       | 5         | 4     | 8GB    | 10-20 min       |
| 100K-1M        | 10        | 4     | 16GB   | 20-40 min       |
| > 1M           | 20        | 8     | 16GB   | 40-60 min       |

### Auto-scaling

```yaml
spark.dynamicAllocation.enabled: true
spark.dynamicAllocation.minExecutors: 2
spark.dynamicAllocation.maxExecutors: 20
```

---

## Seguridad

### Cifrado

- **En tránsito**: TLS para S3
- **En reposo**: SSE-KMS para S3

### Control de Acceso

- **IAM Roles**: Permisos mínimos necesarios
- **S3 Bucket Policies**: Acceso restringido por rol
- **Glue Data Catalog**: Permisos por tabla

---

## Próximos Pasos

1. **Integración con Airflow** (HU10): Orquestación automática
2. **Great Expectations** (HU11): Validaciones avanzadas
3. **CloudWatch Dashboards**: Monitoreo en tiempo real
4. **QuickSight** (HU15): Visualización de KPIs
5. **Terraform** (HU14): Infraestructura como código
