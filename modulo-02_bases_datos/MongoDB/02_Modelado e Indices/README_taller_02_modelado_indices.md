# Taller – Modelado de datos e índices en MongoDB (Clase 2)

En este taller vas a practicar:

- Leer y entender el modelo de documentos actual (`orders`, `customers`).
- Tomar decisiones de modelado (embebido vs referencia).
- Crear índices simples y compuestos.
- Usar `explain` para ver el efecto de los índices.

---

## 1. Preparación

1. Asegúrate de tener MongoDB corriendo con Docker.

   ```bash
   docker run -d --name mongodb          -p 27017:27017          -v "$(pwd)/data/mongo:/data/db"          mongo:latest
   ```

2. Carga los datos si aún no lo has hecho.

   ```bash
   mongoimport          --uri="mongodb://localhost:27017"          --db=sales_db          --collection=orders          --file="data/sales_orders_sample.json"          --jsonArray

   mongoimport          --uri="mongodb://localhost:27017"          --db=sales_db          --collection=customers          --file="data/customers_sample.json"          --jsonArray
   ```

3. Verifica las colecciones.

   ```js
   use("sales_db");
   db.orders.find().limit(3);
   db.customers.find().limit(3);
   ```

---

## 2. Ejercicio 1 – Inspección del modelo actual

1. Examina un documento de `orders`.

   ```js
   db.orders.findOne();
   ```

   Responde:

   - ¿Qué campos hay al nivel raíz?
   - ¿Qué campos están dentro del array `items`?

2. Examina un documento de `customers`.

   ```js
   db.customers.findOne();
   ```

   Responde:

   - ¿Qué atributos del cliente se relacionan con las órdenes?
   - ¿Tiene sentido que `customers` sea una colección aparte? ¿por qué?

Anota tus respuestas en un archivo de texto o como comentarios en tu script `.js`.

---

## 3. Ejercicio 2 – Campo embebido shipping_address

Queremos guardar la dirección de envío como un objeto embebido dentro de `orders`.

1. Define una estructura para `shipping_address`, por ejemplo:

   ```json
   {
     "street": "Calle 123",
     "city": "Bogotá",
     "country": "Colombia"
   }
   ```

2. Usa `updateMany` para añadir un `shipping_address` de ejemplo a las órdenes de `CUST-001`.

   ```js
   db.orders.updateMany(
     { customer_id: "CUST-001" },
     {
       $set: {
         shipping_address: {
           street: "Calle 123",
           city: "Bogotá",
           country: "Colombia"
         }
       }
     }
   );
   ```

3. Verifica:

   ```js
   db.orders.find(
     { customer_id: "CUST-001" },
     { _id: 0, order_id: 1, customer_id: 1, shipping_address: 1 }
   );
   ```

Pregunta de reflexión:

- ¿Tiene sentido que `shipping_address` esté embebido en `orders` y no en `customers`? Justifica.

---

## 4. Ejercicio 3 – Crear índices básicos

### 4.1. Índice por customer_id

1. Crea un índice por `customer_id` en `orders`.

   ```js
   db.orders.createIndex({ customer_id: 1 });
   ```

2. Ejecuta esta consulta con `explain`.

   ```js
   db.orders.find(
     { customer_id: "CUST-001" }
   ).explain("queryPlanner");
   ```

   Observa si aparece IXSCAN (uso de índice) o COLLSCAN (escaneo completo).

### 4.2. Índice por status

1. Crea un índice por `status`.

   ```js
   db.orders.createIndex({ status: 1 });
   ```

2. Ejecuta:

   ```js
   db.orders.find(
     { status: "paid" }
   ).explain("queryPlanner");
   ```

3. Reflexiona:

   - ¿Crees que este índice será muy útil en un sistema real con millones de órdenes?
   - ¿Por qué?

---

## 5. Ejercicio 4 – Índice compuesto para consultas por cliente y fecha

Queremos soportar eficientemente consultas del tipo:

Traer las últimas órdenes de un cliente, ordenadas por fecha descendente.

1. Crea un índice compuesto en `orders`.

   ```js
   db.orders.createIndex({ customer_id: 1, created_at: -1 });
   ```

2. Ejecuta esta consulta con `explain`.

   ```js
   db.orders.find(
     { customer_id: "CUST-001" }
   ).sort({ created_at: -1 }).explain("queryPlanner");
   ```

3. Revisa el winningPlan.

   - ¿Usa el índice compuesto?
   - ¿Hay una etapa de ordenamiento SORT o ya no la necesita?

Anota una breve explicación.

---

## 6. Ejercicio 5 – Diseño conceptual: products y status_history

La empresa quiere extender el modelo:

- Manejar un catálogo de productos en una colección `products`.
- Llevar un historial de cambios de estado `status_history` por orden.

### 6.1. products

Supón que cada producto tiene:

- `sku`
- `name`
- `category`
- `price_list`
- `active`

Preguntas:

1. ¿Crearías una colección `products` separada o embebes toda la info del producto en cada ítem de `orders`?
2. ¿Qué ventajas tiene una colección `products` independiente?
3. Escribe un ejemplo de documento para `products`.

### 6.2. status_history

Queremos registrar el historial de estados de las órdenes:

```json
"status_history": [
  { "status": "pending", "changed_at": "2025-01-10T10:15:00Z" },
  { "status": "paid", "changed_at": "2025-01-10T10:20:00Z" }
]
```

Preguntas:

1. ¿Qué ventajas ves en almacenarlo embebido en `orders`?
2. ¿En qué casos preferirías una colección aparte `order_events` con un documento por cambio de estado?

Escribe tus respuestas como texto.

---

## 7. Ejercicio 6 – explain antes y después de un índice

El objetivo es ver claramente el impacto de un índice.

1. Identifica un índice que quieras eliminar (por ejemplo `customer_id_1`).

   ```js
   db.orders.getIndexes();
   db.orders.dropIndex("customer_id_1");
   ```

2. Ejecuta:

   ```js
   db.orders.find(
     { customer_id: "CUST-001" }
   ).explain("queryPlanner");
   ```

   Anota qué tipo de plan usa.

3. Vuelve a crear el índice.

   ```js
   db.orders.createIndex({ customer_id: 1 });
   ```

4. Ejecuta de nuevo el `explain`.

   ```js
   db.orders.find(
     { customer_id: "CUST-001" }
   ).explain("queryPlanner");
   ```

5. Compara ambos planes y escribe la diferencia.

---

## 9. Preguntas de cierre

Responde brevemente:

1. ¿Qué combinación de campos indexarías primero en `orders` si tuvieras millones de registros?
2. ¿Qué riesgo hay en crear demasiados índices sin analizar los patrones de acceso?
3. ¿Qué tipos de entidades prefieres siempre como colección aparte y cuáles embebidas?

Estas respuestas te ayudan a conectar el modelado lógico de datos con las necesidades reales de rendimiento.
