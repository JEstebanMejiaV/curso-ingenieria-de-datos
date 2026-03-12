"""
Módulo de lectura de datos desde S3 o archivos locales
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType, IntegerType
from pathlib import Path
import logging


class DataReader:
    """Clase para leer datos de diferentes fuentes"""
    
    def __init__(self, spark: SparkSession, config: dict, use_local: bool = False):
        """
        Inicializa el lector de datos
        
        Args:
            spark: Sesión de Spark
            config: Configuración del ETL
            use_local: Si True, lee archivos locales en lugar de S3
        """
        self.spark = spark
        self.config = config
        self.use_local = use_local
        self.logger = logging.getLogger(__name__)
    
    def read_orders(self, run_date: str, mode: str = "incremental") -> DataFrame:
        """
        Lee datos de pedidos
        
        Args:
            run_date: Fecha de ejecución (YYYY-MM-DD)
            mode: Modo de lectura (incremental, full)
        
        Returns:
            DataFrame con pedidos
        """
        schema = StructType([
            StructField("id_pedido", StringType(), False),
            StructField("id_cliente", StringType(), False),
            StructField("id_producto", StringType(), False),
            StructField("fecha", TimestampType(), False),
            StructField("cantidad", IntegerType(), False),
            StructField("precio_unitario", FloatType(), False),
            StructField("estado", StringType(), False),
            StructField("tipo_entrega", StringType(), True)
        ])
        
        if self.use_local:
            path = self.config['input']['local']['pedidos']
            self.logger.info(f"Leyendo pedidos desde archivo local: {path}")
            df = self.spark.read.csv(path, header=True, schema=schema)
        else:
            base_path = self.config['input']['pedidos']
            
            if mode == "incremental":
                # Leer solo la partición de la fecha especificada
                path = f"{base_path}event_date={run_date}/"
                self.logger.info(f"Leyendo pedidos incrementales desde: {path}")
            else:
                # Leer todo el histórico
                path = base_path
                self.logger.info(f"Leyendo todos los pedidos desde: {path}")
            
            df = self.spark.read.parquet(path)
        
        return df
    
    def read_deliveries(self, run_date: str, mode: str = "incremental") -> DataFrame:
        """
        Lee datos de entregas
        
        Args:
            run_date: Fecha de ejecución (YYYY-MM-DD)
            mode: Modo de lectura (incremental, full)
        
        Returns:
            DataFrame con entregas
        """
        schema = StructType([
            StructField("id_pedido", StringType(), False),
            StructField("conductor", StringType(), True),
            StructField("vehiculo", StringType(), True),
            StructField("fecha_asignacion", TimestampType(), True),
            StructField("fecha_recogida", TimestampType(), True),
            StructField("fecha_entrega_prometida", TimestampType(), False),
            StructField("fecha_entrega_real", TimestampType(), True),
            StructField("estado_entrega", StringType(), False),
            StructField("intentos", IntegerType(), True)
        ])
        
        if self.use_local:
            path = self.config['input']['local']['entregas']
            self.logger.info(f"Leyendo entregas desde archivo local: {path}")
            df = self.spark.read.csv(path, header=True, schema=schema)
        else:
            base_path = self.config['input']['entregas']
            
            if mode == "incremental":
                path = f"{base_path}event_date={run_date}/"
                self.logger.info(f"Leyendo entregas incrementales desde: {path}")
            else:
                path = base_path
                self.logger.info(f"Leyendo todas las entregas desde: {path}")
            
            df = self.spark.read.parquet(path)
        
        return df
    
    def read_customers(self) -> DataFrame:
        """
        Lee datos de clientes (tabla maestra)
        
        Returns:
            DataFrame con clientes
        """
        schema = StructType([
            StructField("id_cliente", StringType(), False),
            StructField("nombre", StringType(), False),
            StructField("tipo_cliente", StringType(), False),
            StructField("zona", StringType(), False),
            StructField("direccion", StringType(), True),
            StructField("telefono", StringType(), True)
        ])
        
        if self.use_local:
            path = self.config['input']['local']['clientes']
            self.logger.info(f"Leyendo clientes desde archivo local: {path}")
            df = self.spark.read.csv(path, header=True, schema=schema)
        else:
            path = self.config['input']['clientes']
            self.logger.info(f"Leyendo clientes desde: {path}")
            df = self.spark.read.parquet(path)
        
        return df
    
    def read_catalog(self) -> DataFrame:
        """
        Lee datos del catálogo de productos (tabla maestra)
        
        Returns:
            DataFrame con catálogo
        """
        schema = StructType([
            StructField("id_producto", StringType(), False),
            StructField("nombre_producto", StringType(), False),
            StructField("categoria", StringType(), True),
            StructField("precio", FloatType(), False),
            StructField("tipo_entrega", StringType(), True)
        ])
        
        if self.use_local:
            path = self.config['input']['local']['catalogo']
            self.logger.info(f"Leyendo catálogo desde archivo local: {path}")
            df = self.spark.read.csv(path, header=True, schema=schema)
        else:
            path = self.config['input']['catalogo']
            self.logger.info(f"Leyendo catálogo desde: {path}")
            df = self.spark.read.parquet(path)
        
        return df
