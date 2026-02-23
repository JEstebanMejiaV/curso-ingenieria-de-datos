# Taller Práctico: Arquitectura de Datos Modern en AWS
**Caso de Estudio:** LogiData S.A.S.  
**Duración Estimada:** 3 Horas  
**Metodología:** Role-Playing Colaborativo

---

## 1. Contexto del Caso
**LogiData S.A.S.** es una empresa de logística que procesa 50,000 pedidos diarios. Tienen un problema grave de dispersión de datos: información de clientes, pedidos y sensores IoT de vehículos está aislada en archivos planos (`.csv`).

**El Objetivo:** Construir una plataforma de datos centralizada (Data Lakehouse) en AWS que permita consultar esta información de manera unificada, segura y rápida usando SQL.

---

## 2. Roles del Equipo
Cada estudiante asumirá uno de los siguientes roles. **Nadie puede completar el taller solo; todos dependen del trabajo de los demás.**

1.  **Arquitecto de Soluciones:** Líder técnico. Diseña el flujo, define estándares y vigila el presupuesto.
2.  **Ingeniero DevSecOps:** Dueño de la infraestructura. Gestiona permisos (IAM), seguridad y buckets S3.
3.  **Ingeniero de Ingesta:** Responsable de mover los datos desde el origen (local) a la nube (S3 Raw).
4.  **Ingeniero ETL (Transformación):** Limpia, transforma y optimiza los datos (De CSV a Parquet).
5.  **Analista de Datos:** Cliente interno. Valida la calidad de los datos y crea los reportes de negocio.

---

## Fase 1: Cimientos (Infraestructura y Gobierno)
**Objetivo:** Preparar el entorno seguro en AWS antes de mover un solo byte de datos.

### Tarea Conjunta (Todo el equipo)
* **Definición de Nomenclatura:** El Arquitecto escribe en el tablero/chat el estándar de nombres.
    * *Ejemplo sugerido:* `logidata-g[numero_grupo]-[ambiente]`
    * *Buckets:* `logidata-g1-raw`, `logidata-g1-curated`, `logidata-g1-athena-results`

### Tareas Específicas
* **[Arquitecto]** Dibuja el diagrama lógico de carpetas: `/clientes`, `/pedidos`, `/sensores`, `/entregas`, `/catalogo`.
* **[DevSecOps]** Crea los **Buckets S3** definidos. **IMPORTANTE:** Habilitar encripción por defecto (SSE-S3).
* **[DevSecOps]** Crea los **Roles IAM** necesarios:
    * `GlueServiceRole`: Permisos para Glue y S3 (Full Access para el taller).
    * Comparte el ARN del rol con el Ingeniero ETL.
* **[Analista]** Revisa el archivo `diccionario_datos.csv` localmente y crea una lista de las "Primary Keys" esperadas para validar más tarde.

---

## Fase 2: Ingesta y Descubrimiento (Zona Raw)
**Objetivo:** Subir los archivos CSV tal como están y catalogarlos para ver qué tenemos.

### Tareas Específicas
* **[Ing. Ingesta]** Sube los archivos CSV a la capa `raw/` del bucket S3 respetando las carpetas del Arquitecto.
    * *Reto:* Verificar que `sensores.csv` (IoT) se suba correctamente a su propia carpeta `raw/sensores/`.
* **[Ing. ETL]** Configura un **AWS Glue Crawler** llamado `crawler-raw`.
    * *Source:* `s3://.../raw/`
    * *Output:* Base de datos `logidata_raw_db`.
* **[Ing. ETL]** Ejecuta el Crawler.

### Interacción Crítica (Handshake)
> **Ing. ETL:** *"El Crawler ha terminado. Analista, por favor verifica el esquema."*

* **[Analista]** Entra a **Athena** y hace un `SELECT * FROM sensores LIMIT 10`.
* **[Analista]** **REPORTA EL ERROR:** Debe notar que los campos de fecha están como `STRING` y que hay posibles nulos. Esto justifica la siguiente fase.

---

## Fase 3: Refinería de Datos (Zona Curated)
**Objetivo:** Convertir los datos sucios (CSV) en datos optimizados (Parquet) y particionados.

### Tarea Conjunta (Diseño de Particiones)
* El **Arquitecto** y el **Analista** deciden cómo particionar para ahorrar costos:
    * `Sensores`: Particionar por fecha (año/mes).
    * `Pedidos`: Particionar por estado o fecha.

### Tareas Específicas
* **[Ing. ETL]** Crea un **Glue Visual Job**:
    * **Source:** Tablas de `logidata_raw_db`.
    * **Transform:**
        * `Change Schema`: Convertir fechas de String a Timestamp.
        * `Drop Nulls`: Eliminar filas donde IDs sean nulos.
    * **Target:** Bucket S3 `curated/`, formato `Parquet`, compresión `Snappy`. Habilitar partición si se definió.
* **[DevSecOps]** Mientras corre el Job, configura una regla de ciclo de vida en S3: "Mover objetos de `raw/` a Glacier después de 30 días".
* **[Ing. Ingesta]** Simula una actualización: Sube un nuevo archivo `catalogo_v2.csv` para discutir cómo manejar duplicados (sobrescritura vs append).

### Interacción Crítica (Handshake)
> **Ing. ETL:** *"Datos procesados en la capa Curated. Ing. Ingesta, por favor corre el Crawler de la capa Curated."*

---

## Fase 4: Inteligencia de Negocio (Valor)
**Objetivo:** Responder preguntas de negocio que eran imposibles con los CSV sueltos.

### Tareas Específicas
* **[Analista]** Ejecuta las consultas finales en Athena apuntando a la base de datos `curated`.

#### KPI 1: Eficiencia Logística (Entregas a tiempo)
```sql
SELECT 
    e.conductor,
    AVG(date_diff('minute', e.hora_programada, e.hora_real)) as retraso_promedio_minutos
FROM "logidata_curated_db"."entregas" e
WHERE e.hora_real IS NOT NULL
GROUP BY e.conductor
ORDER BY retraso_promedio_minutos DESC;
```

#### KPI 2: Alerta de Sensores (Temperatura Crítica)
Cruzar datos de sensores con entregas para ver qué vehículo falló.

```sql
SELECT 
    s.vehiculo,
    s.temperatura,
    s.timestamp,
    e.conductor
FROM "logidata_curated_db"."sensores" s
JOIN "logidata_curated_db"."entregas" e ON s.vehiculo = e.vehiculo
WHERE s.temperatura > 5  -- Umbral crítico definido en el PDF
ORDER BY s.timestamp DESC;
```

[Arquitecto] Revisa el historial de consultas en Athena para ver cuántos datos escanearon. Compara el escaneo de la tabla Raw (CSV) vs la tabla Curated (Parquet). Debería ser 90% más eficiente.

### Entregables Finales

- Diagrama de Arquitectura Real: (Arquitecto) ¿Qué cambió respecto al plan original?

- Evidencia de Seguridad: (DevSecOps) Pantallazo de buckets encriptados y roles.

- Datos Procesados: (Ing. ETL) Muestra de archivos Parquet en S3.

- Dashboard/Insights: (Analista) Resultados de los KPIs.