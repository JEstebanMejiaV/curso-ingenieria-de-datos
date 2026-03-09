# Arquitectura del Taller de Apache Airflow

Este documento describe la arquitectura completa del taller de Airflow, incluyendo la infraestructura, el flujo de datos, la integración con el stack DataOps, y cómo todos los componentes trabajan juntos para crear un sistema de orquestación de pipelines de datos robusto y escalable.

---

## 🏛️ Visión General de la Arquitectura

El taller implementa una arquitectura moderna de orquestación de datos basada en Apache Airflow, diseñada para enseñar conceptos de DataOps en un entorno realista. La arquitectura sigue el patrón de capas de datos (raw → processed → analytics) y utiliza contenedores Docker para facilitar el despliegue y la reproducibilidad.

### Principios de Diseño

1. **Separación de Capas**: Datos raw, processed y analytics claramente separados
2. **Idempotencia**: Todas las operaciones pueden ejecutarse múltiples veces con el mismo resultado
3. **Observabilidad**: Logging, auditoría y monitoreo en cada etapa
4. **Escalabilidad**: Arquitectura distribuida con CeleryExecutor
5. **Reproducibilidad**: Todo el entorno en contenedores Docker

---

## 🏗️ Arquitectura de Infraestructura

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUARIO / ESTUDIANTE                        │
│                                                                     │
│  ┌──────────────┐         ┌──────────────┐      ┌──────────────┐  │
│  │   Browser    │         │   Terminal   │      │  IDE/Editor  │  │
│  │ localhost:   │         │   docker-    │      │   DAGs/      │  │
│  │   8080       │         │   compose    │      │   Scripts    │  │
│  └──────┬───────┘         └──────┬───────┘      └──────┬───────┘  │
└─────────┼──────────────────────────┼─────────────────────┼──────────┘
          │                          │                     │
          │                          │                     │
┌─────────▼──────────────────────────▼─────────────────────▼──────────┐
│                      DOCKER COMPOSE NETWORK                         │
│                       (airflow-network)                             │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                   AIRFLOW WEBSERVER                           │ │
│  │  - Puerto: 8080                                               │ │
│  │  - UI Web para monitoreo y gestión                            │ │
│  │  - Visualización de DAGs, logs, métricas                      │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                     │
│  ┌───────────────────────────▼───────────────────────────────────┐ │
│  │                   AIRFLOW SCHEDULER                           │ │
│  │  - Lee DAGs desde /opt/airflow/dags                           │ │
│  │  - Programa ejecuciones basándose en schedule_interval        │ │
│  │  - Gestiona dependencias entre tareas                         │ │
│  │  - Envía tareas al Executor                                   │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                     │
│  ┌───────────────────────────▼───────────────────────────────────┐ │
│  │                   CELERY EXECUTOR                             │ │
│  │  - Distribuye tareas entre workers                            │ │
│  │  - Usa Redis como message broker                              │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                     │
│  ┌───────────────────────────▼───────────────────────────────────┐ │
│  │                      REDIS                                    │ │
│  │  - Puerto: 6379                                               │ │
│  │  - Message broker para Celery                                 │ │
│  │  - Cola de tareas pendientes                                  │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                     │
│         ┌────────────────────┴────────────────────┐               │
│         │                                         │               │
│  ┌──────▼──────────┐                   ┌──────────▼──────────┐   │
│  │ AIRFLOW WORKER  │                   │ AIRFLOW TRIGGERER   │   │
│  │ - Ejecuta       │                   │ - Maneja eventos    │   │
│  │   tareas        │                   │   asíncronos        │   │
│  │ - Accede a      │                   │ - Sensores          │   │
│  │   volúmenes     │                   │   deferibles        │   │
│  └──────┬──────────┘                   └─────────────────────┘   │
│         │                                                         │
│  ┌──────▼──────────────────────────────────────────────────────┐ │
│  │                   POSTGRESQL                                 │ │
│  │  - Puerto: 5432                                              │ │
│  │  - Metadatos de Airflow (dag, dag_run, task_instance, etc.) │ │
│  │  - Datos del taller (raw, processed, analytics, audit)      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                   VOLÚMENES MONTADOS                          │ │
│  │  ./dags       → /opt/airflow/dags                             │ │
│  │  ./data       → /opt/airflow/data                             │ │
│  │  ./logs       → /opt/airflow/logs                             │ │
│  │  ./plugins    → /opt/airflow/plugins                          │ │
│  │  ./scripts    → /opt/airflow/scripts                          │ │
│  │  ./spark_jobs → /opt/airflow/spark_jobs                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

