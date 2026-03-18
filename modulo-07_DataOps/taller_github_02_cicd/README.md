# Taller 2: CI/CD Avanzado y Deployment

## 🎯 Objetivos del Taller

Al finalizar este taller, serás capaz de:

1. Implementar pipelines de CI/CD completos con GitHub Actions
2. Configurar deployment automático a diferentes ambientes
3. Implementar estrategias de versionado semántico
4. Crear workflows de release automatizados
5. Configurar notificaciones y monitoreo de pipelines
6. Implementar prácticas de seguridad en CI/CD

## ⏱️ Duración Estimada

3-4 horas

## 📋 Prerrequisitos

- Haber completado el Taller 1 (Tests Unitarios y GitHub Actions Básico)
- Cuenta de GitHub activa
- Git instalado localmente
- Python 3.8+ instalado
- Conocimientos básicos de Docker (opcional pero recomendado)

## 🏗️ Caso de Estudio

Continuaremos con el sistema de e-commerce del Taller 1, pero ahora implementaremos:
- Pipeline completo de CI/CD
- Deployment a múltiples ambientes (dev, staging, prod)
- Versionado automático
- Releases automatizados
- Monitoreo de calidad de código

## 📚 Contenido del Taller

### Sección 1: Pipeline de CI/CD Completo (60 min)
- Configuración de ambientes
- Jobs paralelos y dependencias
- Caching de dependencias
- Artifacts y reportes

### Sección 2: Deployment Automatizado (60 min)
- Estrategias de deployment
- Secrets y variables de entorno
- Deployment a diferentes ambientes
- Rollback automático

### Sección 3: Versionado y Releases (45 min)
- Semantic Versioning
- Changelog automático
- GitHub Releases
- Tags automáticos

### Sección 4: Calidad y Seguridad (45 min)
- Code coverage
- Análisis de seguridad
- Dependabot
- Code quality gates

## 🚀 Comenzar

Sigue la guía paso a paso en las secciones numeradas del README.


---

## 📖 Sección 1: Pipeline de CI/CD Completo

### Paso 1.1: Estructura del Proyecto

Vamos a crear una estructura más completa que soporte múltiples ambientes:

```
taller_github_02_cicd/
├── src/
│   ├── __init__.py
│   ├── transformations.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_transformations.py
│   └── test_integration.py
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd-dev.yml
│       ├── cd-staging.yml
│       └── cd-prod.yml
├── config/
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```

### Paso 1.2: Configuración por Ambientes

Crea el archivo `src/config.py`:

```python
import os
import yaml
from pathlib import Path

class Config:
    def __init__(self, env='dev'):
        self.env = env
        self._load_config()
    
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'config' / f'{self.env}.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            for key, value in config.items():
                setattr(self, key, value)
```

### Paso 1.3: Workflow de CI Completo

Crea `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
      
      - name: Install dependencies
        run: |
          pip install flake8 black isort
      
      - name: Run Black
        run: black --check src/ tests/
      
      - name: Run isort
        run: isort --check-only src/ tests/
      
      - name: Run Flake8
        run: flake8 src/ tests/ --max-line-length=100

  test:
    name: Run Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=html
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
      
      - name: Upload coverage artifacts
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report-${{ matrix.python-version }}
          path: htmlcov/

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
      
      - name: Upload security report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: bandit-report.json
```


---

## 📖 Sección 2: Deployment Automatizado

### Paso 2.1: Workflow de Deployment a Dev

Crea `.github/workflows/cd-dev.yml`:

```yaml
name: Deploy to Dev

on:
  push:
    branches: [ develop ]
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy to Development
    runs-on: ubuntu-latest
    environment:
      name: development
      url: https://dev.miapp.com
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest
      
      - name: Deploy to Dev
        env:
          DEV_API_KEY: ${{ secrets.DEV_API_KEY }}
          DEV_DATABASE_URL: ${{ secrets.DEV_DATABASE_URL }}
        run: |
          echo "Deploying to development environment..."
          # Aquí irían los comandos reales de deployment
          # Por ejemplo: scp, rsync, aws s3 sync, etc.
      
      - name: Notify deployment
        if: success()
        run: |
          echo "✅ Deployment to DEV successful!"
```

