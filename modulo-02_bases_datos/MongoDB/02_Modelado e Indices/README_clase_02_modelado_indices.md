# Clase 2 – Modelado de datos e índices en MongoDB (para Ingeniería de Datos)

En esta clase nos enfocamos en dos temas clave para ingeniería de datos:

- Cómo modelar datos en MongoDB (documentos, embebidos vs referencias).
- Cómo crear índices y analizar su impacto en las consultas.

Usaremos el mismo dominio de ventas y órdenes de la Clase 1.

---

## 1. Objetivos de la clase

Al finalizar la sesión, deberías ser capaz de:

- Comparar un modelo relacional simple con su equivalente en documentos MongoDB.
- Decidir cuándo embeber información y cuándo referenciar otra colección.
- Identificar patrones de modelado típicos (one-to-many, eventos, series de tiempo).
- Crear índices simples y compuestos en colecciones.
- Interpretar un explain básico para ver si una consulta está usando índice o no.

---

## 2. Prerrequisitos

Se asume que ya tienes:

- MongoDB corriendo (Docker o instalación local).
- Base de datos `sales_db`.
- Colecciones:
  - `orders` cargada desde `data/sales_orders_sample.json` (Clase 1).
  - `customers` cargada desde `data/customers_sample.json` o creada manualmente.

Verificación rápida en una consola de MongoDB (DataGrip, mongosh, etc.):

```js
use("sales_db");
db.orders.find().limit(3);
db.customers.find().limit(3);
```

---

## 3. Relacional vs documentos: ejemplo de modelado

### 3.1. Modelo relacional clásico

En un esquema SQL típico podríamos tener:

- Tabla `orders`
  - `order_id` (PK)
  - `customer_id` (FK a `customers`)
  - `created_at`
  - `status`
  - `total_amount`
- Tabla `order_items`
  - `order_id` (FK a `orders`)
  - `sku`
  - `name`
  - `qty`
  - `price`
- Tabla `customers`
  - `customer_id` (PK)
  - `name`
  - `city`
  - `segment`
  - `signup_date`

Para ver una orden completa con sus ítems harías un JOIN entre `orders` y `order_items`.

### 3.2. Modelo equivalente en MongoDB

En MongoDB, la colección `orders` ya incluye los ítems embebidos:

```js
db.orders.findOne();
```

Ejemplo típico:

```json
{
  "order_id": "O-1001",
  "customer_id": "CUST-001",
  "items": [
    { "sku": "SKU-001", "name": "Silla ergonómica", "qty": 1, "price": 150.0 },
    { "sku": "SKU-002", "name": "Escritorio", "qty": 1, "price": 300.0 }
  ],
  "total_amount": 450.0,
  "status": "paid",
  "created_at": "2025-01-10T10:15:00Z",
  "test_user": false
}
```

Aquí:

- `order_items` está embebido como el array `items`.
- `customers` sigue en una colección aparte, referenciada por `customer_id`.

---

## 4. Embebido vs referencia

### 4.1. Cuándo embeber

Es buena idea embeber cuando:

- La relación es one-to-few (pocos elementos).
- Los datos embebidos casi siempre se usan junto al documento padre.
- No necesitas consultar los datos embebidos de forma independiente.

Ejemplo: `items` dentro de `orders`.

Ventajas:

- Una sola lectura para obtener la orden completa.
- Menos joins que hacer en el cliente.

Desventajas:

- Documentos más grandes.
- Si el array crece demasiado, puede volverse problemático.

### 4.2. Cuándo referenciar

Conviene referenciar otra colección cuando:

- La entidad vive por sí misma y se consulta aparte.
- Es compartida por muchos documentos (catálogo de productos, clientes).
- Cambia con frecuencia y no quieres actualizar copias embebidas.

Ejemplo: `customers` como colección independiente, referenciada por `customer_id`.

---

## 5. Patrones de modelado útiles

### 5.1. One-to-many (órdenes e ítems)

