# Taller: Git — Solo repositorio local (2–3 h)

> **Sustituye `<INI>` por tus iniciales** (ej: `JEMV`). Todos los archivos de ejemplo usan ese sufijo.

## Objetivos
- Dominar el flujo local: *working directory → staging → commit*.
- Crear **ramas**, **fusionar** y **resolver conflictos**.
- Rehacer cambios con **restore / reset / revert / reflog**.
- (Opcional) trabajar con **stash** y **tags** locales.

## Requisitos previos
- Git instalado (`git --version`).
- Editor de texto (VS Code o similar).
- Config inicial (una vez en tu máquina):
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@correo.com"
git config --global init.defaultBranch main
```


## Primer repo y primeros commits (30 min)
**Meta:** crear repo, añadir, hacer commits y ver historial.

1) Crea carpeta y repo:
```bash
mkdir git-local-taller-<INI> && cd git-local-taller-<INI>
git init
```

2) Archivos iniciales (usa tus iniciales):
```bash
mkdir notas
echo "# Diario de laboratorio <INI>" > README_<INI>.md
echo "Día 1: hipótesis" > notas/<INI>_dia1.txt
git status
```

3) Staging & commit:
```bash
git add README_<INI>.md notas/<INI>_dia1.txt
git commit -m "Inicial (<INI>): README y nota día 1"
```

4) Cambios y segundo commit:
```bash
echo "Día 2: experimento" > notas/<INI>_dia2.txt
echo "- Objetivo: probar X" >> README_<INI>.md
git add .
git commit -m "Agregar nota día 2 y objetivo en README (<INI>)"
```

5) Historial y diffs:
```bash
git log --oneline --graph --decorate
git show HEAD~1
git diff HEAD~1..HEAD
```


##  Ramas locales y merge con conflicto (40–50 min)
**Meta:** crear ramas, fusionar y resolver conflictos.

1) Nueva rama de feature:
```bash
git checkout -b feature/resumen-<INI>
echo "Resumen del proyecto (<INI>)" > resumen_<INI>.md
git add resumen_<INI>.md
git commit -m "Crear resumen inicial (<INI>)"
```

2) Cambios en `main`:
```bash
git switch main
echo "Sección Resumen (versión main, <INI>)" >> README_<INI>.md
git commit -am "Añadir sección resumen en README (main, <INI>)"
```

3) Genera conflicto editando **la misma línea** del README en la rama:
```bash
git switch feature/resumen-<INI>
# Abre README_<INI>.md y agrega/edita EXACTAMENTE la misma sección,
# por ejemplo: "Sección Resumen (versión feature, <INI>)"
git commit -am "Actualizar sección resumen en README (feature, <INI>)"
```

4) Merge y resolución:
```bash
git switch main
git merge feature/resumen-<INI>
# Resuelve el conflicto en README_<INI>.md (elimina <<<<<<< ======= >>>>>>)
git add README_<INI>.md
git commit  # finaliza el merge
```

5) Revisa:
```bash
git log --oneline --graph --decorate --all
```


## Rehacer cambios: restore, reset, revert, reflog (35–45 min)
**Meta:** practicar formas seguras de deshacer.

1) Crea un “error”:
```bash
echo "línea errónea (<INI>)" >> README_<INI>.md
git add README_<INI>.md
git commit -m "Error: línea que no debía estar (<INI>)"
```

2) **revert** (crea un commit que deshace el anterior):
```bash
git revert HEAD
```

3) **restore** (volver un archivo al último commit):
```bash
echo "borrón temporal (<INI>)" >> notas/<INI>_dia1.txt
git restore notas/<INI>_dia1.txt
```

4) **reset** (mueve la rama; cuidado):
```bash
echo "prueba reset (<INI>)" >> README_<INI>.md
git commit -am "Commit para reset demo (<INI>)"
git log --oneline -n 3

