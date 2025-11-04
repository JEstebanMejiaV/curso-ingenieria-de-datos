# 🧠 Curso de Ingeniería de Datos – Guía de Instalación y Prework

---

## 🧰 Herramientas de Desarrollo

🟦 **Git**  
_Control de versiones y clonación de repositorios._

🟪 **PostgreSQL**  
_Motor de base de datos relacional y de código abierto, robusto y confiable._

⬛ **PSQL (CLI)**  
_Cliente de línea de comandos para interactuar directamente con la base de datos._

🐳 **Docker + Docker Compose**  
_Ejecuta PostgreSQL y PGAdmin sin instalación manual._

💻 **PGAdmin / DBeaver / VS Code**  
_Herramientas visuales para explorar, consultar y modelar datos._

---

## 🧾 Instalación en 3 pasos

### 1️⃣ Clonar el Repositorio del Curso

Abre tu terminal y ejecuta:

```bash
git clone https://github.com/<usuario>/<curso-ingenieria-datos>.git
cd curso-ingenieria-datos
```

> 💡 Si es tu primera vez usando GitHub con SSH, sigue [esta guía oficial](https://docs.github.com/es/authentication/connecting-to-github-with-ssh).

---

### 2️⃣ Iniciar PostgreSQL

#### 🐳 **Opción A: Usando Docker (recomendada)**

1. Instala [Docker Desktop](https://www.docker.com/products/docker-desktop)  
2. Copia el archivo de entorno de ejemplo:

```bash
cp example.env .env
```

> El archivo `.env` contiene las credenciales de conexión a PostgreSQL y PGAdmin.

3. Inicia los contenedores:

```bash

# Windows o general
docker compose up -d


# macOS o Linux
make up


```

4. Verifica que estén corriendo:

```bash
docker ps -a
```

5. Cuando termines de trabajar:

```bash
docker compose stop
```

---

#### 🧩 **Opción B: Instalación local (manual)**

1. Instala PostgreSQL:  
   - **Windows/Linux:** descarga desde <https://www.postgresql.org/download/>
   - **macOS:** usa [Homebrew](https://brew.sh/)  
   

2. Restaura la base de datos de ejemplo:

```bash
pg_restore -c --if-exists -U <tu_usuario> -d postgres data.dump
```

Si falla, prueba:

```bash
pg_restore -U <usuario> -d <nombre_db> -h <host> -p <puerto> data.dump
```

---

### 3️⃣ Conectarse a PostgreSQL

#### 🌐 **Si usas PGAdmin (vía Docker)**

1. Abre <http://localhost:5050>  
2. Ingresa con las credenciales del archivo `.env`
3. Crea un nuevo servidor:
   - **General → Nombre:** `Curso-Ingenieria-Datos`
   - **Connection →**
     - Host: `my-postgres-container`
     - Puerto: `5432`
     - Base de datos: `postgres`
     - Usuario: `postgres`
     - Contraseña: `postgres`
     - ✅ Guarda la contraseña
4. Guarda los cambios y conecta.  
5. En el panel izquierdo, expande:
   ```
   Servers › Curso-Ingenieria-Datos › Databases › postgres › Schemas › public › Tables
   ```

---

#### 💻 **Si usas un cliente de escritorio (DBeaver, DataGrip, VS Code, etc.)**

Configura una nueva conexión PostgreSQL con los siguientes datos:

| Parámetro | Valor |
|------------|--------|
| Host | localhost |
| Puerto | 5432 |
| Base de datos | postgres |
| Usuario | postgres |
| Contraseña | postgres |

✅ Prueba la conexión y guárdala.

---

## 🧩 Problemas Frecuentes y Soluciones

### 📦 Las tablas no aparecen
- Asegúrate de haber restaurado correctamente `data.dump`.
- Si usas Docker, entra al contenedor y verifica:

```bash
docker exec -it my-postgres-container bash
psql -U postgres -d postgres -c '\dt'
```

---

### ❌ “Connection refused” o no se puede conectar
- Verifica que Docker esté corriendo.
- Revisa el host (`localhost` o `my-postgres-container`).
- Reinicia los contenedores:

```bash
make restart
```

---

### 🔄 Puerto 5432 en uso
Puede haber otro servicio usando el puerto.

**macOS/Linux**
```bash
lsof -i :5432
kill -9 <PID>
```

**Windows**
```cmd
netstat -ano | findstr :5432
taskkill /PID <PID> /F
```

---

### 🚪 Error al iniciar sesión en PGAdmin
Usa las credenciales del archivo `.env`:

```env
PGADMIN_DEFAULT_EMAIL=postgres@postgres.com
PGADMIN_DEFAULT_PASSWORD=postgres
```

Si cambiaste el `.env`, elimina el contenedor de PGAdmin y vuelve a ejecutar:

```bash
docker compose up -d
```

---

## 🔧 Comandos Útiles de Docker

| Comando | Descripción |
|----------|--------------|
| `make up` | Inicia los contenedores de PostgreSQL y PGAdmin |
| `make stop` | Detiene los contenedores |
| `make restart` | Reinicia el entorno completo |
| `make logs` | Muestra los registros |
| `make inspect` | Inspecciona la configuración |
| `make ip` | Muestra la IP del contenedor |

---

## 🧪 Verificación Final

Ejecuta estos comandos para validar tu entorno:

```bash
python --version
git --version
docker --version
psql --version
```

Si todos responden sin error, ¡ya estás listo para comenzar el curso! 🎉

---

