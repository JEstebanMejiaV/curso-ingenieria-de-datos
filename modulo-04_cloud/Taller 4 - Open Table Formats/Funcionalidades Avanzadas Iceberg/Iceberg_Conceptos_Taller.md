# Opción 3: Amazon Athena (Iceberg Avanzado) – Conceptos clave del taller

Este taller usa **Amazon Athena (engine v3)** para trabajar con **Apache Iceberg** sobre datos en **Amazon S3**, con tablas registradas en el **AWS Glue Data Catalog**. El foco está en tres capacidades: **hidden partitioning**, **MERGE (upsert/delete)** y **OPTIMIZE (compaction/maintenance)**.

---

## 1) Apache Iceberg en Athena: qué estás usando realmente

### Componentes
- **S3**: almacena los *data files* (Parquet) y el directorio **metadata/** de Iceberg.
- **Glue Data Catalog**: actúa como **catálogo** (metastore) que registra tablas y apunta al “metadata file” vigente.
- **Athena**: motor SQL (Trino) que ejecuta DDL/DML y entiende Iceberg (snapshots, tablas de metadatos, maintenance commands).

### Qué significa “tabla Iceberg”
Una tabla Iceberg no es “un solo archivo”, sino un conjunto de:
- **data files** (Parquet) con los registros
- **metadata files** (JSON/Avro) que describen esquema, particiones, snapshots y manifests
- **snapshots**: cada cambio relevante crea un nuevo snapshot (versionado transaccional)

Resultado: puedes hacer operaciones ACID, time travel, MERGE y mantenimiento sin “reconstruir” todo el dataset.

---

## 2) Hidden Partitioning (Particionado oculto)

### Problema que resuelve (vs Hive)
En Hive, el particionado suele depender de rutas físicas y convenciones (carpetas), y obliga al consumidor a saber “cómo está particionado” para filtrar bien.

Iceberg mejora esto con **particionado declarativo**:
- Definición lógica de partición en la tabla
- Derivación automática de valores de partición al escribir
- **Partition pruning** automático al leer, usando los filtros de la query

### Partition Spec
Iceberg define el particionado con un **partition spec**, por ejemplo:
- `day(event_ts)`
- `month(event_ts)`
- `year(ws_sales_time)`

En el taller:
- Se elige particionar por año: `PARTITIONED BY (year(ws_sales_time))`
- Motivo: el volumen inicial no es enorme, y agrupar por año simplifica y acelera lecturas con filtros temporales.

### Qué ocurre al consultar (partition pruning)
Cuando ejecutas una query con filtro por `ws_sales_time`, Iceberg:
- traduce filtros de tiempo a filtros de partición
- evita escanear particiones irrelevantes
- reduce filas y archivos leídos

Indicadores prácticos:
- En Athena, revisas **Query stats** y confirmas que las *Input Rows* corresponden solo a la partición filtrada.

---

## 3) Tablas de metadatos de Iceberg en Athena

Iceberg expone “tablas internas” para inspección. Son vitales para entender rendimiento, archivos y versionado.

### `$files`
Lista los archivos físicos que componen la tabla (por partición), con datos como:
- ruta en S3
- formato
- cantidad de registros
- tamaños
- información por partición (ejemplo `ws_sales_time_year=2000`)

Uso típico:
- validar que el particionado existe
- contar cuántos archivos hay por partición (señal de “small files problem”)
- observar cambios después de MERGE u OPTIMIZE

Ejemplo:
```sql
SELECT * FROM "athena_iceberg_db"."web_sales_iceberg$files";
```

### `$history` y `$snapshots`
- `$history`: historial temporal de snapshots (qué snapshot quedó “current” en cada momento).
- `$snapshots`: detalle de snapshots y operación asociada (append/overwrite/replace, etc.).

Uso típico:
- auditar cambios
- verificar que MERGE u OPTIMIZE generaron nuevos snapshots
- base conceptual para time travel (aunque acá el énfasis es performance y mantenimiento)

Ejemplo:
```sql
SELECT * FROM "athena_iceberg_db"."web_sales_iceberg$snapshots";
```

---

## 4) MERGE INTO (upsert + delete en una sola sentencia)

### Qué resuelve
El patrón clásico “update + insert + delete” suele requerir múltiples pasos y puede romper consistencia.

**MERGE INTO** permite en una sola sentencia:
- **DELETE** condicional
- **UPDATE** condicional
- **INSERT** cuando no hay match

### Requisitos importantes
- **Athena engine version 3**
- tabla destino debe ser **Iceberg**
- es una operación **transaccional** (ACID)

### Diseño del taller: tabla staging `merge_table`
Se crea una tabla Iceberg adicional `merge_table` que contiene:
- las mismas columnas del target
- una columna `operation` con banderas:
  - `'U'` update
  - `'I'` insert
  - `'D'` delete

Esto simula un feed de cambios (CDC simplificado).

### Concepto clave: Join key del MERGE
La condición `ON` define el match (en el taller):
- `ws_order_number` + `ws_item_sk`

Esto define el “identificador” lógico de la fila (o combinación de negocio) sobre el cual se decide update/delete.

### Validaciones recomendadas
Después del MERGE, validar por año y por warehouse:
- Inserts: aparece el año 2001
- Updates: warehouse 10 en 2000 pasa a 16
- Deletes: warehouse 9 desaparece en 1999

---

## 5) Delete files, Copy-on-Write y costo de lectura

Iceberg puede representar deletes a nivel fila usando *delete files* (por ejemplo, **position deletes**).
Esto introduce costo adicional:
- el motor debe aplicar esos deletes al resultado durante lectura

Además, muchas operaciones generan:
- nuevos archivos de datos
- más manifests
- potencial “small files problem”

Resultado: con el tiempo, las queries pueden degradarse por:
- demasiados archivos que abrir
- deletes que deben aplicarse al leer

Aquí entra OPTIMIZE.

---

## 6) OPTIMIZE (compaction y mantenimiento de tablas)

### Objetivo
Mejorar performance sin cambiar el contenido lógico de la tabla.

Athena soporta **manual compaction** con:
- `OPTIMIZE ... REWRITE DATA USING BIN_PACK`

### Qué hace BIN_PACK (en términos prácticos)
- **compacta archivos pequeños en archivos más grandes**
  - reduce overhead de apertura de archivos
- **fusiona data files con delete files (cuando aplica)**
  - evita aplicar muchos deletes en tiempo de query (mejor lectura)

### Cómo se valida
1) observar `$files` antes
2) ejecutar OPTIMIZE
3) observar `$files` después
4) comparar número total de archivos y tamaños

Ejemplo:
```sql
OPTIMIZE athena_iceberg_db.web_sales_iceberg REWRITE DATA USING BIN_PACK;
```

### Optimizar solo una partición
Útil cuando sabes dónde está el “dolor” (por ejemplo, partición 2000 tras updates):
```sql
OPTIMIZE athena_iceberg_db.web_sales_iceberg REWRITE DATA USING BIN_PACK
WHERE year(ws_sales_time) = 2000;
```

### Efecto típico en este taller (interpretación)
- 1998: sin cambios (no tocaste partición)
- 1999: baja record_count (por deletes)
- 2000: puede compactar múltiples archivos en 1 (por updates y deletes asociados)
- 2001: puede quedar igual si solo insertaste y ya quedó “bien”

---

## 7) Propiedades de tabla para controlar OPTIMIZE y tamaños de archivos

Athena permite ajustar parámetros de compaction y thresholds con `TBLPROPERTIES`:

### Propiedades más relevantes
- `write_target_data_file_size_bytes`
  - tamaño objetivo de archivos de datos (reduce small files si está bien calibrado)
- `optimize_rewrite_data_file_threshold`
  - umbral (cantidad) de data files en una partición para considerar rewrite/compaction
- `optimize_rewrite_delete_file_threshold`
  - umbral (cantidad) de delete files para disparar rewrite/merge con data files

Se pueden definir:
- al crear la tabla
- luego con `ALTER TABLE ... SET TBLPROPERTIES`

Ejemplo:
```sql
ALTER TABLE athena_iceberg_db.web_sales_iceberg SET TBLPROPERTIES (
  'write_target_data_file_size_bytes'='346870912',
  'optimize_rewrite_delete_file_threshold'='16',
  'optimize_rewrite_data_file_threshold'='16'
);
```

---

## 8) Checklist de “qué debo entender para pasar el taller con confianza”

- Hidden partitioning
  - saber qué es un partition spec
  - entender partition pruning y cómo validar en Query stats
- Metadatos Iceberg en Athena
  - usar `$files` para ver archivos y particiones
  - usar `$snapshots` para auditar cambios operacionales
- MERGE
  - staging table con bandera de operación
  - condición ON correcta
  - validación por año/warehouse
- OPTIMIZE
  - por qué mejora performance (small files + deletes)
  - cómo comparar `$files` antes y después
  - cuándo optimizar una partición específica
- TBLPROPERTIES
  - cómo controlar tamaños y thresholds para evitar degradación

---

## Glosario rápido
- **Snapshot**: versión consistente de la tabla después de un commit.
- **Manifest / Manifest list**: metadatos que enumeran archivos y su pertenencia a snapshots.
- **Partition pruning**: evitar leer particiones innecesarias usando filtros.
- **Small files problem**: muchos archivos pequeños degradan rendimiento por overhead.
- **Delete files (position deletes)**: archivos que registran eliminaciones a nivel fila.
- **Compaction / OPTIMIZE**: reescritura estructural para mejorar performance sin alterar contenido lógico.
