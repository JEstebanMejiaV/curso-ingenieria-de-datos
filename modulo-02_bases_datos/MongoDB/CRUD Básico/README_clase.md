# Módulo MongoDB para Ingeniería de Datos – Guía de Clase

Este módulo introduce MongoDB usando un caso sencillo de ventas y órdenes de un e–commerce.

Trabajaremos con:

- MongoDB levantado en Docker.
- DataGrip como cliente.
- Operaciones típicas de ingeniería de datos: CRUD, agregaciones, exportación e índices.

---

## 1. Estructura de archivos

Descarga o clona este módulo y verifica que tengas al menos:


- `README_clase.md`: esta guía para la sesión en vivo.
- `README_taller.md`: guía con ejercicios para que los estudiantes practiquen después.
- `data/sales_orders_mongo1.json`: archivo con el dataset de órdenes.

---

## 2. Requisitos previos

- Docker instalado y funcionando.
- DataGrip instalado.
- Opcional
  - mongosh
  - MongoDB Compass

---

## 3. Levantar MongoDB con Docker

Desde la carpeta del módulo:

```bash
docker run -d --name mongodb       -p 27017:27017       -v "$(pwd)/data/mongo:/data/db"       mongo:latest
```

Comprobar que está corriendo:

```bash
docker ps
```

Para detenerlo más adelante:

```bash
docker stop mongodb
```

Para eliminar el contenedor:

```bash
docker rm mongodb
```

---

## 4. Conectar DataGrip a MongoDB

1. Abrir DataGrip.
2. Ir a File - New - Data Source - MongoDB.
3. Configurar la conexión.
   - Host: `localhost`
   - Port: `27017`
   - Authentication: sin usuario ni contraseña.
   - Database: puedes dejarlo vacío o escribir `sales_db`.
4. Probar la conexión con Test Connection.
5. Guardar el datasource.

Después de esto puedes abrir una consola sobre el datasource para ejecutar comandos.

---

## 5. Crear base de datos y colección

En la consola de MongoDB dentro de DataGrip:

```js
use("sales_db");
```

Las bases de datos y colecciones se crean cuando insertamos datos. No es necesario crear nada antes.

---

## 6. Cargar datos desde el archivo JSON

El archivo `data/sales_orders_mongo1.json` contiene un array con documentos de ejemplo.

### 6.1. Cargar con mongoimport

Desde la carpeta `modulo-mongodb`:

```bash
mongoimport       --uri="mongodb://localhost:27017"       --db=sales_db       --collection=orders       --file="data/sales_orders_sample.json"       --jsonArray
```

Después, en DataGrip:

```js
use("sales_db");
db.orders.find().limit(5);
```

Deberías ver algunos documentos de ejemplo.

### 6.2. Cargar copiando el contenido en la consola

Como alternativa, puedes abrir el archivo JSON, copiar todo el array y ejecutar:

```js
use("sales_db");

db.orders.insertMany(
  /* aquí pegas el array completo del archivo JSON */
);
```

---

## 7. CRUD básico para mostrar en clase


### 7.1. Lecturas simples (find)

Todas las ventas de un cliente:

```js
db.orders.find({ customer_id: "CUST-001" });
```

Solo algunos campos:

```js
db.orders.find(
  { customer_id: "CUST-001" },
  { _id: 0, order_id: 1, total_amount: 1, status: 1, created_at: 1 }
);
```

Ventas mayores a cierto monto:

```js
db.orders.find(
  { total_amount: { $gt: 200 } },
  { _id: 0, order_id: 1, customer_id: 1, total_amount: 1 }
);
```

Solo `customer_id`, `total_amount`, `created_at`:

```js
db.orders.find(
  {},
  { _id: 0, customer_id: 1, total_amount: 1, created_at: 1 }
);
```

### 7.2. Actualizaciones

Cambiar el estado de órdenes pendientes de un cliente:

```js
db.orders.updateMany(
  { customer_id: "CUST-002", status: "pending" },
  { $set: { status: "paid" } }
);
```

Añadir un nuevo campo `channel` con un valor por defecto:

```js
db.orders.updateMany(
  { channel: { $exists: false } },
  { $set: { channel: "online" } }
);
```

Upsert para insertar o actualizar una orden puntual:

