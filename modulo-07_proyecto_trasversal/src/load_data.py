"""
Script de carga de datos CSV a PostgreSQL
Proyecto LogiData - Módulo 2 HU3
Santiago
"""

import pandas as pd              # Para leer archivos CSV fácilmente
import psycopg2                  # Para conectar con PostgreSQL
from psycopg2.extras import execute_values  # Para insertar muchos datos rápido
import os                        # Para manejar rutas de archivos
from pathlib import Path         # Para rutas multiplataforma
from dotenv import load_dotenv   # Para cargar variables de entorno desde un archivo .env

# Cargar variables desde archivo .env (buscar en carpeta padre)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Ruta a los archivos CSV 
CSV_PATH = Path(__file__).parent.parent / "Datos"  # Busca la carpeta "Datos" donde está el script

# Configuración de conexión PostgreSQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "logidata_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}

# Validar que existe la contraseña
if not DB_CONFIG["password"]:
    raise ValueError("No se encontró DB_PASSWORD. Verifica que el archivo .env existe y tiene la contraseña")

# ============================================================
# FUNCIONES DE CONEXIÓN
# ============================================================

def get_connection():
    """Crear y retornar conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # Usar los datos de configuración
        print("Conexión exitosa a PostgreSQL")
        return conn
    except Exception as e:
        print(f"Error de conexión: {e}")
        raise  # Detener el programa si no puede conectar

# ============================================================
# CARGA DE TABLAS
# ============================================================

def cargar_clientes(conn):
    """Carga clientes.csv a tabla clientes"""
    print("\n Cargando clientes...")
    
    # 1. LEER EL CSV 
    df = pd.read_csv(CSV_PATH / "clientes.csv", encoding='utf-8')  # Asegura que se lean caracteres especiales

    # LIMPIAR DATOS: quitar tildes para cumplir constraints
    df['tipo_cliente'] = df['tipo_cliente'].replace('Farmacéutico', 'Farmaceutico')

    # Normalizar: quitar espacios y asegurar formato correcto
    df['tipo_cliente'] = df['tipo_cliente'].str.strip()
    df['zona'] = df['zona'].str.strip()
    
    print(f"   {len(df)} registros encontrados")
    
    # 2. INSERTAR EN POSTGRESQL 
    with conn.cursor() as cur:  # "with" es como pedir prestado el cursor y devolverlo automático
        execute_values(
            cur,  # El cursor lleva los datos a PostgreSQL
            """
            INSERT INTO clientes (id_cliente, nombre, zona, tipo_cliente)
            VALUES %s
            ON CONFLICT (id_cliente) DO NOTHING
            """,  # SQL: Inserta estos valores. Si ya existe el ID, ignóralo (no duplica)
            df.values.tolist()  # Convierte el DataFrame de pandas a lista de listas para PostgreSQL
        )
    conn.commit()  # "Sella el trato": confirma que los cambios se guarden definitivamente
    print(" Clientes cargados")   

def cargar_catalogo(conn):
    """Carga catalogo.csv a tabla catalogo"""
    print("\n Cargando catálogo...")
    
    # 1. LEER EL CSV
    df = pd.read_csv(CSV_PATH / "catalogo.csv")
    print(f"   {len(df)} registros encontrados")
    
    # 2. INSERTAR EN POSTGRESQL
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO catalogo (id_producto, categoria, precio, tipo_entrega)
            VALUES %s
            ON CONFLICT (id_producto) DO NOTHING
            """,
            df.values.tolist()
        )
    conn.commit()
    print("Catálogo cargado")


