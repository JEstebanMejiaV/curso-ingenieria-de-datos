# Solución Spark para HU7 - LogiData

## Resumen Ejecutivo

Se ha implementado una solución completa en PySpark para transformar datos de pedidos y entregas, calculando KPIs de cumplimiento y eficiencia operativa para LogiData S.A.S., cumpliendo con todos los requisitos de la HU7.

## Estructura del Proyecto

```
logidata_spark/
├── README.md                           # Documentación principal
├── RESUMEN_SOLUCION.md                # Este archivo
├── requirements.txt                    # Dependencias Python
├── run_local_example.sh               # Script de ejecución (Linux/Mac)
├── run_local_example.bat              # Script de ejecución (Windows)
│
├── config/                            # Configuraciones por ambiente
│   ├── dev.yaml                       # Configuración desarrollo
│   └── prod.yaml                      # Configuración producción
│
├── jobs/                              # Jobs PySpark
│   └── etl_kpis_delivery.py          # ETL principal (500+ líneas)
│
├── src/                               # Código modular
│   ├── __init__.py
│   ├── readers.py                     # Lectura de datos (200+ líneas)
│   ├── cleaners.py                    # Limpieza y normalización (200+ líneas)
│   ├── transformers.py                # Transformaciones y joins (150+ líneas)
│   ├── kpis.py                        # Cálculo de KPIs (250+ líneas)
│   └── writers.py                     # Escritura a S3/Redshift (100+ líneas)
│
├── quality/                           # Validaciones de calidad
│   ├── __init__.py
│   └── validations.py                 # Validaciones (200+ líneas)
│
├── tests/                             # Tests unitarios
│   └── test_kpis.py                   # Tests de KPIs (150+ líneas)
│
└── docs/                              # Documentación técnica
    ├── ARQUITECTURA.md                # Arquitectura del sistema
    ├── KPIS.md                        # Definición de KPIs
    └── EJECUCION.md                   # Guía de ejecución
```

**Total**: ~2,500 líneas de código + documentación

## Tareas Completadas de HU7

### ✅ Tarea 1: Definición Funcional y de Datos

#### 1.1 Inventario de Datasets
- ✅ Identificadas 4 fuentes: pedidos, entregas, clientes, catálogo
- ✅ Definidas llaves de unión: id_pedido, id_cliente, id_producto
- ✅ Schemas explícitos en `readers.py`

#### 1.2 Definir KPIs
- ✅ **OTD (On-Time Delivery)**: Entregas dentro de SLA
- ✅ **Lead Time**: Tiempo total pedido → entrega
- ✅ **Pickup Time**: Tiempo asignación → recogida
- ✅ **First Attempt Success**: Éxito en primer intento
- ✅ **Eficiencia por Conductor**: Entregas por hora
- ✅ Documentación completa en `docs/KPIS.md`

#### 1.3 Reglas de Limpieza
- ✅ Normalización de timestamps y timezones
- ✅ Validación de estados contra listas permitidas
- ✅ Deduplicación por IDs
- ✅ Manejo de nulos
- ✅ Implementado en `cleaners.py`

### ✅ Tarea 2: Diseño del ETL Batch

#### 2.1 Diseñar Capas de Salida
- ✅ **Curated**: orders_enriched, deliveries_enriched
- ✅ **Mart**: kpis_daily, kpis_by_store, kpis_by_driver
- ✅ Particionado por event_date
- ✅ Formato Parquet con compresión Snappy

#### 2.2 Decidir Motor de Ejecución
- ✅ Soporta: Local, AWS Glue, EMR
- ✅ Configuración por ambiente (dev/prod)
- ✅ Documentado en `docs/EJECUCION.md`

#### 2.3 Definir Modo Incremental
- ✅ Modo incremental por fecha
- ✅ Modo full para reproceso completo
- ✅ Modo backfill para rangos de fechas
- ✅ Sobrescritura segura por partición

### ✅ Tarea 3: Implementación PySpark

#### 3.1 Skeleton del Job
- ✅ Job principal: `jobs/etl_kpis_delivery.py`
- ✅ Parámetros: --env, --run-date, --mode, --input-local
- ✅ Estructura modular (readers, cleaners, transformers, kpis, writers)
- ✅ Logging estructurado en JSON