- `orders` con `items` embebidos, como en nuestro dataset.
- Alternativa: colección `order_items` si hay millones de ítems y quieres analizarlos sin la orden completa.

### 5.2. Eventos (logs, clickstream)

Patrón típico:

```json
{
  "event_id": "EVT-123",
  "user_id": "USR-001",
  "type": "page_view",
  "url": "/home",
  "timestamp": "2025-01-15T10:00:00Z",
  "metadata": {
    "browser": "Chrome",
    "device": "mobile"
  }
}
```

Útil para:

- Agregaciones por día, canal, campaña.
- Carga posterior a un data lake.

### 5.3. Series de tiempo agregadas

En vez de un documento por punto de dato, se pueden hacer documentos por día con arrays de lecturas, o colecciones agregadas como `daily_sales`, que verás en la Clase 3.

---

## 6. Índices en MongoDB

### 6.1. Índice por defecto

Todas las colecciones tienen un índice por defecto sobre `_id`:

```js
db.orders.getIndexes();
```

Verás algo como:

```json
[
  {
    "v": 2,
    "key": { "_id": 1 },
    "name": "_id_"
  }
]
```

### 6.2. Índices simples

Índice por `customer_id` para acelerar consultas por cliente:

```js
db.orders.createIndex({ customer_id: 1 });
```

Índice por `status`:

```js
db.orders.createIndex({ status: 1 });
```

### 6.3. Índices compuestos

Útiles cuando consultas filtran por varios campos a la vez.

Ejemplo clásico en este dominio: órdenes de un cliente ordenadas por fecha de creación descendente.

```js
db.orders.createIndex({ customer_id: 1, created_at: -1 });
```

Consulta que se beneficia:

```js
db.orders.find(
  { customer_id: "CUST-001" }
).sort({ created_at: -1 });
```

### 6.4. Índices únicos

Para garantizar que no se repita `order_id`:

```js
db.orders.createIndex(
  { order_id: 1 },
  { unique: true }
);
```

---

## 7. explain para ver el plan de ejecución

Queremos ver si una consulta usa índice (IXSCAN) o escaneo completo (COLLSCAN).

Ejemplo antes de crear índices:

```js
db.orders.find(
  { customer_id: "CUST-001" }
).explain("queryPlanner");
```

Luego de crear un índice por `customer_id`:

```js
db.orders.createIndex({ customer_id: 1 });

db.orders.find(
  { customer_id: "CUST-001" }
).explain("queryPlanner");
```

Puntos para comentar en clase:

- Cómo cambia el winningPlan.
- Aparición de IXSCAN cuando la consulta usa índice.

---

## 8. Ejemplo de campo embebido: shipping_address

Podemos extender el modelo añadiendo una dirección de envío embebida en `orders`:

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

db.orders.find(
  { customer_id: "CUST-001" },
  { _id: 0, order_id: 1, shipping_address: 1 }
);
```

Preguntas para el grupo:

- ¿Tiene sentido que shipping_address esté en orders y no en customers?
- ¿Qué pasaría si el cliente cambia de ciudad, pero la orden ya fue enviada?

---

## 9. Diseño conceptual extra: products y status_history

Mini caso para discusión en clase:

- La empresa quiere:
  - Un catálogo de productos `products`.
  - Un historial de cambios de estado `status_history` para cada orden.

Ejemplo de documento en `products`:

```json
{
  "sku": "SKU-001",
  "name": "Silla ergonómica",
  "category": "Sillas",
  "price_list": 150.0,
  "active": true
}
```

Ejemplo de `status_history` embebido en `orders`:

```json
"status_history": [
  { "status": "pending", "changed_at": "2025-01-10T10:15:00Z" },
  { "status": "paid", "changed_at": "2025-01-10T10:20:00Z" }
]
```

Preguntas:

- cuándo conviene poner status_history dentro de orders y cuándo en una colección aparte order_events?
- qué índices pondrías si tuvieras que analizar tiempos de ciclo por estado?

---
