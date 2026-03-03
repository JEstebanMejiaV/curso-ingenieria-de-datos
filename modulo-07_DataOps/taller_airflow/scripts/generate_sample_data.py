#!/usr/bin/env python3
"""
Script de Generación de Datos Sintéticos
Taller de Apache Airflow - Módulo 07 DataOps

Este script genera datos sintéticos realistas para el caso de uso de e-commerce:
- 1000 clientes con datos realistas
- 100 productos en 10 categorías
- 10,000 transacciones distribuidas en 30 días
- Incluye anomalías intencionales para validaciones de calidad

Uso:
    python scripts/generate_sample_data.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

# Configuración
SEED = 42
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 100
NUM_TRANSACTIONS = 10000
NUM_DAYS = 30
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"

# Categorías de productos
CATEGORIES = [
    "Electrónica",
    "Ropa",
    "Hogar",
    "Deportes",
    "Libros",
    "Juguetes",
    "Alimentos",
    "Belleza",
    "Automotriz",
    "Jardín"
]

# Inicializar Faker
fake = Faker(['es_ES', 'es_MX'])
Faker.seed(SEED)
random.seed(SEED)


def generate_customers(num_customers):
    """
    Genera datos de clientes con anomalías intencionales.
    
    Anomalías incluidas:
    - ~2% de clientes con email nulo
    - ~1% de clientes con nombre nulo
    - ~3% de clientes duplicados (mismo customer_id)
    """
    print(f"Generando {num_customers} clientes...")
    customers = []
    used_ids = set()
    duplicate_count = 0
    
    for i in range(num_customers):
        # Generar ID único (con algunas duplicaciones intencionales)
        if random.random() < 0.03 and used_ids:  # 3% duplicados
            customer_id = random.choice(list(used_ids))
            duplicate_count += 1
        else:
            customer_id = f"CUST{i+1:05d}"
            used_ids.add(customer_id)
        
        # Generar datos con anomalías
        customer_name = fake.name() if random.random() > 0.01 else None  # 1% nulos
        email = fake.email() if random.random() > 0.02 else None  # 2% nulos
        
        # Fecha de registro entre 1-3 años atrás
        days_ago = random.randint(365, 1095)
        registration_date = (datetime.now() - timedelta(days=days_ago)).date()
        
        customers.append({
            'customer_id': customer_id,
            'customer_name': customer_name,
            'email': email,
            'registration_date': registration_date
        })
    
    print(f"  ✓ Generados {len(customers)} clientes")
    print(f"  ⚠ Anomalías: {duplicate_count} IDs duplicados")
    return customers


def generate_products(num_products):
    """
    Genera catálogo de productos con anomalías intencionales.
    
    Anomalías incluidas:
    - ~2% de productos con precio nulo
    - ~5% de productos con precio fuera de rango (negativo o > 10000)
    - ~1% de productos con nombre nulo
    """
    print(f"Generando {num_products} productos...")
    products = []
    anomaly_count = {'null_price': 0, 'out_of_range': 0, 'null_name': 0}
    
    for i in range(num_products):
        product_id = f"PROD{i+1:04d}"
        category = random.choice(CATEGORIES)
        
        # Generar nombre de producto
        if random.random() < 0.01:  # 1% nulos
            product_name = None
            anomaly_count['null_name'] += 1
        else:
            product_name = f"{fake.word().capitalize()} {category}"
        
        # Generar precio con anomalías
        if random.random() < 0.02:  # 2% nulos
            price = None
            anomaly_count['null_price'] += 1
        elif random.random() < 0.05:  # 5% fuera de rango
            price = random.choice([
                round(random.uniform(-100, -0.01), 2),  # Negativos
                round(random.uniform(10001, 50000), 2)  # Muy altos
            ])
            anomaly_count['out_of_range'] += 1
        else:
            # Precios normales según categoría
            price_ranges = {
                'Electrónica': (50, 2000),
                'Ropa': (20, 300),
                'Hogar': (30, 1000),
                'Deportes': (25, 500),
                'Libros': (10, 80),
                'Juguetes': (15, 200),
                'Alimentos': (5, 100),
                'Belleza': (10, 150),
                'Automotriz': (100, 3000),
                'Jardín': (20, 500)
            }
            min_price, max_price = price_ranges.get(category, (10, 500))
            price = round(random.uniform(min_price, max_price), 2)
        
        products.append({
            'product_id': product_id,
            'product_name': product_name,
            'category': category,
            'price': price
        })
    
    print(f"  ✓ Generados {len(products)} productos")
    print(f"  ⚠ Anomalías: {anomaly_count['null_price']} precios nulos, "
          f"{anomaly_count['out_of_range']} precios fuera de rango, "
          f"{anomaly_count['null_name']} nombres nulos")
    return products


def generate_transactions(num_transactions, customers, products, num_days):
    """
    Genera transacciones con anomalías intencionales.
    
    Anomalías incluidas:
    - ~2% de transacciones con customer_id inexistente
    - ~2% de transacciones con product_id inexistente
    - ~3% de transacciones con amount nulo
    - ~5% de transacciones con amount fuera de rango (negativo o > 100000)
    - ~2% de transacciones con quantity nula o negativa
    - ~4% de transacciones duplicadas (mismo transaction_id)
    """
    print(f"Generando {num_transactions} transacciones en {num_days} días...")
    transactions = []
    used_ids = set()
    
    # Obtener IDs válidos
    valid_customer_ids = [c['customer_id'] for c in customers]
    valid_product_ids = [p['product_id'] for p in products]
    
    # Crear algunos IDs inválidos para anomalías
    invalid_customer_ids = [f"CUST99{i:03d}" for i in range(10)]
    invalid_product_ids = [f"PROD99{i:02d}" for i in range(10)]
    
    anomaly_count = {
        'duplicate_id': 0,
        'invalid_customer': 0,
        'invalid_product': 0,
        'null_amount': 0,
        'out_of_range_amount': 0,
        'invalid_quantity': 0
    }
    
    for i in range(num_transactions):
        # Generar ID de transacción (con duplicados intencionales)
        if random.random() < 0.04 and used_ids:  # 4% duplicados
            transaction_id = random.choice(list(used_ids))
            anomaly_count['duplicate_id'] += 1
        else:
            transaction_id = f"TXN{i+1:06d}"
            used_ids.add(transaction_id)
        
        # Seleccionar customer_id (con algunos inválidos)
        if random.random() < 0.02:  # 2% inválidos
            customer_id = random.choice(invalid_customer_ids)
            anomaly_count['invalid_customer'] += 1
        else:
            customer_id = random.choice(valid_customer_ids)
        
        # Seleccionar product_id (con algunos inválidos)
        if random.random() < 0.02:  # 2% inválidos
            product_id = random.choice(invalid_product_ids)
            anomaly_count['invalid_product'] += 1
        else:
            product_id = random.choice(valid_product_ids)
        
        # Generar fecha de transacción (distribuida en los últimos num_days días)
        days_ago = random.randint(0, num_days - 1)
        transaction_date = datetime.now() - timedelta(days=days_ago)
        # Agregar hora aleatoria
        transaction_date = transaction_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        # Generar cantidad
        if random.random() < 0.02:  # 2% inválidos
            quantity = random.choice([None, -1, -5, 0])
            anomaly_count['invalid_quantity'] += 1
        else:
            quantity = random.randint(1, 10)
        
        # Generar monto con anomalías
        if random.random() < 0.03:  # 3% nulos
            amount = None
            anomaly_count['null_amount'] += 1
        elif random.random() < 0.05:  # 5% fuera de rango
            amount = random.choice([
                round(random.uniform(-1000, -0.01), 2),  # Negativos
                round(random.uniform(100001, 500000), 2)  # Muy altos
            ])
            anomaly_count['out_of_range_amount'] += 1
        else:
            # Monto normal basado en precio del producto y cantidad
            product = next((p for p in products if p['product_id'] == product_id), None)
            if product and product['price'] and quantity:
                base_amount = product['price'] * quantity
                # Agregar variación de ±10%
                variation = random.uniform(0.9, 1.1)
                amount = round(base_amount * variation, 2)
            else:
                amount = round(random.uniform(10, 1000), 2)
        
        transactions.append({
            'transaction_id': transaction_id,
            'customer_id': customer_id,
            'product_id': product_id,
            'transaction_date': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'amount': amount,
            'quantity': quantity
        })
    
    print(f"  ✓ Generadas {len(transactions)} transacciones")
    print(f"  ⚠ Anomalías:")
    print(f"     - {anomaly_count['duplicate_id']} IDs duplicados")
    print(f"     - {anomaly_count['invalid_customer']} customer_id inválidos")
    print(f"     - {anomaly_count['invalid_product']} product_id inválidos")
    print(f"     - {anomaly_count['null_amount']} montos nulos")
    print(f"     - {anomaly_count['out_of_range_amount']} montos fuera de rango")
    print(f"     - {anomaly_count['invalid_quantity']} cantidades inválidas")
    
    return transactions


def save_to_csv(data, filename, fieldnames):
    """Guarda datos en archivo CSV."""
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"  ✓ Guardado en {filepath}")


def main():
    """Función principal."""
    print("=" * 70)
    print("Generador de Datos Sintéticos - Taller Airflow")
    print("=" * 70)
    print()
    
    # Crear directorio de salida si no existe
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generar datos
    customers = generate_customers(NUM_CUSTOMERS)
    print()
    
    products = generate_products(NUM_PRODUCTS)
    print()
    
    transactions = generate_transactions(NUM_TRANSACTIONS, customers, products, NUM_DAYS)
    print()
    
    # Guardar en archivos CSV
    print("Guardando archivos CSV...")
    save_to_csv(
        customers,
        'customers.csv',
        ['customer_id', 'customer_name', 'email', 'registration_date']
    )
    
    save_to_csv(
        products,
        'products.csv',
        ['product_id', 'product_name', 'category', 'price']
    )
    
    save_to_csv(
        transactions,
        'transactions.csv',
        ['transaction_id', 'customer_id', 'product_id', 'transaction_date', 'amount', 'quantity']
    )
    
    print()
    print("=" * 70)
    print("✓ Generación completada exitosamente")
    print("=" * 70)
    print()
    print("Resumen:")
    print(f"  - {len(customers)} clientes generados")
    print(f"  - {len(products)} productos generados")
    print(f"  - {len(transactions)} transacciones generadas")
    print(f"  - Archivos guardados en: {OUTPUT_DIR}")
    print()
    print("Nota: Los datos incluyen anomalías intencionales para practicar")
    print("      validaciones de calidad de datos en los DAGs de Airflow.")
    print()


if __name__ == "__main__":
    main()
