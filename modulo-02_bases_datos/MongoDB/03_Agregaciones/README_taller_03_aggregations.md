# Taller – Aggregations y pipelines tipo ETL en MongoDB (Clase 3)

En este taller vas a practicar el **Aggregation Framework de MongoDB** para construir pipelines tipo ETL y generar una colección agregada `daily_sales`.

Trabajarás con:

- `sales_db.orders`
- `sales_db.customers`
- Aggregations con `$match`, `$project`, `$addFields`, `$group`, `$sort`, `$lookup`, `$unwind`.
- `$merge` para crear una colección `daily_sales`.
- `mongoexport` para sacar datos a un CSV.

---

## 1. Preparación

1. Asegúrate de tener MongoDB corriendo con Docker.

   ```bash
   docker run -d --name mongodb          -p 27017:27017          -v "$(pwd)/data/mongo:/data/db"          mongo:latest
   ```

2. Carga el dataset de `orders` si aún no lo tienes.

   ```bash
   mongoimport          --uri="mongodb://localhost:27017"          --db=sales_db          --collection=orders          --file="data/sales_orders_sample.json"          --jsonArray
   ```

3. Carga también el dataset de `customers`.

   ```bash
   mongoimport          --uri="mongodb://localhost:27017"          --db=sales_db          --collection=customers          --file="data/customers_sample.json"          --jsonArray
   ```

4. Verifica que ambas colecciones tienen datos.

   ```js
   use("sales_db");
   db.orders.find().limit(3);
   db.customers.find().limit(3);
   ```

---

## 2. Calentamiento: agregaciones básicas

### Ejercicio 1 – Ventas por cliente

Crea un pipeline que obtenga, por cada `customer_id`:

- `total_orders`: número de órdenes.
- `total_amount_sum`: suma de `total_amount`.
- `avg_ticket`: valor promedio del ticket.

Ordena los resultados por `total_amount_sum` de mayor a menor.

Pista:

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

Preguntas:

- ¿Qué cliente ha comprado más?
- ¿Cuál es su ticket promedio?

---

### Ejercicio 2 – Filtrar por fecha y marcar alto valor

Queremos marcar órdenes de **alto valor** (`high_value`) para aquellas con `total_amount >= 300`, pero solo considerando órdenes creadas a partir de `"2025-01-10"`.

1. Usa `$match` para filtrar por `created_at >= "2025-01-10"`.
2. Usa `$addFields` para crear `high_value` (booleano).
3. Proyecta solo los campos:
   - `order_id`
   - `customer_id`
   - `total_amount`
   - `high_value`
   - `created_at`

Puedes basarte en este ejemplo:

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

---

## 3. Enriquecimiento con `$lookup` (join con customers)

### Ejercicio 3 – Unir órdenes con clientes

Crea un pipeline que:

1. Haga un `$lookup` entre `orders` y `customers` por `customer_id`.
2. Use `$unwind` para obtener un solo documento por orden con su cliente.
3. Use `$project` para mostrar:
   - `order_id`
   - `customer_id`
   - `total_amount`
   - `status`
   - `city` (desde `customers`)
   - `segment` (desde `customers`)

Pista:

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
      city: "$customer.city",
      segment: "$customer.segment"
    }
  }
]);
```

Pregunta:

- ¿Qué diferencia ves entre tener `city` y `segment` dentro de `orders` versus tenerlos en otra colección y hacer el join?

---

### Ejercicio 4 – Ventas por ciudad

Usando un pipeline con `$lookup` + `$unwind` para enriquecer las órdenes con `city`, calcula las **ventas totales por ciudad**:

1. Agrupa por `city`.
2. Calcula:
   - `total_orders`
   - `total_amount_sum`
3. Ordena por `total_amount_sum` de mayor a menor.

Pista (solo la estructura):

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
    $group: {
      _id: "$customer.city",
      total_orders: { $sum: 1 },
      total_amount_sum: { $sum: "$total_amount" }
    }
  },
  { $sort: { total_amount_sum: -1 } }
]);
```

---

## 4. Vista a nivel de producto con `$unwind`

### Ejercicio 5 – Líneas de producto

Construye un pipeline que:

1. Aplique `$unwind` sobre `items`.
2. Proyecte:
   - `order_id`
   - `customer_id`
   - `sku` (`items.sku`)
   - `product_name` (`items.name`)
   - `qty` (`items.qty`)
   - `price` (`items.price`)
   - `line_amount` (`qty * price`)

Pista:

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

---

### Ejercicio 6 – Ranking de productos

A partir de la vista a nivel de producto, calcula la cantidad total y el monto total vendido por `sku`:

- `total_qty`
- `total_amount`

Ordena por `total_amount` de mayor a menor.

Pista:

```js
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.sku",
      total_qty: { $sum: "$items.qty" },
      total_amount: {
        $sum: { $multiply: ["$items.qty", "$items.price"] }
      }
    }
  },
  { $sort: { total_amount: -1 } }
]);
```

---

## 5. Mini ETL: construir `daily_sales`

### Ejercicio 7 – Colección `daily_sales`

Queremos construir una colección `daily_sales` con:

- Dimensiones:
  - `date` (YYYY-MM-DD, a partir de `created_at`).
  - `channel` (campo de `orders`).
  - `city` (desde `customers.city`).
- Métricas:
  - `total_orders`
  - `total_amount_sum`
  - `avg_ticket`
- Además, debemos excluir clientes de prueba (`customers.test_user = true`).

Arma un pipeline que:

1. Haga `$lookup` con `customers`.
2. Use `$unwind` para tener un solo cliente por orden.
3. Use `$match` para excluir `customer.test_user = true`.
4. Use `$group` por combinación de:
   - `date` (`$dateToString` sobre `created_at`).
   - `channel`.
   - `customer.city`.
5. Use `$project` para construir el documento final.
6. Use `$merge` para guardar el resultado en una colección `daily_sales`.

Puedes usar este esqueleto:

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
    $match: {
      "customer.test_user": { $ne: true }
    }
  },
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
  {
    $merge: {
      into: "daily_sales",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
]);
```

Luego:

```js
db.daily_sales.find();
```

Preguntas:

- ¿Cuántas filas tiene `daily_sales`?
- ¿Qué pasa si vuelves a ejecutar el mismo pipeline?

---

## 6. Exportar `daily_sales` a CSV

### Ejercicio 8 – `mongoexport` para analítica externa

Exporta la colección `daily_sales` a un archivo CSV llamado `data/daily_sales.csv`.

```bash
mongoexport       --uri="mongodb://localhost:27017"       --db=sales_db       --collection=daily_sales       --type=csv       --fields=date,channel,city,total_orders,total_amount_sum,avg_ticket       --out="data/daily_sales.csv"
```

Revisa el archivo CSV con un editor de texto, una hoja de cálculo, o una herramienta de BI.

Preguntas:

- ¿Qué columnas aparecen?
- ¿Cómo cargarías este archivo a un data warehouse relacional?

---

## 7. Reflexión final

Responde brevemente:

1. ¿En qué casos te parece más conveniente usar el Aggregation Framework que hacer la transformación en Python o Spark?
2. ¿Qué limitaciones ves al usar MongoDB como motor principal de ETL?
3. ¿Te parece razonable usar colecciones como `daily_sales` como “tablas de hechos” dentro de MongoDB?

---