git reset --soft HEAD~1   # vuelve atrás manteniendo cambios en staging
git reset --mixed HEAD~1  # vuelve atrás y saca de staging (deja en working dir)
# git reset --hard HEAD~1 # (PELIGROSO) descarta cambios definitivos
```

5) **reflog** (recuperar referencias recientes):
```bash
git reflog
git reset --hard <hash_seguro>
```


## Anexo: tipos de reset
- `--soft`: mueve la rama atrás **manteniendo** cambios en *staging* (index).
- `--mixed` *(por defecto)*: mueve la rama y saca los cambios del *staging* (quedan en *working dir*).
- `--hard`: mueve la rama y **descarta** cambios del *staging* y *working dir* (peligroso).


**Sugerencia:** crea un alias útil para ver el historial bonito:
```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
```


# Taller: Git remoto & GitHub — Trabajo **dentro de una carpeta fija**

**Repositorio canónico:** `https://github.com/JEstebanMejiaV/curso-ingenieria-de-datos`  
**Carpeta de trabajo (obligatoria):** `modulo-01_fundamentos/Taller Git/`

> 🔐 **Regla de oro del taller:** *Todos los archivos y cambios deben quedar **dentro** de tu subcarpeta de equipo bajo `modulo-01_fundamentos/Taller Git/`.*  
> Ejemplo de subcarpeta: `modulo-01_fundamentos/Taller Git/equipo-01-<INI>/` (reemplaza `<INI>` por tus iniciales, p. ej., `JEM`).

---

## Objetivos
- Conectar repos **locales** con **remotos** (GitHub) y trabajar por **ramas**.
- Colaborar mediante **Pull Requests** (PR), revisiones y comentarios.
- Aplicar **protección de rama**, **Issues** y referencias (`Closes #n`).
- Sincronizar forks con `upstream` y resolver divergencias (p. ej., **squash merge**).
- (Opcional) Ejecutar un **check** mínimo con **GitHub Actions**.

## Requisitos
- Cuenta en GitHub y Git instalado (`git --version`).
- Autenticación (elige una):
  - **SSH (recomendado)** → `ssh-keygen -t ed25519 -C "tu@correo.com"` → agrega clave pública a GitHub → prueba: `ssh -T git@github.com`.
  - **HTTPS + Personal Access Token (PAT)** con scope `repo` (úsalo como contraseña al hacer `git push`).


## Convención de carpetas y ramas
- **Subcarpeta obligatoria por equipo:** `modulo-01_fundamentos/Taller Git/equipo-XX-<INI>/`
- **Ramas:** `equipo-XX-<INI>` (una rama por equipo).
- **Mensajes de commit:** modo imperativo y claro (ej.: *"Agregar checklist inicial"*).

> ⚠️ **No modifiques** archivos fuera de `modulo-01_fundamentos/Taller Git/`. Si lo haces, se solicitará corrección en el PR.


## Modo A (recomendado): **Fork hacia PR al repo original**
**Meta:** .

1) **Haz fork** de `JEstebanMejiaV/curso-ingenieria-de-datos` en tu cuenta de GitHub.  
2) **Clona tu fork** y configura remoto de referencia:
```bash
git clone git@github.com:TU-USUARIO/curso-ingenieria-de-datos.git
cd curso-ingenieria-de-datos
git remote add upstream git@github.com:JEstebanMejiaV/curso-ingenieria-de-datos.git
git remote -v
```
3) **Crea rama por equipo**:
```bash
git checkout -b equipo-01-<INI>
```
4) **Crea tu subcarpeta dentro de la ruta fija** (nota el espacio en “Taller Git”):
```bash
# macOS/Linux (bash/zsh)
mkdir -p "modulo-01_fundamentos/Taller Git/equipo-01-<INI>"
echo "# Taller Git (equipo-01-<INI>)" > "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/README_<INI>.md"

# Windows PowerShell
New-Item -ItemType Directory -Path "modulo-01_fundamentos/Taller Git/equipo-01-<INI>" -Force | Out-Null
'# Taller Git (equipo-01-<INI>)' | Out-File "modulo-01_fundamentos/Taller Git/equipo-01-<INI>/README_<INI>.md" -Encoding utf8
```
5) **Commit y push** de la rama a tu fork:
```bash
git add .
git commit -m "equipo-01-<INI>: crear carpeta y README inicial"
git push -u origin equipo-01-<INI>
```
6) **Abre Pull Request (PR)** desde tu fork :
- **Base repository:** `JEstebanMejiaV/curso-ingenieria-de-datos`
- **Base branch:** `main`
- **Compare:** `TU-USUARIO:equipo-01-<INI>`

7) **Mantén tu fork sincronizado** (si el original avanza):
```bash
git fetch upstream
git checkout main
git pull --rebase upstream main
git push origin main
```

