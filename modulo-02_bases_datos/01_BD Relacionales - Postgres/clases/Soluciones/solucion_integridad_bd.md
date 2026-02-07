# **Taller: Reglas de Integridad e integridad referencial con Olist (PostgreSQL)**
### Contexto:

Diseñar y aplicar **reglas de integridad** a nivel de tabla.

- **Reglas de Integridad:**
    
    Son condiciones que garantizan que los datos en una base de datos sean correctos, coherentes y confiables. 
    
    **Principales reglas de integridad:**
    
    1. Integridad de entidad - Cada fila debe ser unica y tener una **Clave primaria (PRIMARY KEY).**
    2. Integridad de dominio - Los valores deben cumpli con el tipo y rango definido.
    3. Integridad referencial - Las relaciones entre tablas deben ser válidas.
    4. Integridad de negocio - Reglas especificas de negocio. 
    
    ✅ **¿Cómo se aplican a nivel de tabla?**
    
    Se definen mediante restricciones (constrains) en la creación de la tabla:
    ```sql
    CREATE TABLE Movies (
		Id INT PRIMARY KEY,                 -- Integridad de entidad
		Title VARCHAR(100) NOT NULL,        -- Integridad de Dominio
		Director VARCHAR(100),
		Year INT CHECK (Year >= 1888),      -- Ano minimo 
		length_minutes INT CHECK (length_minutes > 0)
		); 
    ```

Lo anterior es un ejemplo de como se garantizan algunos tipos de integridades (especificados en los comentarios). Ahora para integridad referencial:

    ```sql
    CREATE TABLE Boxoffice (
	    Movie_id INT,
	    Rating DECIMAL(2,1),
	    Domestic_sales BIGINT,
	    International_sales BIGINT,
	    FOREIGN KEY (Movie_id) REFERENCES Movies(Id)   -- Integridad referencial
    );
    ```

En el anterior ejemplo se ve como la relacion entre las dos tablas (Movies y Boxoffice) es valida debido a la FOREING KEY que usa como referncia el Movie_id.

- **Lave Foránea**
    
    Una **llave foránea** es una **restricción (constraint)** en SQL que sirve para **relacionar dos tablas**.
    
    - Es una columna (o conjunto de columnas) en una tabla que **apunta a la clave primaria** de otra tabla.
        - Su función principal es **mantener la integridad referencial**, es decir, asegurar que los datos estén siempre consistentes entre tablas relacionadas.
        
       ✅ Pensemos que es un “puente” que conecta registros de una tabla con registros de otra.

            ```sql
        CREATE TABLE pedidos (
        id_pedido INT PRIMARY KEY,
        id_cliente INT,
        producto VARCHAR(100),
        CONSTRAINT fk_pedidos_clientes
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );
        ```
Probar que las reglas funcionan intentando insertar datos erroneos:

1. **Parte A : Reglas de integridad en una sola tabla**
    
    1.1. Diseñar constraints para `olist_customers`
    
    La tabla incialmente es:
    
    ```sql
    CREATE TABLE IF NOT EXISTS 
    olist_customers ( 
    						customer_id                VARCHAR(50),
    						customer_unique_id         VARCHAR(50),
    						customer_zip_code_prefix   INT,
    						customer_city              VARCHAR(100),
    						customer_state             VARCHAR(10)
    						);
    ```
    
    1.2. Propuesta de reglas para `olist_customers`
    
    - Elige:
        - `PRIMARY KEY`
        - Columnas `NOT NULL`
        - Columnas `UNIQUE` (por ejemplo, `customer_unique_id`).
        - Algún `CHECK` razonable, por ejemplo para `customer_state`.
    
    ```sql
    DROP TABLE IF EXISTS olist_customers CASCADE;
    CREATE TABLE IF NOT EXISTS 
    oliat_customers (
    						customer_id                VARCHAR(50)          PRIMARY KEY,
    						customer_unique_id         VARCHAR(50)          UNIQUE,
    						customerzip_code_prefix    INT,
    						customer_city              VARCHAR(100)       NOT NULL,
    						customer_state             VARCHAR(10)       CHECK (customer_state IN ('SP','RJ','MG','BA','RS'))
    						);       
    ```
    
    El primer comando que aparece: 
    
    ```sql
    DROP TABLE IF EXISTS olist_customers CASCADE;
    ```
    
    Implica que estamos borrando la tabla anterior y creando una nueva con la estructura correcta. **CUIDADO**, al hacer esto se pierden los datos que estaban guardados en la tabla original. En estos casos si la tabla ya existe usamos el `ALTER TABLE`:
    
    **Actividad 3 – Ajustar una tabla ya existente:**
    
    ```sql
    ALERT TABLE olist_customers
    	ADD CONSTRAINT pk_customers_id PRIMARY KEY (customer_id),
    	ADD CONSTRAINT uq_customer_unique_id UNIQUE (customer_unique_id),
    	ADD CONSTRAINT chk_customer_state CHECK (customer_state IN ('SP','RJ','MG','BA','RS'))
    	;
    
    -- Segunda: modificar columnas para NOT NULL
    	ALTER TABLE olist_customers
    	ALTER COLUMN customer_city SET NOT NULL
    	;
    ```
    
    **4 Diseñar constraints para `olist_products`:**
    
    Supongamos que tenemos la siguiente tabla:
    
    ```sql
    CREATE TABLE IF NOT EXISTS
    olist_products (
    							product_weight_g                INT,
    							product_length_cm               INT,
    							product_height_cm               INT,
    							product_width_cm                INT,
    							);
    ```
    
    **Actividad 4.2 – Reglas de integridad:**
    
    1. Define:
        - `PRIMARY KEY` para `olist_products`.
        - Columnas `NOT NULL` (al menos para identificadores).
    2. Define al menos 2 reglas `CHECK`. Por ejemplo:
        - Peso y dimensiones no pueden ser negativos.
        - Podrías permitir `NULL`, pero si hay valor, que sea mayor que cero.

El problema aca es que la tabla no tine identificador unico (Clave primaria) y tampoco las columnas olbigatorias (NOT NULL). Primero necesitmoas crear el identificador unico ya que las dimensiones y el peso no identifican u producto de forma unica, usaremos `product_id` :

```sql
CREATE TABLE IF NOT EXISTS olist_products (
    product_id VARCHAR(50) PRIMARY KEY, -- Identificador único
    product_weight_g INT NOT NULL CHECK (product_weight_g > 0), -- Peso obligatorio
    product_length_cm INT NOT NULL CHECK (product_length_cm > 0), -- Longitud obligatoria
    product_height_cm INT NOT NULL CHECK (product_height_cm > 0), -- Altura obligatoria
    product_width_cm INT NOT NULL CHECK (product_width_cm > 0) -- Ancho obligatorio
);
```

puedes usar `ALTER TABLE` si la tabla ya existe:

```sql
-- 1) Primary Key
ALTER TABLE olist_products
ADD CONSTRAINT pk_olist_products PRIMARY KEY (product_id);

-- 2) NOT NULL
ALTER TABLE olist_products
ALTER COLUMN product_weight_g SET NOT NULL,
ALTER COLUMN product_length_cm SET NOT NULL,
ALTER COLUMN product_height_cm SET NOT NULL,
ALTER COLUMN product_width_cm SET NOT NULL;

-- 3) CHECKs
ALTER TABLE olist_products
ADD CONSTRAINT chk_weight_pos  CHECK (product_weight_g > 0),
ADD CONSTRAINT chk_length_pos  CHECK (product_length_cm > 0),
ADD CONSTRAINT chk_height_pos  CHECK (product_height_cm > 0),
ADD CONSTRAINT chk_width_pos   CHECK (product_width_cm > 0);
```

**5. Parte B: Integridad referencial**
Se va a trabajar las relaciones entre tablas:

- `olist_orders.customer_id` referencia a `olist_customers.customer_id`.
- `olist_order_items.order_id` referencia a `olist_orders.order_id`.
- `olist_order_items.product_id` referencia a `olist_products.product_id`.
- `olist_order_items.seller_id` referencia a `olist_sellers.seller_id`.
- `olist_order_payments.order_id` referencia a `olist_orders.order_id`.

**5.1. Relación `orders` y `customers`:**

Definición sin constraints:

```sql
CREATE TABLE IF NOT EXISTS olist_orders (
    order_id                        VARCHAR(50),
    customer_id                     VARCHAR(50),
    order_status                    VARCHAR(20),
    order_purchase_timestamp        TIMESTAMP,
    order_approved_at               TIMESTAMP,
    order_delivered_carrier_date    TIMESTAMP,
    order_delivered_customer_date   TIMESTAMP
);
```

