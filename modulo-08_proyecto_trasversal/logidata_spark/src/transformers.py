"""
Módulo de transformaciones y enriquecimiento de datos
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, broadcast
import logging


class DataTransformer:
    """Clase para transformaciones y enriquecimiento de datos"""
    
    def __init__(self, config: dict):
        """
        Inicializa el transformador de datos
        
        Args:
            config: Configuración del ETL
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.enable_broadcast = config['execution'].get('enable_broadcast_join', True)
    
    def enrich_orders(self, df_orders: DataFrame, df_customers: DataFrame, 
                     df_catalog: DataFrame) -> DataFrame:
        """
        Enriquece pedidos con información de clientes y catálogo
        
        Args:
            df_orders: DataFrame de pedidos limpios
            df_customers: DataFrame de clientes limpios
            df_catalog: DataFrame de catálogo limpio
        
        Returns:
            DataFrame de pedidos enriquecidos
        """
        self.logger.info("Enriqueciendo pedidos con clientes y catálogo")
        
        # Join con clientes (broadcast si está habilitado)
        if self.enable_broadcast:
            df_enriched = df_orders.join(
                broadcast(df_customers),
                on="id_cliente",
                how="left"
            )
        else:
            df_enriched = df_orders.join(
                df_customers,
                on="id_cliente",
                how="left"
            )
        
        # Join con catálogo (broadcast si está habilitado)
        if self.enable_broadcast:
            df_enriched = df_enriched.join(
                broadcast(df_catalog),
                on="id_producto",
                how="left"
            )
        else:
            df_enriched = df_enriched.join(
                df_catalog,
                on="id_producto",
                how="left"
            )
        
        # Seleccionar y renombrar columnas relevantes
        df_enriched = df_enriched.select(
            col("id_pedido"),
            col("id_cliente"),
            col("nombre").alias("nombre_cliente"),
            col("tipo_cliente"),
            col("zona"),
            col("id_producto"),
            col("nombre_producto"),
            col("categoria"),
            col("fecha").alias("fecha_pedido"),
            col("cantidad"),
            col("precio_unitario"),
            col("monto_total"),
            col("estado").alias("estado_pedido"),
            col("tipo_entrega")
        )
        
        # Validar cardinalidad (no debe haber duplicados de id_pedido)
        count_before = df_orders.count()
        count_after = df_enriched.count()
        
        if count_after > count_before:
            self.logger.warning(
                f"Posible multiplicación de registros en enriquecimiento de pedidos: "
                f"{count_before} -> {count_after}"
            )
        
        self.logger.info(f"Pedidos enriquecidos: {count_after} registros")
        
        return df_enriched
    
    def enrich_deliveries(self, df_deliveries: DataFrame, 
                         df_orders_enriched: DataFrame) -> DataFrame:
        """
        Enriquece entregas con información de pedidos
        
        Args:
            df_deliveries: DataFrame de entregas limpias
            df_orders_enriched: DataFrame de pedidos enriquecidos
        
        Returns:
            DataFrame de entregas enriquecidas
        """
        self.logger.info("Enriqueciendo entregas con información de pedidos")
        
        # Join con pedidos enriquecidos
        df_enriched = df_deliveries.join(
            df_orders_enriched,
            on="id_pedido",
            how="inner"  # Solo entregas con pedidos válidos
        )
        
        # Seleccionar columnas relevantes
        df_enriched = df_enriched.select(
            # IDs
            col("id_pedido"),
            col("id_cliente"),
            col("id_producto"),
            
            # Información del pedido
            col("fecha_pedido"),
            col("monto_total"),
            col("estado_pedido"),
            col("tipo_entrega"),
            
            # Información del cliente
            col("nombre_cliente"),
            col("tipo_cliente"),
            col("zona"),
            
            # Información del producto
            col("nombre_producto"),
            col("categoria"),
            
            # Información de la entrega
            col("conductor"),
            col("vehiculo"),
            col("fecha_asignacion"),
            col("fecha_recogida"),
            col("fecha_entrega_prometida"),
            col("fecha_entrega_real"),
            col("estado_entrega"),
            col("intentos")
        )
        
        # Validar que no haya huérfanos (entregas sin pedido)
        count_deliveries = df_deliveries.count()
        count_enriched = df_enriched.count()
        orphans = count_deliveries - count_enriched
        
        if orphans > 0:
            orphan_rate = orphans / count_deliveries
            self.logger.warning(
                f"Entregas huérfanas (sin pedido): {orphans} ({orphan_rate:.2%})"
            )
            
            # Si la tasa de huérfanos es muy alta, puede ser un problema
            max_orphan_rate = 0.05  # 5%
            if orphan_rate > max_orphan_rate:
                raise ValueError(
                    f"Tasa de entregas huérfanas muy alta: {orphan_rate:.2%} "
                    f"(máximo permitido: {max_orphan_rate:.2%})"
                )
        
        self.logger.info(f"Entregas enriquecidas: {count_enriched} registros")
        
        return df_enriched
