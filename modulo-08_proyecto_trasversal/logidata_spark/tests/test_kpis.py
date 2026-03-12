"""
Tests unitarios para el cálculo de KPIs
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, FloatType, IntegerType
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kpis import KPICalculator


@pytest.fixture(scope="session")
def spark():
    """Fixture para crear sesión de Spark para tests"""
    spark = SparkSession.builder \
        .master("local[2]") \
        .appName("test_kpis") \
        .getOrCreate()
    
    yield spark
    
    spark.stop()


@pytest.fixture
def config():
    """Fixture con configuración de prueba"""
    return {
        'kpis': {
            'sla_hours': {
                'Same Day': 8,
                'Next Day': 24,
                'Standard': 48,
                'Express': 4
            },
            'alerts': {
                'otd_critical': 0.85,
                'otd_warning': 0.90
            }
        }
    }


@pytest.fixture
def sample_deliveries(spark):
    """Fixture con datos de muestra de entregas"""
    schema = StructType([
        StructField("id_pedido", StringType(), False),
        StructField("id_cliente", StringType(), False),
        StructField("id_producto", StringType(), False),
        StructField("fecha_pedido", TimestampType(), False),
        StructField("monto_total", FloatType(), False),
        StructField("estado_pedido", StringType(), False),
        StructField("tipo_entrega", StringType(), False),
        StructField("nombre_cliente", StringType(), False),
        StructField("tipo_cliente", StringType(), False),
        StructField("zona", StringType(), False),
        StructField("nombre_producto", StringType(), False),
        StructField("categoria", StringType(), False),
        StructField("conductor", StringType(), True),
        StructField("vehiculo", StringType(), True),
        StructField("fecha_asignacion", TimestampType(), True),
        StructField("fecha_recogida", TimestampType(), True),
        StructField("fecha_entrega_prometida", TimestampType(), False),
        StructField("fecha_entrega_real", TimestampType(), True),
        StructField("estado_entrega", StringType(), False),
        StructField("intentos", IntegerType(), False)
    ])
    
    # Crear datos de muestra
    base_date = datetime(2025, 1, 15, 10, 0, 0)
    
    data = [
        # Entrega a tiempo
        (
            "P001", "C001", "PROD001", base_date, 100.0, "COMPLETADO", "Same Day",
            "Cliente 1", "Retail", "NORTE", "Producto 1", "Categoria A",
            "Conductor 1", "VEH001", base_date + timedelta(hours=1),
            base_date + timedelta(hours=2), base_date + timedelta(hours=8),
            base_date + timedelta(hours=6), "ENTREGADO", 1
        ),
        # Entrega con retraso
        (
            "P002", "C002", "PROD002", base_date, 200.0, "COMPLETADO", "Next Day",
            "Cliente 2", "Farmacéutico", "SUR", "Producto 2", "Categoria B",
            "Conductor 2", "VEH002", base_date + timedelta(hours=1),
            base_date + timedelta(hours=3), base_date + timedelta(hours=24),
            base_date + timedelta(hours=30), "ENTREGADO", 1
        ),
        # Entrega fallida
        (
            "P003", "C003", "PROD003", base_date, 150.0, "COMPLETADO", "Standard",
            "Cliente 3", "Supermercado", "CENTRO", "Producto 3", "Categoria A",
            "Conductor 1", "VEH001", base_date + timedelta(hours=2),
            base_date + timedelta(hours=4), base_date + timedelta(hours=48),
            None, "FALLIDO", 2
        )
    ]
    
    return spark.createDataFrame(data, schema)


def test_calculate_daily_kpis(spark, config, sample_deliveries):
    """Test de cálculo de KPIs diarios"""
    calculator = KPICalculator(config)
    
    df_kpis = calculator.calculate_daily_kpis(sample_deliveries)
    
    # Verificar que se generaron KPIs
    assert df_kpis.count() > 0
    
    # Verificar columnas esperadas
    expected_columns = [
        "event_date", "total_deliveries", "successful_deliveries",
        "on_time_deliveries", "otd_rate", "avg_lead_time_hours"
    ]
    
    for col in expected_columns:
        assert col in df_kpis.columns
    
    # Verificar valores
    row = df_kpis.collect()[0]
    assert row["total_deliveries"] == 3
    assert row["successful_deliveries"] == 2
    assert row["on_time_deliveries"] == 1
    assert 0 <= row["otd_rate"] <= 1


def test_calculate_kpis_by_store(spark, config, sample_deliveries):
    """Test de cálculo de KPIs por tienda/zona"""
    calculator = KPICalculator(config)
    
    df_kpis = calculator.calculate_kpis_by_store(sample_deliveries)
    
    # Verificar que se generaron KPIs por zona
    assert df_kpis.count() == 3  # 3 zonas diferentes
    
    # Verificar columnas
    assert "zona" in df_kpis.columns
    assert "otd_rate" in df_kpis.columns


def test_calculate_kpis_by_driver(spark, config, sample_deliveries):
    """Test de cálculo de KPIs por conductor"""
    calculator = KPICalculator(config)
    
    df_kpis = calculator.calculate_kpis_by_driver(sample_deliveries)
    
    # Verificar que se generaron KPIs por conductor
    assert df_kpis.count() == 2  # 2 conductores diferentes
    
    # Verificar columnas
    assert "conductor" in df_kpis.columns
    assert "deliveries_per_hour" in df_kpis.columns


def test_otd_calculation(spark, config, sample_deliveries):
    """Test específico del cálculo de OTD"""
    calculator = KPICalculator(config)
    
    # Agregar métricas calculadas
    df_with_metrics = calculator._add_calculated_metrics(sample_deliveries)
    
    # Verificar que se agregó la columna is_on_time
    assert "is_on_time" in df_with_metrics.columns
    
    # Verificar valores
    on_time_count = df_with_metrics.filter(df_with_metrics.is_on_time == 1).count()
    assert on_time_count == 1  # Solo 1 entrega a tiempo en los datos de muestra


def test_lead_time_calculation(spark, config, sample_deliveries):
    """Test del cálculo de Lead Time"""
    calculator = KPICalculator(config)
    
    df_with_metrics = calculator._add_calculated_metrics(sample_deliveries)
    
    # Verificar que se agregó la columna lead_time_hours
    assert "lead_time_hours" in df_with_metrics.columns
    
    # Verificar que los valores son positivos (o nulos para entregas no completadas)
    negative_lead_times = df_with_metrics.filter(
        (df_with_metrics.lead_time_hours < 0) & 
        (df_with_metrics.lead_time_hours.isNotNull())
    ).count()
    
    assert negative_lead_times == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