### Paso 2.2: Workflow de Deployment a Staging

Crea `.github/workflows/cd-staging.yml`:

```yaml
name: Deploy to Staging

on:
  push:
    tags:
      - 'v*-rc*'
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.miapp.com
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run full test suite
        run: |
          pytest --cov=src --cov-report=term
      
      - name: Deploy to Staging
        env:
          STAGING_API_KEY: ${{ secrets.STAGING_API_KEY }}
          STAGING_DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: |
          echo "Deploying to staging environment..."
          # Comandos de deployment a staging
      
      - name: Run smoke tests
        run: |
          echo "Running smoke tests..."
          # Pruebas básicas post-deployment
      
      - name: Notify team
        if: success()
        run: |
          echo "✅ Deployment to STAGING successful!"
```

### Paso 2.3: Workflow de Deployment a Producción

Crea `.github/workflows/cd-prod.yml`:

```yaml
name: Deploy to Production

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://miapp.com
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run full test suite
        run: |
          pytest --cov=src --cov-report=term --cov-fail-under=80
      
      - name: Create backup
        run: |
          echo "Creating backup before deployment..."
          # Comandos para crear backup
      
      - name: Deploy to Production
        env:
          PROD_API_KEY: ${{ secrets.PROD_API_KEY }}
          PROD_DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
        run: |
          echo "Deploying to production environment..."
          # Comandos de deployment a producción
      
      - name: Run smoke tests
        run: |
          echo "Running smoke tests..."
          # Pruebas críticas post-deployment
      
      - name: Rollback on failure
        if: failure()
        run: |
          echo "❌ Deployment failed! Rolling back..."
          # Comandos de rollback
      
      - name: Notify team
        if: always()
        run: |
          if [ "${{ job.status }}" == "success" ]; then
            echo "✅ Deployment to PRODUCTION successful!"
          else
            echo "❌ Deployment to PRODUCTION failed!"
          fi
```


---

## 📖 Sección 3: Versionado y Releases

### Paso 3.1: Workflow de Versionado Automático

Crea `.github/workflows/release.yml`:

```yaml
name: Create Release

on:
  push:
    branches: [ main ]
    paths-ignore:
      - '**.md'
      - 'docs/**'

jobs:
  release:
    name: Create Release
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Bump version and push tag
        id: tag_version
        uses: mathieudutour/github-tag-action@v6.1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          default_bump: patch
          release_branches: main
      
      - name: Create changelog
        id: changelog
        uses: mikepenz/release-changelog-builder-action@v4
        with:
          configuration: ".github/changelog-config.json"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Create GitHub Release
        uses: ncipollo/release-action@v1
        with:
          tag: ${{ steps.tag_version.outputs.new_tag }}
          name: Release ${{ steps.tag_version.outputs.new_tag }}
          body: ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: false
```

### Paso 3.2: Configuración del Changelog

Crea `.github/changelog-config.json`:

```json
{
  "categories": [
    {
      "title": "## 🚀 Features",
      "labels": ["feature", "enhancement"]
    },
    {
      "title": "## 🐛 Bug Fixes",
      "labels": ["bug", "fix"]
    },
    {
      "title": "## 📚 Documentation",
      "labels": ["documentation"]
    },
    {
      "title": "## 🔧 Maintenance",
      "labels": ["maintenance", "chore"]
    }
  ],
  "template": "#{{CHANGELOG}}\n\n**Full Changelog**: #{{RELEASE_DIFF}}",
  "pr_template": "- #{{TITLE}} by @#{{AUTHOR}} in ##{{NUMBER}}",
  "empty_template": "- No changes",
  "label_extractor": [
    {
      "pattern": "^(feat|feature)",
      "target": "feature"
    },
    {
      "pattern": "^(fix|bugfix)",
      "target": "bug"
    },
    {
      "pattern": "^docs",
      "target": "documentation"
    }
  ]
}
```

### Paso 3.3: Script de Versionado Manual

