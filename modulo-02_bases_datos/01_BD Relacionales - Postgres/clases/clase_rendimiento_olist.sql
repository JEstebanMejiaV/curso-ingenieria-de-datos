-- Clase: Rendimiento y optimización de consultas con Olist
-- Archivo de apoyo: clase_rendimiento_olist.sql
-- Este archivo contiene ejemplos de consultas, índices y ANALYZE
-- para que el docente o los estudiantes los ejecuten en PostgreSQL.

------------------------------------------------------------
-- 1. Ejemplo de join base entre orders y customers
------------------------------------------------------------

EXPLAIN ANALYZE
SELECT
    o.order_id,
    o.order_purchase_timestamp,
    c.customer_city,
    c.customer_state
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id;


------------------------------------------------------------
-- 2. Mismo join con filtro de fechas
------------------------------------------------------------

EXPLAIN ANALYZE
SELECT
    o.order_id,
    o.order_purchase_timestamp,
    c.customer_city,
    c.customer_state
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id
WHERE o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp < '2017-02-01';


------------------------------------------------------------
-- 3. Índice compuesto en order_status y order_purchase_timestamp
------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_olist_orders_status_date
    ON olist_orders (order_status, order_purchase_timestamp);

-- Volver a medir:

EXPLAIN ANALYZE
SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp
FROM olist_orders o
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp < '2017-02-01';


------------------------------------------------------------
-- 4. Top productos más vendidos
------------------------------------------------------------

EXPLAIN ANALYZE
SELECT
    oi.product_id,
    COUNT(*) AS num_items
FROM olist_order_items oi
GROUP BY oi.product_id
ORDER BY num_items DESC
LIMIT 20;

-- Índice en product_id

CREATE INDEX IF NOT EXISTS idx_olist_order_items_product
    ON olist_order_items (product_id);

-- Volver a medir

EXPLAIN ANALYZE
SELECT
    oi.product_id,
    COUNT(*) AS num_items
FROM olist_order_items oi
GROUP BY oi.product_id
ORDER BY num_items DESC
LIMIT 20;


------------------------------------------------------------
-- 5. SELECT * vs seleccionar solo columnas necesarias
------------------------------------------------------------

-- Versión amplia
EXPLAIN ANALYZE
SELECT
    *
FROM olist_orders o
JOIN olist_order_items oi ON o.order_id = oi.order_id
JOIN olist_products p ON oi.product_id = p.product_id
WHERE o.order_purchase_timestamp::date = '2017-01-10';


-- Versión optimizada (menos columnas)
EXPLAIN ANALYZE
SELECT
    o.order_id,
    o.order_purchase_timestamp,
    p.product_category_name,
    oi.price
FROM olist_orders o
JOIN olist_order_items oi ON o.order_id = oi.order_id
JOIN olist_products p ON oi.product_id = p.product_id
WHERE o.order_purchase_timestamp::date = '2017-01-10';


------------------------------------------------------------
-- 6. Función en columna indexada vs rango de fechas
------------------------------------------------------------

-- Opción con función (peor para índice)
EXPLAIN ANALYZE
SELECT
    o.order_id,
    o.order_purchase_timestamp
FROM olist_orders o
WHERE o.order_purchase_timestamp::date = '2017-01-10';


-- Crear índice sobre order_purchase_timestamp
CREATE INDEX IF NOT EXISTS idx_olist_orders_purchase_ts
    ON olist_orders (order_purchase_timestamp);

-- Opción con rango (mejor para índice)
EXPLAIN ANALYZE
SELECT
    o.order_id,
    o.order_purchase_timestamp
FROM olist_orders o
WHERE o.order_purchase_timestamp >= '2017-01-10'
  AND o.order_purchase_timestamp < '2017-01-11';


------------------------------------------------------------
-- 7. Paginación con OFFSET
------------------------------------------------------------

EXPLAIN ANALYZE
SELECT
    o.order_id,
    o.order_purchase_timestamp,
    c.customer_city
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id
ORDER BY o.order_purchase_timestamp DESC
LIMIT 50 OFFSET 5000;


------------------------------------------------------------
-- 8. Paginación tipo keyset (ejemplo conceptual)
------------------------------------------------------------

-- Supongamos que '2018-01-01 10:00:00' es la última fecha de la página anterior
EXPLAIN ANALYZE
SELECT
    o.order_id,
    o.order_purchase_timestamp,
    c.customer_city
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id
WHERE o.order_purchase_timestamp < '2018-01-01 10:00:00'
ORDER BY o.order_purchase_timestamp DESC
LIMIT 50;


------------------------------------------------------------
-- 9. Estadísticas: ANALYZE
------------------------------------------------------------

-- Actualizar estadísticas de las tablas principales
ANALYZE olist_orders;
ANALYZE olist_order_items;
ANALYZE olist_customers;
ANALYZE olist_products;
ANALYZE olist_sellers;
ANALYZE olist_order_payments;

-- Después de esto, volver a ejecutar algunas de las consultas anteriores
-- con EXPLAIN ANALYZE y observar si cambian los planes o las filas estimadas.