def cargar_pedidos(conn):
    """Carga pedidos.csv a tabla pedidos"""
    print("\n Cargando pedidos...")
    
    # 1. LEER EL CSV
    df = pd.read_csv(CSV_PATH / "pedidos.csv")
    
    # 2. CONVERTIR FECHAS (detalle nuevo)
    df['fecha'] = pd.to_datetime(df['fecha'])
    #    ↑↑↑↑↑↑↑
    #    PostgreSQL necesita fechas en formato especial
    #    Pandas las lee como texto del CSV, hay que convertirlas
    
    print(f"   {len(df)} registros encontrados")
    
    # 3. INSERTAR EN POSTGRESQL
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO pedidos (id_pedido, id_cliente, id_producto, fecha, monto, estado)
            VALUES %s
            ON CONFLICT (id_pedido) DO NOTHING
            """,
            df.values.tolist()
        )
    conn.commit()
    print("Pedidos cargados")


def cargar_entregas(conn):
    """Carga entregas.csv a tabla entregas"""
    print("\n Cargando entregas...")
    
    # 1. LEER EL CSV
    df = pd.read_csv(CSV_PATH / "entregas.csv")
    
    # 2. CONVERTIR AMBAS FECHAS
    df['hora_programada'] = pd.to_datetime(df['hora_programada'])
    df['hora_real'] = pd.to_datetime(df['hora_real'])
    #    ↑↑↑↑↑↑↑↑↑
    #    Dos columnas de fecha, dos conversiones
    
    print(f"   {len(df)} registros encontrados")
    
    # 3. INSERTAR EN POSTGRESQL
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO entregas (id_pedido, hora_programada, hora_real, zona, conductor, vehiculo)
            VALUES %s
            ON CONFLICT (id_pedido) DO NOTHING
            """,
            df.values.tolist()
        )
    conn.commit()
    print(" Entregas cargados")

# ============================================================
# VALIDACIÓN
# ============================================================

def validar_carga(conn):
    """Verifica volúmenes esperados"""
    print("\n Validación de carga:")
    
    with conn.cursor() as cur:
        # Lista de tablas y cuántos registros deberían tener
        tablas = ['clientes', 'catalogo', 'pedidos', 'entregas']
        esperados = [300, 200, 2000, 1800]  # Ajustar
        
        # Revisar cada tabla
        for tabla, esperado in zip(tablas, esperados):
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
            real = cur.fetchone()[0]  # Trae el número de filas
            
            # ¿Coincide con lo esperado?
            if real == esperado:
                print(f"{tabla}: {real} registros (OK)")
            else:
                print(f"{tabla}: {real} registros (esperado: {esperado})")

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    """Función principal que ejecuta todo el proceso de carga"""
    
    # 1. ENCABEZADO VISUAL (para saber que empezó)
    print("=" * 50)
    print("CARGA DE DATOS LOGIDATA A POSTGRESQL")
    print("=" * 50)
    
    # 2. VERIFICAR QUE EXISTEN LOS ARCHIVOS CSV
    
    if not (CSV_PATH / "clientes.csv").exists():
        print(f"No se encontraron CSV en: {CSV_PATH.absolute()}")
        print("   Ajusta la variable CSV_PATH en el script")
        return  # Termina el programa si no hay archivos
    
    # 3. CONECTAR A LA BASE DE DATOS
    #    (como llamar al almacén y confirmar que están abiertos)
    conn = get_connection()
    
    # 4. EJECUTAR TODAS LAS CARGAS EN ORDEN
    #    (el orden importa: primero maestros, luego transaccionales)
    try:
        cargar_clientes(conn)      # Paso 1: Maestro
        cargar_catalogo(conn)      # Paso 2: Maestro
        cargar_pedidos(conn)       # Paso 3: Transaccional (necesita 1 y 2)
        cargar_entregas(conn)      # Paso 4: Transaccional (necesita 3)
        validar_carga(conn)        # Paso 5: Verificación
        
        # 5. MENSAJE DE ÉXITO
        print("\n" + "=" * 50)
        print("CARGA COMPLETADA EXITOSAMENTE")
        print("=" * 50)
        
    except Exception as e:
        # Si algo falla, revierte todo (no quedan datos a medias)
        print(f"\n Error durante la carga: {e}")
        conn.rollback()  # Deshace cambios parciales
        raise  # Vuelve a lanzar el error para ver qué pasó
        
    finally:
        # 6. SIEMPRE CERRAR LA CONEXIÓN 
        conn.close()
        print("\n Conexión cerrada")


# Esta línea verifica si el script se ejecuta directamente
# (no si se importa como librería en otro archivo)
if __name__ == "__main__":
    main()