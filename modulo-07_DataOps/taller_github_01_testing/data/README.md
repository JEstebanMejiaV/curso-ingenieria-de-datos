# Datos de Ejemplo

Este directorio contiene datos sintéticos de transacciones de e-commerce para practicar testing.

## Archivo: transactions.csv

Contiene 25 transacciones de ejemplo con la siguiente estructura:

### Columnas

- **transaction_id**: Identificador único de la transacción (formato: TXN001, TXN002, ...)
- **amount**: Monto total de la transacción en dólares (número decimal)
- **quantity**: Cantidad de productos comprados (número entero >= 1)
- **date**: Fecha de la transacción (formato: YYYY-MM-DD)
- **status**: Estado de la transacción (completed, pending, cancelled)

### Ejemplos de Registros

```csv
transaction_id,amount,quantity,date,status
TXN001,150.50,2,2024-01-15,completed
TXN002,89.99,1,2024-01-15,completed
TXN003,250.00,5,2024-01-16,completed
```

### Reglas de Validación

1. **transaction_id**: Debe ser único
2. **amount**: Debe ser >= 0
3. **quantity**: Debe ser >= 1
4. **date**: Debe ser formato válido YYYY-MM-DD
5. **status**: Debe ser uno de: completed, pending, cancelled

## Uso en Tests

Estos datos pueden ser usados para:
- Testear funciones de cálculo de totales
- Testear funciones de aplicación de descuentos
- Practicar lectura de archivos CSV
- Validar reglas de negocio
