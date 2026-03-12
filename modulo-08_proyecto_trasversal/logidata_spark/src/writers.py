"""
Módulo de escritura de datos a S3 y Redshift
"""

from pyspark.sql import SparkSession, DataFrame
import logging


class DataWriter:
    """Clase para escribir datos a diferentes destinos"""
    
    def __init__(self, spark: SparkSession, config: dict, use_local: bool = False):
        """
        Inicializa el escritor de datos
        
        Args:
            spark: Sesión de Spark
            config: Configuración del ETL
            use_local: Si True, escribe a archivos locales en lugar de S3
        """
        self.spark = spark
        self.config = config
        self.use_local = use_local
        self.logger = logging.getLogger(__name__)
        
        self.output_format = config['output_format']['curated']
        self.compression = config['output_format']['compression']
    
    def write_curated(self, df: DataFrame, dataset_name: str, run_date: str):
        """
        Escribe datos a la capa curated
        
        Args:
            df: DataFrame a escribir
            dataset_name: Nombre del dataset (orders_enriched, deliveries_enriched)
            run_date: Fecha de ejecución (YYYY-MM-DD)
        """
        if self.use_local:
            path = f"{self.config['output']['local']['curated']}{dataset_name}/"
            self.logger.info(f"Escribiendo {dataset_name} a archivo local: {path}")
        else:
            path = self.config['output']['curated'][dataset_name]
            self.logger.info(f"Escribiendo {dataset_name} a S3: {path}")
        
        # Escribir con particionado por fecha
        df.write \
            .mode("overwrite") \
            .partitionBy("event_date") \
            .format(self.output_format) \
            .option("compression", self.compression) \
            .save(path)
        
        self.logger.info(f"{dataset_name} escrito exitosamente: {df.count()} registros")
    
    def write_mart(self, df: DataFrame, mart_name: str, run_date: str):
        """
        Escribe datos a la capa mart (KPIs)
        
        Args:
            df: DataFrame a escribir
            mart_name: Nombre del mart (kpis_daily, kpis_by_store, kpis_by_driver)
            run_date: Fecha de ejecución (YYYY-MM-DD)
        """
        if self.use_local:
            path = f"{self.config['output']['local']['mart']}{mart_name}/"
            self.logger.info(f"Escribiendo {mart_name} a archivo local: {path}")
        else:
            path = self.config['output']['mart'][mart_name]
            self.logger.info(f"Escribiendo {mart_name} a S3: {path}")
        
        # Escribir con particionado por fecha
        df.write \
            .mode("overwrite") \
            .partitionBy("event_date") \
            .format(self.output_format) \
            .option("compression", self.compression) \
            .save(path)
        
        self.logger.info(f"{mart_name} escrito exitosamente: {df.count()} registros")
    
    def write_to_redshift(self, df: DataFrame, table_name: str):
        """
        Escribe datos a Redshift (opcional)
        
        Args:
            df: DataFrame a escribir
            table_name: Nombre de la tabla en Redshift
        """
        if not self.config.get('redshift', {}).get('enabled', False):
            self.logger.info("Carga a Redshift deshabilitada")
            return
        
        redshift_config = self.config['redshift']
        
        jdbc_url = (
            f"jdbc:redshift://{redshift_config['host']}:{redshift_config['port']}"
            f"/{redshift_config['database']}"
        )
        
        self.logger.info(f"Escribiendo a Redshift: {redshift_config['schema']}.{table_name}")
        
        df.write \
            .format("io.github.spark_redshift_community.spark.redshift") \
            .option("url", jdbc_url) \
            .option("dbtable", f"{redshift_config['schema']}.{table_name}") \
            .option("tempdir", redshift_config['temp_dir']) \
            .option("aws_iam_role", redshift_config['iam_role']) \
            .mode("overwrite") \
            .save()
        
        self.logger.info(f"Datos escritos a Redshift exitosamente: {df.count()} registros")
