# Clase 4 – MongoDB en pipelines de datos: Python, ETL y calidad básica

En esta clase vemos cómo integrar MongoDB en un pipeline de datos usando Python:

- Conectar a MongoDB con `pymongo`.
- Ejecutar queries y pipelines de agregación desde Python.
- Cargar los resultados en `pandas` para análisis y calidad de datos.
- Exportar resultados a CSV simulando la carga a un data warehouse.

---

## 1. Objetivos

Al finalizar la clase, deberías poder:

- Configurar una conexión a MongoDB desde Python usando variables de entorno.
- Ejecutar consultas y pipelines de agregación (`aggregate`) desde código.
- Transformar resultados de MongoDB en DataFrames de `pandas`.
- Aplicar reglas básicas de calidad de datos (nulos, rangos, valores inesperados).
- Exportar los resultados a CSV, listo para un warehouse relacional o data lake.

---

## 2. Prerrequisitos

Requisitos de infraestructura:

- MongoDB corriendo (por ejemplo en Docker).
- Base de datos `sales_db` con:
  - Colección `orders` (de `sales_orders_sample.json` de la Clase 1).
  - Colección `customers` (de `customers_sample.json` de la Clase 3).

Rápida verificación en mongosh o DataGrip:

```js
use("sales_db");
db.orders.find().limit(3);
db.customers.find().limit(3);
```

Requisitos de Python:

- Python 3.10 o superior.
- Pip disponible.

---

## 3. Instalación de dependencias en Python

En la carpeta del módulo (por ejemplo `modulo-mongodb/clase-04-python-etl/`):

```bash
python -m venv .venv
# Linux / Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install pymongo python-dotenv pandas
```

Dependencias:

- `pymongo`: cliente oficial de MongoDB para Python.
- `python-dotenv`: para cargar variables de entorno desde un archivo `.env`.
- `pandas`: para manipular los datos tabulares.

---

## 4. Configuración de variables de entorno

Crea un archivo `.env` (no lo subas a Git) en la raíz de la clase:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=sales_db
MONGO_ORDERS_COLLECTION=orders
MONGO_CUSTOMERS_COLLECTION=customers
```

En producción normalmente:

- `MONGO_URI` apuntaría a un cluster (con usuario, password, TLS, etc.).
- Podrías tener varias DBs o colecciones por ambiente (dev, qa, prod).

---

## 5. Código base de conexión (`etl_mongo_example.py`)

Ejemplo sencillo para probar la conexión y listar colecciones:

```python
import os
from dotenv import load_dotenv
from pymongo import MongoClient


def get_mongo_client():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(mongo_uri)


def main():
    client = get_mongo_client()
    db_name = os.getenv("MONGO_DB", "sales_db")
    db = client[db_name]

    print(f"Conectado a MongoDB, base: {db_name}")
    print("Colecciones disponibles:")
    print(db.list_collection_names())


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python scripts/etl_mongo_example.py
```

Deberías ver algo tipo: `['orders', 'customers', 'daily_sales', ...]`.

---

## 6. Leer datos de MongoDB a pandas

Ejemplo: leer órdenes de alto valor (`total_amount > 100`) y llevarlas a DataFrame.

```python
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd


load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("MONGO_DB", "sales_db")]
orders_coll = db[os.getenv("MONGO_ORDERS_COLLECTION", "orders")]

cursor = orders_coll.find(
    {"total_amount": {"$gt": 100}},
    {
        "_id": 0,
        "order_id": 1,
        "customer_id": 1,
        "total_amount": 1,
        "status": 1,
        "created_at": 1,
    },
)

orders_df = pd.DataFrame(list(cursor))
print(orders_df.head())
print("Filas:", len(orders_df))
```

Puntos para comentar en clase:

- `list(cursor)` trae todos los documentos al cliente (bien para demos; en producción se cuida el volumen).
- La proyección de campos se hace en Mongo para reducir datos.

---

## 7. Ejecutar un pipeline de agregación desde Python

MongoDB permite ejecutar el mismo pipeline que usamos en Clase 3, pero enviado desde Python.

Ejemplo: pipeline para construir `daily_sales` (día, canal, ciudad) y materializar en la colección `daily_sales`:

```python
import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("MONGO_DB", "sales_db")]
orders_coll = db[os.getenv("MONGO_ORDERS_COLLECTION", "orders")]

