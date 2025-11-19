# Contrato de datos: tabla `sales`

Este documento describe la tabla de ventas que genera el pipeline `etl_sales_daily.py`.

## Columnas

| Columna      | Tipo   | Descripción                             | Reglas básicas                           |
|-------------|--------|-----------------------------------------|------------------------------------------|
| order_id    | string | Identificador único del pedido          | No nulo, único por día                   |
| customer_id | string | Identificador del cliente               | No nulo                                  |
| amount      | float  | Importe de la orden en moneda local     | No nulo                                  |
| order_date  | date   | Fecha de la orden                       | No nulo                                  |

## Reglas de calidad iniciales

- `amount` debe ser mayor o igual que cero.
- `order_date` debe ser una fecha válida en formato `YYYY-MM-DD`.
- El archivo raw debe contener cabeceras exactamente iguales a los nombres de columna.
- Esto e un prueba de conflicto en main

Durante el taller irás ampliando este contrato para reflejar nuevas columnas y reglas de negocio.
