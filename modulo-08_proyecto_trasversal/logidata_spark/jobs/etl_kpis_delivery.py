"""
ETL Principal para cálculo de KPIs de entregas - LogiData
HU7: Transformar pedidos y entregas en PySpark para KPIs de cumplimiento y eficiencia

Autor: Equipo de Ingeniería de Datos
Fecha: 2025-01-15
"""

import sys
import argparse
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyspark.sql import SparkSession
import yaml

# Importar módulos propios
from readers import DataReader
from cleaners import DataCleaner
from transformers import DataTransformer
from kpis import KPICalculator
from writers import DataWriter
from quality.validations import DataValidator


class ETLKPIsDelivery:
    """Clase principal del ETL para KPIs de entregas"""
    
    def __init__(self, env: str, run_date: str, mode: str = "incremental", 
                 use_local: bool = False):
        """
        Inicializa el ETL
        
        Args:
            env: Ambiente (dev, prod)
            run_date: Fecha de ejecución (YYYY-MM-DD)
            mode: Modo de ejecución (incremental, full, backfill)
            use_local: Si True, usa archivos locales en lugar de S3
        """
        self.env = env
        self.run_date = run_date
        self.mode = mode
        self.use_local = use_local
        self.batch_id = f"{run_date}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Cargar configuración
        self.config = self._load_config()
        
        # Configurar logging
        self._setup_logging()
        
        # Inicializar Spark
        self.spark = self._create_spark_session()
        
        # Inicializar componentes
        self.reader = DataReader(self.spark, self.config, use_local)
        self.cleaner = DataCleaner(self.config)
        self.transformer = DataTransformer(self.config)
        self.kpi_calculator = KPICalculator(self.config)
        self.writer = DataWriter(self.spark, self.config, use_local)
        self.validator = DataValidator(self.config)
        
        self.logger.info(f"ETL inicializado", extra={
            "batch_id": self.batch_id,
            "env": self.env,
            "run_date": self.run_date,
            "mode": self.mode,
            "use_local": self.use_local
        })
    
    def _load_config(self) -> dict:
        """Carga la configuración del ambiente"""
        config_path = Path(__file__).parent.parent / "config" / f"{self.env}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_format = self.config.get('logging', {}).get('format', 'json')
        
        if log_format == 'json':
            # Formato JSON estructurado
            logging.basicConfig(
                level=getattr(logging, log_level),
                format='%(message)s'
            )
        else:
            # Formato tradicional
            logging.basicConfig(
                level=getattr(logging, log_level),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        self.logger = logging.getLogger(__name__)
    
    def _create_spark_session(self) -> SparkSession:
        """Crea y configura la sesión de Spark"""
        builder = SparkSession.builder.appName(
            self.config['spark']['app_name']
        )
        
        # Aplicar configuraciones de Spark
        spark_config = self.config['spark'].get('config', {})
        for key, value in spark_config.items():
            builder = builder.config(key, value)
        
        spark = builder.getOrCreate()
        
        # Configurar nivel de log de Spark
        spark.sparkContext.setLogLevel("WARN")
        
        self.logger.info("Sesión de Spark creada exitosamente")
        return spark
    
    def run(self):
        """Ejecuta el ETL completo"""
        try:
            self.logger.info(f"Iniciando ETL", extra={
                "stage": "start",
                "batch_id": self.batch_id
            })
            
            # 1. Lectura de datos
            self.logger.info("Etapa 1: Lectura de datos", extra={"stage": "read"})
            df_pedidos, df_entregas, df_clientes, df_catalogo = self._read_data()
            
            # 2. Validación de entrada
            self.logger.info("Etapa 2: Validación de entrada", extra={"stage": "validate_input"})
            self._validate_input(df_pedidos, df_entregas)
            
            # 3. Limpieza y normalización
            self.logger.info("Etapa 3: Limpieza y normalización", extra={"stage": "clean"})
            df_pedidos_clean = self.cleaner.clean_orders(df_pedidos)
            df_entregas_clean = self.cleaner.clean_deliveries(df_entregas)
            df_clientes_clean = self.cleaner.clean_customers(df_clientes)
            df_catalogo_clean = self.cleaner.clean_catalog(df_catalogo)
            
            # 4. Enriquecimiento y transformaciones
            self.logger.info("Etapa 4: Enriquecimiento", extra={"stage": "transform"})
            df_orders_enriched = self.transformer.enrich_orders(
                df_pedidos_clean, df_clientes_clean, df_catalogo_clean
            )
            df_deliveries_enriched = self.transformer.enrich_deliveries(
                df_entregas_clean, df_orders_enriched
            )
            
            # 5. Cálculo de KPIs
            self.logger.info("Etapa 5: Cálculo de KPIs", extra={"stage": "kpis"})
            df_kpis_daily = self.kpi_calculator.calculate_daily_kpis(df_deliveries_enriched)
            df_kpis_by_store = self.kpi_calculator.calculate_kpis_by_store(df_deliveries_enriched)
            df_kpis_by_driver = self.kpi_calculator.calculate_kpis_by_driver(df_deliveries_enriched)
            
            # 6. Validación de salida
            self.logger.info("Etapa 6: Validación de salida", extra={"stage": "validate_output"})
            self._validate_output(df_kpis_daily)
            
            # 7. Escritura de resultados
            self.logger.info("Etapa 7: Escritura de resultados", extra={"stage": "write"})
            self._write_results(
                df_orders_enriched,
                df_deliveries_enriched,
                df_kpis_daily,
                df_kpis_by_store,
                df_kpis_by_driver
            )
            
            # 8. Métricas finales
            self._log_final_metrics(df_kpis_daily)
            
            self.logger.info(f"ETL completado exitosamente", extra={
                "stage": "complete",
                "batch_id": self.batch_id,
                "status": "success"
            })
            
        except Exception as e:
            self.logger.error(f"Error en ETL: {str(e)}", extra={
                "stage": "error",
                "batch_id": self.batch_id,
                "error": str(e)
            }, exc_info=True)
            raise
        
        finally:
            self.spark.stop()
    
    def _read_data(self):
        """Lee los datos de entrada"""
        start_time = datetime.now()
        
        df_pedidos = self.reader.read_orders(self.run_date, self.mode)
        df_entregas = self.reader.read_deliveries(self.run_date, self.mode)
        df_clientes = self.reader.read_customers()
        df_catalogo = self.reader.read_catalog()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        self.logger.info("Datos leídos exitosamente", extra={
            "stage": "read",
            "metrics": {
                "pedidos_count": df_pedidos.count(),
                "entregas_count": df_entregas.count(),
                "clientes_count": df_clientes.count(),
                "catalogo_count": df_catalogo.count(),
                "duration_seconds": duration
            }
        })
        
        return df_pedidos, df_entregas, df_clientes, df_catalogo
    
    def _validate_input(self, df_pedidos, df_entregas):
        """Valida los datos de entrada"""
        self.validator.validate_schema(df_pedidos, "orders")
        self.validator.validate_schema(df_entregas, "deliveries")
        self.validator.validate_data_quality(df_pedidos, "orders")
        self.validator.validate_data_quality(df_entregas, "deliveries")
    
    def _validate_output(self, df_kpis):
        """Valida los datos de salida"""
        self.validator.validate_kpis(df_kpis)
    
    def _write_results(self, df_orders_enriched, df_deliveries_enriched,
                      df_kpis_daily, df_kpis_by_store, df_kpis_by_driver):
        """Escribe los resultados"""
        start_time = datetime.now()
        
        # Escribir capas curated
        self.writer.write_curated(df_orders_enriched, "orders_enriched", self.run_date)
        self.writer.write_curated(df_deliveries_enriched, "deliveries_enriched", self.run_date)
        
        # Escribir marts de KPIs
        self.writer.write_mart(df_kpis_daily, "kpis_daily", self.run_date)
        self.writer.write_mart(df_kpis_by_store, "kpis_by_store", self.run_date)
        self.writer.write_mart(df_kpis_by_driver, "kpis_by_driver", self.run_date)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        self.logger.info("Resultados escritos exitosamente", extra={
            "stage": "write",
            "metrics": {
                "orders_enriched_count": df_orders_enriched.count(),
                "deliveries_enriched_count": df_deliveries_enriched.count(),
                "kpis_daily_count": df_kpis_daily.count(),
                "kpis_by_store_count": df_kpis_by_store.count(),
                "kpis_by_driver_count": df_kpis_by_driver.count(),
                "duration_seconds": duration
            }
        })
    
    def _log_final_metrics(self, df_kpis):
        """Registra métricas finales del ETL"""
        # Calcular métricas agregadas
        metrics = df_kpis.agg({
            "otd_rate": "avg",
            "avg_lead_time_hours": "avg",
            "total_deliveries": "sum"
        }).collect()[0]
        
        self.logger.info("Métricas finales del ETL", extra={
            "stage": "metrics",
            "batch_id": self.batch_id,
            "kpis": {
                "avg_otd_rate": float(metrics[0]) if metrics[0] else 0,
                "avg_lead_time_hours": float(metrics[1]) if metrics[1] else 0,
                "total_deliveries": int(metrics[2]) if metrics[2] else 0
            }
        })


def parse_args():
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="ETL para cálculo de KPIs de entregas - LogiData"
    )
    
    parser.add_argument(
        "--env",
        required=True,
        choices=["dev", "prod"],
        help="Ambiente de ejecución"
    )
    
    parser.add_argument(
        "--run-date",
        required=False,
        help="Fecha de ejecución (YYYY-MM-DD). Por defecto: ayer"
    )
    
    parser.add_argument(
        "--mode",
        default="incremental",
        choices=["incremental", "full", "backfill"],
        help="Modo de ejecución"
    )
    
    parser.add_argument(
        "--start-date",
        help="Fecha inicial para backfill (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--end-date",
        help="Fecha final para backfill (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--input-local",
        action="store_true",
        help="Usar archivos locales en lugar de S3"
    )
    
    return parser.parse_args()


def main():
    """Función principal"""
    args = parse_args()
    
    # Determinar fecha de ejecución
    if args.run_date:
        run_date = args.run_date
    else:
        # Por defecto, procesar el día anterior
        run_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Modo backfill: procesar múltiples fechas
    if args.mode == "backfill":
        if not args.start_date or not args.end_date:
            raise ValueError("Modo backfill requiere --start-date y --end-date")
        
        start = datetime.strptime(args.start_date, "%Y-%m-%d")
        end = datetime.strptime(args.end_date, "%Y-%m-%d")
        
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            print(f"\n{'='*60}")
            print(f"Procesando fecha: {date_str}")
            print(f"{'='*60}\n")
            
            etl = ETLKPIsDelivery(
                env=args.env,
                run_date=date_str,
                mode="incremental",  # Backfill usa incremental por fecha
                use_local=args.input_local
            )
            etl.run()
            
            current += timedelta(days=1)
    
    else:
        # Modo normal (incremental o full)
        etl = ETLKPIsDelivery(
            env=args.env,
            run_date=run_date,
            mode=args.mode,
            use_local=args.input_local
        )
        etl.run()


if __name__ == "__main__":
    main()
