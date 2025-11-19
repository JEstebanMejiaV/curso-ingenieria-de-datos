"""
Pequeño pipeline de ejemplo para el taller de Git orientado a Ingeniería de Datos.

Este script no pretende ser un ETL completo; solo da contexto.
Ahora usa pandas para facilitar transformaciones y filtrados.
"""

from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

INPUT_FILE = RAW_DIR / "sales_2025-01-01.csv"
OUTPUT_FILE = PROCESSED_DIR / "sales_2025-01-01_clean.csv"


def run_etl(input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE) -> None:
    """Carga el CSV, aplica reglas de limpieza básicas y escribe el resultado."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar datos con pandas
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"No se encontró el archivo de entrada: {input_file}")
        return

    if df.empty:
        print("El archivo de entrada no tiene filas.")
        return

    # Aseguramos que la columna 'amount' sea numérica
    if "amount" not in df.columns:
        print("La columna 'amount' no existe en el archivo de entrada.")
        return

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Regla de limpieza muy básica: ignorar montos negativos o no numéricos
    df_clean = df[df["amount"] >= 0].copy()

    # Opcional: eliminar filas donde 'amount' sea NaN
    df_clean = df_clean.dropna(subset=["amount"])

    if df_clean.empty:
        print("No hay filas válidas para procesar después de la limpieza.")
        return

    # Aquí es fácil agregar más transformaciones con pandas
    # Ejemplo:
    # df_clean["amount_with_tax"] = df_clean["amount"] * 1.19

    df_clean.to_csv(output_file, index=False, encoding="utf-8")

    print(f"Filas procesadas: {len(df_clean)}")
    print(f"Archivo limpio escrito en {output_file}")


if __name__ == "__main__":
    run_etl()
