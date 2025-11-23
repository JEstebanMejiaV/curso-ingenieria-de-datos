-- 02_olist_load.sql
-- Carga de datos CSV de Olist
-- IMPORTANTE: este script asume que ya estás conectado a la base `olist`.

-- 1. Tablas de traducción y dimensiones

-- 02_olist_load.sql
-- Carga de datos CSV de Olist
-- IMPORTANTE: este script asume que ya estás conectado a la base `olist`.

-- 1. Tablas de traducción y dimensiones

\COPY product_category_name_translation FROM '/data/olist/product_category_name_translation.csv' WITH (FORMAT csv, HEADER true);

\COPY olist_geolocation                FROM '/data/olist/olist_geolocation_dataset.csv'      WITH (FORMAT csv, HEADER true);

\COPY olist_customers                  FROM '/data/olist/olist_customers_dataset.csv'        WITH (FORMAT csv, HEADER true);

\COPY olist_sellers                    FROM '/data/olist/olist_sellers_dataset.csv'          WITH (FORMAT csv, HEADER true);

\COPY olist_products                   FROM '/data/olist/olist_products_dataset.csv'         WITH (FORMAT csv, HEADER true);

-- 2. Tablas de hechos

\COPY olist_orders                     FROM '/data/olist/olist_orders_dataset.csv'           WITH (FORMAT csv, HEADER true);

\COPY olist_order_items                FROM '/data/olist/olist_order_items_dataset.csv'      WITH (FORMAT csv, HEADER true);

\COPY olist_order_payments             FROM '/data/olist/olist_order_payments_dataset.csv'   WITH (FORMAT csv, HEADER true);

\COPY olist_order_reviews              FROM '/data/olist/olist_order_reviews_dataset.csv'    WITH (FORMAT csv, HEADER true);
