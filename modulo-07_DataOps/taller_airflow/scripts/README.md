# Scripts del Taller de Airflow

Este directorio contiene scripts de utilidad para el taller de Apache Airflow.

## Scripts Disponibles

### 1. generate_sample_data.py

Script para generar datos sintéticos realistas para el caso de uso de e-commerce.

**Uso:**
```bash
python scripts/generate_sample_data.py
```

**Datos Generados:**
- **1000 clientes** con nombres, emails y fechas de registro
- **100 productos** distribuidos en 10 categorías
- **10,000 transacciones** distribuidas en los últimos 30 días

**Archivos de Salida:**
- `data/raw/customers.csv`
- `data/raw/products.csv`
- `data/raw/transactions.csv`

**Anomalías Intencionales:**

El script incluye anomalías intencionales para practicar validaciones de calidad de datos:

| Tipo de Anomalía | Porcentaje | Descripción |
|------------------|------------|-------------|
| IDs duplicados | ~3-4% | Clientes y transacciones con IDs repetidos |
| Valores nulos | ~1-3% | Nombres, emails, precios y montos nulos |
| Valores fuera de rango | ~5% | Precios y montos negativos o excesivamente altos |
| Referencias inválidas | ~2% | customer_id y product_id que no existen |
| Cantidades inválidas | ~2% | Cantidades nulas, negativas o cero |

**Dependencias:**
```bash
pip install Faker==22.0.0
```

### 2. init_db.sql

Script SQL para inicializar la base de datos con los esquemas y tablas necesarios.

**Uso:**
```bash
# Desde el contenedor de Postgres
psql -U airflow -d airflow -f /opt/airflow/scripts/init_db.sql

# O desde docker-compose
docker-compose exec postgres psql -U airflow -d airflow -f /opt/airflow/scripts/init_db.sql
```

**Esquemas Creados:**
- `raw`: Datos sin procesar
- `processed`: Datos limpios y transformados
- `analytics`: Métricas agregadas
- `audit`: Logs y auditoría

### 3. test_validation_utils.py

Script de pruebas para las funciones de validación de calidad de datos.

**Uso:**
```bash
python scripts/test_validation_utils.py
```

## Notas

- Los datos generados son completamente sintéticos y no representan información real
- Las anomalías están diseñadas para ser detectadas por los DAGs de validación de calidad
- Se recomienda regenerar los datos si se necesita un conjunto limpio para pruebas