### Descripción de Componentes

**Airflow Webserver**
- Servidor web Flask que proporciona la interfaz de usuario
- Puerto 8080 expuesto al host
- Permite visualizar DAGs, monitorear ejecuciones, ver logs
- Autenticación básica (usuario: airflow, password: airflow)

**Airflow Scheduler**
- Corazón de Airflow, responsable de programar ejecuciones
- Lee archivos Python del directorio `dags/` cada 30 segundos
- Determina qué tareas están listas para ejecutar
- Envía tareas al Executor para su ejecución

**Celery Executor**
- Ejecutor distribuido que permite paralelismo
- Envía tareas a una cola en Redis
- Workers toman tareas de la cola y las ejecutan
- Permite escalar horizontalmente agregando más workers

**Redis**
- Message broker para Celery
- Almacena cola de tareas pendientes
- Ligero y rápido para mensajería
- Puerto 6379 (interno, no expuesto al host)

**Airflow Worker**
- Proceso que ejecuta las tareas
- Puede haber múltiples workers (escalabilidad horizontal)
- Tiene acceso a todos los volúmenes montados
- Ejecuta el código de los Operators

**Airflow Triggerer**
- Componente para manejar tareas asíncronas (deferrable operators)
- Optimiza recursos para sensores de larga duración
- Libera workers mientras espera condiciones externas

**PostgreSQL**
- Base de datos principal del sistema
- Almacena metadatos de Airflow (estado de DAGs, tareas, ejecuciones)
- Almacena datos del taller (capas raw, processed, analytics, audit)
- Puerto 5432 expuesto al host para acceso directo

---

## 📊 Arquitectura de Datos

### Modelo de Capas

El taller implementa una arquitectura de datos en capas, siguiendo mejores prácticas de ingeniería de datos:

```
┌─────────────────────────────────────────────────────────────────┐
│                        FUENTES DE DATOS                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ transactions │  │   products   │  │   customers  │          │
│  │    .csv      │  │     .csv     │  │     .csv     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │    DAG 01: Ingesta Básica          │
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RAW LAYER                                │
│  Schema: raw                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │     raw.     │  │     raw.     │  │     raw.     │          │
│  │ transactions │  │   products   │  │   customers  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                 │
│  Datos sin procesar, tal como llegan de las fuentes            │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │    DAG 02: Transformaciones        │
          │    DAG 03: Validación de Calidad   │
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESSED LAYER                             │
│  Schema: processed                                              │
│  ┌──────────────────────────────────────────────┐               │
│  │      processed.transactions_clean            │               │
│  │  - Datos limpios                             │               │
│  │  - Enriquecidos con info de productos        │               │
│  │  - Validados (sin nulos, rangos correctos)   │               │
│  └──────────────────┬───────────────────────────┘               │
│                     │                                           │
│  Datos limpios, transformados y validados                       │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      │    DAG 02: Agregaciones
                      │    DAG 06: Spark Jobs
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ANALYTICS LAYER                             │
│  Schema: analytics                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │  daily_sales_metrics │  │  customer_metrics    │            │
│  │  - Total ventas      │  │  - RFM scores        │            │
│  │  - Transacciones     │  │  - Lifetime value    │            │
│  │  - Top categorías    │  │  - Segmentación      │            │
│  └──────────────────────┘  └──────────────────────┘            │
│                                                                 │
│  Métricas agregadas, KPIs, datos listos para reportes          │
└─────────────────────────────────────────────────────────────────┘

                      ┌───────────────┐
                      │  AUDIT LAYER  │
                      │ Schema: audit │
                      ├───────────────┤
                      │ - Validaciones│
                      │ - Ejecuciones │
                      │ - Logs        │
                      └───────────────┘
```

