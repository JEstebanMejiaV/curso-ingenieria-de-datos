# Datos XM/SiMEM (Colombia) starter

Stack listo para enseñar **OLTP (PostgreSQL + TimescaleDB)**, **OLAP (ClickHouse)**, **Documentos (MongoDB)**, 
**NoSQL clave-valor con partición (DynamoDB Local)** y **Lakehouse (Iceberg sobre MinIO + Trino)** usando datos 
abiertos del **mercado eléctrico colombiano (XM/SiMEM)**.

## Servicios (via Docker Compose)
- **TimescaleDB** (PostgreSQL + extensión): modelado 3FN, *hypertables*, agregados continuos.
- **ClickHouse**:  OLAP columnar de alto rendimiento.
- **MongoDB**:  documentos/JSON (ingesta cruda + agregaciones).
- **DynamoDB Local** : tablas particionadas (PK/SK) para acceso clave-valor.
- **MinIO**:  S3 local para *data lake*.
- **Trino** : consultas SQL unificadas + **Iceberg** con *catalog JDBC* (sin Hive Metastore).

> **Requisitos**: Docker/Docker Compose, Python 3.10+, `pip`.

---

## Quickstart

1) Clona este folder y copia `.env.example` a `.env` (ajusta valores si quieres):
```bash
cp .env.example .env
```

2) Levanta los servicios:
```bash
docker compose up -d
```

3) Crea el bucket en MinIO (se hace automáticamente al levantar el contenedor `mc-init`).  
   Accede a consola MinIO: http://localhost:9001 (user `admin`, pass `changeme123`).

4) Crea entorno Python e instala dependencias:
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r scripts/requirements.txt
```

5) Descarga datos desde **SiMEM** (rango de fechas y `dataset_id` en `.env` o CLI):
```bash
python scripts/fetch_xm.py --source simem --dataset-id $SIMEM_DATASET_ID       --start-date $START_DATE --end-date $END_DATE --out-dir $RAW_DIR
```

6) Carga a **TimescaleDB** (crea tabla, la convierte en *hypertable* y hace *upsert*):
```bash
python scripts/load_postgres_timescale.py       --parquet-dir $RAW_DIR/$SIMEM_DATASET_ID       --pg-host localhost --pg-port 5432 --pg-user $POSTGRES_USER --pg-password $POSTGRES_PASSWORD       --pg-db $POSTGRES_DB --schema $PG_SCHEMA --table $PG_TABLE --time-col $TS_TIME_COLUMN
```

7) Carga a **ClickHouse** (crea tabla MergeTree particionada por mes):
```bash
python scripts/load_clickhouse.py       --parquet-dir $RAW_DIR/$SIMEM_DATASET_ID --host localhost --port 9000       --database energy --table demanda_horaria --time-col $TS_TIME_COLUMN
```

8) Carga a **MongoDB** (inserta documentos desde Parquet → dict):
```bash
python scripts/load_mongo.py --parquet-dir $RAW_DIR/$SIMEM_DATASET_ID       --mongo-uri mongodb://localhost:27017 --database energy --collection demanda
```

9) Crea tabla y carga *items* de ejemplo en **DynamoDB Local** (PK/SK):
```bash
python scripts/load_dynamo.py --parquet-dir $RAW_DIR/$SIMEM_DATASET_ID       --endpoint-url http://localhost:8000 --table EnergyDaily --pk pk --sk sk --time-col $TS_TIME_COLUMN
```

10) **Lakehouse (Iceberg + Trino):** Abre Trino UI en `http://localhost:8080/ui` y ejecuta:
- `sql/trino/00_create_schema.sql`
- `sql/trino/01_create_iceberg_tables.sql`
- `sql/trino/02_load_iceberg_from_parquet.sql`

> Nota: el *catalog* `iceberg` guarda su **metadato** en PostgreSQL (JDBC catalog) y los **archivos** en MinIO (bucket `datalake`). No necesitas Hive Metastore.

---

## Datasets (SiMEM)
Este starter funciona con cualquier recurso público **SiMEM** que exponga un `datasetId` y un rango `startDate/endDate`.
- Abre el portal SiMEM, identifica el conjunto, copia el **datasetId** y ajusta `.env`.
- El script `fetch_xm.py` usa `SIMEM_BASE` (por defecto: `https://www.simem.co/backend-files/api/PublicData`).

> Si prefieres una librería, puedes adaptar `fetch_xm.py` para usar `pydataxm` (ver comentarios dentro del archivo).

---

## Estructura
```
xm-simem-starter/
├─ docker-compose.yml
├─ .env.example  # copia a .env
├─ README.md
├─ init/
│  └─ minio-create-bucket.sh
├─ trino/
│  └─ etc/catalog/
│     ├─ iceberg.properties
│     └─ README.txt
├─ scripts/
│  ├─ requirements.txt
│  ├─ config.py
│  ├─ utils.py
│  ├─ fetch_xm.py
│  ├─ load_postgres_timescale.py
│  ├─ load_clickhouse.py
│  ├─ load_mongo.py
│  └─ load_dynamo.py
├─ sql/
│  ├─ trino/
│  │  ├─ 00_create_schema.sql
│  │  ├─ 01_create_iceberg_tables.sql
│  │  └─ 02_load_iceberg_from_parquet.sql
│  └─ postgres_timescale.sql
└─ data/
   └─ raw/  (aquí se guardan los Parquet por dataset y fecha)
```

