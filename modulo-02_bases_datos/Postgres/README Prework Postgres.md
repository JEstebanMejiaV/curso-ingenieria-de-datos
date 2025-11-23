# Prework Postgres + PGAdmin (Olist)

Este proyecto levanta una base de datos **Postgres** con el esquema de **Olist**
y un **PGAdmin** para explorarla gráficamente.

---

## 1. Estructura del proyecto

Los scripts de `initdb/` se ejecutan automáticamente cuando se crea el contenedor
de Postgres **por primera vez** (cuando el volumen `postgres_data` está vacío).

La carpeta `data/olist/` se monta dentro del contenedor en `/data/olist` y es
desde donde `02_olist_load.sql` hace los `\COPY`.

---

## 2. Variables de entorno

Revisa el archivo `.env` (y el `env` de ejemplo). Por defecto:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=olist
POSTGRES_PORT=5432

PGADMIN_DEFAULT_EMAIL=postgres@postgres.com
PGADMIN_DEFAULT_PASSWORD=postgres
PGADMIN_PORT=5050

POSTGRES_CONTAINER_NAME=my-postgres-olist
PGADMIN_CONTAINER_NAME=my-pgadmin-olist
```

Puntos importantes:

- El contenedor crea directamente la base de datos **`olist`** (no `postgres`).
- Los scripts `01_olist_schema.sql` y `02_olist_load.sql` asumen que se ejecutan
  ya conectados a `olist`.

---

## 3. Levantar el entorno con Makefile

Comandos típicos:

```bash
make up        # Levanta Postgres y PGAdmin
make status    # Muestra contenedores activos
make logs      # Muestra logs de Postgres
make psql      # Abre psql dentro del contenedor (DB: olist)
make seed      # Re-ejecuta los scripts SQL en initdb/ sobre la base olist
make down      # Apaga contenedores y borra el volumen de datos
```

> Importante: Si cambias los scripts SQL y quieres que se apliquen desde cero,
> usa `make down` para borrar el volumen y luego `make up` para que se vuelva
> a inicializar la base.

---

## 4. Conexión a Postgres desde PGAdmin

1. Abre `http://localhost:5050` (o el puerto que tengas en `PGADMIN_PORT`).
2. Inicia sesión con:
   - Email: `postgres@postgres.com`
   - Password: `postgres`

3. Crea un nuevo servidor:

   - En el panel izquierdo haz clic derecho en **Servers** → **Create** → **Server...**

   Pestaña **General**:
   - Name: `Curso-Ingenieria-Datos`

   Pestaña **Connection**:
   - Host name/address: `postgres`  
     (este es el **nombre del servicio** definido en `docker-compose.yml`,
      *no* `localhost`, *no* `my-postgres-container`)
   - Port: `5432`
   - Maintenance database: `postgres`
   - Username: `postgres`
   - Password: `postgres` (o la que tengas en tu `.env`)

4. Guarda. Ahora verás en el árbol:

```text
Servers
  └─ Curso-Ingenieria-Datos
      └─ Databases
          ├─ postgres
          └─ olist
```

---

## 5. ¿Dónde están las tablas de Olist?

Las tablas del dataset Olist se crean en la base de datos **`olist`**.

En el árbol de PGAdmin navega a:

```text
Servers › Curso-Ingenieria-Datos › Databases › olist › Schemas › public › Tables
```

Allí deberías ver:

- `olist_customers`
- `olist_geolocation`
- `olist_orders`
- `olist_order_items`
- `olist_order_payments`
- `olist_order_reviews`
- `olist_products`
- `olist_sellers`
- `product_category_name_translation`

Si no aparecen:

1. Verifica que los CSV estén en `data/olist` con los nombres correctos.
2. Ejecuta:

   ```bash
   make seed
   ```

   Esto vuelve a lanzar los scripts de `initdb/` dentro del contenedor
   (sobre la base `olist`).

3. Como última opción, recrea todo desde cero:

   ```bash
   make down     # Detiene contenedores y borra volumen
   make up       # Levanta de nuevo y reinicializa la BD
   ```

---

## 6. Uso desde la terminal (opcional)

Si quieres conectarte directamente desde el contenedor de Postgres:

```bash
make psql
```

Esto abre una sesión de `psql` usando las variables de tu `.env` (DB: `olist`).  
Una vez dentro, puedes hacer:

```sql
\l           -- listar bases de datos
\c olist     -- conectarte a la base olist (si no lo estás ya)
\dt          -- listar tablas
SELECT * FROM olist_orders LIMIT 5;
```

Con esto tienes un pequeño data warehouse de Olist listo para usar en ejercicios
de SQL intermedio y avanzado.
