# Clase 3 – Agregaciones y pipelines tipo ETL en MongoDB

En esta clase usamos el **Aggregation Framework de MongoDB** como un pequeño motor de ETL:

- Filtros, proyecciones y campos derivados.
- Agrupaciones y ordenamientos.
- Joins entre colecciones con `$lookup`.
- Desanidamiento de arrays con `$unwind`.
- Construcción de una colección agregada `daily_sales` y exportación a CSV.

---

## 1. Objetivos

Al finalizar la clase, deberías poder:

- Entender la estructura básica de un **pipeline de agregación**.
- Usar etapas como `$match`, `$project`, `$addFields`, `$group`, `$sort`, `$limit`, `$lookup`, `$unwind`.
- Construir un pipeline tipo ETL para generar una tabla intermedia `daily_sales`.
- Exportar datos con `mongoexport` para llevarlos a un data warehouse u otra base relacional.

---

## 2. Prerrequisitos

Se asume que ya tienes:

- MongoDB corriendo en Docker (como en la Clase 1).
- La colección `orders` en la base de datos `sales_db`, cargada desde `data/sales_orders_sample.json` (Clase 1).

En esta clase añadiremos una colección `customers` (que también se entrega en `data/customers_sample.json`).

---

## 3. Datasets: `orders` y `customers`

### 3.1. `orders`

La colección `orders` debe haberse cargado previamente con:

```bash
mongoimport       --uri="mongodb://localhost:27017"       --db=sales_db       --collection=orders       --file="data/sales_orders_sample.json"       --jsonArray
```

### 3.2. `customers`

Para esta clase añadimos la colección `customers`. Puedes cargarla desde el archivo JSON incluido:

```bash
mongoimport       --uri="mongodb://localhost:27017"       --db=sales_db       --collection=customers       --file="data/customers_sample.json"       --jsonArray
```

O, si prefieres, crearla con `insertMany`:

```js
use("sales_db");

db.customers.insertMany([
  {
    customer_id: "CUST-001",
    name: "Ana Pérez",
    city: "Bogotá",
    segment: "retail",
    signup_date: ISODate("2024-12-01T09:00:00Z"),
    test_user: false
  },
  {
    customer_id: "CUST-002",
    name: "Carlos Gómez",
    city: "Medellín",
    segment: "retail",
    signup_date: ISODate("2024-12-05T11:30:00Z"),
    test_user: false
  },
  {
    customer_id: "CUST-003",
    name: "Oficina Central SA",
    city: "Barranquilla",
    segment: "corporate",
    signup_date: ISODate("2024-12-10T15:00:00Z"),
    test_user: false
  },
  {
    customer_id: "CUST-004",
    name: "Laura Torres",
    city: "Cali",
    segment: "retail",
    signup_date: ISODate("2024-12-15T08:45:00Z"),
    test_user: true
  }
]);
```

Verificación rápida:

```js
use("sales_db");
db.orders.find().limit(3);
db.customers.find().limit(3);
```

---

## 4. Aggregation Framework: concepto y estructura

Un **pipeline de agregación** es una secuencia de etapas que transforman los documentos de entrada.

Ejemplo básico: ventas totales por cliente a partir de 2025-01-01.

```js
db.orders.aggregate([
  // 1. Filtro por fecha
  { 
    $match: { 
      created_at: { $gte: ISODate("2025-01-01T00:00:00Z") } 
    } 
  },
  // 2. Agrupación por cliente
  {
    $group: {
      _id: "$customer_id",
      total_amount: { $sum: "$total_amount" },
      total_orders: { $sum: 1 }
    }
  },
  // 3. Orden por mayor monto
  { $sort: { total_amount: -1 } },
  // 4. Límite a los 10 primeros
  { $limit: 10 }
]);
```

Etapas que usaremos en la clase:

- `$match`: filtra documentos (equivalente a WHERE).
- `$project`: selecciona campos y crea nuevos.
- `$addFields`: añade campos derivados sin eliminar los existentes.
- `$group`: agrupa y calcula métricas.
- `$sort`: ordena los resultados.
- `$limit`: limita el número de documentos.
- `$lookup`: join entre colecciones.
- `$unwind`: desanida arrays (un documento por elemento del array).

---

## 5. Demostraciones en clase

### 5.1. Ventas totales por cliente

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

Puntos a discutir:

- El campo `_id` como “clave de agrupación”.
- Cómo se vería esto en SQL (GROUP BY customer_id).

---

### 5.2. `$match`, `$addFields` y `$project`

Marcar órdenes de alto valor (`high_value`) para `total_amount >= 300`, solo para fechas desde `2025-01-10`:

```js
db.orders.aggregate([
  {
    $match: {
      created_at: { $gte: ISODate("2025-01-10T00:00:00Z") }
    }
  },
  {
    $addFields: {
      high_value: { $gte: ["$total_amount", 300] }
    }
  },
  {
    $project: {
      _id: 0,
      order_id: 1,
      customer_id: 1,
      total_amount: 1,
      high_value: 1,
      created_at: 1
    }
  }
]);
```

Discusión:

- La lógica condicional reside en el servidor.
- `$addFields` vs `$project` para añadir campos.

---

### 5.3. `$lookup`: join con `customers`

Enriquecer las órdenes con ciudad y segmento del cliente:

```js
db.orders.aggregate([
  {
    $lookup: {
      from: "customers",
      localField: "customer_id",
      foreignField: "customer_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" },
  {
    $project: {
      _id: 0,
      order_id: 1,
      customer_id: 1,
      total_amount: 1,
      status: 1,
      created_at: 1,
      city: "$customer.city",
      segment: "$customer.segment"
    }
  }
]);
```**

Temas para la discusión:

- Diferencias con un JOIN en SQL.
- Qué ocurre si no hay coincidencia en `customers`.

---

### 5.4. `$unwind`: vista a nivel de producto

Pasar de nivel orden a nivel ítem:

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

Uso típico:

- Agrupar por SKU para ver productos más vendidos.
- Crear una tabla de hechos a nivel de línea de producto.

---

## 6. Pipeline tipo ETL: colección `daily_sales`

Vamos a construir una pequeña colección agregada `daily_sales` dentro de MongoDB, parecida a una tabla de hechos de un data mart.

**Dimensiones:**

- `date` (YYYY-MM-DD, derivado de `created_at`).
- `channel` (campo de `orders`, si existe; si no, se puede asumir `"online"`).
- `city` (desde `customers.city`).

**Métricas:**

- `total_orders`
- `total_amount_sum`
- `avg_ticket`

Además, queremos excluir clientes marcados como `test_user = true` en `customers`.

Ejemplo de pipeline completo:

```js
db.orders.aggregate([
  // Enriquecimiento con customers
  {
    $lookup: {
      from: "customers",
      localField: "customer_id",
      foreignField: "customer_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" },

  // Excluir clientes de prueba
  {
    $match: {
      "customer.test_user": { $ne: true }
    }
  },

  // Agrupar por día, canal y ciudad
  {
    $group: {
      _id: {
        date: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
        channel: "$channel",
        city: "$customer.city"
      },
      total_orders: { $sum: 1 },
      total_amount_sum: { $sum: "$total_amount" },
      avg_ticket: { $avg: "$total_amount" }
    }
  },

  // Proyección final
  {
    $project: {
      _id: 0,
      date: "$_id.date",
      channel: "$_id.channel",
      city: "$_id.city",
      total_orders: 1,
      total_amount_sum: 1,
      avg_ticket: 1
    }
  },

  // Guardar en colección daily_sales
  {
    $merge: {
      into: "daily_sales",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
]);
```

Después de ejecutar:

```js
db.daily_sales.find();
```

Preguntas para clase:

- ¿Qué pasa si ejecutas de nuevo el mismo pipeline?

---

## 7. Ingesta y exportación

### 7.1. Recordatorio de `mongoimport`

Para cargar colecciones desde archivos JSON:

```bash
mongoimport       --uri="mongodb://localhost:27017"       --db=sales_db       --collection=orders       --file="data/sales_orders_sample.json"       --jsonArray

mongoimport       --uri="mongodb://localhost:27017"       --db=sales_db       --collection=customers       --file="data/customers_sample.json"       --jsonArray
```

### 7.2. Exportar `daily_sales` a CSV

```bash
mongoexport       --uri="mongodb://localhost:27017"       --db=sales_db       --collection=daily_sales       --type=csv       --fields=date,channel,city,total_orders,total_amount_sum,avg_ticket       --out="data/daily_sales.csv"
```

Este CSV se puede cargar en un almacén analítico (Redshift, Snowflake, BigQuery, etc.) o en una base relacional.

---

## 8. Buen uso del Aggregation Framework

**Ventajas:**

- Mucha lógica de agregación cerca de los datos.
- Menos tráfico entre cliente y servidor.
- Ideal para preagregar datos y construir tablas intermedias.

**Cuándo puede no ser la mejor opción:**

- Pipelines enormes con reglas de negocio complejas.
- Muchos joins multi-hop sobre varias colecciones.
- Necesidad de integración con múltiples fuentes de datos externas (mejor usar Spark, dbt, etc.).

---


