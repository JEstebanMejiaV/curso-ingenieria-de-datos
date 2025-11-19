"""
Pequeño pipeline de ejemplo para el taller de Git orientado a Ingeniería de Datos.

Este script no pretende ser un ETL completo; solo da contexto.
"""

from pathlib import Path
import csv

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

INPUT_FILE = RAW_DIR / "sales_2025-01-01.csv"
OUTPUT_FILE = PROCESSED_DIR / "sales_2025-01-01_clean.csv"


def run_etl():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    rows_in = []
    with INPUT_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Regla de limpieza muy básica: ignorar montos negativos
            amount = float(row["amount"])
            if amount < 0:
                continue
            rows_in.append(row)

    # Por ahora solo reescribimos las filas válidas
    if not rows_in:
        print("No hay filas válidas para procesar.")
        return


if __name__ == "__main__":
    run_etl()
