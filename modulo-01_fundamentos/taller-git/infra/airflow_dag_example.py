"""
Pseudocódigo de un DAG de Airflow para orquestar el pipeline de ventas.

Este archivo se usa solo como contexto para el taller de Git.
"""

DAG_DESCRIPTION = """
DAG diario que:
- Lee archivos de data/raw
- Ejecuta el script pipelines/etl_sales_daily.py
- Publica la tabla de ventas limpia en data/processed
"""


if __name__ == "__main__":
    print(DAG_DESCRIPTION)
