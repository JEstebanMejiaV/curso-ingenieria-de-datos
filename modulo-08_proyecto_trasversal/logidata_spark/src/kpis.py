"""
Módulo de cálculo de KPIs de entregas
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, sum as spark_sum, count, avg, max as spark_max, min as spark_min,
    datediff, hour, minute, lit, round as spark_round, to_date, coalesce
)
from pyspark.sql.window import Window
import logging


class KPICalculator:
    """Clase para cálculo de KPIs de entregas"""
    
    def __init__(self, config: dict):
        """
        Inicializa el calculador de KPIs
        
        Args:
            config: Configuración del ETL
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sla_hours = config['kpis']['sla_hours']
    
    def calculate_daily_kpis(self, df: DataFrame) -> DataFrame:
        """
        Calcula KPIs agregados por día
        
        Args:
            df: DataFrame de entregas enriquecidas
        
        Returns:
            DataFrame con KPIs diarios
        """
        self.logger.info("Calculando KPIs diarios")
        
        # Agregar columnas calculadas
        df_with_metrics = self._add_calculated_metrics(df)
        
        # Agregar por fecha
        df_kpis = df_with_metrics.groupBy(
            to_date(col("fecha_pedido")).alias("event_date")
        ).agg(
            # Contadores
            count("*").alias("total_deliveries"),
            spark_sum(when(col("estado_entrega") == "ENTREGADO", 1).otherwise(0)).alias("successful_deliveries"),
            spark_sum(when(col("estado_entrega") == "FALLIDO", 1).otherwise(0)).alias("failed_deliveries"),
            
            # OTD (On-Time Delivery)
            spark_sum(when(col("is_on_time") == 1, 1).otherwise(0)).alias("on_time_deliveries"),
            (spark_sum(when(col("is_on_time") == 1, 1).otherwise(0)) / count("*")).alias("otd_rate"),
            
            # Lead Time
            avg("lead_time_hours").alias("avg_lead_time_hours"),
            spark_min("lead_time_hours").alias("min_lead_time_hours"),
            spark_max("lead_time_hours").alias("max_lead_time_hours"),
            
            # Pickup Time
            avg("pickup_time_minutes").alias("avg_pickup_time_minutes"),
            
            # First Attempt Success
            spark_sum(when(col("intentos") == 1, 1).otherwise(0)).alias("first_attempt_success"),
            (spark_sum(when(col("intentos") == 1, 1).otherwise(0)) / count("*")).alias("first_attempt_rate"),
            
            # Montos
            spark_sum("monto_total").alias("total_revenue"),
            avg("monto_total").alias("avg_order_value")
        )
        
        # Redondear valores
        df_kpis = df_kpis \
            .withColumn("otd_rate", spark_round(col("otd_rate"), 4)) \
            .withColumn("first_attempt_rate", spark_round(col("first_attempt_rate"), 4)) \
            .withColumn("avg_lead_time_hours", spark_round(col("avg_lead_time_hours"), 2)) \
            .withColumn("avg_pickup_time_minutes", spark_round(col("avg_pickup_time_minutes"), 2)) \
            .withColumn("avg_order_value", spark_round(col("avg_order_value"), 2))
        
        self.logger.info(f"KPIs diarios calculados: {df_kpis.count()} días")
        
        return df_kpis
    
    def calculate_kpis_by_store(self, df: DataFrame) -> DataFrame:
        """
        Calcula KPIs agregados por tienda/zona
        
        Args:
            df: DataFrame de entregas enriquecidas
        
        Returns:
            DataFrame con KPIs por tienda
        """
        self.logger.info("Calculando KPIs por tienda/zona")
        
        # Agregar columnas calculadas
        df_with_metrics = self._add_calculated_metrics(df)
        
        # Agregar por fecha y zona
        df_kpis = df_with_metrics.groupBy(
            to_date(col("fecha_pedido")).alias("event_date"),
            col("zona")
        ).agg(
            count("*").alias("total_deliveries"),
            spark_sum(when(col("estado_entrega") == "ENTREGADO", 1).otherwise(0)).alias("successful_deliveries"),
            spark_sum(when(col("is_on_time") == 1, 1).otherwise(0)).alias("on_time_deliveries"),
            (spark_sum(when(col("is_on_time") == 1, 1).otherwise(0)) / count("*")).alias("otd_rate"),
            avg("lead_time_hours").alias("avg_lead_time_hours"),
            spark_sum("monto_total").alias("total_revenue")
        )
        
        # Redondear valores
        df_kpis = df_kpis \
            .withColumn("otd_rate", spark_round(col("otd_rate"), 4)) \
            .withColumn("avg_lead_time_hours", spark_round(col("avg_lead_time_hours"), 2))
        
        self.logger.info(f"KPIs por tienda calculados: {df_kpis.count()} registros")
        
        return df_kpis
    
    def calculate_kpis_by_driver(self, df: DataFrame) -> DataFrame:
        """
        Calcula KPIs de eficiencia por conductor
        
        Args:
            df: DataFrame de entregas enriquecidas
        
        Returns:
            DataFrame con KPIs por conductor
        """
        self.logger.info("Calculando KPIs por conductor")
        
        # Agregar columnas calculadas
        df_with_metrics = self._add_calculated_metrics(df)
        
        # Filtrar solo entregas con conductor asignado
        df_with_driver = df_with_metrics.filter(col("conductor").isNotNull())
        
        # Agregar por fecha y conductor
        df_kpis = df_with_driver.groupBy(
            to_date(col("fecha_pedido")).alias("event_date"),
            col("conductor")
        ).agg(
            count("*").alias("total_deliveries"),
            spark_sum(when(col("estado_entrega") == "ENTREGADO", 1).otherwise(0)).alias("successful_deliveries"),
            spark_sum(when(col("is_on_time") == 1, 1).otherwise(0)).alias("on_time_deliveries"),
            (spark_sum(when(col("is_on_time") == 1, 1).otherwise(0)) / count("*")).alias("otd_rate"),
            avg("lead_time_hours").alias("avg_lead_time_hours"),
            avg("pickup_time_minutes").alias("avg_pickup_time_minutes"),
            (spark_sum(when(col("intentos") == 1, 1).otherwise(0)) / count("*")).alias("first_attempt_rate")
        )
        
        # Calcular eficiencia (entregas por hora)
        # Asumiendo jornada de 8 horas
        df_kpis = df_kpis.withColumn(
            "deliveries_per_hour",
            spark_round(col("total_deliveries") / 8, 2)
        )
        
        # Redondear valores
        df_kpis = df_kpis \
            .withColumn("otd_rate", spark_round(col("otd_rate"), 4)) \
            .withColumn("first_attempt_rate", spark_round(col("first_attempt_rate"), 4)) \
            .withColumn("avg_lead_time_hours", spark_round(col("avg_lead_time_hours"), 2)) \
            .withColumn("avg_pickup_time_minutes", spark_round(col("avg_pickup_time_minutes"), 2))
        
        self.logger.info(f"KPIs por conductor calculados: {df_kpis.count()} registros")
        
        return df_kpis
    
    def _add_calculated_metrics(self, df: DataFrame) -> DataFrame:
        """
        Agrega métricas calculadas al DataFrame
        
        Args:
            df: DataFrame de entregas enriquecidas
        
        Returns:
            DataFrame con métricas calculadas
        """
        # Calcular Lead Time (tiempo total desde pedido hasta entrega)
        df = df.withColumn(
            "lead_time_hours",
            when(
                col("fecha_entrega_real").isNotNull(),
                (col("fecha_entrega_real").cast("long") - col("fecha_pedido").cast("long")) / 3600
            ).otherwise(None)
        )
        
        # Calcular Pickup Time (tiempo desde asignación hasta recogida)
        df = df.withColumn(
            "pickup_time_minutes",
            when(
                col("fecha_recogida").isNotNull() & col("fecha_asignacion").isNotNull(),
                (col("fecha_recogida").cast("long") - col("fecha_asignacion").cast("long")) / 60
            ).otherwise(None)
        )
        
        # Calcular SLA en horas según tipo de entrega
        df = df.withColumn(
            "sla_hours",
            when(col("tipo_entrega") == "Same Day", lit(self.sla_hours.get("Same Day", 8)))
            .when(col("tipo_entrega") == "Next Day", lit(self.sla_hours.get("Next Day", 24)))
            .when(col("tipo_entrega") == "Express", lit(self.sla_hours.get("Express", 4)))
            .otherwise(lit(self.sla_hours.get("Standard", 48)))
        )
        
        # Calcular si la entrega fue a tiempo (OTD)
        df = df.withColumn(
            "is_on_time",
            when(
                (col("fecha_entrega_real").isNotNull()) &
                (col("fecha_entrega_real") <= col("fecha_entrega_prometida")),
                lit(1)
            ).otherwise(lit(0))
        )
        
        # Calcular retraso en horas (si aplica)
        df = df.withColumn(
            "delay_hours",
            when(
                (col("fecha_entrega_real").isNotNull()) &
                (col("fecha_entrega_real") > col("fecha_entrega_prometida")),
                (col("fecha_entrega_real").cast("long") - col("fecha_entrega_prometida").cast("long")) / 3600
            ).otherwise(lit(0))
        )
        
        return df
