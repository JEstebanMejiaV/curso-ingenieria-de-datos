import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
import os

# --- 1. CONFIGURACIÓN POSTGRESQL (Local) ---

try:
    pg_pass = 'admin123' 
    pg_url = f'postgresql://postgres:{pg_pass}@localhost:5432/logidata_sas'
    pg_engine = create_engine(pg_url)
    print("✅ Conexión preparada para PostgreSQL")
except Exception as e:
    print(f" Error configurando PostgreSQL: {e}")

# --- 2. CONFIGURACIÓN MONGODB ATLAS (Nube) ---
try:
    mongo_uri = "mongodb+srv://logi_admin:clWf5rZf1BPW0NUG@logidata-cluster.epi3caj.mongodb.net/?appName=LogiData-Cluster"
    mongo_client = MongoClient(mongo_uri)
    db_iot = mongo_client['logidata_iot']
    print(" Conexión preparada para MongoDB Atlas")
except Exception as e:
    print(f" Error configurando MongoDB: {e}")

def ejecutar_migracion():
    print("\n Iniciando migración masiva...")

    # A. CARGA A POSTGRESQL (Tablas Relacionales)
    # El orden es vital para no romper las llaves foráneas (FK)
    tablas = ['clientes', 'catalogo', 'pedidos', 'entregas']
    
    for tabla in tablas:
        archivo = f"{tabla}.csv"
        if os.path.exists(archivo):
            print(f"    Procesando {archivo}...")
            df = pd.read_csv(archivo)
            # if_exists='append' para llenar las tablas que creamos en el ERD
            df.to_sql(tabla, pg_engine, if_exists='append', index=False)
            print(f"    {len(df)} registros insertados en la tabla '{tabla}'")
        else:
            print(f"   No se encontró el archivo: {archivo}")

    # B. CARGA A MONGODB (Datos de Sensores)
    archivo_sensores = "sensores.csv"
    if os.path.exists(archivo_sensores):
        print(f"   Procesando {archivo_sensores}...")
        df_iot = pd.read_csv(archivo_sensores)
        # Convertimos el DataFrame a una lista de diccionarios (formato JSON)
        datos_dict = df_iot.to_dict(orient='records')
        db_iot.sensores.insert_many(datos_dict)
        print(f"    {len(datos_dict)} eventos IoT enviados a MongoDB Atlas")
    else:
        print(f" No se encontró el archivo: {archivo_sensores}")

    print("\n Datos cargados exitosamente.")

if __name__ == "__main__":
    ejecutar_migracion()