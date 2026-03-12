"""
Validaciones de calidad de datos
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when, isnan, isnull
import logging


class DataValidator:
    """Clase para validaciones de calidad de datos"""
    
    def __init__(self, config: dict):
        """
        Inicializa el validador de datos
        
        Args:
            config: Configuración del ETL
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.max_null_rate = config['data_quality']['max_null_rate']
        self.max_duplicate_rate = config['data_quality']['max_duplicate_rate']
        self.min_otd_threshold = config['data_quality']['min_otd_threshold']
    
    def validate_schema(self, df: DataFrame, dataset_name: str):
        """
        Valida que el schema del DataFrame sea el esperado
        
        Args:
            df: DataFrame a validar
            dataset_name: Nombre del dataset (para logging)
        """
        self.logger.info(f"Validando schema de {dataset_name}")
        
        # Obtener columnas actuales
        actual_columns = set(df.columns)
        
        # Definir columnas esperadas por dataset
        expected_columns = self._get_expected_columns(dataset_name)
        
        # Validar que existan las columnas críticas
        missing_columns = expected_columns - actual_columns
        
        if missing_columns:
            raise ValueError(
                f"Columnas faltantes en {dataset_name}: {missing_columns}"
            )
        
        self.logger.info(f"Schema de {dataset_name} validado correctamente")
    
    def validate_data_quality(self, df: DataFrame, dataset_name: str):
        """
        Valida la calidad de los datos
        
        Args:
            df: DataFrame a validar
            dataset_name: Nombre del dataset (para logging)
        """
        self.logger.info(f"Validando calidad de datos de {dataset_name}")
        
        total_records = df.count()
        
        if total_records == 0:
            raise ValueError(f"Dataset {dataset_name} está vacío")
        
        # Validar tasa de nulos en columnas críticas
        critical_columns = self._get_critical_columns(dataset_name)
        
        for column in critical_columns:
            if column not in df.columns:
                continue
            
            null_count = df.filter(col(column).isNull()).count()
            null_rate = null_count / total_records
            
            if null_rate > self.max_null_rate:
                raise ValueError(
                    f"Tasa de nulos muy alta en {dataset_name}.{column}: "
                    f"{null_rate:.2%} (máximo permitido: {self.max_null_rate:.2%})"
                )
            
            if null_rate > 0:
                self.logger.warning(
                    f"Nulos detectados en {dataset_name}.{column}: "
                    f"{null_count} ({null_rate:.2%})"
                )
        
        self.logger.info(f"Calidad de datos de {dataset_name} validada correctamente")
    
    def validate_kpis(self, df_kpis: DataFrame):
        """
        Valida que los KPIs estén en rangos esperados
        
        Args:
            df_kpis: DataFrame con KPIs calculados
        """
        self.logger.info("Validando KPIs calculados")
        
        # Validar que existan registros
        if df_kpis.count() == 0:
            raise ValueError("No se generaron KPIs")
        
        # Validar rangos de KPIs
        kpi_stats = df_kpis.agg({
            "otd_rate": "avg",
            "avg_lead_time_hours": "avg",
            "total_deliveries": "sum"
        }).collect()[0]
        
        avg_otd = kpi_stats[0]
        avg_lead_time = kpi_stats[1]
        total_deliveries = kpi_stats[2]
        
        # Validar OTD
        if avg_otd is not None:
            if avg_otd < 0 or avg_otd > 1:
                raise ValueError(
                    f"OTD rate fuera de rango [0, 1]: {avg_otd}"
                )
            
            if avg_otd < self.min_otd_threshold:
                self.logger.warning(
                    f"OTD rate por debajo del umbral esperado: "
                    f"{avg_otd:.2%} (mínimo: {self.min_otd_threshold:.2%})"
                )
        
        # Validar Lead Time
        if avg_lead_time is not None:
            max_lead_time = self.config['data_quality']['max_lead_time_days'] * 24
            
            if avg_lead_time < 0:
                raise ValueError(
                    f"Lead time negativo detectado: {avg_lead_time}"
                )
            
            if avg_lead_time > max_lead_time:
                self.logger.warning(
                    f"Lead time promedio muy alto: {avg_lead_time:.2f} horas "
                    f"(máximo esperado: {max_lead_time} horas)"
                )
        
        # Validar conteos
        if total_deliveries is None or total_deliveries == 0:
            raise ValueError("No se encontraron entregas en los KPIs")
        
        self.logger.info(
            f"KPIs validados correctamente - "
            f"OTD: {avg_otd:.2%}, Lead Time: {avg_lead_time:.2f}h, "
            f"Entregas: {total_deliveries}"
        )
    
    def _get_expected_columns(self, dataset_name: str) -> set:
        """Retorna las columnas esperadas para un dataset"""
        schemas = {
            "orders": {
                "id_pedido", "id_cliente", "id_producto", "fecha",
                "cantidad", "precio_unitario", "estado"
            },
            "deliveries": {
                "id_pedido", "conductor", "vehiculo", "fecha_asignacion",
                "fecha_entrega_prometida", "estado_entrega"
            }
        }
        
        return schemas.get(dataset_name, set())
    
    def _get_critical_columns(self, dataset_name: str) -> list:
        """Retorna las columnas críticas (no deben tener nulos) para un dataset"""
        critical = {
            "orders": ["id_pedido", "id_cliente", "id_producto", "fecha"],
            "deliveries": ["id_pedido", "fecha_entrega_prometida", "estado_entrega"]
        }
        
        return critical.get(dataset_name, [])