### Descripción de Capas

**Raw Layer (Capa Cruda)**
- **Propósito**: Almacenar datos tal como llegan de las fuentes
- **Características**:
  - Sin transformaciones
  - Incluye timestamp de carga (`loaded_at`)
  - Permite reprocesamiento desde el origen
  - Idempotente: se puede recargar sin problemas
- **Tablas**: `raw.transactions`, `raw.products`, `raw.customers`

**Processed Layer (Capa Procesada)**
- **Propósito**: Datos limpios, transformados y validados
- **Características**:
  - Datos normalizados y estandarizados
  - Enriquecidos con información de múltiples fuentes
  - Validados (sin nulos, rangos correctos, integridad referencial)
  - Listos para análisis
- **Tablas**: `processed.transactions_clean`

**Analytics Layer (Capa Analítica)**
- **Propósito**: Métricas agregadas y KPIs
- **Características**:
  - Datos pre-agregados para performance
  - Cálculos complejos ya realizados
  - Optimizados para consultas de reportes
  - Particionados por fecha
- **Tablas**: `analytics.daily_sales_metrics`, `analytics.customer_metrics`

**Audit Layer (Capa de Auditoría)**
- **Propósito**: Trazabilidad y observabilidad
- **Características**:
  - Logs de validaciones de calidad
  - Métricas de ejecución de pipelines
  - Historial de errores
  - Información para debugging
- **Tablas**: `audit.data_quality_checks`, `audit.pipeline_executions`

---

## 🔄 Flujo de Datos End-to-End

### Pipeline Completo

```
1. INGESTA (DAG 01)
   ┌─────────────────────────────────────────────────────────┐
   │ check_source_files                                      │
   │   ↓                                                     │
   │ create_raw_tables                                       │
   │   ↓                                                     │
   │ [load_transactions, load_products, load_customers]     │
   │   ↓                                                     │
   │ log_completion                                          │
   └─────────────────────────────────────────────────────────┘
                          ↓
2. TRANSFORMACIÓN (DAG 02)
   ┌─────────────────────────────────────────────────────────┐
   │ extract_raw_data                                        │
   │   ↓                                                     │
   │ clean_transactions                                      │
   │   ↓                                                     │
   │ enrich_with_product_info                                │
   │   ↓                                                     │
   │ [calculate_daily_metrics, calculate_customer_metrics]  │
   │   ↓                                                     │
   │ load_to_processed                                       │
   └─────────────────────────────────────────────────────────┘
                          ↓
3. VALIDACIÓN (DAG 03)
   ┌─────────────────────────────────────────────────────────┐
   │ extract_data                                            │
   │   ↓                                                     │
   │ [validate_nulls, validate_ranges, validate_uniqueness] │
   │   ↓                                                     │
   │ branch_on_quality                                       │
   │   ↓                    ↓                                │
   │ handle_quality_pass   handle_quality_fail              │
   │   ↓                    ↓                                │
   │ log_audit ←────────────┘                                │
   └─────────────────────────────────────────────────────────┘
                          ↓
4. PROCESAMIENTO AVANZADO (DAG 06, 07)
   ┌─────────────────────────────────────────────────────────┐
   │ Spark: Agregaciones complejas                          │
   │ Great Expectations: Validaciones avanzadas              │
   └─────────────────────────────────────────────────────────┘
                          ↓
5. PIPELINE PRODUCCIÓN (DAG 08)
   ┌─────────────────────────────────────────────────────────┐
   │ Pipeline completo con:                                  │
   │ - Manejo de errores                                     │
   │ - Reintentos                                            │
   │ - Alertas                                               │
   │ - SLA monitoring                                        │
   └─────────────────────────────────────────────────────────┘
```

