# LogiData - Solución Spark para HU7

## Descripción General

Solución PySpark para transformar datos de pedidos y entregas, calculando KPIs de cumplimiento y eficiencia operativa para LogiData S.A.S.

## Estructura del Proyecto

```
logidata_spark/
├── README.md                    # Este archivo
├── config/                      # Configuraciones por ambiente
│   ├── dev.yaml
│   └── prod.yaml
├── jobs/                        # Jobs PySpark
│   └── etl_kpis_delivery.py    # ETL principal
├── src/                         # Código modular
│   ├── __init__.py
│   ├── readers.py              # Lectura de datos
│   ├── cleaners.py             # Limpieza y normalización
│   ├── transformers.py         # Transformaciones y joins
│   ├── kpis.py                 # Cálculo de KPIs
│   └── writers.py              # Escritura a S3/Redshift
├── quality/                     # Validaciones de calidad
│   └── validations.py
├── tests/                       # Tests unitarios
│   └── test_kpis.py
├── data/                        # Datos de prueba (local)
│   └── sample/
└── docs/                        # Documentación técnica
    ├── ARQUITECTURA.md
    ├── KPIS.md
    └── EJECUCION.md
```

## KPIs Implementados

### 1. OTD (On-Time Delivery)
- **Definición**: Porcentaje de entregas realizadas dentro del SLA prometido
- **Fórmula**: `(Entregas a tiempo / Total entregas) * 100`
- **Umbral**: >= 95%

### 2. Lead Time
- **Definición**: Tiempo total desde creación del pedido hasta entrega
- **Fórmula**: `fecha_entrega_real - fecha_pedido`
- **Unidad**: Horas

### 3. Pickup Time
- **Definición**: Tiempo desde asignación hasta recogida
- **Fórmula**: `fecha_recogida - fecha_asignacion`
- **Unidad**: Minutos

### 4. First Attempt Success
- **Definición**: Porcentaje de entregas exitosas en el primer intento
- **Fórmula**: `(Entregas exitosas primer intento / Total entregas) * 100`

### 5. Eficiencia por Conductor
- **Definición**: Entregas promedio por hora por conductor
- **Fórmula**: `Total entregas / Horas trabajadas`

## Requisitos

### Software
- Python 3.8+
- PySpark 3.3+
- AWS CLI (para S3)
- boto3 (para interacción con AWS)

### Dependencias Python
```bash
pip install -r requirements.txt
```

## Configuración

### Variables de Entorno
```bash
export AWS_PROFILE=logidata-dev
export SPARK_ENV=dev
export RUN_DATE=2025-01-15
```

### Archivo de Configuración (config/dev.yaml)
```yaml
input:
  pedidos: s3://logidata-raw/pedidos/
  entregas: s3://logidata-raw/entregas/
  
output:
  curated: s3://logidata-curated/
  mart: s3://logidata-mart/kpis/
  
spark:
  app_name: "LogiData KPIs ETL"
  shuffle_partitions: 200
  
quality:
  max_null_rate: 0.05
  min_otd_threshold: 0.80
```

## Ejecución

### Local (Desarrollo)
```bash
# Con datos de muestra locales
python jobs/etl_kpis_delivery.py \
  --env dev \
  --run-date 2025-01-15 \
  --mode incremental \
  --input-local data/sample/

# Con datos en S3
python jobs/etl_kpis_delivery.py \
  --env dev \
  --run-date 2025-01-15 \
  --mode incremental
```

### AWS Glue
```bash
aws glue start-job-run \
  --job-name logidata-kpis-etl \
  --arguments '{
    "--env":"prod",
    "--run-date":"2025-01-15",
    "--mode":"incremental"
  }'
```

### EMR
```bash
aws emr add-steps \
  --cluster-id j-XXXXXXXXXXXXX \
  --steps Type=Spark,Name="LogiData KPIs",\
ActionOnFailure=CONTINUE,\
Args=[--deploy-mode,cluster,\
--master,yarn,\
--conf,spark.sql.shuffle.partitions=200,\
s3://logidata-code/jobs/etl_kpis_delivery.py,\
--env,prod,\
--run-date,2025-01-15]
```

### Backfill (Reprocesar múltiples fechas)
```bash
# Reprocesar últimos 7 días
python jobs/etl_kpis_delivery.py \
  --env prod \
  --mode backfill \
  --start-date 2025-01-08 \
  --end-date 2025-01-15
```

## Modos de Ejecución

### 1. Incremental (Recomendado)
- Procesa solo la fecha especificada en `--run-date`
- Sobrescribe la partición correspondiente
- Más rápido y eficiente

### 2. Full
- Reprocesa todo el histórico
- Útil para cambios de lógica o correcciones
- Más lento y costoso

### 3. Backfill
- Procesa un rango de fechas
- Útil para recuperar datos faltantes
- Requiere `--start-date` y `--end-date`

## Validaciones de Calidad

El job incluye validaciones automáticas:

1. **Validaciones de entrada**:
   - Existencia de archivos/particiones
   - Schemas esperados
   - Rangos de fechas válidos

2. **Validaciones de transformación**:
   - No duplicación de IDs
   - Coherencia temporal (entrega no antes de pedido)
   - Valores en rangos permitidos

3. **Validaciones de salida**:
   - Conteos por partición
   - KPIs en rangos esperados (0-100% para tasas)
   - Freshness de datos

## Monitoreo y Logs

### Logs Estructurados
Todos los logs se generan en formato JSON con:
- `timestamp`: Marca de tiempo
- `level`: INFO, WARNING, ERROR
- `batch_id`: Identificador único del batch
- `stage`: Etapa del ETL (read, clean, transform, write)
- `metrics`: Contadores y métricas

### Métricas Clave
- `records_read`: Registros leídos por fuente
- `records_written`: Registros escritos
- `records_rejected`: Registros rechazados
- `duration_seconds`: Duración por etapa
- `otd_rate`: Tasa OTD calculada
- `avg_lead_time_hours`: Lead time promedio

## Troubleshooting

### Error: "Partition not found"
- Verificar que existan datos para la fecha especificada
- Revisar el formato de particionado en S3

### Error: "Schema mismatch"
- Verificar que los CSVs tengan las columnas esperadas
- Revisar el diccionario de datos

### Performance lento
- Ajustar `spark.sql.shuffle.partitions`
- Verificar el tamaño de los archivos de entrada
- Considerar usar Parquet en lugar de CSV

## Próximos Pasos

1. Integrar con Airflow (HU10)
2. Agregar validaciones con Great Expectations (HU11)
3. Configurar alertas en CloudWatch
4. Optimizar performance con cache y broadcast joins
5. Implementar carga a Redshift

## Contacto y Soporte

Para preguntas o issues, contactar al equipo de Ingeniería de Datos de LogiData.
