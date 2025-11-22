# Taller: MongoDB para Ingeniería de Datos

Este taller consolida lo visto en la clase de MongoDB usando la colección `orders` y algunas operaciones típicas de ingeniería de datos.

Trabajarás con:

- CRUD básico en la colección `orders`.
- Agregaciones simples y un pequeño data mart diario.
- Índices para mejorar el rendimiento de consultas.
- Exportación de datos a CSV.

---

## 1. Preparación

1. Levanta MongoDB con Docker desde la carpeta del módulo.

   ```bash
   docker run -d --name mongodb          -p 27017:27017          -v "$(pwd)/data/mongo:/data/db"          mongo:latest
   ```

2. Abre DataGrip y conecta un datasource a MongoDB.
   - Host: `localhost`
   - Port: `27017`

3. Carga el dataset de ejemplo usando `mongoimport`:

   ```bash
   mongoimport          --uri="mongodb://localhost:27017"          --db=sales_db          --collection=orders          --file="data/sales_orders_sample.json"          --jsonArray
   ```

4. Verifica que la colección tiene datos:

   ```js
   use("sales_db");
   db.orders.find().limit(5);
   ```

---

## 2. Ejercicios de CRUD básico

### Ejercicio 1. Órdenes por cliente

1. Obtén todas las órdenes del cliente `CUST-001`.


2. Repite la consulta mostrando solo:
   - `order_id`
   - `total_amount`
   - `status`
   - `created_at`


3. Preguntas.
   - ¿Cuántas órdenes tiene este cliente?
   - ¿Cuál es el total acumulado de sus compras?

Puedes responder estas preguntas sumando manualmente o usando una agregación (ver más abajo).

### Ejercicio 2. Ventas mayores a un monto

1. Lista todas las órdenes con `total_amount > 200` y muestra:
   - `order_id`
   - `customer_id`
   - `total_amount`


2. Ordena los resultados de mayor a menor `total_amount`.


3. Preguntas.
   - ¿Cuál es el ticket más alto?
   - ¿A qué cliente pertenece?

### Ejercicio 3. Proyección y conteo

1. Muestra únicamente `customer_id`, `total_amount` y `created_at` de todas las órdenes.


2. Cuenta cuántas órdenes tienen `total_amount >= 100`.


---

## 3. Ejercicios de actualización

### Ejercicio 4. Cambiar estado de órdenes

Supón que todas las órdenes con `status = "pending"` del cliente `CUST-004` fueron aprobadas y pagadas.

1. Actualiza su `status` a `paid`.


2. Verifica el cambio mostrando `order_id` y `status` para `CUST-004`.


3. Explica en una frase qué hace `updateMany`.

### Ejercicio 5. Agregar canal de compra

Queremos añadir el campo `channel` a las órdenes.

- Para `CUST-001` el canal debe ser `"online"`.
- Para `CUST-003` el canal debe ser `"store"`.

1. Actualiza las órdenes de estos clientes.


2. Muestra `order_id`, `customer_id` y `channel` de todas las órdenes para comprobar.


---

## 4. Borrado de registros de prueba

### Ejercicio 6. Eliminar órdenes de test

1. Consulta cuántas órdenes tienen `test_user = true`.



2. Elimina estas órdenes.



3. Verifica que ya no quedan órdenes de prueba.


---

## 5. Agregaciones para análisis

### Ejercicio 7. Conteo de órdenes por estado

1. Usa el Aggregation Framework para contar cuántas órdenes hay en cada `status`.


2. ¿Qué estados existen y cuántas órdenes tiene cada uno?

### Ejercicio 8. Ventas por cliente

1. Calcula el total de ventas por cliente y el ticket promedio.


2. ¿Qué cliente es el que más ha comprado?

### Ejercicio 9. Vista a nivel de producto

1. Usa `$unwind` para obtener una vista a nivel de ítem, donde cada documento represente una línea de producto dentro de una orden.


2. Calcula la cantidad total vendida por SKU.

   Pista.

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

## 6. Construir una tabla intermedia diaria

### Ejercicio 10. Colección `daily_sales`

Construye una colección `daily_sales` con una agregación que agrupe por día y cliente.

1. Ejecuta el siguiente pipeline.

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

2. Consulta la colección `daily_sales`.


3. ¿Qué ventajas tiene esta colección respecto a hacer el cálculo en cada consulta directamente sobre `orders`?

---

## 7. Índices y rendimiento

### Ejercicio 11. Índice por cliente y fecha

1. Crea un índice sobre `customer_id` y `created_at`.


2. Verifica los índices de la colección.


3. Usa `explain` para ver el plan de ejecución de una consulta de órdenes por cliente.


Compara el plan antes y después de crear el índice. Comenta qué cambia.

---

## 8. Exportación de datos a CSV

### Ejercicio 12. Exportar `daily_sales`

1. Exporta la colección `daily_sales` a un archivo CSV.

   ```bash
   mongoexport          --uri="mongodb://localhost:27017"          --db=sales_db          --collection=daily_sales          --type=csv          --fields=date,customer_id,total_orders,total_amount_sum,avg_ticket          --out="data/daily_sales.csv"
   ```

2. Abre el CSV en tu editor favorito o en una herramienta de hojas de cálculo y revisa el resultado.

3. Piensa en cómo usarías ese archivo en un pipeline de carga a un data warehouse.

---

