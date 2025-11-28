-- olist_denormalized_table.sql
-- Tabla desnormalizada a nivel de línea de pedido (order_id + order_item_id)
-- Pensada para análisis en motores analíticos (ej. reporting, BI, etc.).
-- Dataset base: Olist en PostgreSQL.

CREATE SCHEMA IF NOT EXISTS analytics;

DROP TABLE IF EXISTS analytics.olist_orders_denorm;

CREATE TABLE analytics.olist_orders_denorm AS
WITH payments AS (
    SELECT
        order_id,
        SUM(payment_value)              AS total_payment_value,
        COUNT(*)                        AS num_payments,
        MAX(payment_installments)       AS max_installments
    FROM olist_order_payments
    GROUP BY order_id
),
reviews AS (
    SELECT
        order_id,
        MAX(review_score)              AS review_score,
        MAX(review_creation_date)      AS review_creation_date,
        MAX(review_answer_timestamp)   AS review_answer_timestamp,
        MAX(review_comment_title)      AS review_comment_title,
        MAX(review_comment_message)    AS review_comment_message
    FROM olist_order_reviews
    GROUP BY order_id
),
customers AS (
    SELECT
        c.customer_id,
        c.customer_unique_id,
        c.customer_zip_code_prefix,
        c.customer_city,
        c.customer_state
    FROM olist_customers c
),
sellers AS (
    SELECT
        s.seller_id,
        s.seller_zip_code_prefix,
        s.seller_city,
        s.seller_state
    FROM olist_sellers s
),
products AS (
    SELECT
        p.product_id,
        p.product_category_name,
        p.product_name_lenght,
        p.product_description_lenght,
        p.product_photos_qty,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM olist_products p
)
SELECT
    -- Grano de la tabla
    o.order_id,
    oi.order_item_id,

    -- Fechas y estado de la orden
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    -- Cliente
    o.customer_id,
    c.customer_unique_id,
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state,

    -- Vendedor
    oi.seller_id,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state,

    -- Producto
    oi.product_id,
    p.product_category_name,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,

    -- Métricas de la línea (item)
    oi.price,
    oi.freight_value,

    -- Pagos agregados a nivel de orden
    pay.total_payment_value,
    pay.num_payments,
    pay.max_installments,

    -- Reseñas agregadas
    r.review_score,
    r.review_creation_date,
    r.review_answer_timestamp,
    r.review_comment_title,
    r.review_comment_message
FROM olist_orders o
JOIN olist_order_items oi
    ON o.order_id = oi.order_id
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
LEFT JOIN sellers s
    ON oi.seller_id = s.seller_id
LEFT JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN payments pay
    ON o.order_id = pay.order_id
LEFT JOIN reviews r
    ON o.order_id = r.order_id;

-- Opcional: agregar índices típicos para acelerar filtros comunes

CREATE INDEX idx_olist_orders_denorm_order_purchase_timestamp
    ON analytics.olist_orders_denorm (order_purchase_timestamp);

CREATE INDEX idx_olist_orders_denorm_customer_id
    ON analytics.olist_orders_denorm (customer_id);

CREATE INDEX idx_olist_orders_denorm_seller_id
    ON analytics.olist_orders_denorm (seller_id);

CREATE INDEX idx_olist_orders_denorm_product_id
    ON analytics.olist_orders_denorm (product_id);