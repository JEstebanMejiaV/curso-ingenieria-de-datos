### Vistas materializadas y vistas simples

CREATE VIEW vw_order_payments_summary AS
SELECT
    order_id,
    COUNT(*)          AS num_payments,
    SUM(payment_value) AS total_payment
FROM olist_order_payments
GROUP BY order_id;

SELECT *
FROM vw_order_payments_summary
LIMIT 10


-- 1. Crear la vista materializada
CREATE MATERIALIZED VIEW mvw_daily_payments AS
SELECT
    o.order_purchase_timestamp::date AS order_date,
    SUM(p.payment_value)            AS total_payments,
    COUNT(DISTINCT o.order_id)      AS num_orders
FROM olist_orders o
JOIN olist_order_payments p
    ON o.order_id = p.order_id
GROUP BY o.order_purchase_timestamp::date;

-- 2. Crear índice único sobre la clave "natural" de la vista
CREATE UNIQUE INDEX idx_mvw_daily_payments_pk
    ON mvw_daily_payments (order_date);

-- 3. Refrescar concurrentemente
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_daily_payments;

CREATE EXTENSION IF NOT EXISTS pg_cron;


SELECT cron.schedule(
    'refresh_mvw_daily_payments',
    '0 * * * *',
    $$REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_daily_payments;$$
);


### Transacciones en SQL

BEGIN;

-- 1) Crear el pedido usando un customer_id real cualquiera
INSERT INTO olist_orders (
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp
)
SELECT
    'ORDER-TEST-1' AS order_id,
    customer_id,
    'created'      AS order_status,
    now()          AS order_purchase_timestamp
FROM olist_customers
LIMIT 1;

-- 2) Crear ítems con product_id reales
INSERT INTO olist_order_items (
    order_id,
    order_item_id,
    product_id,
    price,
    freight_value
)
SELECT
    'ORDER-TEST-1' AS order_id,
    1              AS order_item_id,
    product_id,
    100.00         AS price,
    10.00          AS freight_value
FROM olist_products
LIMIT 1;

-- 3) Registrar pago
INSERT INTO olist_order_payments (
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
)
VALUES (
    'ORDER-TEST-1',
    1,
    'credit_card',
    1,
    110.00
);

COMMIT;

-- Simulación de un pago fallido con ROLLBACK

BEGIN;

UPDATE olist_orders
SET order_status = 'processing'
WHERE order_id = 'ORDER-101';

INSERT INTO olist_order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
VALUES ('ORDER-101', 1, 'credit_card', 1, 300.00);

/* La tarjeta fue rechazada, no queremos aplicar nada */

ROLLBACK;


### Consultas SQL con funciones ventana (window functions)

SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_value,
    COUNT(*) OVER (PARTITION BY order_id) AS num_payments_for_order
FROM olist_order_payments;


with seq as (
SELECT
        order_id,
        payment_sequential,
        payment_type,
        payment_value,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY payment_sequential
        ) AS rn
    FROM olist_order_payments
)
SELECT *
FROM seq
WHERE rn = 1;



SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    SUM(payment_value) OVER (PARTITION BY order_id) AS order_total,
    payment_value
    / NULLIF(SUM(payment_value) OVER (PARTITION BY order_id), 0) AS pct_of_order
FROM olist_order_payments
ORDER BY order_id, payment_sequential;


WITH items_with_category AS (
    SELECT
        oi.order_id,
        oi.product_id,
        oi.price,
        p.product_category_name
    FROM olist_order_items AS oi
    JOIN olist_products AS p
        ON oi.product_id = p.product_id
), rnk_cat as(
SELECT
        product_category_name,
        product_id,
        SUM(price) AS revenue,
        RANK() OVER (
            PARTITION BY product_category_name
            ORDER BY SUM(price) DESC
        ) AS rnk
    FROM items_with_category
    GROUP BY
        product_category_name,
        product_id
)
SELECT
    product_category_name,
    product_id,
    revenue,
    rnk
FROM rnk_cat
WHERE rnk <= 3
ORDER BY product_category_name, rnk;