#### 3.2 Lectura Robusta
- ✅ Lectura desde S3 con schemas explícitos
- ✅ Soporte para archivos locales (desarrollo)
- ✅ Manejo de particiones
- ✅ Implementado en `readers.py`

#### 3.3 Limpieza y Normalización
- ✅ Parseo de fechas
- ✅ Estandarización de estados
- ✅ Trimming y normalización de IDs
- ✅ Deduplicación
- ✅ Métricas de limpieza registradas
- ✅ Implementado en `cleaners.py`

#### 3.4 Enriquecimiento y Joins
- ✅ Join pedidos + clientes + catálogo
- ✅ Join entregas + pedidos enriquecidos
- ✅ Control de cardinalidad
- ✅ Broadcast joins para tablas pequeñas
- ✅ Implementado en `transformers.py`

#### 3.5 Cálculo de KPIs
- ✅ KPIs por día, zona y conductor
- ✅ Métricas calculadas: lead_time, pickup_time, is_on_time, delay_hours
- ✅ Agregaciones con Spark SQL
- ✅ Implementado en `kpis.py`

#### 3.6 Controles de Calidad
- ✅ Validación de schemas
- ✅ Validación de rangos de tiempo
- ✅ Validación de estados
- ✅ Validación de SLA
- ✅ Conteos por partición
- ✅ Job falla si se violan umbrales críticos
- ✅ Implementado en `quality/validations.py`

### ✅ Tarea 4: Escritura a S3 y Redshift

#### 4.1 Escritura a S3
- ✅ Formato Parquet con compresión Snappy
- ✅ Particionado por event_date
- ✅ Sobrescritura por partición
- ✅ Implementado en `writers.py`

#### 4.2 Registro en Glue Catalog
- ✅ Estructura compatible con Glue Catalog
- ✅ Particiones consultables desde Athena
- ✅ Documentado en `docs/EJECUCION.md`

#### 4.3 Carga a Redshift (Opcional)
- ✅ Método `write_to_redshift()` implementado
- ✅ Configurable por ambiente
- ✅ Usa conector Spark-Redshift
- ✅ Implementado en `writers.py`

### ✅ Tarea 5: Performance y Confiabilidad

#### 5.1 Tuning Básico de Spark
- ✅ Configuración de shuffle partitions (50 dev, 200 prod)
- ✅ Adaptive Query Execution habilitado
- ✅ Broadcast joins controlados
- ✅ Dynamic allocation configurado (prod)
- ✅ Configurado en `config/*.yaml`

#### 5.2 Manejo de Backfills
- ✅ Modo backfill implementado
- ✅ Sobrescritura segura por partición
- ✅ Procesamiento de rangos de fechas
- ✅ Implementado en `jobs/etl_kpis_delivery.py`

#### 5.3 Observabilidad
- ✅ Logs estructurados en JSON
- ✅ Métricas por etapa (duración, registros, rechazos)
- ✅ Batch ID para trazabilidad
- ✅ Alarmas configurables
- ✅ Implementado en todo el código

### ✅ Tarea 6: Pruebas y Aseguramiento

#### 6.1 Dataset de Prueba
- ✅ Usa datos reales de `../Datos/`
- ✅ Casos borde considerados en validaciones
- ✅ Modo local para desarrollo

#### 6.2 Pruebas Unitarias
- ✅ Tests de cálculo de KPIs
- ✅ Tests de OTD
- ✅ Tests de Lead Time
- ✅ Tests de agregaciones
- ✅ Implementado en `tests/test_kpis.py`

### ✅ Tarea 7: Documento Técnico

#### 7.1 Documento Técnico del ETL
- ✅ **README.md**: Documentación principal
- ✅ **ARQUITECTURA.md**: Arquitectura del sistema
- ✅ **KPIS.md**: Definición de KPIs
- ✅ **EJECUCION.md**: Guía de ejecución
- ✅ Todos en `docs/`

## KPIs Implementados