Crea `scripts/bump_version.py`:

```python
#!/usr/bin/env python3
"""
Script para incrementar la versión del proyecto
Uso: python scripts/bump_version.py [major|minor|patch]
"""

import sys
import re
from pathlib import Path

def get_current_version():
    """Lee la versión actual del archivo __init__.py"""
    init_file = Path('src/__init__.py')
    content = init_file.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    return '0.0.0'

def bump_version(current, bump_type='patch'):
    """Incrementa la versión según el tipo"""
    major, minor, patch = map(int, current.split('.'))
    
    if bump_type == 'major':
        return f'{major + 1}.0.0'
    elif bump_type == 'minor':
        return f'{major}.{minor + 1}.0'
    else:  # patch
        return f'{major}.{minor}.{patch + 1}'

def update_version_file(new_version):
    """Actualiza el archivo __init__.py con la nueva versión"""
    init_file = Path('src/__init__.py')
    content = init_file.read_text()
    new_content = re.sub(
        r'__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content
    )
    init_file.write_text(new_content)

if __name__ == '__main__':
    bump_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    
    if bump_type not in ['major', 'minor', 'patch']:
        print(f'Error: bump_type debe ser major, minor o patch')
        sys.exit(1)
    
    current = get_current_version()
    new_version = bump_version(current, bump_type)
    
    print(f'Versión actual: {current}')
    print(f'Nueva versión: {new_version}')
    
    update_version_file(new_version)
    print(f'✅ Versión actualizada en src/__init__.py')
```


---

## 📖 Sección 4: Calidad y Seguridad

### Paso 4.1: Workflow de Code Coverage

Crea `.github/workflows/coverage.yml`:

```yaml
name: Code Coverage

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  coverage:
    name: Code Coverage Report
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=html --cov-report=term
      
      - name: Coverage comment
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}
          MINIMUM_GREEN: 80
          MINIMUM_ORANGE: 60
      
      - name: Check coverage threshold
        run: |
          coverage report --fail-under=70
```

### Paso 4.2: Configuración de Dependabot

Crea `.github/dependabot.yml`:

```yaml
version: 2
updates:
  # Mantener dependencias de Python actualizadas
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "tu-usuario"
    labels:
      - "dependencies"
      - "python"
    commit-message:
      prefix: "chore"
      include: "scope"
  
  # Mantener GitHub Actions actualizadas
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
```

### Paso 4.3: Workflow de Análisis de Seguridad

Crea `.github/workflows/security.yml`:

```yaml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 1'  # Cada lunes a medianoche

jobs:
  security:
    name: Security Analysis
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install bandit safety
      
      - name: Run Bandit (SAST)
        run: |
          bandit -r src/ -f json -o bandit-report.json || true
          bandit -r src/ -f screen
      
      - name: Run Safety (dependency check)
        run: |
          pip install -r requirements.txt
          safety check --json > safety-report.json || true
          safety check
      
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
      
      - name: CodeQL Analysis
        uses: github/codeql-action/init@v2
        with:
          languages: python
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
```

### Paso 4.4: Quality Gates

Crea `.github/workflows/quality-gate.yml`:

```yaml
name: Quality Gate

on:
  pull_request:
    branches: [ main ]

jobs:
  quality:
    name: Quality Checks
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pip install radon complexity-report
      
      - name: Check code complexity
        run: |
          radon cc src/ -a -nb
          radon mi src/ -nb
      
      - name: Check test coverage
        run: |
          pytest --cov=src --cov-report=term --cov-fail-under=70
      
      - name: Check code style
        run: |
          black --check src/ tests/
          flake8 src/ tests/ --max-complexity=10
      
      - name: Check for TODO/FIXME
        run: |
          ! grep -r "TODO\|FIXME" src/ || echo "⚠️ Found TODO/FIXME comments"
      
      - name: Quality Gate Summary
        if: always()
        run: |
          echo "## Quality Gate Results" >> $GITHUB_STEP_SUMMARY
          echo "✅ All quality checks passed!" >> $GITHUB_STEP_SUMMARY
```
