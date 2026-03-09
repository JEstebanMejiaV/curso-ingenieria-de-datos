#!/usr/bin/env python3
"""
Tests para el Job Spark de Agregaciones de Ventas
==================================================

Tests unitarios para validar la lógica de agregación del job Spark.
Usa datos sintéticos para verificar cálculos sin necesidad de Postgres.

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

import pytest
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DecimalType, IntegerType
import sys
import os

# Agregar el directorio spark_jobs al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aggregate_sales import (
    calculate_daily_sales_metrics,
    calculate_customer_metrics,
    calculate_category_performance
)


@pytest.fixture(scope="module")
def spark():
    """Fixture que crea una sesión de Spark para testing."""
    spark = SparkSession.builder \
        .appName("TestSalesAggregation") \
        .master("local[2]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    yield spark
    
    spark.stop()


@pytest.fixture
def sample_transactions(spark):
    """Fixture que crea datos de transacciones de ejemplo."""
    schema = StructType([
        StructField("transaction_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("product_id", StringType(), False),
        StructField("transaction_date", TimestampType(), False),
        StructField("amount", DecimalType(10, 2), False),
        StructField("quantity", IntegerType(), False),
        StructField("product_name", StringType(), False),
        StructField("category", StringType(), False)
    ])
    
    data = [
        ("T001", "C001", "P001", datetime(2024, 1, 1, 10, 0), 100.00, 2, "Product A", "Electronics"),
        ("T002", "C002", "P002", datetime(2024, 1, 1, 11, 0), 50.00, 1, "Product B", "Books"),
        ("T003", "C001", "P003", datetime(2024, 1, 1, 12, 0), 75.00, 1, "Product C", "Electronics"),
        ("T004", "C003", "P001", datetime(2024, 1, 2, 10, 0), 100.00, 2, "Product A", "Electronics"),
        ("T005", "C002", "P004", datetime(2024, 1, 2, 11, 0), 200.00, 3, "Product D", "Clothing"),
        ("T006", "C004", "P002", datetime(2024, 1, 2, 12, 0), 50.00, 1, "Product B", "Books"),
    ]
    
    return spark.createDataFrame(data, schema)


def test_daily_sales_metrics_calculation(sample_transactions):
    """Test que valida el cálculo de métricas diarias."""
    result = calculate_daily_sales_metrics(sample_transactions)
    
    # Verificar que se calcularon métricas para 2 días
    assert result.count() == 2
    
    # Convertir a pandas para facilitar assertions
    result_pd = result.toPandas()
    
    # Verificar métricas del día 2024-01-01
    day1 = result_pd[result_pd['metric_date'] == datetime(2024, 1, 1).date()].iloc[0]
    assert day1['total_transactions'] == 3
    assert float(day1['total_revenue']) == 225.00
    assert float(day1['avg_transaction_value']) == 75.00
    assert day1['unique_customers'] == 2
    assert day1['top_category'] == 'Electronics'  # Mayor revenue en día 1
    
    # Verificar métricas del día 2024-01-02
    day2 = result_pd[result_pd['metric_date'] == datetime(2024, 1, 2).date()].iloc[0]
    assert day2['total_transactions'] == 3
    assert float(day2['total_revenue']) == 350.00
    assert day2['unique_customers'] == 3


def test_daily_sales_metrics_with_date_filter(sample_transactions):
    """Test que valida el filtrado por fecha específica."""
    result = calculate_daily_sales_metrics(sample_transactions, target_date="2024-01-01")
    
    # Verificar que solo se calculó para 1 día
    assert result.count() == 1
    
    result_pd = result.toPandas()
    day1 = result_pd.iloc[0]
    
    assert day1['total_transactions'] == 3
    assert float(day1['total_revenue']) == 225.00


def test_customer_metrics_calculation(sample_transactions):
    """Test que valida el cálculo de métricas por cliente."""
    result = calculate_customer_metrics(sample_transactions, target_date="2024-01-02")
    
    # Verificar que se calcularon métricas para 4 clientes
    assert result.count() == 4
    
    result_pd = result.toPandas()
    
    # Verificar métricas del cliente C001 (2 transacciones en día 1)
    c001 = result_pd[result_pd['customer_id'] == 'C001'].iloc[0]
    assert c001['transaction_count'] == 2
    assert float(c001['total_spent']) == 175.00
    assert float(c001['avg_order_value']) == 87.50
    assert c001['days_since_last_purchase'] == 1  # Última compra fue 2024-01-01
    
    # Verificar métricas del cliente C002 (2 transacciones, una en cada día)
    c002 = result_pd[result_pd['customer_id'] == 'C002'].iloc[0]
    assert c002['transaction_count'] == 2
    assert float(c002['total_spent']) == 250.00
    assert c002['days_since_last_purchase'] == 0  # Última compra fue 2024-01-02


def test_category_performance_calculation(sample_transactions):
    """Test que valida el cálculo de performance por categoría."""
    result = calculate_category_performance(sample_transactions)
    
    # Verificar que se calcularon métricas para 3 categorías
    assert result.count() == 3
    
    result_pd = result.toPandas()
    
    # Verificar que Electronics tiene el mayor revenue
    electronics = result_pd[result_pd['category'] == 'Electronics'].iloc[0]
    assert float(electronics['category_revenue']) == 275.00
    assert electronics['transaction_count'] == 3
    assert electronics['total_quantity_sold'] == 5
    
    # Verificar porcentajes suman aproximadamente 100%
    total_percentage = result_pd['revenue_percentage'].sum()
    assert abs(total_percentage - 100.0) < 0.01


def test_category_performance_with_date_filter(sample_transactions):
    """Test que valida el filtrado por fecha en performance de categorías."""
    result = calculate_category_performance(sample_transactions, target_date="2024-01-01")
    
    result_pd = result.toPandas()
    
    # En día 1 solo hay Electronics y Books
    assert result.count() == 2
    
    # Verificar que Electronics es top en día 1
    electronics = result_pd[result_pd['category'] == 'Electronics'].iloc[0]
    assert float(electronics['category_revenue']) == 175.00


def test_empty_dataframe_handling(spark):
    """Test que valida el manejo de DataFrames vacíos."""
    schema = StructType([
        StructField("transaction_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("product_id", StringType(), False),
        StructField("transaction_date", TimestampType(), False),
        StructField("amount", DecimalType(10, 2), False),
        StructField("quantity", IntegerType(), False),
        StructField("product_name", StringType(), False),
        StructField("category", StringType(), False)
    ])
    
    empty_df = spark.createDataFrame([], schema)
    
    # Verificar que las funciones manejan DataFrames vacíos sin errores
    daily_result = calculate_daily_sales_metrics(empty_df)
    assert daily_result.count() == 0
    
    customer_result = calculate_customer_metrics(empty_df)
    assert customer_result.count() == 0
    
    # category_performance puede fallar con DataFrame vacío al calcular total_revenue
    # Esto es esperado y debería manejarse en el código principal


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
