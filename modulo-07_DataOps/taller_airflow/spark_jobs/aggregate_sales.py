#!/usr/bin/env python3
"""
Job Spark para Agregaciones Complejas de Ventas
================================================

Este job Spark demuestra cómo procesar grandes volúmenes de datos usando
Apache Spark integrado con Airflow. El job realiza:
- Lectura de datos desde PostgreSQL
- Agregaciones complejas usando Spark SQL y DataFrames
- Escritura de resultados de vuelta a PostgreSQL

Caso de uso: Análisis de ventas e-commerce con métricas avanzadas

Autor: Taller de Apache Airflow - Módulo 07 DataOps
"""

import argparse
import sys
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def create_spark_session(app_name: str = "SalesAggregation") -> SparkSession:
    """
    Crea y configura una sesión de Spark con soporte para PostgreSQL.
    
    Args:
        app_name: Nombre de la aplicación Spark
        
    Returns:
        SparkSession configurada
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    
    # Configurar nivel de log
    spark.sparkContext.setLogLevel("WARN")
    
    return spark


def get_jdbc_properties() -> dict:
    """
    Retorna las propiedades de conexión JDBC para PostgreSQL.
    
    Returns:
        Diccionario con propiedades de conexión
    """
    return {
        "user": "airflow",
        "password": "airflow",
        "driver": "org.postgresql.Driver"
    }


def read_from_postgres(spark: SparkSession, table: str, schema: str = "processed") -> "DataFrame":
    """
    Lee datos desde una tabla de PostgreSQL.
    
    Args:
        spark: Sesión de Spark
        table: Nombre de la tabla
        schema: Schema de la base de datos
        
    Returns:
        DataFrame de Spark con los datos
    """
    jdbc_url = "jdbc:postgresql://postgres:5432/airflow"
    full_table = f"{schema}.{table}"
    
    df = spark.read \
        .jdbc(
            url=jdbc_url,
            table=full_table,
            properties=get_jdbc_properties()
        )
    
    return df


def write_to_postgres(df: "DataFrame", table: str, schema: str = "analytics", mode: str = "overwrite"):
    """
    Escribe un DataFrame a una tabla de PostgreSQL.
    
    Args:
        df: DataFrame de Spark a escribir
        table: Nombre de la tabla destino
        schema: Schema de la base de datos
        mode: Modo de escritura ('overwrite', 'append', 'ignore', 'error')
    """
    jdbc_url = "jdbc:postgresql://postgres:5432/airflow"
    full_table = f"{schema}.{table}"
    
    df.write \
        .jdbc(
            url=jdbc_url,
            table=full_table,
            mode=mode,
            properties=get_jdbc_properties()
        )


def calculate_daily_sales_metrics(transactions_df: "DataFrame", target_date: str = None) -> "DataFrame":
    """
    Calcula métricas diarias de ventas agregadas.
    
    Métricas calculadas:
    - Total de transacciones
    - Revenue total
    - Valor promedio de transacción
    - Número de clientes únicos
    - Categoría más vendida
    
    Args:
        transactions_df: DataFrame con transacciones limpias
        target_date: Fecha objetivo en formato YYYY-MM-DD (opcional)
        
    Returns:
        DataFrame con métricas diarias
    """
    # Filtrar por fecha si se especifica
    if target_date:
        transactions_df = transactions_df.filter(
            F.to_date(F.col("transaction_date")) == target_date
        )
    
    # Calcular métricas básicas por día
    daily_metrics = transactions_df.groupBy(
        F.to_date(F.col("transaction_date")).alias("metric_date")
    ).agg(
        F.count("transaction_id").alias("total_transactions"),
        F.sum("amount").alias("total_revenue"),
        F.avg("amount").alias("avg_transaction_value"),
        F.countDistinct("customer_id").alias("unique_customers")
    )
    
    # Calcular categoría más vendida por día
    top_category_by_day = transactions_df.groupBy(
        F.to_date(F.col("transaction_date")).alias("metric_date"),
        "category"
    ).agg(
        F.sum("amount").alias("category_revenue")
    )
    
    # Usar window function para obtener la categoría top por día
    window_spec = Window.partitionBy("metric_date").orderBy(F.desc("category_revenue"))
    top_category_by_day = top_category_by_day.withColumn(
        "rank",
        F.row_number().over(window_spec)
    ).filter(
        F.col("rank") == 1
    ).select(
        "metric_date",
        F.col("category").alias("top_category")
    )
    
    # Unir métricas con categoría top
    result = daily_metrics.join(
        top_category_by_day,
        on="metric_date",
        how="left"
    )
    
    # Agregar timestamp de cálculo
    result = result.withColumn(
        "calculated_at",
        F.current_timestamp()
    )
    
    # Redondear valores decimales
    result = result.withColumn(
        "total_revenue",
        F.round(F.col("total_revenue"), 2)
    ).withColumn(
        "avg_transaction_value",
        F.round(F.col("avg_transaction_value"), 2)
    )
    
    return result


def calculate_customer_metrics(transactions_df: "DataFrame", target_date: str = None) -> "DataFrame":
    """
    Calcula métricas por cliente con análisis de comportamiento.
    
    Métricas calculadas:
    - Número de transacciones por cliente
    - Total gastado por cliente
    - Valor promedio de orden
    - Días desde última compra
    - Frecuencia de compra
    
    Args:
        transactions_df: DataFrame con transacciones limpias
        target_date: Fecha objetivo en formato YYYY-MM-DD (opcional)
        
    Returns:
        DataFrame con métricas por cliente
    """
    # Determinar fecha de referencia
    if target_date:
        reference_date = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        # Usar la fecha máxima en los datos
        max_date = transactions_df.agg(F.max("transaction_date")).collect()[0][0]
        reference_date = max_date if max_date else datetime.now()
    
    # Calcular métricas básicas por cliente
    customer_metrics = transactions_df.groupBy("customer_id").agg(
        F.count("transaction_id").alias("transaction_count"),
        F.sum("amount").alias("total_spent"),
        F.avg("amount").alias("avg_order_value"),
        F.max("transaction_date").alias("last_purchase_date"),
        F.min("transaction_date").alias("first_purchase_date")
    )
    
    # Calcular días desde última compra
    customer_metrics = customer_metrics.withColumn(
        "days_since_last_purchase",
        F.datediff(
            F.lit(reference_date),
            F.col("last_purchase_date")
        )
    )
    
    # Calcular frecuencia de compra (días entre primera y última compra / número de compras)
    customer_metrics = customer_metrics.withColumn(
        "purchase_frequency_days",
        F.when(
            F.col("transaction_count") > 1,
            F.datediff(F.col("last_purchase_date"), F.col("first_purchase_date")) / 
            (F.col("transaction_count") - 1)
        ).otherwise(None)
    )
    
    # Agregar fecha de métrica y timestamp
    customer_metrics = customer_metrics.withColumn(
        "metric_date",
        F.lit(reference_date).cast("date")
    )
    
    # Redondear valores decimales
    customer_metrics = customer_metrics.withColumn(
        "total_spent",
        F.round(F.col("total_spent"), 2)
    ).withColumn(
        "avg_order_value",
        F.round(F.col("avg_order_value"), 2)
    ).withColumn(
        "purchase_frequency_days",
        F.round(F.col("purchase_frequency_days"), 1)
    )
    
    # Seleccionar columnas finales
    result = customer_metrics.select(
        "customer_id",
        "metric_date",
        "transaction_count",
        "total_spent",
        "avg_order_value",
        "days_since_last_purchase",
        "purchase_frequency_days"
    )
    
    return result


def calculate_category_performance(transactions_df: "DataFrame", target_date: str = None) -> "DataFrame":
    """
    Calcula métricas de performance por categoría de producto.
    
    Métricas calculadas:
    - Revenue por categoría
    - Número de transacciones por categoría
    - Ticket promedio por categoría
    - Cantidad de productos vendidos
    - Porcentaje del revenue total
    
    Args:
        transactions_df: DataFrame con transacciones limpias
        target_date: Fecha objetivo en formato YYYY-MM-DD (opcional)
        
    Returns:
        DataFrame con métricas por categoría
    """
    # Filtrar por fecha si se especifica
    if target_date:
        transactions_df = transactions_df.filter(
            F.to_date(F.col("transaction_date")) == target_date
        )
    
    # Calcular métricas por categoría
    category_metrics = transactions_df.groupBy("category").agg(
        F.sum("amount").alias("category_revenue"),
        F.count("transaction_id").alias("transaction_count"),
        F.avg("amount").alias("avg_ticket"),
        F.sum("quantity").alias("total_quantity_sold"),
        F.countDistinct("customer_id").alias("unique_customers")
    )
    
    # Calcular revenue total para porcentajes
    total_revenue = transactions_df.agg(F.sum("amount")).collect()[0][0]
    
    # Calcular porcentaje del revenue total
    category_metrics = category_metrics.withColumn(
        "revenue_percentage",
        F.round((F.col("category_revenue") / total_revenue) * 100, 2)
    )
    
    # Redondear valores
    category_metrics = category_metrics.withColumn(
        "category_revenue",
        F.round(F.col("category_revenue"), 2)
    ).withColumn(
        "avg_ticket",
        F.round(F.col("avg_ticket"), 2)
    )
    
    # Ordenar por revenue descendente
    result = category_metrics.orderBy(F.desc("category_revenue"))
    
    return result


def main():
    """
    Función principal que ejecuta el job Spark.
    """
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Job Spark para agregaciones de ventas")
    parser.add_argument(
        "--input-date",
        type=str,
        help="Fecha de entrada en formato YYYY-MM-DD (opcional, procesa todos los datos si no se especifica)"
    )
    parser.add_argument(
        "--metrics",
        type=str,
        default="all",
        choices=["all", "daily", "customer", "category"],
        help="Tipo de métricas a calcular (default: all)"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Job Spark: Agregaciones de Ventas")
    print("=" * 80)
    print(f"Fecha de entrada: {args.input_date if args.input_date else 'Todos los datos'}")
    print(f"Métricas a calcular: {args.metrics}")
    print("=" * 80)
    
    # Crear sesión de Spark
    print("\n[1/5] Creando sesión de Spark...")
    spark = create_spark_session()
    print("✓ Sesión de Spark creada exitosamente")
    
    # Leer datos desde PostgreSQL
    print("\n[2/5] Leyendo datos desde PostgreSQL...")
    transactions_df = read_from_postgres(spark, "transactions_clean", "processed")
    
    # Mostrar información de los datos
    record_count = transactions_df.count()
    print(f"✓ Leídos {record_count:,} registros de transacciones")
    
    if record_count == 0:
        print("\n⚠ No hay datos para procesar. Finalizando job.")
        spark.stop()
        return
    
    # Cache del DataFrame para reutilización
    transactions_df.cache()
    
    # Calcular métricas según lo especificado
    print("\n[3/5] Calculando métricas...")
    
    if args.metrics in ["all", "daily"]:
        print("  - Calculando métricas diarias de ventas...")
        daily_metrics = calculate_daily_sales_metrics(transactions_df, args.input_date)
        daily_count = daily_metrics.count()
        print(f"    ✓ Calculadas métricas para {daily_count} días")
        
        # Mostrar muestra de resultados
        print("\n    Muestra de métricas diarias:")
        daily_metrics.show(5, truncate=False)
    
    if args.metrics in ["all", "customer"]:
        print("  - Calculando métricas por cliente...")
        customer_metrics = calculate_customer_metrics(transactions_df, args.input_date)
        customer_count = customer_metrics.count()
        print(f"    ✓ Calculadas métricas para {customer_count} clientes")
        
        # Mostrar muestra de resultados
        print("\n    Muestra de métricas por cliente:")
        customer_metrics.show(5, truncate=False)
    
    if args.metrics in ["all", "category"]:
        print("  - Calculando métricas por categoría...")
        category_metrics = calculate_category_performance(transactions_df, args.input_date)
        category_count = category_metrics.count()
        print(f"    ✓ Calculadas métricas para {category_count} categorías")
        
        # Mostrar resultados de categorías
        print("\n    Performance por categoría:")
        category_metrics.show(truncate=False)
    
    # Escribir resultados a PostgreSQL
    print("\n[4/5] Escribiendo resultados a PostgreSQL...")
    
    if args.metrics in ["all", "daily"]:
        print("  - Escribiendo métricas diarias...")
        write_to_postgres(daily_metrics, "daily_sales_metrics", "analytics", "append")
        print("    ✓ Métricas diarias escritas exitosamente")
    
    if args.metrics in ["all", "customer"]:
        print("  - Escribiendo métricas por cliente...")
        write_to_postgres(customer_metrics, "customer_metrics", "analytics", "append")
        print("    ✓ Métricas por cliente escritas exitosamente")
    
    if args.metrics in ["all", "category"]:
        print("  - Escribiendo métricas por categoría...")
        # Crear tabla si no existe (para categorías usamos una tabla temporal)
        write_to_postgres(category_metrics, "category_performance", "analytics", "overwrite")
        print("    ✓ Métricas por categoría escritas exitosamente")
    
    # Limpiar y finalizar
    print("\n[5/5] Finalizando job...")
    transactions_df.unpersist()
    spark.stop()
    
    print("\n" + "=" * 80)
    print("✓ Job completado exitosamente")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error ejecutando job Spark: {str(e)}", file=sys.stderr)
        sys.exit(1)