## Modo B (si tienes permiso de escritura): **Clonar directo + PR interno**

**Meta:** crear repo, añadir, hacer commits y ver historial.

1) Clona el repo canónico:
```bash
git clone git@github.com:JEstebanMejiaV/curso-ingenieria-de-datos.git
cd curso-ingenieria-de-datos
```
2) Crea tu rama por equipo:
```bash
git checkout -b equipo-02-<INI>
```
3) Trabaja **solo** dentro de la ruta fija:
```bash
mkdir -p "modulo-01_fundamentos/Taller Git/equipo-02-<INI>"
echo "Checklist <INI>" > "modulo-01_fundamentos/Taller Git/equipo-02-<INI>/CHECKLIST_<INI>.md"
git add .
git commit -m "equipo-02-<INI>: agregar carpeta y checklist"
git push -u origin equipo-02-<INI>
```
4) Abre PR `equipo-02-<INI> -main` (ideal: **Squash merge**).


## Ejercicios prácticos 

### PR mínimo (calentamiento)
- Crea `README_<INI>.md` con integrantes y objetivos.
- Añade `plan_<INI>.md` con 3 tareas del taller.
- Abre un **PR**. Pide revisión a otro equipo.
- **Entrega:** enlace al PR.

### Ramas y revisión con *Suggested changes*
- En tu rama `equipo-XX-<INI>`, agrega `notas_<INI>.md` y envía PR.
- El revisor propone *suggested changes*; aplícalos y haz `push`.
- **Entrega:** PR con al menos 1 comentario resuelto.

### Conflicto controlado
- Dos equipos editan la **misma línea** de `README_<INI>.md` (cada uno en su PR).
- Provocan conflicto y lo resuelven con **merge commit** o **rebase**.
- **Entrega:** PR fusionado + captura del conflicto resuelto.

### Protección de `main` (para el owner)
- En **Settings -> Branches -> Branch protection rules** para `main`: exigir **1 review** y (opcional) **status checks**.
- Intentar `git push origin main` debe **fallar** (sin PR).
- Solución: abrir PR desde la rama del equipo.
- **Entrega:** captura del error y PR aprobado.

### Sincronización tras **Squash merge**
- Fusiona un PR con **Squash**.
- En local:
```bash
git fetch origin
git checkout main
git pull --rebase origin main
git branch -D equipo-XX-<INI>
```

### Issue: PR que lo cierra
- Crea un **Issue** (tarea concreta en tu subcarpeta).
- Crea un PR que diga `Closes #<n>` y ejecuta el cambio.


## Convenciones del taller
- **Ruta fija**: `modulo-01_fundamentos/Taller Git/`
- **Subcarpeta por equipo**: `equipo-XX-<INI>`
- **Rama por equipo**: `equipo-XX-<INI>`
- **Nada fuera** de tu subcarpeta.




### Notas rápidas sobre autenticación
- **SSH**: si te pide usuario/contraseña en `push`, probablemente estás usando la URL HTTPS; cambia a SSH:  
  `git remote set-url origin git@github.com:TU-USUARIO/curso-ingenieria-de-datos.git`
- **HTTPS + PAT**: usa el **token** como contraseña cuando Git lo pida.



# Convenciones del taller
- **Ruta fija**: `modulo-01_fundamentos/Taller Git/`
- **Subcarpeta por equipo**: `equipo-XX-<INI>`
- **Rama por equipo**: `equipo-XX-<INI>`
- **Nada fuera** de tu subcarpeta.



## Comandos útiles

```bash

# Trabajo con repo local

git init
git status
git add <archivo> | git add .
git commit -m "mensaje"
git log --oneline --graph --decorate
git diff [<rango>]
git switch -c <rama> | git checkout -b <rama>
git switch <rama>
git merge <rama>

# Resolución de conflictos

git restore <archivo>
git reset --soft|--mixed|--hard <ref>
git revert <ref>
git reflog
git stash push -m "WIP"; git stash list; git stash apply/pop
git tag -a vX.Y-<INI> -m "nota"; git show vX.Y-<INI>


# Crear rama y empujar

git checkout -b equipo-01-<INI>
git push -u origin equipo-01-<INI>

# Actualizar main y rebasear

git fetch origin
git checkout main
git pull --rebase origin main

# Sincronizar fork con upstream
git fetch upstream
git checkout main
git pull --rebase upstream main
git push origin main

```