### Flujo Temporal

```
Día 1 (2024-01-01):
  00:00 - Scheduler detecta que DAG 01 debe ejecutarse
  00:01 - DAG 01 ingesta datos del 2024-01-01
  00:05 - DAG 01 completa exitosamente
  00:06 - DAG 02 detecta (via sensor) que DAG 01 completó
  00:07 - DAG 02 transforma datos
  00:12 - DAG 02 completa exitosamente
  00:13 - DAG 03 valida calidad de datos procesados
  00:15 - DAG 03 completa exitosamente
  
Día 2 (2024-01-02):
  00:00 - Proceso se repite para datos del 2024-01-02
  ...
```

---

## 🔗 Integración con Stack DataOps

### Herramientas del Curso Integradas

El taller integra herramientas vistas en módulos anteriores del curso, demostrando cómo Airflow orquesta un stack completo de ingeniería de datos:

```
┌─────────────────────────────────────────────────────────────────┐
│                    STACK DATAOPS COMPLETO                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  MÓDULO 01:     │  ┌──────────────────────────────────────────┐
│  Contenedores   │──│ Docker & Docker Compose                  │
└─────────────────┘  │ - Todo el entorno en contenedores        │
                     │ - Reproducible y portable                │
                     └──────────────────────────────────────────┘

┌─────────────────┐
│  MÓDULO 02:     │  ┌──────────────────────────────────────────┐
│  Bases de Datos │──│ PostgreSQL                               │
└─────────────────┘  │ - Almacenamiento de datos                │
                     │ - Metadatos de Airflow                   │
                     │ - DAGs usan PostgresOperator             │
                     └──────────────────────────────────────────┘

┌─────────────────┐
│  MÓDULO 03:     │  ┌──────────────────────────────────────────┐
│  Spark          │──│ Apache Spark (DAG 06)                    │
└─────────────────┘  │ - Procesamiento distribuido              │
                     │ - Agregaciones complejas                 │
                     │ - Orquestado por Airflow                 │
                     └──────────────────────────────────────────┘

┌─────────────────┐
│  MÓDULO 06:     │  ┌──────────────────────────────────────────┐
│  Calidad Datos  │──│ Great Expectations (DAG 07)              │
└─────────────────┘  │ - Validaciones avanzadas                 │
                     │ - Expectation suites                     │
                     │ - Data docs                              │
                     └──────────────────────────────────────────┘

┌─────────────────┐
│  MÓDULO 07:     │  ┌──────────────────────────────────────────┐
│  DataOps        │──│ Apache Airflow (Este Taller)             │
└─────────────────┘  │ - Orquestación de pipelines              │
                     │ - Monitoreo y alertas                    │
                     │ - Gestión de dependencias                │
                     └──────────────────────────────────────────┘
```

### Rol de Airflow en DataOps

Airflow actúa como el **orquestador central** del stack DataOps, coordinando todas las herramientas y procesos:

**1. Orquestación de Pipelines**
- Coordina la ejecución de múltiples herramientas (Spark, Great Expectations, etc.)
- Gestiona dependencias entre procesos
- Programa ejecuciones basándose en horarios o eventos

**2. Observabilidad**
- Centraliza logs de todas las operaciones
- Proporciona visibilidad del estado de pipelines
- Facilita debugging y troubleshooting

**3. Gestión de Errores**
- Reintentos automáticos en caso de fallos transitorios
- Alertas cuando algo falla
- Recuperación de fallos sin intervención manual

**4. Calidad de Datos**
- Integra validaciones en cada etapa del pipeline
- Detiene procesamiento si la calidad no cumple estándares
- Registra resultados de validaciones para auditoría

**5. Automatización**
- Elimina procesos manuales
- Reduce errores humanos
- Permite escalabilidad

---

## 📈 Diagrama de Arquitectura Completa

