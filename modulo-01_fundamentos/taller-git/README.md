# Taller Git para Ingeniería de Datos

Este repositorio acompaña un taller práctico de 2 a 3 horas pensado para estudiantes de Ingeniería de Datos.

## Escenario

Eres parte del equipo de datos de una empresa ficticia de retail y crédito llamada **EcoShop 3000**. El equipo mantiene un repositorio con:

- Un pequeño pipeline de ingesta diaria de ventas.
- Un contrato de datos para la tabla de ventas.
- Archivos de datos de ejemplo.
- Un boceto de infraestructura para orquestar el pipeline.

Tu trabajo en el taller será versionar estos artefactos con Git, probar cambios en ramas, romper cosas a propósito y aprender a deshacerte de los errores sin miedo.

## Objetivos

Al finalizar el taller deberías ser capaz de:

- Manejar el flujo local de Git (working directory, staging, commit) usando archivos típicos de un proyecto de datos.
- Crear ramas para nuevas features de datos (nuevas columnas, reglas de calidad, particionamiento) y fusionarlas con `main`.
- Resolver conflictos cuando dos personas modifican el mismo pipeline o contrato.
- Usar `restore`, `reset`, `revert` y `reflog` para recuperar el estado de tu repo tras un cambio problemático.
- Entender cómo se conecta este flujo local con un flujo remoto en GitHub basado en ramas y Pull Requests.

## Requisitos previos

- Git instalado (`git --version`).
- Un editor de texto (VS Code o similar).
- Config básica de Git en tu máquina (solo la primera vez):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@correo.com"
git config --global init.defaultBranch main
```

Opcional pero recomendado:

- Instalar extensión de Git en VS Code.
- Tener una cuenta en GitHub para la parte de trabajo remoto.

## Estructura de los archivos del taller

```bash
taller-git/
├─ README.md
├─ data/
│  ├─ raw/
│  │  └─ sales_2025-01-01.csv
│  └─ processed/
├─ pipelines/
│  └─ etl_sales_daily.py
├─ docs/
│  └─ data_contract_sales.md
└─ infra/
   └─ airflow_dag_example.py
