# Comandos Rápidos - Taller 2

## 🚀 Setup Inicial

```bash
# Clonar repositorio
git clone https://github.com/TU-USUARIO/ecommerce-cicd-workshop.git
cd ecommerce-cicd-workshop

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src

# Tests con reporte HTML
pytest --cov=src --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows

# Tests específicos
pytest tests/test_transformations.py

# Tests con verbose
pytest -v

# Tests con markers
pytest -m unit
pytest -m integration
```

## 🎨 Code Quality

```bash
# Formatear código con Black
black src/ tests/

# Verificar formato (sin modificar)
black --check src/ tests/

# Ordenar imports con isort
isort src/ tests/

# Verificar imports
isort --check-only src/ tests/

# Lint con Flake8
flake8 src/ tests/

# Lint con configuración personalizada
flake8 src/ tests/ --max-line-length=100 --max-complexity=10

# Análisis de complejidad con Radon
radon cc src/ -a
radon mi src/
```

## 🔒 Security

```bash
# Análisis de seguridad con Bandit
bandit -r src/

# Reporte en JSON
bandit -r src/ -f json -o bandit-report.json

# Verificar vulnerabilidades en dependencias
safety check

# Safety con reporte JSON
safety check --json
```

## 📦 Git & GitHub

```bash
# Crear nueva rama
git checkout -b feature/nueva-funcionalidad

# Ver status
git status

# Agregar cambios
git add .
git add src/transformations.py

# Commit
git commit -m "feat: agregar nueva funcionalidad"

# Push
git push origin feature/nueva-funcionalidad

# Pull latest changes
git pull origin main

# Merge main en tu rama
git merge main

# Rebase interactivo
git rebase -i HEAD~3

# Ver log
git log --oneline --graph

# Ver diferencias
git diff
git diff main..feature/nueva-funcionalidad
```

## 🔄 GitHub CLI

```bash
# Instalar GitHub CLI
# Mac:
brew install gh
# Windows:
winget install GitHub.cli

# Login
gh auth login

# Ver workflows
gh workflow list

# Ejecutar workflow
gh workflow run ci.yml

# Ver runs
gh run list

# Ver detalles de un run
gh run view <run-id>

# Ver logs
gh run view <run-id> --log

# Re-ejecutar workflow
gh run rerun <run-id>

# Crear PR
gh pr create --title "feat: nueva funcionalidad" --body "Descripción"

# Ver PRs
gh pr list

# Ver detalles de PR
gh pr view <pr-number>

# Aprobar PR
gh pr review <pr-number> --approve

# Merge PR
gh pr merge <pr-number> --squash

# Crear release
gh release create v1.0.0 --title "Release 1.0.0" --notes "Notas del release"

# Ver releases
gh release list
```

## 🏷️ Versionado

```bash
# Ver tags
git tag

# Crear tag
git tag v1.0.0

# Crear tag anotado
git tag -a v1.0.0 -m "Release 1.0.0"

# Push tag
git push origin v1.0.0

# Push todos los tags
git push --tags

# Eliminar tag local
git tag -d v1.0.0

# Eliminar tag remoto
git push origin --delete v1.0.0

# Ver versión actual
cat src/__init__.py | grep __version__

# Bump version (con script)
python scripts/bump_version.py patch
python scripts/bump_version.py minor
python scripts/bump_version.py major
```

## 🐳 Docker (Opcional)

```bash
# Build imagen
docker build -t ecommerce-app:latest .

# Ejecutar container
docker run -p 8000:8000 ecommerce-app:latest

# Ver containers
docker ps

# Ver logs
docker logs <container-id>

# Detener container
docker stop <container-id>

# Limpiar
docker system prune -a
```

## 📊 Coverage

```bash
# Generar reporte de cobertura
coverage run -m pytest

# Ver reporte en terminal
coverage report

# Ver reporte detallado
coverage report -m

# Generar HTML
coverage html

# Verificar umbral mínimo
coverage report --fail-under=70
```

## 🔍 Debugging

```bash
# Ejecutar tests con pdb
pytest --pdb

# Ejecutar tests hasta el primer fallo
pytest -x

# Ejecutar último test fallido
pytest --lf

# Ejecutar tests con output completo
pytest -s

# Ejecutar tests con traceback completo
pytest --tb=long
```

## 🧹 Cleanup

```bash
# Limpiar archivos de Python
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

# Limpiar coverage
rm -rf htmlcov/
rm .coverage

# Limpiar pytest cache
rm -rf .pytest_cache/

# Limpiar todo
make clean  # si tienes Makefile
```

## 📝 Conventional Commits

```bash
# Feature
git commit -m "feat: agregar cálculo de envío"

# Bug fix
git commit -m "fix: corregir cálculo de descuento"

# Documentation
git commit -m "docs: actualizar README"

# Style
git commit -m "style: formatear código con black"

# Refactor
git commit -m "refactor: simplificar función de validación"

# Test
git commit -m "test: agregar tests para cupones"

# Chore
git commit -m "chore: actualizar dependencias"

# Breaking change
git commit -m "feat!: cambiar API de cálculo de total"
```

## 🎯 Workflows Comunes

### Crear Feature

```bash
git checkout main
git pull
git checkout -b feature/mi-feature
# ... hacer cambios ...
pytest
black src/ tests/
git add .
git commit -m "feat: mi nueva feature"
git push origin feature/mi-feature
gh pr create
```

### Hotfix en Producción

```bash
git checkout main
git pull
git checkout -b hotfix/bug-critico
# ... hacer fix ...
pytest
git add .
git commit -m "fix: corregir bug crítico"
git push origin hotfix/bug-critico
gh pr create --label "hotfix"
```

### Release

```bash
git checkout main
git pull
python scripts/bump_version.py minor
git add src/__init__.py
git commit -m "chore: bump version to 1.1.0"
git tag v1.1.0
git push origin main --tags
gh release create v1.1.0
```

## 🆘 Troubleshooting

```bash
# Ver configuración de git
git config --list

# Ver remote
git remote -v

# Verificar conexión a GitHub
ssh -T git@github.com

# Limpiar cache de git
git rm -r --cached .
git add .

# Reset a commit anterior
git reset --hard HEAD~1

# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Ver qué archivos cambiarían con merge
git diff --name-only main..feature/mi-feature

# Ver conflictos
git diff --name-only --diff-filter=U
```

## 💡 Tips

```bash
# Alias útiles (agregar a ~/.gitconfig)
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'

# Ver tamaño del repositorio
git count-objects -vH

# Buscar en commits
git log --all --grep='palabra'

# Ver quién modificó cada línea
git blame src/transformations.py

# Ver historial de un archivo
git log --follow src/transformations.py
```