**Actividad 5.1.1 – Llave primaria y foránea**

1. Define:
    - `PRIMARY KEY` para `olist_orders`.
    - `FOREIGN KEY` de `olist_orders.customer_id` que apunte a `olist_customers(customer_id)`
    
    ```sql
    CREATE TABLE IF NOT EXISTS olist_orders (
        order_id VARCHAR(50)            PRIMARY KEY,
        customer_id VARCHAR(50),
        order_status VARCHAR(20), 
        order_purchase_timestamp        TIMESTAMP,
        order_approved_at               TIMESTAMP,
        order_delivered_carrier_date    TIMESTAMP,
        order_delivered_customer_date   TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES olist_customers(customer_id)
    																				);
    
    ```
    

Si la tabla ya existe y quisieramos usar el `ALTER TABLE`:

```sql
		-- Agregar la PRIMARY KEY de order_id
ALTER TABLE olist_orders
ADD CONSTRAINT pk_olist_orders PRIMARY KEY (order_id);

		-- Poner NOT NULL (Tal vez no sea tan necesario)
ALTER TABLE olist_orders
ALTER COLUMN customer_id SET NOT NULL,
ALTER COLUMN order_status SET NOT NULL,
ALTER COLUMN order_purchase_timestamp SET NOT NULL;

		-- Agregar la FOREIGN KEY customer_id -> olist_customers(customer_id)
ALTER TABLE olist_orders
ADD CONSTRAINT fk_orders_customer
FOREIGN KEY (customer_id) REFERENCES olist_customers(customer_id);
```

1. Elige una política de borrado y actualización:
    - `ON DELETE RESTRICT` o `NO ACTION`
    - `ON DELETE CASCADE`
    - `ON DELETE SET NULL`
    
- `ON DELETE RESTRICT` / `ON DELETE NO ACTION`
    
    **Bloquea** la eliminación del padre si hay hijos relacionados
    
    - Ejemplo: No puedes borrar un cliente si tiene órdenes.
    - Ideal para mantener histórico.
- `ON DELETE CASCADE`
    
    Si borras el padre, **borra automáticamente todos los hijos**.
    
    - Ejemplo: Borras un cliente → se borran todas sus órdenes.
    - Útil si no quieres datos huérfanos, pero cuidado en producción.
- `ON UPDATE CASCADE`
    
    Si actualizas el valor de la PK en el padre, **propaga el cambio** a los hijos
    
    - Ejemplo: Cambias `customer_id` en `olist_customers` → se actualiza en todas las órdenes.

```sql
		-- Si no tenemos que crear la tabla
CREATE TABLE IF NOT EXISTS olist_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES olist_customers(customer_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

		-- Si tenemos la tabla creada o bien ya existe

ALTER TABLE olist_orders
ADD CONSTRAINT fk_orders_customer
FOREIGN KEY (customer_id) REFERENCES olist_customers(customer_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

```

**5.2. `order_items` como tabla de detalle**
Definición simplificada:

```sql
CREATE TABLE IF NOT EXISTS olist_order_items (
    order_id             VARCHAR(50),
    order_item_id        INT,
    product_id           VARCHAR(50),
    seller_id            VARCHAR(50),
    shipping_limit_date  TIMESTAMP,
    price                NUMERIC(10,2),
    freight_value        NUMERIC(10,2)
);
```

**Actividad 5.2.1 – Clave primaria compuesta y FKs**

1. Propón una `PRIMARY KEY` razonable para `olist_order_items`.
Pista: un pedido puede tener varios ítems.
    
```sql
CREATE TABLE IF NOT EXISTS olist_order_items (
    order_id VARCHAR(50)      PRIMARY KEY,
    order_item_id             INT,
    product_id                VARCHAR(50),
    seller_id                 VARCHAR(50),
    shipping_limit_date       TIMESTAMP,
    price                     NUMERIC(10,2),
    freight_value             NUMERIC(10,2)
);

	--  Si la tabla ya existe
ALTER TABLE olist_order_items
    ADD CONSTRAINT pk_olist_orders PRIMARY KEY (order_id);
```
    