```

- `data/raw/`: simula la **zona raw** de un data lake.
- `data/processed/`: simula la **zona limpia / curated**. La irás poblando durante el taller.
- `pipelines/etl_sales_daily.py`: script Python muy simple que representa un pipeline de ingesta y limpieza diaria.
- `docs/data_contract_sales.md`: contrato de datos con la definición de columnas, tipos y reglas básicas.
- `infra/airflow_dag_example.py`: pseudocódigo de un DAG que orquesta el pipeline.

⚠️ > Nota: en las instrucciones se usa el marcador `<INI>` para tus iniciales (ej.: `JEM`). No lo pongas en nombres de archivos de verdad en Windows; úsalo solo dentro de los textos o como parte del contenido.

---

## Parte A: Repo local de un pipeline de datos (60–75 min)

### A1. Crear el repo y primer snapshot del proyecto

1. Clona o descomprime este repositorio en tu máquina.
2. Desde la carpeta raíz `git-taller/` inicializa Git:

```bash
git init
git status
```

3. Revisa el contenido de los archivos:

- `pipelines/etl_sales_daily.py`
- `docs/data_contract_sales.md`
- `data/raw/sales_2025-01-01.csv`

4. Añade todo al staging y crea el primer commit:

```bash
git add .
git commit -m "Snapshot inicial del pipeline de ventas"
git log --oneline
```

**Idea de contexto:** este primer commit es tu *estado base* de la plataforma de datos. A partir de aquí podrás evolucionar el pipeline y el contrato.

---

### A2. Evolucionar el pipeline como data engineer

Ahora simularás un cambio funcional típico: agregar una nueva columna derivada y actualizar el contrato de datos.

1. Abre `pipelines/etl_sales_daily.py` y agrega una transformación que calcule, por ejemplo, una columna `net_amount` (monto después de descuento) o `amount_usd` usando una tasa fija.

2. Abre `docs/data_contract_sales.md` y documenta:

- La nueva columna.
- El tipo de dato esperado.
- Alguna regla de calidad básica (por ejemplo, `net_amount >= 0`).

3. Guarda los cambios y revisa el estado:

```bash
git status
git diff
```

4. Añade y commitea:

```bash
git add pipelines/etl_sales_daily.py docs/data_contract_sales.md
git commit -m "Agregar columna derivada y actualizar contrato de datos"
git log --oneline --graph
```

**Pregunta para comentar en grupo:**

- ¿Por qué es importante que el contrato de datos evolucione al mismo tiempo que el pipeline?

---

### A3. Crear una rama de feature para una versión nueva del pipeline

Vas a crear una rama donde experimentarás una nueva forma de particionar los datos procesados.

1. Crea y cambia a una rama nueva:

```bash
git switch -c feature/particionado-ventas-<INI>
```
2. Añade un comentario en `docs/data_contract_sales.md` indicando la estrategia de particionado.

3. Crea el commit:

```bash
git add pipelines/etl_sales_daily.py docs/data_contract_sales.md
git commit -m "Definir nuevo particionamiento de datos de ventas (<INI>)"
```

Esta rama representa una **feature** aún no aprobada en producción.

---

### A4. Simular trabajo paralelo en `main` y un conflicto de merge

Mientras tú trabajabas en la rama de particionado, otra persona del equipo hizo cambios en `main` para añadir una regla de calidad extra en el mismo archivo.

1. Cambia a `main`:

```bash
git switch main
```

2. Edita `docs/data_contract_sales.md` en la **misma sección** donde documentaste columnas y reglas, y agrega una regla nueva (por ejemplo, "amount nunca debe ser negativo").

3. Crea un commit en `main`:

```bash
git add docs/data_contract_sales.md
git commit -m "Añadir regla de calidad sobre amount en contrato de ventas"
```

4. Vuelve a la rama de feature:

```bash
git switch feature/particionado-ventas-<INI>
```

5. Intenta fusionar `main` dentro de tu rama de feature:

```bash
git merge main
```

Seguramente verás un **conflicto** en `docs/data_contract_sales.md`, porque tanto `main` como tu rama editaron la misma sección.

6. Abre el archivo y resuelve el conflicto combinando las dos ideas:

- Mantén las nuevas reglas de calidad.
- Mantén la documentación del particionamiento.

Elimina las marcas `<<<<<<<`, `=======`, `>>>>>>>`.

7. Marca el conflicto como resuelto y completa el merge:

```bash
git add docs/data_contract_sales.md
git commit
```

8. Revisa el historial con todas las ramas:

```bash
git log --oneline --graph --decorate --all
```

---

### A5. Deshacer cambios 
Ahora vas a romper algo adrede y usar diferentes comandos para recuperarte.

#### 1. Crear un commit problemático

Edita `pipelines/etl_sales_daily.py` y borra por completo el cálculo de la nueva columna derivada, como si accidentalmente hubieras perdido una feature en producción.

```bash
git commit -am "Eliminar cálculo de columna derivada por error"
git log --oneline -n 3
```

#### 2. `git revert`: crear un commit que corrige el error

```bash
git revert HEAD
git log --oneline -n 5
```

Observa cómo `revert` crea un nuevo commit que revierte el cambio sin borrar historial.

#### 3. `git restore`: volver un archivo al último commit

Simula un error :

```bash
echo "Regla inventada que no aplica a este dataset" >> docs/data_contract_sales.md
git status
git restore docs/data_contract_sales.md
git status
```

#### 4. `git reset`: mover la rama

Crea un commit que solo sirva para practicar:

```bash
echo "# TODO: refactorizar particionamiento" >> pipelines/etl_sales_daily.py
git commit -am "Commit temporal para demo de reset (<INI>)"
git log --oneline -n 3
```

Prueba diferentes reset:

```bash
git reset --soft HEAD~1   # la rama vuelve atrás pero cambios quedan en staging
git status

git reset --mixed HEAD~1  # saca cambios del staging, quedan solo en working dir
git status

