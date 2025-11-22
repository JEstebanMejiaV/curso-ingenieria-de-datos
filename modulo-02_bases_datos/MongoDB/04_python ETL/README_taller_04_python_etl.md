# Taller – MongoDB + Python: mini ETL y calidad de datos (Clase 4)

En este taller vas a:

- Conectar a MongoDB desde Python usando variables de entorno.
- Ejecutar consultas y pipelines de agregación.
- Cargar los resultados en `pandas`.
- Aplicar reglas simples de calidad de datos.
- Exportar resultados a CSV.

---

## 1. Preparación

1. Ten MongoDB levantado con `sales_db` y las colecciones `orders` y `customers`.

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv .venv
   # Linux / Mac
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   ```

3. Instala dependencias:

   ```bash
   pip install pymongo python-dotenv pandas
   ```

4. Crea un archivo `.env` en la carpeta del taller:

   ```env
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=sales_db
   MONGO_ORDERS_COLLECTION=orders
   MONGO_CUSTOMERS_COLLECTION=customers
   ```

---

## 2. Ejercicio 1 – Conectar y listar colecciones

Crea un archivo `etl_mongo_student.py` y escribe una función para:

1. Cargar variables de entorno.
2. Conectarse a MongoDB.
3. Imprimir la lista de colecciones de `sales_db`.

Guía:

```python
from dotenv import load_dotenv
from pymongo import MongoClient
import os


def get_db():
    load_dotenv()
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client[os.getenv("MONGO_DB", "sales_db")]
    return db


def main():
    db = get_db()
    print("Colecciones:", db.list_collection_names())


if __name__ == "__main__":
    main()
```

Ejecuta el script y verifica que ves `orders`, `customers` y, si vienes de la Clase 3, `daily_sales`.

---

## 3. Ejercicio 2 – Órdenes de alto valor a DataFrame

Objetivo: obtener órdenes con `total_amount > 200` y analizarlas en `pandas`.

1. Desde tu script, obtén la colección `orders`:

   ```python
   import os
   db = get_db()
   orders_coll = db[os.getenv("MONGO_ORDERS_COLLECTION", "orders")]
   ```

2. Ejecuta un `find` con filtro y proyección:

   ```python
   cursor = orders_coll.find(
       {"total_amount": {"$gt": 200}},
       {
           "_id": 0,
           "order_id": 1,
           "customer_id": 1,
           "total_amount": 1,
           "status": 1,
           "created_at": 1,
       },
   )
   ```

3. Crea un DataFrame:

   ```python
   import pandas as pd

   high_value_df = pd.DataFrame(list(cursor))
   print(high_value_df)
   print("Número de órdenes de alto valor:", len(high_value_df))
   print("Ticket promedio:", high_value_df["total_amount"].mean())
   ```

---

## 4. Ejercicio 3 – Ejecutar un pipeline de agregación desde Python

Objetivo: construir una versión de `daily_sales` desde Python, usando un pipeline de agregación.

1. Define un pipeline que:

   - Haga `$lookup` con `customers`.
   - Haga `$unwind` de `customer`.
   - Excluya `customer.test_user = true`.
   - Agrupe por:
     - `date` (usando `$dateToString` sobre `created_at`).
     - `channel`.
     - `customer.city`.
   - Calcule:
     - `total_orders`.
     - `total_amount_sum`.
     - `avg_ticket`.

2. Ejecuta `orders_coll.aggregate(pipeline)` desde Python.

3. Convierte el resultado en un DataFrame `daily_df` y muéstralo por pantalla.

Pista de estructura:

```python
pipeline = [
    {
        "$lookup": {
            "from": os.getenv("MONGO_CUSTOMERS_COLLECTION", "customers"),
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "customer",
        }
    },
    {"$unwind": "$customer"},
    # agrega aquí $match, $group, $project
]

result = list(orders_coll.aggregate(pipeline))
import pandas as pd
daily_df = pd.DataFrame(result)
print(daily_df.head())
```

---

## 5. Ejercicio 4 – Reglas básicas de calidad de datos

Usa `daily_df` para hacer algunos checks:

1. Nulos por columna:

   ```python
   print("Nulos por columna:")
   print(daily_df.isna().sum())
   ```

2. Revisar si hay filas con `total_amount_sum` negativo:

   ```python
   invalid_amount = daily_df[daily_df["total_amount_sum"] < 0]
   print("Filas con total_amount_sum negativo:", len(invalid_amount))
   ```

3. Revisar si `avg_ticket` está en un rango razonable, por ejemplo entre 0 y 100000:

   ```python
   invalid_avg = daily_df[(daily_df["avg_ticket"] < 0) | (daily_df["avg_ticket"] > 100000)]
   print("Filas con avg_ticket fuera de rango:", len(invalid_avg))
   ```

4. Validar que `channel` sea uno de `["online", "store"]` (o los que definan en clase):

   ```python
   expected_channels = {"online", "store"}
   invalid_channel = daily_df[~daily_df["channel"].isin(expected_channels)]
   print("Filas con channel inesperado:", len(invalid_channel))
   ```

Escribe un pequeño resumen en comentarios sobre:

- Si encontraste registros inválidos.
- Qué tipo de reglas agregarías en un entorno de producción.

---

## 6. Ejercicio 5 – Exportar resultados a CSV

Exporta el DataFrame `daily_df` a un archivo CSV:

```python
output_path = "data/daily_sales_from_python.csv"
daily_df.to_csv(output_path, index=False)
print(f"Exportado a: {output_path}")
```

Revisa el archivo con un editor de texto o una hoja de cálculo.

Preguntas:

- ¿Qué columnas aparecen?
- ¿Se parece a una tabla de hechos en un data warehouse?

---

## 7. Ejercicio 6 (opcional) – Esquema para cargar a un warehouse

Solo a nivel conceptual (o si tienes tiempo, de forma práctica):

- Supón que quieres cargar `daily_sales_from_python.csv` a una tabla `fact_daily_sales` en una base relacional (Postgres, Redshift, etc.).
- Define el esquema SQL para esa tabla.
- Escribe un pequeño comentario sobre cómo harías la carga:
  - Comando `COPY` (Redshift, Postgres).
  - Bulk insert con Python.
  - Herramienta de orquestación (Airflow, etc.).

---

## 8. Entrega sugerida

Si este taller se usa para evaluación, entrega:

- El archivo `etl_mongo_student.py` con:
  - Código de conexión.
  - Ejercicios 2 a 5 resueltos.
  - Comentarios con tus reflexiones de calidad de datos.
- El archivo `data/daily_sales_from_python.csv` generado.

---

## 9. Preguntas de reflexión final

Responde brevemente (en comentarios o en un archivo aparte):

1. ¿Qué ventajas tiene ejecutar agregaciones en MongoDB y solo traer resultados agregados a Python?
2. ¿En qué casos preferirías hacer toda la transformación en un motor externo (Spark, dbt, etc.)?
3. ¿Qué reglas de calidad de datos añadirías si este fuera un pipeline de producción?