2. Define las llaves foráneas:

- `order_id` referencia a `olist_orders(order_id)`.
- `product_id` referencia a `olist_products(product_id)`.
- `seller_id` referencia a `olist_sellers(seller_id)`.
    
    ```sql
    ALTER TABLE olist_order_items
    		ADD CONSTRAINT fk_order_id 
    		FOREIGN KEY (order_id) REFERENCES olist_orders(order_id);
    		
    ALTER TABLE olist_order_items
    		ADD CONSTRAINT fk_product_id 
    		FOREIGN KEY (product_id) REFERENCES olist_products(product_id);
        
    ALTER TABLE olist_order_items
    		ADD CONSTRAINT fk_seller_id 
    		FOREIGN KEY (seller_id) REFERENCES olist_sellers(seller_id);
    ```
    

**Actividad 5.2.2 – Debate de políticas de borrado**

- ¿Es buena idea usar `ON DELETE CASCADE` en la FK de `order_id`?

*NO es recomendable en este caso usar dicha clausula. Si borramos una orden en `olist_orders`, automaticamente se borran todos los items ascociados en `olist_orders_items`.  Probablemente es mejor usar `ON DELETE RESTRICT o NO ACTION` para bloquear la eliminacion de la orden si esta tiene items. Normalmente no se borran las ordenes, se marcan como canceladas o archivadas y asi mantener trazabilidad.*

- ¿Qué pasaría si alguien borra un `order` por error?

*La base de datos **automáticamente eliminará todos los ítems asociados a esa orden** en `olist_order_items`.  Se borran **todas las filas** en `olist_order_items` con `order_id = 'ORD123'.` no solo la orden, sino también el detalle de productos, precios, vendedores, etc.*

- ¿Qué alternativas propondrías en un sistema real?

*Probablemente es mejor usar `ON DELETE RESTRICT o NO ACTION` para bloquear la eliminacion de la orden si esta tiene items. Normalmente no se borran las ordenes, se marcan como canceladas o archivadas y asi mantener trazabilidad.*

**5.3. `order_payments` y `orders`**

Definición simplificada:

```sql
CREATE TABLE IF NOT EXISTS olist_order_payments (
    order_id              VARCHAR(50),
    payment_sequential    INT,
    payment_type          VARCHAR(50),
    payment_installments  INT,
    payment_value         NUMERIC(10,2)
);
```

**Actividad 5.3.1 – Clave compuesta, CHECK y FK**

1. Elige una `PRIMARY KEY` (por ejemplo, `(order_id, payment_sequential)`).
2. Define un `CHECK` para asegurar que `payment_value` sea mayor que cero.
3. Define una `FOREIGN KEY` desde `order_id` a `olist_orders(order_id)`.
    
    ```sql
    -- 1) PRIMARY KEY compuest
    ALTER TABLE olist_order_payments
    			ADD CONSTRAINT pk_olist_order_payments
    			PRIMARY KEY (order_id, payment_sequential)
    			;
    -- 2) CHECK: payment_value > 0
    ALTER TABLE olist_order_payments
    			ADD CONSTRAINT chk_payment_value CHECK (payment_value > 0)
    			;
    			
    ALTER TABLE fk_order_id
    			ADD CONSTRAINT FOREIGN KEY order_ir REFERENCES olist_orders(order_id)	
    			ON DELETE RESTRICT
    			ON UPDATE CASCADE
    			;
    ```
    

## 6. Parte C: Probar las reglas con datos “malos”

El objetivo de esta parte es **forzar errores** y leer los mensajes que genera PostgreSQL.

### 6.1. Pruebas de integridad simple

### Actividad 6.1.1 – NOT NULL y CHECK

Escribe `INSERT` que deban fallar y guárdalos en `03_pruebas_errores.sql`:

1. Insertar un `customer` sin `customer_id` (si lo marcaste `NOT NULL` o `PRIMARY KEY`).
2. Insertar un `product` con `product_weight_g = -10`.
3. Insertar un `order_payment` con `payment_value = 0` o negativo.

Ejemplo orientativo (ajusta según tus constraints):

```sql
-- Ejemplo: debe disparar un CHECK o NOT NULL
INSERT INTO olist_products (product_id, product_weight_g)
VALUES ('TEST-PROD-001', -10);
```