# PELIGROSO: descarta todo
# git reset --hard HEAD~1
```

#### 5. `git reflog`: máquina del tiempo del data engineer

```bash
git reflog
```

Identifica un hash anterior donde el proyecto estaba “sano” y vuelve a él:

```bash
git reset --hard <hash_seguro>
```

---

## Parte B: Git remoto y GitHub en un equipo de datos (40–60 min)

En esta parte conectas el concepto de ramas y commits con un flujo real de colaboración en GitHub, pensado para una **plataforma de datos**.

El escenario típico:

- Repo central: `plataforma-datos-empresa` (por ejemplo tu repo de curso).
- Cada equipo trabaja en una rama `equipo-XX-<INI>` dentro de una carpeta propia.
- Los cambios se integran a `main` mediante Pull Requests.

### B1. Preparar el repositorio remoto

Puedes reutilizar tu propio repo `curso-ingenieria-de-datos` como “plataforma de datos” o crear uno nuevo.

**Opción 1 (fork desde un repo docente):**

1. Haz fork del repo del curso en tu cuenta.
2. Clona tu fork:

```bash
git clone git@github.com:TU-USUARIO/curso-ingenieria-de-datos.git
cd curso-ingenieria-de-datos
git remote add upstream git@github.com:JEstebanMejiaV/curso-ingenieria-de-datos.git
git remote -v
```

**Opción 2 (acceso directo al repo del curso):**

1. Clona directamente el repo canónico:

```bash
git clone git@github.com:JEstebanMejiaV/curso-ingenieria-de-datos.git
cd curso-ingenieria-de-datos
```

### B2. Carpeta y rama por equipo 

En lugar de crear archivos genéricos, define una mini plataforma de datos por equipo dentro del curso:

```bash
# Usa un número de equipo y tus iniciales, por ejemplo equipo-01-JEM
git switch -c equipo-01-<INI>

mkdir -p "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/data/raw"
mkdir -p "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/pipelines"
mkdir -p "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/docs"
```

Crea algunos archivos con contexto de datos:

```bash
echo "# Plataforma de datos del equipo-01-<INI>"   > "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/README_<INI>.md"

echo "Definición inicial de contrato para tabla transacciones_<INI>"   > "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/docs/contrato_transacciones_<INI>.md"

echo "id_cliente,monto,fecha"   > "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/data/raw/transacciones_2025-01-01_<INI>.csv"

echo "# Pseudocódigo ETL: leer raw/transacciones y escribir processed/transacciones_limpias"   > "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/pipelines/etl_transacciones_<INI>.py"
```

Añade y empuja la rama:

```bash
git add .
git commit -m "equipo-01-<INI>: definir mini plataforma de datos del equipo"
git push -u origin equipo-01-<INI>
```

Abre un Pull Request desde `equipo-01-<INI>` hacia `main` en GitHub.

---

### B3. Ejercicios de colaboración 

Algunas ideas de ejercicios guiados que puedes hacer sobre estas carpetas:

1. **PR mínimo **

   - Actualizar el contrato de datos para agregar nuevas columnas.
   - Actualizar el pipeline para escribir una tabla limpia.
   - Abrir un PR con título tipo:  
     `"equipo-01-<INI>: agregar columna riesgo_crediticio al contrato y pipeline"`.

2. **Conflicto en el pipeline**

   - Dos personas del equipo editan la misma función en `etl_transacciones_<INI>.py` en ramas distintas.
   - Provocan conflicto y lo resuelven en el PR.
   - Documentan en el PR qué versión del cálculo quedó al final.

3. **Issue y PR vinculados a calidad de datos**

   - Crear un Issue: `"Agregar validación de montos negativos en transacciones_<INI>"`.
   - Abrir un PR que mencione `Closes #<n>` y que implemente la validación en el pipeline y en el contrato.


---

## Comandos útiles durante el taller

```bash
# Trabajo con repo local
git init
git status
git add <archivo>      # o: git add .
git commit -m "mensaje"
git log --oneline --graph --decorate
git diff [<rango>]
git switch -c <rama>   # crear y cambiar a rama nueva
git switch <rama>
git merge <rama>

# Deshacer y recuperar
git restore <archivo>
git reset --soft|--mixed|--hard <ref>
git revert <ref>
git reflog
git stash push -m "WIP"
git stash list
git stash apply

# Trabajo con remoto
git remote -v
git push -u origin <rama>
git fetch origin
git pull --rebase origin main

# Forks y upstream
git fetch upstream
git checkout main
git pull --rebase upstream main
git push origin main
```

Sugerencia: define un alias cómodo para ver el historial del repositorio de datos:

```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
```

