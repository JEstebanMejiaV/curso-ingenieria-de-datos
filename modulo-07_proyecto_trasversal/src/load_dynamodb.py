"""
Script de carga de datos de sensores IoT a DynamoDB
Proyecto LogiData - Módulo 2 HU4
"""

import boto3  # Librería oficial de AWS para Python
import pandas as pd  # Leer el CSV
from pathlib import Path  # Manejar rutas de archivos
from decimal import Decimal  # DynamoDB requiere Decimals, no floats

# ============================================================
# CONFIGURACIÓN
# ============================================================

# Ruta a los archivos CSV
CSV_PATH = Path(__file__).parent.parent / "Datos"

# Configuración de conexión a DynamoDB Local
# endpoint_url: le decimos que NO use AWS real, sino nuestro servidor local
DYNAMODB_CONFIG = {
    "endpoint_url": "http://localhost:8000",  # DynamoDB Local corre aquí
    "region_name": "us-east-1",  # Región ficticia para local
    "aws_access_key_id": "fake",  # Credenciales falsas (no valida en local)
    "aws_secret_access_key": "fake"  # Credenciales falsas (no valida en local)
}

# ============================================================
# FUNCIÓN DE CONEXIÓN
# ============================================================

def get_dynamodb_resource():
    """Crea conexión a DynamoDB Local"""
    try:
        # resource es más alto nivel (más fácil de usar)
        dynamodb = boto3.resource('dynamodb', **DYNAMODB_CONFIG)
        print("Conexión exitosa a DynamoDB Local")
        return dynamodb
    except Exception as e:
        print(f"Error de conexión: {e}")
        print("   ¿Está corriendo el servidor? (java -jar DynamoDBLocal.jar)")
        raise

# ============================================================
# CREAR LA TABLA
# ============================================================

def crear_tabla_sensores(dynamodb):
    """Crea la tabla Sensores si no existe"""
    print("\n Creando tabla Sensores...")
    
    try:
        # Definición de la tabla
        tabla = dynamodb.create_table(
            TableName='Sensores',
            
            # CLAVES: cómo se organizan y buscan los datos
            KeySchema=[
                {
                    'AttributeName': 'vehiculo',  # Partition Key (PK)
                    'KeyType': 'HASH'  # Distribuye datos en "cajones"
                },
                {
                    'AttributeName': 'timestamp',  # Sort Key (SK)
                    'KeyType': 'RANGE'  # Ordena dentro del cajón
                }
            ],
            
            # TIPOS DE DATOS de las claves
            AttributeDefinitions=[
                {
                    'AttributeName': 'vehiculo',
                    'AttributeType': 'S'  # S = String
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'  # S = String (ISO 8601)
                }
            ],
            
            # CONFIGURACIÓN DE CAPACIDAD (para DynamoDB Local no importa mucho)
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Esperar a que la tabla esté creada
        tabla.wait_until_exists()
        print("Tabla Sensores creada")
        return tabla
        
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        # La tabla ya existe, solo la obtenemos
        print("Tabla Sensores ya existe, usando existente")
        return dynamodb.Table('Sensores')   
    

# ============================================================
# PREPARAR DATOS PARA DYNAMODB
# ============================================================   

def preparar_item(row):
    """
    Convierte una fila de pandas a formato DynamoDB.
    DynamoDB requiere tipos específicos.
    """
    item = {
        'vehiculo': str(row['vehiculo']),
        'timestamp': str(row['timestamp']),
        'latitud': Decimal(str(row['latitud'])),  # Decimal, no float
        'longitud': Decimal(str(row['longitud'])),
        'temperatura': Decimal(str(row['temperatura'])),
        'evento': str(row['evento'])
    }
    return item

# ============================================================
# CARGAR DATOS
# ============================================================  

def cargar_sensores(tabla):
    """Carga sensores.csv a DynamoDB"""
    print("\n Cargando sensores...")
    
    # Leer CSV
    df = pd.read_csv(CSV_PATH / "sensores.csv")
    print(f"   {len(df)} registros encontrados")
    
    # Cargar en lotes (más eficiente)
    with tabla.batch_writer() as batch:
        for idx, row in df.iterrows():
            item = preparar_item(row)
            batch.put_item(Item=item)
            
            # Mostrar progreso cada 1000 registros
            if (idx + 1) % 1000 == 0:
                print(f"   {idx + 1} registros cargados...")
    
    print(f"   ✅ {len(df)} sensores cargados")


# ============================================================
# VALIDAR CARGA
# ============================================================  


def validar_carga(tabla):
    """Verifica cuántos items hay en la tabla"""
    print("\n Validación de carga:")
    
    # Scan cuenta todos los items (en tablas grandes es lento, pero acá está bien)
    response = tabla.scan(Select='COUNT')
    total = response['Count']
    
    print(f"   Total items en tabla: {total}")
    
    # Contar por vehículo de ejemplo
    response = tabla.query(
        KeyConditionExpression='vehiculo = :v',
        ExpressionAttributeValues={':v': 'V0001'},
        Select='COUNT'
    )
    print(f"   Eventos del vehículo V0001: {response['Count']}")

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    print("=" * 50)
    print("CARGA DE SENSORES IoT A DYNAMODB LOCAL")
    print("=" * 50)

    # 1. Conectar
    dynamodb = get_dynamodb_resource()

    # 2. Crear tabla
    tabla = crear_tabla_sensores(dynamodb)

    # 3. Cargar datos
    cargar_sensores(tabla)

    # 4. Validar
    validar_carga(tabla)

    print("\n" + "=" * 50)
    print("CARGA COMPLETADA EXITOSAMENTE")
    print("=" * 50)

if __name__ == "__main__":
    main()