```js
db.orders.updateOne(
  { order_id: "O-9999" },
  {
    $set: {
      customer_id: "CUST-999",
      total_amount: 123.45,
      status: "paid",
      created_at: ISODate("2025-01-20T12:00:00Z"),
      test_user: true
    }
  },
  { upsert: true }
);
```

### 7.3. Borrado de datos de prueba

Ver órdenes de prueba:

```js
db.orders.find(
  { test_user: true },
  { _id: 0, order_id: 1, customer_id: 1, test_user: 1 }
);
```

Borrar órdenes de prueba:

```js
db.orders.deleteMany({ test_user: true });
```

Comprobar:

```js
db.orders.countDocuments({ test_user: true });
```

---

## 8. Operaciones típicas de ingeniería de datos


### 8.1. Agregaciones para métricas

Conteo de órdenes por estado:

```js
db.orders.aggregate([
  {
    $group: {
      _id: "$status",
      total_orders: { $sum: 1 },
      total_amount_sum: { $sum: "$total_amount" }
    }
  }
]);
```

Ventas totales por cliente:

```js
db.orders.aggregate([
  {
    $group: {
      _id: "$customer_id",
      total_orders: { $sum: 1 },
      total_amount_sum: { $sum: "$total_amount" },
      avg_ticket: { $avg: "$total_amount" }
    }
  },
  { $sort: { total_amount_sum: -1 } }
]);
```

Flatten de items con `$unwind` para crear una vista a nivel de producto:

```js
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $project: {
      _id: 0,
      order_id: 1,
      customer_id: 1,
      sku: "$items.sku",
      product_name: "$items.name",
      qty: "$items.qty",
      price: "$items.price",
      line_amount: { $multiply: ["$items.qty", "$items.price"] }
    }
  }
]);
```

### 8.2. Crear una tabla intermedia tipo fact de ventas diarias

Ejemplo de pipeline para construir una colección `daily_sales`:

```js
db.orders.aggregate([
  {
    $group: {
      _id: {
        date: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
        customer_id: "$customer_id"
      },
      total_orders: { $sum: 1 },
      total_amount_sum: { $sum: "$total_amount" },
      avg_ticket: { $avg: "$total_amount" }
    }
  },
  {
    $project: {
      _id: 0,
      date: "$_id.date",
      customer_id: "$_id.customer_id",
      total_orders: 1,
      total_amount_sum: 1,
      avg_ticket: 1
    }
  },
  {
    $merge: {
      into: "daily_sales",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
]);
```

Ahora puedes consultar la colección `daily_sales` como si fuera una tabla de hechos simple.

### 8.3. Índices para mejorar el rendimiento

Crear un índice por `customer_id` y `created_at`:

```js
db.orders.createIndex({ customer_id: 1, created_at: -1 });
```

Ver índices de la colección:

```js
db.orders.getIndexes();
```

Ver el plan de ejecución de una consulta con `explain`:

```js
db.orders.find(
  { customer_id: "CUST-001" }
).sort({ created_at: -1 }).explain("queryPlanner");
```

Discute con los estudiantes cómo cambia el plan al tener o no el índice creado.

### 8.4. Exportar datos para otros sistemas de análisis

Exportar la colección `daily_sales` a CSV:

```bash
mongoexport       --uri="mongodb://localhost:27017"       --db=sales_db       --collection=daily_sales       --type=csv       --fields=date,customer_id,total_orders,total_amount_sum,avg_ticket       --out="data/daily_sales.csv"
```

Ese CSV se puede cargar a una base relacional o a un data warehouse para análisis adicionales.

---

## 9. Lectura desde Python (ejemplo opcional)

Ejemplo simple usando `pymongo` y `pandas` para leer desde MongoDB y convertir el resultado en un DataFrame.

```python
from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017")
db = client["sales_db"]

# Leer órdenes mayores a cierto monto
cursor = db.orders.find(
    {"total_amount": {"$gt": 100}},
    {"_id": 0, "order_id": 1, "customer_id": 1, "total_amount": 1, "created_at": 1}
)

df = pd.DataFrame(list(cursor))
print(df.head())
```

Este tipo de patrón es común en tareas de ingeniería de datos cuando MongoDB es una fuente más dentro de un pipeline.

---

