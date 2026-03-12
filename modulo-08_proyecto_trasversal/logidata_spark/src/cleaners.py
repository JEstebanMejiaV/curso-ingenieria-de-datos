"""
Módulo de limpieza y normalización de datos
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, trim, upper, lower, to_timestamp, when, 
    regexp_replace, coalesce, lit
)
import logging


class DataCleaner:
    """Clase para limpieza y normalización de datos"""
    
    def __init__(self, config: dict):
        """
        Inicializa el limpiador de datos
        
        Args:
            config: Configuración del ETL
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.valid_zones = config['data_quality']['valid_zones']
        self.valid_order_states = config['data_quality']['valid_order_states']
        self.valid_delivery_states = config['data_quality']['valid_delivery_states']
    
    def clean_orders(self, df: DataFrame) -> DataFrame:
        """
        Limpia y normaliza datos de pedidos
        
        Args:
            df: DataFrame de pedidos sin limpiar
        
        Returns:
            DataFrame de pedidos limpio
        """
        self.logger.info("Limpiando datos de pedidos")
        
        df_clean = df \
            .withColumn("id_pedido", trim(col("id_pedido"))) \
            .withColumn("id_cliente", trim(col("id_cliente"))) \
            .withColumn("id_producto", trim(col("id_producto"))) \
            .withColumn("estado", trim(upper(col("estado")))) \
            .withColumn("tipo_entrega", trim(col("tipo_entrega"))) \
            .withColumn("cantidad", col("cantidad").cast("int")) \
            .withColumn("precio_unitario", col("precio_unitario").cast("float"))
        
        # Normalizar estados
        df_clean = df_clean.withColumn(
            "estado",
            when(col("estado").isin(self.valid_order_states), col("estado"))
            .otherwise("DESCONOCIDO")
        )
        
        # Calcular monto total
        df_clean = df_clean.withColumn(
            "monto_total",
            col("cantidad") * col("precio_unitario")
        )
        
        # Filtrar registros con IDs nulos
        df_clean = df_clean.filter(
            col("id_pedido").isNotNull() &
            col("id_cliente").isNotNull() &
            col("id_producto").isNotNull()
        )
        
        # Deduplicar por id_pedido (mantener el más reciente)
        df_clean = df_clean.dropDuplicates(["id_pedido"])
        
        records_before = df.count()
        records_after = df_clean.count()
        records_removed = records_before - records_after
        
        self.logger.info(f"Limpieza de pedidos completada: {records_before} -> {records_after} "
                        f"({records_removed} removidos)")
        
        return df_clean
    
    def clean_deliveries(self, df: DataFrame) -> DataFrame:
        """
        Limpia y normaliza datos de entregas
        
        Args:
            df: DataFrame de entregas sin limpiar
        
        Returns:
            DataFrame de entregas limpio
        """
        self.logger.info("Limpiando datos de entregas")
        
        df_clean = df \
            .withColumn("id_pedido", trim(col("id_pedido"))) \
            .withColumn("conductor", trim(col("conductor"))) \
            .withColumn("vehiculo", trim(upper(col("vehiculo")))) \
            .withColumn("estado_entrega", trim(upper(col("estado_entrega")))) \
            .withColumn("intentos", coalesce(col("intentos"), lit(1)))
        
        # Normalizar estados de entrega
        df_clean = df_clean.withColumn(
            "estado_entrega",
            when(col("estado_entrega").isin(self.valid_delivery_states), col("estado_entrega"))
            .otherwise("DESCONOCIDO")
        )
        
        # Validar coherencia temporal: entrega no puede ser antes de asignación
        df_clean = df_clean.withColumn(
            "fecha_entrega_real",
            when(
                col("fecha_entrega_real") < col("fecha_asignacion"),
                None
            ).otherwise(col("fecha_entrega_real"))
        )
        
        # Filtrar registros con id_pedido nulo
        df_clean = df_clean.filter(col("id_pedido").isNotNull())
        
        # Deduplicar por id_pedido
        df_clean = df_clean.dropDuplicates(["id_pedido"])
        
        records_before = df.count()
        records_after = df_clean.count()
        records_removed = records_before - records_after
        
        self.logger.info(f"Limpieza de entregas completada: {records_before} -> {records_after} "
                        f"({records_removed} removidos)")
        
        return df_clean
    
    def clean_customers(self, df: DataFrame) -> DataFrame:
        """
        Limpia y normaliza datos de clientes
        
        Args:
            df: DataFrame de clientes sin limpiar
        
        Returns:
            DataFrame de clientes limpio
        """
        self.logger.info("Limpiando datos de clientes")
        
        df_clean = df \
            .withColumn("id_cliente", trim(col("id_cliente"))) \
            .withColumn("nombre", trim(col("nombre"))) \
            .withColumn("tipo_cliente", trim(col("tipo_cliente"))) \
            .withColumn("zona", trim(upper(col("zona")))) \
            .withColumn("telefono", regexp_replace(col("telefono"), "[^0-9]", ""))
        
        # Validar zonas
        df_clean = df_clean.withColumn(
            "zona",
            when(col("zona").isin(self.valid_zones), col("zona"))
            .otherwise("DESCONOCIDO")
        )
        
        # Filtrar registros con id_cliente nulo
        df_clean = df_clean.filter(col("id_cliente").isNotNull())
        
        # Deduplicar por id_cliente
        df_clean = df_clean.dropDuplicates(["id_cliente"])
        
        records_before = df.count()
        records_after = df_clean.count()
        
        self.logger.info(f"Limpieza de clientes completada: {records_before} -> {records_after}")
        
        return df_clean
    
    def clean_catalog(self, df: DataFrame) -> DataFrame:
        """
        Limpia y normaliza datos del catálogo
        
        Args:
            df: DataFrame de catálogo sin limpiar
        
        Returns:
            DataFrame de catálogo limpio
        """
        self.logger.info("Limpiando datos de catálogo")
        
        df_clean = df \
            .withColumn("id_producto", trim(col("id_producto"))) \
            .withColumn("nombre_producto", trim(col("nombre_producto"))) \
            .withColumn("categoria", trim(col("categoria"))) \
            .withColumn("tipo_entrega", trim(col("tipo_entrega"))) \
            .withColumn("precio", col("precio").cast("float"))
        
        # Filtrar registros con id_producto nulo
        df_clean = df_clean.filter(col("id_producto").isNotNull())
        
        # Deduplicar por id_producto
        df_clean = df_clean.dropDuplicates(["id_producto"])
        
        records_before = df.count()
        records_after = df_clean.count()
        
        self.logger.info(f"Limpieza de catálogo completada: {records_before} -> {records_after}")
        
        return df_clean
