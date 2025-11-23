-- 01_olist_schema.sql
-- Esquema de la base de datos Olist (todas las tablas principales)
-- IMPORTANTE: este script asume que ya estás conectado a la base de datos `olist`.
-- El contenedor de Postgres se inicializa con POSTGRES_DB=olist, así que se ejecutará ahí.

-- 1. Borrar tablas si ya existen (orden respetando claves foráneas)
DROP TABLE IF EXISTS olist_order_reviews CASCADE;
DROP TABLE IF EXISTS olist_order_payments CASCADE;
DROP TABLE IF EXISTS olist_order_items CASCADE;
DROP TABLE IF EXISTS olist_orders CASCADE;
DROP TABLE IF EXISTS olist_customers CASCADE;
DROP TABLE IF EXISTS olist_products CASCADE;
DROP TABLE IF EXISTS olist_sellers CASCADE;
DROP TABLE IF EXISTS olist_geolocation CASCADE;
DROP TABLE IF EXISTS product_category_name_translation CASCADE;

-- 2. Tablas de traducción y dimensiones

CREATE TABLE product_category_name_translation (
    product_category_name           VARCHAR(100) PRIMARY KEY,
    product_category_name_english   VARCHAR(100)
);

CREATE TABLE olist_geolocation (
    geolocation_zip_code_prefix INTEGER,
    geolocation_lat             NUMERIC(9,6),
    geolocation_lng             NUMERIC(9,6),
    geolocation_city            VARCHAR(100),
    geolocation_state           CHAR(2)
);

CREATE TABLE olist_customers (
    customer_id              VARCHAR(50) PRIMARY KEY,
    customer_unique_id       VARCHAR(50),
    customer_zip_code_prefix INTEGER,
    customer_city            VARCHAR(100),
    customer_state           CHAR(2)
);

CREATE TABLE olist_sellers (
    seller_id              VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city            VARCHAR(100),
    seller_state           CHAR(2)
);

CREATE TABLE olist_products (
    product_id                    VARCHAR(50) PRIMARY KEY,
    product_category_name         VARCHAR(100),
    product_name_lenght           INTEGER,
    product_description_lenght    INTEGER,
    product_photos_qty            INTEGER,
    product_weight_g              INTEGER,
    product_length_cm             INTEGER,
    product_height_cm             INTEGER,
    product_width_cm              INTEGER
);

-- 3. Tablas de hechos

CREATE TABLE olist_orders (
    order_id                      VARCHAR(50) PRIMARY KEY,
    customer_id                   VARCHAR(50) REFERENCES olist_customers(customer_id),
    order_status                  VARCHAR(20),
    order_purchase_timestamp      TIMESTAMP,
    order_approved_at             TIMESTAMP,
    order_delivered_carrier_date  TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE olist_order_items (
    order_id            VARCHAR(50) REFERENCES olist_orders(order_id),
    order_item_id       INTEGER,
    product_id          VARCHAR(50) REFERENCES olist_products(product_id),
    seller_id           VARCHAR(50) REFERENCES olist_sellers(seller_id),
    shipping_limit_date TIMESTAMP,
    price               NUMERIC(10,2),
    freight_value       NUMERIC(10,2),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE olist_order_payments (
    order_id             VARCHAR(50) REFERENCES olist_orders(order_id),
    payment_sequential   INTEGER,
    payment_type         VARCHAR(50),
    payment_installments INTEGER,
    payment_value        NUMERIC(10,2),
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TABLE olist_order_reviews (
    review_id               VARCHAR(50) PRIMARY KEY,
    order_id                VARCHAR(50) REFERENCES olist_orders(order_id),
    review_score            SMALLINT,
    review_comment_title    TEXT,
    review_comment_message  TEXT,
    review_creation_date    TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

-- 4. Índices recomendados para consultas frecuentes

CREATE INDEX idx_orders_customer_id ON olist_orders(customer_id);
CREATE INDEX idx_orders_purchase_ts ON olist_orders(order_purchase_timestamp);
CREATE INDEX idx_items_product_id ON olist_order_items(product_id);
CREATE INDEX idx_items_seller_id ON olist_order_items(seller_id);
CREATE INDEX idx_payments_order_id ON olist_order_payments(order_id);
CREATE INDEX idx_reviews_order_id ON olist_order_reviews(order_id);
