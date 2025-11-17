import os
import time
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


INPUT_PATH = Path("/app/data/input/sales.csv")
OUTPUT_DIR = Path("/app/data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "sales_clean.csv"


def wait_for_db(engine, max_tries: int = 10, delay_seconds: int = 5) -> None:
    """
    Espera a que la base de datos esté disponible.
    Intenta conectarse varias veces antes de rendirse.
    """
    tries = 0
    while tries < max_tries:
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("Base de datos disponible.")
            return
        except OperationalError as exc:
            tries += 1
            print(
                f"No se pudo conectar a la base de datos (intento {tries}/{max_tries}). "
                f"Error: {exc}"
            )
            time.sleep(delay_seconds)

    raise RuntimeError("No fue posible conectar a la base de datos después de varios intentos.")


def main():
    # 1. Cargar datos
    print(f"Cargando datos desde: {INPUT_PATH}")
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    # 2. Limpieza simple: quedarnos con amount > 0
    df_clean = df[df["amount"] > 0].copy()
    df_clean["order_date"] = pd.to_datetime(df_clean["order_date"])

    print(f"Filas originales: {len(df)}")
    print(f"Filas limpias: {len(df_clean)}")

    # 3. Guardar CSV limpio
    df_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"Datos limpios guardados en: {OUTPUT_PATH}")

    # 4. Preparar conexión a Postgres usando variables de entorno
    user = os.getenv("DB_USER", "sales_user")
    password = os.getenv("DB_PASSWORD", "sales_pass")
    host = os.getenv("DB_HOST", "db")
    dbname = os.getenv("DB_NAME", "sales_db")

    url = f"postgresql://{user}:{password}@{host}:5432/{dbname}"
    print(f"Conectando a la base de datos en: {url}")

    engine = create_engine(url)

    # 5. Esperar a que la base de datos esté lista
    wait_for_db(engine)

    # 6. Cargar datos a la tabla "sales"
    print("Cargando datos a la tabla 'sales' en Postgres...")
    df_clean.to_sql("sales", engine, if_exists="replace", index=False)
    print("Carga completada. Tabla 'sales' creada o reemplazada en la base de datos.")


if __name__ == "__main__":
    main()
