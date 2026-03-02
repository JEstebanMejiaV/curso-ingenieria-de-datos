import pandas as pd
import numpy as np
import uuid
import datetime
import random

def generate_dirty_dataset(num_rows=1000):
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    categories = ['Electronics', 'Clothing', 'Home', 'Toys']
    dirty_categories = ['Electronics', 'Clothing', 'Home', 'Toys', 'Elctronics', 'Clothin', None]
    
    start_date = datetime.date(2023, 1, 1)
    
    for _ in range(num_rows):
        # Generate some valid data
        order_id = str(uuid.uuid4())
        
        # Add some date issues (future dates or very old ones)
        if random.random() < 0.05:
            # Future date
            order_date = datetime.date(2030, 1, 1) + datetime.timedelta(days=random.randint(0, 100))
        elif random.random() < 0.05:
            # Null date
            order_date = None
        else:
            order_date = start_date + datetime.timedelta(days=random.randint(0, 365))
            
        customer_id = random.randint(1000, 9999)
        if random.random() < 0.02:
            customer_id = None
            
        if random.random() < 0.1:
            category = random.choice(dirty_categories)
        else:
            category = random.choice(categories)
            
        # Prices
        if random.random() < 0.03:
            price = round(random.uniform(-50.0, -1.0), 2)  # Negative price
        elif random.random() < 0.02:
            price = 0.0 # Zero price
        else:
            price = round(random.uniform(5.0, 500.0), 2)
            
        # Quantity
        if random.random() < 0.04:
            quantity = random.randint(-5, 0) # Negative or zero quantity
        elif random.random() < 0.01:
            quantity = random.randint(1000, 5000) # Unreasonably high
        else:
            quantity = random.randint(1, 10)
            
        data.append({
            'order_id': order_id,
            'order_date': order_date,
            'customer_id': customer_id,
            'product_category': category,
            'price': price,
            'quantity': quantity
        })
        
    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    df = generate_dirty_dataset(1500)
    output_path = 'ventas_sucias.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows in {output_path}")