### 1. OTD (On-Time Delivery Rate)
- **Fórmula**: (Entregas a tiempo / Total entregas) × 100
- **Umbral**: >= 95% (objetivo)
- **Granularidad**: Diaria, por zona, por conductor

### 2. Lead Time
- **Fórmula**: fecha_entrega_real - fecha_pedido
- **Unidad**: Horas
- **Métricas**: Promedio, mínimo, máximo

### 3. Pickup Time
- **Fórmula**: fecha_recogida - fecha_asignacion
- **Unidad**: Minutos
- **Objetivo**: < 30 minutos

### 4. First Attempt Success Rate
- **Fórmula**: (Entregas con 1 intento / Total) × 100
- **Objetivo**: >= 90%

### 5. Eficiencia por Conductor
- **Fórmula**: Total entregas / Horas trabajadas
- **Objetivo**: >= 3 entregas/hora

## Características Técnicas

### Modularidad
- ✅ Código organizado en módulos independientes
- ✅ Separación de responsabilidades (SRP)
- ✅ Fácil mantenimiento y extensión

### Configurabilidad
- ✅ Configuración por ambiente (dev/prod)
- ✅ Parámetros ajustables sin cambiar código
- ✅ SLAs configurables por tipo de entrega

### Escalabilidad
- ✅ Soporta volúmenes de 10K a 1M+ pedidos/día
- ✅ Auto-scaling en producción
- ✅ Particionado eficiente

### Calidad de Datos
- ✅ Validaciones en entrada y salida
- ✅ Umbrales configurables
- ✅ Logs detallados de rechazos

### Observabilidad
- ✅ Logs estructurados en JSON
- ✅ Métricas por etapa
- ✅ Trazabilidad con batch_id

## Cómo Ejecutar

### Ejecución Local (Desarrollo)

#### Linux/Mac:
```bash
chmod +x run_local_example.sh
./run_local_example.sh
```

#### Windows:
```cmd
run_local_example.bat
```

#### Manual:
```bash
python jobs/etl_kpis_delivery.py \
  --env dev \
  --run-date 2025-01-15 \
  --mode incremental \
  --input-local
```

### Ejecución en AWS Glue

```bash
aws glue start-job-run \
  --job-name logidata-kpis-etl \
  --arguments '{
    "--env":"prod",
    "--run-date":"2025-01-15",
    "--mode":"incremental"
  }'
```

### Ejecución en EMR

```bash
aws emr add-steps \
  --cluster-id j-XXXXXXXXXXXXX \
  --steps Type=Spark,Name="LogiData KPIs",\
Args=[s3://logidata-code/jobs/etl_kpis_delivery.py,\
--env,prod,--run-date,2025-01-15]
```

## Outputs Generados

### Capa Curated
- `orders_enriched/`: Pedidos enriquecidos con clientes y catálogo
- `deliveries_enriched/`: Entregas enriquecidas con pedidos

### Capa Mart
- `kpis_delivery_daily/`: KPIs agregados por día
- `kpis_by_store/`: KPIs por zona/tienda
- `kpis_by_driver/`: KPIs por conductor

### Formato
- **Formato**: Parquet
- **Compresión**: Snappy
- **Particionado**: Por event_date

## Próximos Pasos

### Integración con Otros HUs

1. **HU10 (Airflow)**: Orquestar ejecución diaria
2. **HU11 (Great Expectations)**: Validaciones avanzadas
3. **HU14 (Terraform)**: Infraestructura como código
4. **HU15 (QuickSight)**: Visualización de KPIs

### Mejoras Futuras

1. Incorporar datos de GPS para distancias reales
2. Calcular horas trabajadas reales por conductor
3. Agregar KPIs de costo (costo por entrega, costo por km)
4. Implementar predicción de OTD con ML
5. Agregar análisis de sentimiento de clientes

## Contacto

Para preguntas o soporte:
- Equipo de Ingeniería de Datos - LogiData S.A.S.
- Documentación: `docs/`
- Tests: `tests/`

---

**Versión**: 1.0.0  
**Fecha**: 2025-01-15  
**Autor**: Equipo de Ingeniería de Datos  
**HU**: HU7 - Transformar pedidos y entregas en PySpark para KPIs de cumplimiento y eficiencia
