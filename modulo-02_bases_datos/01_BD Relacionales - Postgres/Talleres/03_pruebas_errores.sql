-- 1. Customer sin customer_id (PK/NOT NULL)
INSERT INTO olist_customers (customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
VALUES ('U-123', 5000, 'Medellín', 'CO');

-- 2. Product con peso negativo
INSERT INTO olist_products (product_id, product_category_name, product_weight_g)
VALUES ('TEST-PROD-001', 'electronics', -10);

-- 3. Order payment con valor negativo
INSERT INTO olist_order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
VALUES ('ORDER-002', 1, 'boleto', 1, -50);

-- 4. Order con customer_id inexistente
INSERT INTO olist_orders (order_id, customer_id, order_status, order_purchase_timestamp)
VALUES ('ORDER-FAKE-001', 'CUST-FAKE-999', 'delivered', NOW());

-- 5. Order_item con product_id inexistente
INSERT INTO olist_order_items (order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value)
VALUES ('ORDER-001', 1, 'PROD-FAKE-999', 'SELLER-001', NOW(), 100, 10);

-- 6. Order_payment con order_id inexistente
INSERT INTO olist_order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
VALUES ('ORDER-FAKE-002', 1, 'credit_card', 1, 200);
