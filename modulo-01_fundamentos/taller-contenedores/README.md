# Taller práctico de Docker y Docker Compose para Ingeniería de Datos

Este taller contiene un mini proyecto para aprender:

- Conceptos básicos de Docker (imágenes, contenedores, volúmenes).
- Cómo empaquetar un pipeline de datos en una imagen Docker.
- Cómo usar Docker Compose para levantar un pequeño stack de datos:
  - PostgreSQL
  - pgAdmin
  - Un pipeline de limpieza y carga de datos con Python.



## Estructura del proyecto

```bash
taller-contenedores/
├─ README.md
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ src/
│  └─ pipeline.py
└─ data/
   ├─ input/
   │  └─ sales.csv
   └─ output/
```

- `data/input/sales.csv`: archivo de ventas de ejemplo.
- `data/output/`: aquí se guardará el CSV limpio.
- `src/pipeline.py`: script en Python que:
  - Lee el CSV, Aplica reglas simples de limpieza, Guarda un CSV limpio, Carga los datos en PostgreSQL.
- `Dockerfile`: define la imagen del pipeline.
- `docker-compose.yml`: orquesta la base de datos, pgAdmin y el pipeline.

## Primeros pasos con Docker

Desde la raíz del proyecto:

```bash
docker version
docker run hello-world
```

Prueba un contenedor interactivo de Python:

```bash
docker run -it python:3.12-slim python
```

Dentro del contenedor:

```python
import sys
print("Hola desde Docker:", sys.version)
```

## Ejecutar el pipeline con Docker (sin Compose)

Primero construye la imagen:

```bash
docker build -t sales-pipeline:latest .
```

Ejecuta el contenedor montando la carpeta `data`:

```bash
docker run --rm   -v "$(pwd)/data:/app/data"   sales-pipeline:latest
```

Esto debería:

- Leer `data/input/sales.csv`.
- Crear `data/output/sales_clean.csv`.

Puedes revisar el archivo de salida:

```bash
ls data/output
cat data/output/sales_clean.csv
```

## Levantar el stack completo con Docker Compose

El archivo `docker-compose.yml` define tres servicios:

- `db`: PostgreSQL.
- `pgadmin`: interfaz gráfica para administrar la base de datos.
- `pipeline`: contenedor con el script de limpieza y carga.

Levantar todo:

```bash
docker compose up --build
```

Esto:

- Construye la imagen del pipeline.
- Levanta Postgres y pgAdmin.
- Ejecuta el pipeline, que limpia datos y los carga en la tabla `sales`.

### Acceder a pgAdmin

1. Abre el navegador en:  
   `http://localhost:8081`
2. Usuario: `admin@example.com`  
   Contraseña: `admin`
3. Crea un nuevo servidor en pgAdmin:
   - Host: `db`
   - Puerto: `5432`
   - Usuario: `sales_user`
   - Password: `sales_pass`
   - Base de datos: `sales_db`
4. Ve a la base `sales_db` y busca la tabla `public.sales`.
5. Ejecuta:

   ```sql
   SELECT * FROM public.sales;
   ```

Deberías ver los datos limpios cargados desde el pipeline.



## Retos extra

- Cambiar la lógica de limpieza en `pipeline.py` (por ejemplo, filtrar `amount >= 50`).
- Agregar una nueva columna calculada (por ejemplo, `amount_usd`).
- Añadir un servicio de Jupyter Notebook en el `docker-compose.yml` para explorar la tabla `sales` desde notebooks.

