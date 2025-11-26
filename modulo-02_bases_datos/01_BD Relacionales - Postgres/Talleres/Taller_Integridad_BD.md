# Taller: Reglas de integridad e integridad referencial con Olist (PostgreSQL)

## Contexto del taller

Trabajas como ingeniero o ingeniera de datos en el equipo de analítica de un e-commerce (Olist).  
La base de datos fue cargada rápidamente desde archivos CSV y **casi no tiene reglas de integridad**.

Tu trabajo en este taller es:

- Diseñar y aplicar **reglas de integridad** a nivel de tabla.
- Diseñar y aplicar **reglas de integridad referencial** entre tablas relacionadas.
- Probar que las reglas funcionan intentando insertar datos “malos”.

---


## 1. Parte A: Reglas de integridad en una sola tabla

### 1.1. Diseñar constraints para `olist_customers`

Supón que tu tabla actual (sin constraints) es algo así:

```sql
CREATE TABLE IF NOT EXISTS olist_customers (
    customer_id              VARCHAR(50),
    customer_unique_id       VARCHAR(50),
    customer_zip_code_prefix INT,
    customer_city            VARCHAR(100),
    customer_state           VARCHAR(10)
);
```

#### Actividad 1.2 – Propuesta de reglas

Define reglas de integridad **a nivel de tabla** para `olist_customers`:

- Elige:
  - `PRIMARY KEY`
  - Columnas `NOT NULL`
  - Columnas `UNIQUE` (por ejemplo, `customer_unique_id`).
  - Algún `CHECK` razonable, por ejemplo para `customer_state`.

Escribe tu propuesta como DDL:

```sql
-- OPCIÓN 1: crear la tabla desde cero con constraints
DROP TABLE IF EXISTS olist_customers CASCADE;

CREATE TABLE olist_customers (
    customer_id              VARCHAR(50)      -- COMPLETAR
    customer_unique_id       VARCHAR(50)      -- COMPLETAR
    customer_zip_code_prefix INT              -- COMPLETAR
    customer_city            VARCHAR(100)     -- COMPLETAR
    customer_state           VARCHAR(10)      -- COMPLETAR
    -- COMPLETAR: PRIMARY KEY, UNIQUE, CHECK, etc.
);
```


#### Actividad 3 – Ajustar una tabla ya existente

Si la tabla ya existe **sin constraints**, debes usar `ALTER TABLE`:

```sql
ALTER TABLE olist_customers
    -- COMPLETAR: agregar PRIMARY KEY, NOT NULL, UNIQUE, CHECK, etc.
;
```

---

### 4 Diseñar constraints para `olist_products`

Supón una definición simplificada:

```sql
CREATE TABLE IF NOT EXISTS olist_products (
    product_id              VARCHAR(50),
    product_category_name   VARCHAR(100),
    product_weight_g        INT,
    product_length_cm       INT,
    product_height_cm       INT,
    product_width_cm        INT
);
```

#### Actividad 4.2 – Reglas de integridad

1. Define:
   - `PRIMARY KEY` para `olist_products`.
   - Columnas `NOT NULL` (al menos para identificadores).
2. Define al menos 2 reglas `CHECK`. Por ejemplo:
   - Peso y dimensiones no pueden ser negativos.
   - Podrías permitir `NULL`, pero si hay valor, que sea mayor que cero.

Escribe tu propuesta como DDL (puedes usar `ALTER TABLE` si la tabla ya existe):

```sql
ALTER TABLE olist_products
    -- COMPLETAR: agregar PRIMARY KEY (product_id),
    -- NOT NULL a columnas clave,
    -- y un CHECK para validar medidas positivas.
;
```

---

## 5. Parte B: Integridad referencial

Ahora trabajamos las **relaciones entre tablas**.

Relaciones típicas (puedes ajustarlas según tu modelo):

- `olist_orders.customer_id` referencia a `olist_customers.customer_id`.
- `olist_order_items.order_id` referencia a `olist_orders.order_id`.
- `olist_order_items.product_id` referencia a `olist_products.product_id`.
- `olist_order_items.seller_id` referencia a `olist_sellers.seller_id`.
- `olist_order_payments.order_id` referencia a `olist_orders.order_id`.

### 5.1. Relación `orders` y `customers`

Definición sin constraints:

```sql
CREATE TABLE IF NOT EXISTS olist_orders (
    order_id                        VARCHAR(50),
    customer_id                     VARCHAR(50),
    order_status                    VARCHAR(20),
    order_purchase_timestamp        TIMESTAMP,
    order_approved_at               TIMESTAMP,
    order_delivered_carrier_date    TIMESTAMP,
    order_delivered_customer_date   TIMESTAMP
);
```

#### Actividad 5.1.1 – Llave primaria y foránea

1. Define:
   - `PRIMARY KEY` para `olist_orders`.
   - `FOREIGN KEY` de `olist_orders.customer_id` que apunte a `olist_customers(customer_id)`.

2. Elige una política de borrado y actualización:

   - `ON DELETE RESTRICT` o `NO ACTION`
   - `ON DELETE CASCADE`
   - `ON DELETE SET NULL`


