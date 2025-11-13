
# Guía rápida de **Git** y buenas prácticas para colaborar en **GitHub**


---

## Configuración inicial
```bash
# Identidad
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@example.com"

# Preferencias útiles
git config --global init.defaultBranch main
git config --global core.editor "code --wait"     # o "nano"
# Estrategia de pull (elige 1)
# Rebase lineal (historial más limpio):
git config --global pull.rebase true
# Merge por defecto (historial con merges):
# git config --global pull.rebase false

# Colores y formato del log
git config --global color.ui auto
```

---

## Crear o clonar un repositorio
```bash
# Iniciar repo local
mkdir mi-proyecto && cd mi-proyecto
git init

# Conectar a remoto
git remote add origin https://github.com/usuario/mi-proyecto.git

# Clonar existente
git clone https://github.com/org/proyecto.git
cd proyecto
```

---

## Flujo básico (status → add → commit → push)
```bash
git status                      # ver cambios
git add <archivo>               # stage individual
git add -A                      # stage todo
git commit -m "feat: agrega módulo X"
git push -u origin main         # primer push de la rama

# Ver historial compacto con ramas
git log --oneline --graph --decorate --all
```

---

## Ramas (branch) y trabajo aislado
```bash
# Crear/saltar de rama
git branch                      # listado
git switch -c feature/etl-kafka # crear y cambiar
git switch main                 # volver a main

# Publicar/eliminar rama remota
git push -u origin feature/etl-kafka
git branch -d feature/etl-kafka       # local
git push origin --delete feature/etl-kafka  # remota
```
**Convención sugerida:** `feature/...`, `fix/...`, `chore/...`, `hotfix/...`.

---

## Sincronización con remoto
```bash
# Traer referencias sin mezclar
git fetch --prune

# Actualizar tu rama con main de remoto (rebase recomendado)
git switch feature/etl-kafka
git fetch origin
git rebase origin/main
# si prefieres merge:
# git merge origin/main

# Actualizar local desde remoto en la misma rama
git pull --rebase     # o: git pull
```

---

## Merge y resolución de conflictos
```bash
# Iniciar merge a la rama actual
git switch main
git merge feature/etl-kafka

# Si hay conflictos: edita los marcadores <<<<<<<, =======, >>>>>>>
# Luego marca como resuelto y cierra el merge
git add <archivos-resueltos>
git commit -m "merge: resuelve conflictos con feature/etl-kafka"

# Aceptar todo lo tuyo (ours) o lo remoto (theirs) en un archivo
git checkout --ours   path/al/archivo
git checkout --theirs path/al/archivo

# Abortar un merge en curso
git merge --abort
```

---

## Rebase (limpiar/linearizar historial)
```bash
# Rebase simple de tu rama sobre main
git switch feature/etl-kafka
git fetch origin
git rebase origin/main

# Interactivo (squash, reword, drop) sobre últimos N commits
git rebase -i HEAD~5

# Si hay conflictos durante rebase
git add <archivo>
git rebase --continue         # seguir
git rebase --skip             # saltar commit
git rebase --abort            # volver al inicio
```
**Tip:** No hagas `rebase` de commits que ya empujaste a ramas compartidas, salvo que el equipo lo permita.

---

## Stash (guardar cambios sin commitear)
```bash
git stash push -m "wip: parser"  # guarda cambios sin stage
git stash list                    # ver entradas
git stash show -p stash@{0}       # diff de un stash
git stash apply stash@{0}         # aplica (conserva en lista)
git stash pop                     # aplica y elimina de la lista
git stash drop stash@{0}          # borra una entrada
```

---

## Etiquetas (tags) y versiones
```bash
# Ligera
git tag v1.0.0
# Anotada (recomendada para releases)
git tag -a v1.0.0 -m "Release 1.0.0"
# Publicar etiquetas
git push origin --tags
# Borrar etiqueta
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

---

## Deshacer y limpiar
```bash
# Quitar del stage, conservar en trabajo
git restore --staged <archivo>

# Restaurar archivo desde HEAD (¡deshace cambios locales!)
git restore <archivo>

# Deshacer último commit pero dejar cambios en stage
git reset --soft HEAD~1
# Deshacer y devolver a working dir
git reset --mixed HEAD~1
# Deshacer y tirar cambios (peligroso)
git reset --hard HEAD~1

# Revertir un commit público (crea un commit inverso)
git revert <hash>

# Limpiar archivos no versionados (cuidado)
git clean -fd     # -x para incluir ignorados
```


---

## Colaborar en GitHub con Pull Requests
1. **Crear rama** desde `main`: `git switch -c feature/nombre`.
2. Hacer commits pequeños y descriptivos (ver Convencional Commits abajo).
3. **Sincronizar** con `origin/main` (rebase o merge) antes de abrir PR.
4. **Push** de tu rama: `git push -u origin feature/nombre`.
5. Abre un **Pull Request** y describe *qué/por qué* (screenshots si aplica).
6. Atiende **code review**, actualiza la rama si hay cambios en `main`.
7. Mantén el PR pequeño; ideal < 300–400 líneas cambiadas.

**Protecciones de rama** (en Settings → Branches):
- Requerir PRs para `main`.
- Mínimo 1–2 revisores.
- Checks obligatorios (CI, linter, tests).
- Prohibir pushes directos a `main`.

---

## Commits convencionales (recomendado)
Formato: `tipo(scope?): mensaje`
- `feat`: nueva funcionalidad.
- `fix`: corrección de bug.
- `docs`: solo documentación.
- `chore`: tareas varias (build, deps).
- `refactor`: cambio interno sin alterar comportamiento.
- `test`: pruebas.
- `perf`: mejora de rendimiento.
- `ci`: pipelines.

Ejemplos:
```bash
git commit -m "feat(api): endpoint de login"
git commit -m "fix(ui): corrige overflow en card"
git commit -m "docs: agrega sección de instalación"
```

---

## Releases y versionado
- Crea una **tag** y desde GitHub → **Releases** genera notas.
- Sigue **SemVer**: `MAJOR.MINOR.PATCH`.

---


## Troubleshooting común
```bash
# "MERGE_HEAD exists" → hay un merge pendiente
# Opciones:
git add <archivos> && git commit        # finalizar merge
git merge --abort                        # abortar merge

# Cambié mensaje del commit de merge por accidente
git commit --amend -m "merge: integra rama X"

# Origen incorrecto o URL
git remote -v
git remote set-url origin <nueva_url>
```

---

## Tabla rápida de comandos
| Tarea | Comando |
|---|---|
| Ver estado | `git status` |
| Preparar cambios | `git add <f>` / `git add -A` |
| Crear commit | `git commit -m "msg"` |
| Crear rama y cambiar | `git switch -c <rama>` |
| Traer cambios | `git pull --rebase` |
| Enviar cambios | `git push -u origin <rama>` |
| Ver ramas | `git branch` |
| Merge | `git merge <rama>` |
| Rebase | `git rebase <base>` |
| Stash | `git stash push -m "wip"` |
| Tags | `git tag -a v1.0.0 -m "..."` |
| Revertir | `git revert <hash>` |
| Reset duro | `git reset --hard <hash>` |

---