### Vista de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CAPA DE PRESENTACIÓN                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Airflow UI      │  │  Dashboards      │  │  Notebooks       │      │
│  │  (Monitoreo)     │  │  (BI Tools)      │  │  (Análisis)      │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE ORQUESTACIÓN                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      APACHE AIRFLOW                               │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │  │
│  │  │ DAG 01  │  │ DAG 02  │  │ DAG 03  │  │   ...   │  │ DAG 08 │ │  │
│  │  │ Ingesta │  │Transform│  │ Calidad │  │         │  │Completo│ │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE PROCESAMIENTO                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Python     │  │ Apache Spark │  │    Great     │                  │
│  │   Scripts    │  │   (DAG 06)   │  │ Expectations │                  │
│  │              │  │              │  │   (DAG 07)   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE ALMACENAMIENTO                             │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        POSTGRESQL                                 │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │  │
│  │  │   Raw   │  │Processed│  │Analytics│  │  Audit  │             │  │
│  │  │  Layer  │  │  Layer  │  │  Layer  │  │  Layer  │             │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    SISTEMA DE ARCHIVOS                            │  │
│  │  ./data/raw/  →  ./data/processed/  →  ./data/analytics/         │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE INFRAESTRUCTURA                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      DOCKER COMPOSE                               │  │
│  │  Webserver | Scheduler | Worker | Triggerer | Postgres | Redis   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Flujo de Datos Detallado

```
FUENTES                 INGESTA              TRANSFORMACIÓN         ANÁLISIS
  │                       │                       │                    │
  │  CSV Files            │  DAG 01               │  DAG 02            │  DAG 06
  │  ┌──────────┐         │  ┌──────────┐         │  ┌──────────┐     │  ┌──────────┐
  ├─→│transactions│───────┼─→│  Load    │────────┼─→│ Clean &  │────┼─→│  Spark   │
  │  │  .csv    │         │  │  to Raw  │         │  │Transform │     │  │  Jobs    │
  │  └──────────┘         │  └──────────┘         │  └──────────┘     │  └──────────┘
  │                       │       ↓               │       ↓            │       ↓
  │  ┌──────────┐         │  ┌──────────┐         │  ┌──────────┐     │  ┌──────────┐
  ├─→│ products │───────┼─→│raw.trans-│────────┼─→│processed.│────┼─→│analytics.│
  │  │  .csv    │         │  │ actions  │         │  │trans_cln │     │  │ metrics  │
  │  └──────────┘         │  └──────────┘         │  └──────────┘     │  └──────────┘
  │                       │       ↓               │       ↓            │
  │  ┌──────────┐         │  ┌──────────┐         │  ┌──────────┐     │
  └─→│customers │───────┼─→│raw.prod- │         │  │  DAG 03  │     │
     │  .csv    │         │  │  ucts    │         │  │ Quality  │     │
     └──────────┘         │  └──────────┘         │  │ Checks   │     │
                          │       ↓               │  └──────────┘     │
                          │  ┌──────────┐         │       ↓            │
                          │  │raw.cust- │         │  ┌──────────┐     │
                          │  │  omers   │         │  │  Audit   │     │
                          │  └──────────┘         │  │  Logs    │     │
                          │                       │  └──────────┘     │
                          │                       │                    │
                       POSTGRES              POSTGRES             POSTGRES
                       Raw Layer          Processed Layer      Analytics Layer
```

---

## 🎯 Caso de Uso: Sistema de Análisis de Ventas E-commerce

### Contexto del Negocio

El taller simula un sistema real de análisis de datos para una plataforma de e-commerce que necesita:

**Requisitos de Negocio**
- Reportes diarios de ventas disponibles antes de las 9 AM
- Análisis de comportamiento de clientes
- Detección de anomalías en transacciones
- Métricas de productos más vendidos
- Segmentación de clientes (RFM)

**Fuentes de Datos**
- Transacciones de ventas (CSV diario)
- Catálogo de productos (CSV actualizado semanalmente)
- Información de clientes (CSV incremental)

