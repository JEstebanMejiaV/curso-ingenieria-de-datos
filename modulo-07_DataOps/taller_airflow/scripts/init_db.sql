-- ============================================================================
-- Script de Inicialización de Base de Datos
-- Taller de Apache Airflow - Módulo 07 DataOps
-- ============================================================================
-- Este script crea los esquemas y tablas necesarios para el taller de Airflow
-- Arquitectura de capas: raw -> processed -> analytics + audit
-- ============================================================================

-- ============================================================================
-- SCHEMAS
-- ============================================================================

-- Schema para datos sin procesar (raw layer)
CREATE SCHEMA IF NOT EXISTS raw;

-- Schema para datos limpios y transformados (processed layer)
CREATE SCHEMA IF NOT EXISTS processed;

-- Schema para métricas agregadas y análisis (analytics layer)
CREATE SCHEMA IF NOT EXISTS analytics;

-- Schema para auditoría y logs (audit layer)
CREATE SCHEMA IF NOT EXISTS audit;

-- ============================================================================
-- RAW LAYER - Datos sin procesar
-- ============================================================================

-- Tabla de transacciones raw
CREATE TABLE IF NOT EXISTS raw.transactions (
    transaction_id VARCHAR(50),
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    transaction_date TIMESTAMP,
    amount DECIMAL(10,2),
    quantity INTEGER,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos raw
CREATE TABLE IF NOT EXISTS raw.products (
    product_id VARCHAR(50),
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10,2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de clientes raw
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id VARCHAR(50),
    customer_name VARCHAR(255),
    email VARCHAR(255),
    registration_date DATE,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PROCESSED LAYER - Datos limpios y transformados
-- ============================================================================

-- Tabla de transacciones limpias y enriquecidas
CREATE TABLE IF NOT EXISTS processed.transactions_clean (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    transaction_date TIMESTAMP,
    amount DECIMAL(10,2),
    quantity INTEGER,
    product_name VARCHAR(255),
    category VARCHAR(100),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ANALYTICS LAYER - Métricas agregadas
-- ============================================================================

-- Tabla de métricas diarias de ventas
CREATE TABLE IF NOT EXISTS analytics.daily_sales_metrics (
    metric_date DATE PRIMARY KEY,
    total_transactions INTEGER,
    total_revenue DECIMAL(12,2),
    avg_transaction_value DECIMAL(10,2),
    unique_customers INTEGER,
    top_category VARCHAR(100),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de métricas por cliente
CREATE TABLE IF NOT EXISTS analytics.customer_metrics (
    customer_id VARCHAR(50),
    metric_date DATE,
    transaction_count INTEGER,
    total_spent DECIMAL(12,2),
    avg_order_value DECIMAL(10,2),
    days_since_last_purchase INTEGER,
    PRIMARY KEY (customer_id, metric_date)
);

-- ============================================================================
-- AUDIT LAYER - Logs y auditoría
-- ============================================================================

-- Tabla de validaciones de calidad de datos
CREATE TABLE IF NOT EXISTS audit.data_quality_checks (
    check_id SERIAL PRIMARY KEY,
    dag_id VARCHAR(255),
    execution_date TIMESTAMP,
    check_name VARCHAR(255),
    check_result VARCHAR(50),
    records_checked INTEGER,
    records_failed INTEGER,
    error_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ejecuciones de pipelines
CREATE TABLE IF NOT EXISTS audit.pipeline_executions (
    execution_id SERIAL PRIMARY KEY,
    dag_id VARCHAR(255),
    execution_date TIMESTAMP,
    status VARCHAR(50),
    records_processed INTEGER,
    duration_seconds INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ÍNDICES para optimizar consultas
-- ============================================================================

-- Índices en raw layer
CREATE INDEX IF NOT EXISTS idx_raw_transactions_date ON raw.transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_raw_transactions_customer ON raw.transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_raw_transactions_product ON raw.transactions(product_id);

-- Índices en processed layer
CREATE INDEX IF NOT EXISTS idx_processed_transactions_date ON processed.transactions_clean(transaction_date);
CREATE INDEX IF NOT EXISTS idx_processed_transactions_customer ON processed.transactions_clean(customer_id);
CREATE INDEX IF NOT EXISTS idx_processed_transactions_category ON processed.transactions_clean(category);

-- Índices en analytics layer
CREATE INDEX IF NOT EXISTS idx_daily_sales_date ON analytics.daily_sales_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_customer_metrics_date ON analytics.customer_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_customer_metrics_customer ON analytics.customer_metrics(customer_id);

-- Índices en audit layer
CREATE INDEX IF NOT EXISTS idx_quality_checks_dag ON audit.data_quality_checks(dag_id);
CREATE INDEX IF NOT EXISTS idx_quality_checks_date ON audit.data_quality_checks(execution_date);
CREATE INDEX IF NOT EXISTS idx_pipeline_executions_dag ON audit.pipeline_executions(dag_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_executions_date ON audit.pipeline_executions(execution_date);

-- ============================================================================
-- COMENTARIOS en tablas y columnas para documentación
-- ============================================================================

COMMENT ON SCHEMA raw IS 'Capa de datos sin procesar (raw layer) - datos tal como llegan de las fuentes';
COMMENT ON SCHEMA processed IS 'Capa de datos procesados - datos limpios y transformados';
COMMENT ON SCHEMA analytics IS 'Capa de análisis - métricas agregadas y KPIs';
COMMENT ON SCHEMA audit IS 'Capa de auditoría - logs de ejecución y validaciones de calidad';

COMMENT ON TABLE raw.transactions IS 'Transacciones de ventas sin procesar';
COMMENT ON TABLE raw.products IS 'Catálogo de productos sin procesar';
COMMENT ON TABLE raw.customers IS 'Información de clientes sin procesar';

COMMENT ON TABLE processed.transactions_clean IS 'Transacciones limpias y enriquecidas con información de productos';

COMMENT ON TABLE analytics.daily_sales_metrics IS 'Métricas agregadas diarias de ventas';
COMMENT ON TABLE analytics.customer_metrics IS 'Métricas por cliente calculadas por fecha';

COMMENT ON TABLE audit.data_quality_checks IS 'Registro de validaciones de calidad de datos ejecutadas por los DAGs';
COMMENT ON TABLE audit.pipeline_executions IS 'Registro de ejecuciones de pipelines con métricas de performance';

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
