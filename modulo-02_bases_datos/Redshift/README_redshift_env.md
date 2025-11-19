# Guía de configuración de variables de entorno para Amazon Redshift

Este proyecto utiliza **Amazon Redshift** como base de datos y **NO** guarda credenciales en el código.  
En su lugar, la conexión se realiza a través de **variables de entorno**, que cada usuario debe configurar en su propio equipo.

Esta guía explica cómo definir esas variables en distintos sistemas operativos y entornos.

---

## 1. Variables de entorno requeridas

Los notebooks y scripts esperan las siguientes variables:

- `REDSHIFT_HOST`  
  Endpoint del clúster de Redshift  
  Ejemplo: `mi-cluster.abc123xyz.us-east-1.redshift.amazonaws.com`

- `REDSHIFT_PORT`  
  Puerto de Redshift  
  Valor típico: `5439` (opcional; si no se define, el código usa 5439 por defecto)

- `REDSHIFT_DB`  
  Nombre de la base de datos  
  Ejemplo: `dev`, `analytics` (opcional; por defecto `dev`)

- `REDSHIFT_USER`  
  Usuario de base de datos con permisos de lectura y escritura

- `REDSHIFT_PASSWORD`  
  Contraseña del usuario

> ⚠️ **No publiques estas variables en GitHub** ni las subas a repositorios compartidos.  
> Mantén tus credenciales locales o en un gestor de secretos.

---

## 2. Configuración en Linux / macOS (bash o zsh)

1. Abre una terminal.
2. Exporta las variables de entorno:

```bash
export REDSHIFT_HOST="TU-ENDPOINT.redshift.amazonaws.com"
export REDSHIFT_PORT="5439"
export REDSHIFT_DB="dev"
export REDSHIFT_USER="tu_usuario"
export REDSHIFT_PASSWORD="tu_password_super_secreta"
```

3. En la misma terminal, ejecuta Jupyter:

```bash
jupyter notebook
# o
jupyter lab
```

Las variables estarán disponibles para todos los notebooks abiertos desde esa sesión.

### 2.1. Hacerlo permanente (opcional)

Si quieres que las variables se definan siempre que abras una terminal:

- Edita tu archivo `~/.bashrc` o `~/.zshrc` y añade al final las líneas `export` anteriores.
- Recarga la configuración:

```bash
source ~/.bashrc
# o
source ~/.zshrc
```

---

## 3. Configuración en Windows (Command Prompt / CMD)

1. Abre **Command Prompt**.
2. Define las variables:

```bat
set REDSHIFT_HOST=TU-ENDPOINT.redshift.amazonaws.com
set REDSHIFT_PORT=5439
set REDSHIFT_DB=dev
set REDSHIFT_USER=tu_usuario
set REDSHIFT_PASSWORD=tu_password_super_secreta
```

3. En esa misma ventana, inicia Jupyter:

```bat
jupyter notebook
```

Las variables aplican solo para esa ventana de CMD.

---

## 4. Configuración en Windows (PowerShell)

1. Abre **PowerShell**.
2. Define las variables:

```powershell
$env:REDSHIFT_HOST = "TU-ENDPOINT.redshift.amazonaws.com"
$env:REDSHIFT_PORT = "5439"
$env:REDSHIFT_DB = "dev"
$env:REDSHIFT_USER = "tu_usuario"
$env:REDSHIFT_PASSWORD = "tu_password_super_secreta"
```

3. Luego ejecuta:

```powershell
jupyter lab
# o
jupyter notebook
```

---

## 5. Configurar variables desde el propio notebook (solo para demos)

Si no quieres modificar tu sistema, puedes definir las variables al inicio del notebook.  
Esto es útil en talleres o entornos temporales, pero no es lo ideal en producción.

En una celda de Python:

```python
import os

os.environ["REDSHIFT_HOST"] = "TU-ENDPOINT.redshift.amazonaws.com"
os.environ["REDSHIFT_PORT"] = "5439"
os.environ["REDSHIFT_DB"] = "dev"
os.environ["REDSHIFT_USER"] = "tu_usuario"
os.environ["REDSHIFT_PASSWORD"] = "tu_password_super_secreta"
```

Después de ejecutar esa celda, el resto del notebook podrá leer las variables sin problemas.

---

## 6. Uso de las variables en el código (ejemplo)

En los notebooks de este proyecto, la conexión a Redshift se hace así:

```python
import os
import redshift_connector
import pandas as pd

def get_redshift_config_from_env():
    missing = []
    host = os.environ.get("REDSHIFT_HOST")
    user = os.environ.get("REDSHIFT_USER")
    password = os.environ.get("REDSHIFT_PASSWORD")
    db = os.environ.get("REDSHIFT_DB", "dev")
    port = int(os.environ.get("REDSHIFT_PORT", "5439"))

    if host is None:
        missing.append("REDSHIFT_HOST")
    if user is None:
        missing.append("REDSHIFT_USER")
    if password is None:
        missing.append("REDSHIFT_PASSWORD")

    if missing:
        raise RuntimeError(
            "Faltan variables de entorno para conectar a Redshift: "
            + ", ".join(missing)
        )

    return {
        "host": host,
        "port": port,
        "database": db,
        "user": user,
        "password": password,
    }

REDSHIFT_CONFIG = get_redshift_config_from_env()

conn = redshift_connector.connect(
    host=REDSHIFT_CONFIG["host"],
    port=REDSHIFT_CONFIG["port"],
    database=REDSHIFT_CONFIG["database"],
    user=REDSHIFT_CONFIG["user"],
    password=REDSHIFT_CONFIG["password"],
)

def execute(sql: str):
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

def query(sql: str) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)
```

Si alguna variable falta, se lanza un error explicando qué variable debes definir.

---

## 7. Buenas prácticas

- No subas `.env` ni scripts con credenciales a repositorios públicos.
- Usa usuarios de Redshift con permisos mínimos necesarios para el taller.
- Si compartes este proyecto con estudiantes:
  - Deja este `README.md` en el repo.
  - Pídeles que **no** pongan credenciales en el código.
  - Si usan `.env`, recuérdales añadirlo al `.gitignore`.