**SLAs (Service Level Agreements)**
- Datos disponibles en < 2 horas desde la llegada
- Calidad de datos > 99.5%
- Disponibilidad del sistema > 99%

### Implementación en el Taller

**Pipeline Diario (Ejecución a las 00:00)**

1. **00:00 - Inicio**: Scheduler detecta nueva ejecución
2. **00:01 - Ingesta**: DAG 01 carga archivos CSV a raw layer
3. **00:05 - Transformación**: DAG 02 limpia y enriquece datos
4. **00:10 - Validación**: DAG 03 valida calidad de datos
5. **00:15 - Agregación**: DAG 02 calcula métricas diarias
6. **00:20 - Finalización**: Datos disponibles en analytics layer

**Monitoreo y Alertas**
- Email si algún DAG falla
- Slack notification si SLA se excede
- Dashboard en Airflow UI para monitoreo en tiempo real

**Recuperación de Errores**
- Reintentos automáticos (3 intentos con 5 min de delay)
- Backfill para reprocesar datos históricos
- Logs detallados para debugging

---

## 🔐 Seguridad y Mejores Prácticas

### Seguridad

**Credenciales**
- Almacenadas en variables de entorno (.env)
- Connections de Airflow para sistemas externos
- Fernet key para encriptar secretos

**Acceso**
- Autenticación básica en Airflow UI
- PostgreSQL con usuario/password
- Red Docker aislada

**Datos Sensibles**
- No incluir datos reales de clientes en el taller
- Usar datos sintéticos generados
- Enmascarar información sensible

### Mejores Prácticas Implementadas

**Idempotencia**
- Todas las operaciones pueden ejecutarse múltiples veces
- Uso de `if_exists='replace'` en cargas a DB
- Validación de existencia antes de crear recursos

**Observabilidad**
- Logging en cada tarea
- Tabla de auditoría para validaciones
- Métricas de ejecución registradas

**Escalabilidad**
- CeleryExecutor permite agregar workers
- Procesamiento paralelo de tareas independientes
- Particionamiento de datos por fecha

**Mantenibilidad**
- Código modular en `utils/`
- Documentación inline en DAGs
- Convenciones de nombres claras

---

## 📚 Recursos y Referencias

### Documentación del Taller

- `README.md`: Guía de inicio rápido
- `docs/COMANDOS_UTILES.md`: Referencia de comandos
- `docs/CONCEPTOS_AIRFLOW.md`: Conceptos fundamentales
- `docs/ARQUITECTURA.md`: Este documento

### Archivos Clave

- `docker-compose.yml`: Definición de servicios
- `.env`: Variables de entorno
- `dags/`: Directorio de DAGs
- `scripts/init_db.sql`: Inicialización de base de datos
- `scripts/generate_sample_data.py`: Generador de datos

### Enlaces Externos

- [Documentación Oficial de Airflow](https://airflow.apache.org/docs/)
- [Guía de Mejores Prácticas](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Repositorio GitHub de Airflow](https://github.com/apache/airflow)

---

## 🚀 Próximos Pasos

### Para Estudiantes

1. **Explorar la UI**: Familiarízate con la interfaz web de Airflow
2. **Ejecutar DAGs**: Ejecuta manualmente cada DAG y observa el flujo
3. **Revisar Logs**: Aprende a leer logs para debugging
4. **Modificar DAGs**: Experimenta modificando DAGs existentes
5. **Crear DAGs**: Crea tus propios DAGs desde cero

### Extensiones Posibles

- Integración con servicios cloud (AWS S3, GCP BigQuery)
- Implementación de data lineage
- Integración con herramientas de BI (Tableau, Power BI)
- Implementación de CI/CD para DAGs
- Monitoreo avanzado con Prometheus/Grafana

---

**Última actualización**: Enero 2024  
**Versión de Airflow**: 2.7.3  
**Autor**: Taller de Apache Airflow - Módulo 07 DataOps