```sql
ALTER TABLE olist_orders
    -- COMPLETAR: agregar PRIMARY KEY (order_id);

ALTER TABLE olist_orders
    -- COMPLETAR: agregar FOREIGN KEY (customer_id)
    --             REFERENCES olist_customers (customer_id)
    --             ON DELETE ...;
```

---

### 5.2. `order_items` como tabla de detalle

Definición simplificada:

```sql
CREATE TABLE IF NOT EXISTS olist_order_items (
    order_id             VARCHAR(50),
    order_item_id        INT,
    product_id           VARCHAR(50),
    seller_id            VARCHAR(50),
    shipping_limit_date  TIMESTAMP,
    price                NUMERIC(10,2),
    freight_value        NUMERIC(10,2)
);
```

#### Actividad 5.2.1 – Clave primaria compuesta y FKs

1. Propón una `PRIMARY KEY` razonable para `olist_order_items`.  
   Pista: un pedido puede tener varios ítems.

2. Define las llaves foráneas:

   - `order_id` referencia a `olist_orders(order_id)`.
   - `product_id` referencia a `olist_products(product_id)`.
   - `seller_id` referencia a `olist_sellers(seller_id)`.


```sql
ALTER TABLE olist_order_items
    -- COMPLETAR: PRIMARY KEY (order_id, order_item_id) u otra que decidas;

ALTER TABLE olist_order_items
    -- COMPLETAR: FK de order_id a olist_orders(order_id);

ALTER TABLE olist_order_items
    -- COMPLETAR: FK de product_id a olist_products(product_id);

ALTER TABLE olist_order_items
    -- COMPLETAR: FK de seller_id a olist_sellers(seller_id);
```


#### Actividad 5.2.2 – Debate de políticas de borrado


- ¿Es buena idea usar `ON DELETE CASCADE` en la FK de `order_id`?
- ¿Qué pasaría si alguien borra un `order` por error?
- ¿Qué alternativas propondrías en un sistema real?

---

### 5.3. `order_payments` y `orders`

Definición simplificada:

```sql
CREATE TABLE IF NOT EXISTS olist_order_payments (
    order_id              VARCHAR(50),
    payment_sequential    INT,
    payment_type          VARCHAR(50),
    payment_installments  INT,
    payment_value         NUMERIC(10,2)
);
```

#### Actividad 5.3.1 – Clave compuesta, CHECK y FK

1. Elige una `PRIMARY KEY` (por ejemplo, `(order_id, payment_sequential)`).
2. Define un `CHECK` para asegurar que `payment_value` sea mayor que cero.
3. Define una `FOREIGN KEY` desde `order_id` a `olist_orders(order_id)`.


```sql
ALTER TABLE olist_order_payments
    -- COMPLETAR: PRIMARY KEY (order_id, payment_sequential);

ALTER TABLE olist_order_payments
    -- COMPLETAR: CHECK para asegurar payment_value > 0;

ALTER TABLE olist_order_payments
    -- COMPLETAR: FK de order_id a olist_orders(order_id);
```

---

## 6. Parte C: Probar las reglas con datos “malos”

El objetivo de esta parte es **forzar errores** y leer los mensajes que genera PostgreSQL.

### 6.1. Pruebas de integridad simple

#### Actividad 6.1.1 – NOT NULL y CHECK

Escribe `INSERT` que deban fallar y guárdalos en `03_pruebas_errores.sql`:

1. Insertar un `customer` sin `customer_id` (si lo marcaste `NOT NULL` o `PRIMARY KEY`).
2. Insertar un `product` con `product_weight_g = -10`.
3. Insertar un `order_payment` con `payment_value = 0` o negativo.

Ejemplo orientativo (ajusta según tus constraints):

```sql
-- Ejemplo: debe disparar un CHECK o NOT NULL
INSERT INTO olist_products (product_id, product_weight_g)
VALUES ('TEST-PROD-001', -10);
```

---

### 6.2. Pruebas de integridad referencial

#### Actividad 6.2.1 – Foreign keys

Escribe `INSERT` que deban fallar y guárdalos también en `03_pruebas_errores.sql`:

1. Insertar un `order` con `customer_id` que no exista en `olist_customers`.
2. Insertar un `order_item` con `product_id` que no exista en `olist_products`.
3. Insertar un `order_payment` con `order_id` inexistente en `olist_orders`.

Ejemplo orientativo:

```sql
INSERT INTO olist_orders (order_id, customer_id, order_status)
VALUES ('ORDER-FAKE-001', 'CUST-FAKE-999', 'delivered');
```

> - Qué constraint se menciona en el error.
> - Cómo lo solucionarías (insertar primero la fila padre, corregir dato, etc.).

---

## 7. Parte D: Preguntas de reflexión

1. ¿Qué riesgos hay en **no** definir reglas de integridad en una base analítica, si “igual se limpia en el ETL”?
2. En un entorno de microservicios, ¿qué ventajas y desventajas ves en:
   - Poner las reglas de integridad solo en la base de datos.
   - Ponerlas solo en el código de los servicios.
   - Tener una combinación de ambas?

---

