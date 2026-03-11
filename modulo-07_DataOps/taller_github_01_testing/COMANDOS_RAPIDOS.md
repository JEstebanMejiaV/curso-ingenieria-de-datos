# Comandos Rápidos - Referencia

Esta es una guía de referencia rápida con todos los comandos que necesitas.

## 🐍 Python y Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (Mac/Linux)
source venv/bin/activate

# Desactivar entorno virtual
deactivate

# Instalar dependencias
pip install -r requirements.txt

# Ver paquetes instalados
pip list

# Verificar versión de Python
python --version
```

## 🧪 Pytest

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con más detalle (-v = verbose)
pytest -v

# Ejecutar tests de un archivo específico
pytest tests/test_basico.py

# Ejecutar un test específico
pytest tests/test_basico.py::test_calcular_total_venta_caso_basico

# Ejecutar tests que contengan una palabra en el nombre
pytest -k descuento

# Ejecutar y mostrar prints
pytest -s

# Ejecutar y parar en el primer fallo
pytest -x

# Ejecutar y mostrar resumen de fallos
pytest --tb=short

# Ver qué tests se ejecutarían sin ejecutarlos
pytest --collect-only
```

## 📁 Git - Básico

```bash
# Ver estado de archivos
git status

# Ver diferencias
git diff

# Agregar archivo específico
git add archivo.py

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Mensaje descriptivo"

# Ver historial de commits
git log

# Ver historial resumido
git log --oneline

# Ver ramas
git branch

# Crear nueva rama
git branch nombre-rama

# Cambiar de rama
git checkout nombre-rama

# Crear y cambiar a nueva rama
git checkout -b nombre-rama
```

## 🚀 Git - GitHub

```bash
# Clonar repositorio
git clone https://github.com/usuario/repo.git

# Ver repositorios remotos
git remote -v

# Agregar repositorio remoto
git remote add origin https://github.com/usuario/repo.git

# Subir cambios a GitHub
git push

# Subir por primera vez
git push -u origin main

# Descargar cambios de GitHub
git pull

# Ver diferencias con remoto
git fetch
git diff origin/main
```

## 🔧 Git - Configuración

```bash
# Configurar nombre
git config --global user.name "Tu Nombre"

# Configurar email
git config --global user.email "tu@email.com"

# Ver configuración
git config --list

# Configurar editor por defecto
git config --global core.editor "code --wait"
```

## 📝 Flujo de Trabajo Típico

```bash
# 1. Hacer cambios en el código
# (editar archivos en tu editor)

# 2. Ejecutar tests localmente
pytest -v

# 3. Ver qué cambió
git status
git diff

# 4. Agregar cambios
git add .

# 5. Hacer commit
git commit -m "Descripción del cambio"

# 6. Subir a GitHub
git push

# 7. Verificar en GitHub Actions
# (ir a la pestaña Actions en GitHub)
```

## 🐛 Debugging

```bash
# Ejecutar Python en modo interactivo
python

# Ejecutar un archivo Python
python src/transformations.py

# Ejecutar con debugger
python -m pdb src/transformations.py

# Ver ayuda de pytest
pytest --help

# Ver versión de pytest
pytest --version

# Limpiar cache de pytest
pytest --cache-clear
```

## 📊 Información del Sistema

```bash
# Ver versión de Python
python --version

# Ver versión de pip
pip --version

# Ver versión de Git
git --version

# Ver directorio actual
pwd  # Mac/Linux
cd   # Windows

# Listar archivos
ls      # Mac/Linux
dir     # Windows

# Cambiar directorio
cd nombre-directorio

# Volver al directorio anterior
cd ..
```

## 🔍 Buscar y Encontrar

```bash
# Buscar en archivos (Mac/Linux)
grep -r "texto" .

# Buscar en archivos (Windows PowerShell)
Select-String -Path *.py -Pattern "texto"

# Encontrar archivos por nombre (Mac/Linux)
find . -name "*.py"

# Encontrar archivos por nombre (Windows)
Get-ChildItem -Recurse -Filter "*.py"
```

## 🧹 Limpieza

```bash
# Eliminar archivos de cache de Python
find . -type d -name "__pycache__" -exec rm -rf {} +  # Mac/Linux
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force  # Windows

# Eliminar cache de pytest
rm -rf .pytest_cache  # Mac/Linux
Remove-Item -Recurse -Force .pytest_cache  # Windows

# Eliminar entorno virtual
rm -rf venv  # Mac/Linux
Remove-Item -Recurse -Force venv  # Windows
```

## 📦 Gestión de Dependencias

```bash
# Instalar paquete específico
pip install pytest

# Instalar versión específica
pip install pytest==7.4.0

# Actualizar paquete
pip install --upgrade pytest

# Desinstalar paquete
pip uninstall pytest

# Generar requirements.txt
pip freeze > requirements.txt

# Instalar desde requirements.txt
pip install -r requirements.txt
```

## 🎯 Atajos Útiles

```bash
# Ctrl+C: Cancelar comando en ejecución
# Ctrl+D: Salir de Python interactivo
# Ctrl+L: Limpiar terminal (Mac/Linux)
# cls: Limpiar terminal (Windows)
# Tab: Autocompletar
# ↑/↓: Navegar historial de comandos
```

## 🚨 Comandos de Emergencia

```bash
# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Deshacer cambios en un archivo
git checkout -- archivo.py

# Deshacer todos los cambios no commiteados
git reset --hard

# Ver qué haría git clean sin ejecutarlo
git clean -n

# Eliminar archivos no trackeados
git clean -f

# Forzar push (¡CUIDADO!)
git push --force
```

## 📚 Ayuda

```bash
# Ayuda de Git
git help
git help commit

# Ayuda de pytest
pytest --help

# Ayuda de pip
pip help
pip help install

# Manual de comando (Mac/Linux)
man git
man python
```

## 🎓 Tips Pro

```bash
# Alias útiles (agregar a ~/.bashrc o ~/.zshrc)
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline'
alias pt='pytest -v'

# Usar después de agregar a .bashrc/.zshrc
source ~/.bashrc  # o ~/.zshrc
```

## 🔗 URLs Útiles

```bash
# Abrir repositorio en GitHub desde terminal
# (si tienes GitHub CLI instalado)
gh repo view --web

# Abrir Actions en GitHub
gh run list
gh run view
```

---

## 📋 Checklist de Comandos Esenciales

Los comandos que DEBES conocer:

- [ ] `python --version` - Verificar Python
- [ ] `pip install -r requirements.txt` - Instalar dependencias
- [ ] `pytest -v` - Ejecutar tests
- [ ] `git status` - Ver estado
- [ ] `git add .` - Agregar cambios
- [ ] `git commit -m "mensaje"` - Hacer commit
- [ ] `git push` - Subir a GitHub
- [ ] `git pull` - Descargar de GitHub

---

**💡 Tip**: Imprime esta página y tenla cerca mientras trabajas en el taller.