daily_sales_pipeline = [
    {
        "$lookup": {
            "from": os.getenv("MONGO_CUSTOMERS_COLLECTION", "customers"),
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "customer",
        }
    },
    {"$unwind": "$customer"},
    {
        "$match": {
            "customer.test_user": {"$ne": True}
        }
    },
    {
        "$group": {
            "_id": {
                "date": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at",
                    }
                },
                "channel": "$channel",
                "city": "$customer.city",
            },
            "total_orders": {"$sum": 1},
            "total_amount_sum": {"$sum": "$total_amount"},
            "avg_ticket": {"$avg": "$total_amount"},
        }
    },
    {
        "$project": {
            "_id": 0,
            "date": "$_id.date",
            "channel": "$_id.channel",
            "city": "$_id.city",
            "total_orders": 1,
            "total_amount_sum": 1,
            "avg_ticket": 1,
        }
    },
    {
        "$merge": {
            "into": "daily_sales",
            "whenMatched": "replace",
            "whenNotMatched": "insert",
        }
    },
]

result = list(orders_coll.aggregate(daily_sales_pipeline))
print("Pipeline ejecutado. Registros procesados (salida del pipeline):", len(result))
```

Después de esto, puedes consultar en Mongo:

```js
use("sales_db");
db.daily_sales.find();
```

---

## 8. Calidad de datos básica en pandas

Imaginemos que ahora queremos revisar calidad sobre `daily_sales` desde Python.

```python
import pandas as pd

daily_coll = db["daily_sales"]
daily_cursor = daily_coll.find({}, {"_id": 0})
daily_df = pd.DataFrame(list(daily_cursor))

print(daily_df.head())
print(daily_df.dtypes)
```

### 8.1. Checks simples

- Comprobar nulos en dimensiones clave:

```python
print("Nulos por columna:")
print(daily_df.isna().sum())
```

- Validar que `total_amount_sum` y `avg_ticket` sean no negativos y razonables:

```python
invalid_amount = daily_df[daily_df["total_amount_sum"] < 0]
print("Filas con total_amount_sum negativo:", len(invalid_amount))

invalid_avg = daily_df[(daily_df["avg_ticket"] < 0) | (daily_df["avg_ticket"] > 100000)]
print("Filas con avg_ticket fuera de rango razonable:", len(invalid_avg))
```

- Validar que `channel` esté en una lista esperada (por ejemplo `["online", "store"]`):

```python
expected_channels = {"online", "store"}
invalid_channel = daily_df[~daily_df["channel"].isin(expected_channels)]
print("Filas con channel inesperado:", len(invalid_channel))
```

Conecta esto con prácticas de data quality en ingeniería de datos:

- En proyectos más grandes se usaría Great Expectations, dbt tests, etc.
- Aquí solo estamos haciendo checks “manuales” en pandas.

---

## 9. Exportar resultados a CSV

Exportar `daily_sales` a un CSV:

```python
output_path = "data/daily_sales_from_python.csv"
daily_df.to_csv(output_path, index=False)
print(f"Archivo CSV exportado en: {output_path}")
```

Este archivo se puede:

- Cargar en un warehouse (Redshift, Snowflake, BigQuery).
- Conectar a una herramienta de BI.
- Usar como dataset de pruebas.

---

## 10. Opcional: escribir a una base relacional

Comentario conceptual:

- Podrías crear una tabla `fact_daily_sales` en Postgres o Redshift.
- Desde Python, usar `sqlalchemy` o `psycopg2` para insertar los datos.
- MongoDB quedaría como fuente operacional, y el warehouse como capa analítica.

---

## 11. Cierre y enlace con el taller

Con esta clase:

- Viste a MongoDB como origen de un pipeline de datos.
- Mezclaste capacidades nativas de agregación (Clase 3) con transformación en Python.
- Aplicaste checks de calidad básicos sobre tablas derivadas.

En el taller (`README_taller_04_python_etl.md`) los estudiantes implementan su propio mini ETL y sus reglas de calidad.
