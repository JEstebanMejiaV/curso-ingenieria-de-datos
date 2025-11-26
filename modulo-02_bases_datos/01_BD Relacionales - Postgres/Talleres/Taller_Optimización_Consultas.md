# Ejercicio: Análisis de rendimiento de entregas y ventas con el dataset Olist

La empresa Olist quiere entender mejor el comportamiento de sus pedidos entregados en los últimos meses, para responder preguntas de negocio de los equipos de Operaciones y Marketing.
En particular, están interesados en:

- Cómo se comportan las ventas por categoría de producto y estado del cliente.

- Cuántos pedidos y clientes únicos atienden por mes.

- Cuánto dinero generan (ingresos brutos por pedido).

- Qué tan frecuentes son los retrasos de entrega respecto a la fecha estimada.

- Qué proporción de los pagos se hace con tarjeta de crédito frente al total pagado.


> Consigna> Optimizar la siguinte consulta:

```sql
WITH recent_delivered_orders AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_purchase_timestamp::date        AS purchase_date,
        o.order_delivered_customer_date::date   AS delivered_date,
        o.order_estimated_delivery_date::date   AS estimated_date
    FROM olist_orders AS o
    WHERE o.order_status = 'delivered'
      -- Ventana de los últimos 6 meses *dentro del dataset*,
      -- no desde la fecha actual del servidor
      AND o.order_purchase_timestamp >= (
            SELECT max(order_purchase_timestamp) - INTERVAL '6 months'
            FROM olist_orders
          )
      -- Por seguridad, descartamos entregas/estimadas nulas
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
),
orders_with_delay AS (
    SELECT
        r.*,
        (r.delivered_date - r.estimated_date) AS delivery_delay_days
    FROM recent_delivered_orders AS r
),
order_revenue AS (
    -- ingresos por pedido
    SELECT
        oi.order_id,
        SUM(oi.price + oi.freight_value) AS order_gross_revenue
    FROM olist_order_items AS oi
    GROUP BY oi.order_id
),
payments_by_order AS (
    -- pagos totales y por tarjeta de crédito por pedido
    SELECT
        op.order_id,
        SUM(op.payment_value) AS total_payment_value,
        SUM(
            CASE WHEN op.payment_type = 'credit_card'
                 THEN op.payment_value
                 ELSE 0 END
        ) AS credit_card_value
    FROM olist_order_payments AS op
    GROUP BY op.order_id
),
customer_region AS (
    -- nos quedamos con clientes de SP y RJ
    SELECT
        c.customer_id,
        c.customer_state
    FROM olist_customers AS c
    WHERE c.customer_state IN ('SP', 'RJ')
),
order_fact AS (
    -- “hecho” de órdenes ya enriquecido con región, pagos y retraso
    SELECT
        owd.order_id,
        owd.customer_id,
        cr.customer_state,
        owd.purchase_date,
        owd.delivery_delay_days,
        orv.order_gross_revenue,
        pb.total_payment_value,
        pb.credit_card_value
    FROM orders_with_delay     AS owd
    JOIN customer_region       AS cr  ON cr.customer_id = owd.customer_id
    JOIN order_revenue         AS orv ON orv.order_id   = owd.order_id
    JOIN payments_by_order     AS pb  ON pb.order_id    = owd.order_id
),
order_with_product AS (
    -- asociamos cada orden con sus productos y la categoría
    SELECT
        ofa.*,
        p.product_id,
        COALESCE(t.product_category_name_english,
                 p.product_category_name) AS product_category
    FROM order_fact                AS ofa
    JOIN olist_order_items         AS oi ON oi.order_id   = ofa.order_id
    JOIN olist_products            AS p  ON p.product_id  = oi.product_id
    LEFT JOIN product_category_name_translation AS t
           ON t.product_category_name = p.product_category_name
)
SELECT
    product_category,
    customer_state,
    date_trunc('month', purchase_date) AS purchase_month,
    COUNT(DISTINCT order_id)           AS num_orders,
    COUNT(DISTINCT customer_id)        AS num_customers,
    SUM(order_gross_revenue)           AS total_gross_revenue,
    AVG(delivery_delay_days)           AS avg_delivery_delay_days,
    SUM(credit_card_value)
        / NULLIF(SUM(total_payment_value), 0) AS credit_card_share
FROM order_with_product
GROUP BY
    product_category,
    customer_state,
    date_trunc('month', purchase_date)
HAVING COUNT(DISTINCT order_id) >= 50
ORDER BY
    total_gross_revenue DESC,
    purchase_month DESC
LIMIT 50;
```
