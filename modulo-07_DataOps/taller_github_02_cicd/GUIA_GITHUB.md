# Guía de GitHub para CI/CD Avanzado

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Secrets y Variables](#secrets-y-variables)
3. [Environments](#environments)
4. [Branch Protection](#branch-protection)
5. [Pull Requests](#pull-requests)

## Configuración Inicial

### 1. Crear Repositorio en GitHub

1. Ve a GitHub.com y haz clic en "New repository"
2. Nombre: `ecommerce-cicd-workshop`
3. Descripción: "Taller 2: CI/CD Avanzado y Deployment"
4. Visibilidad: Público o Privado
5. Inicializar con README: No (ya tenemos uno)
6. Clic en "Create repository"

### 2. Conectar Repositorio Local

```bash
# Inicializar git (si no está inicializado)
git init

# Agregar remote
git remote add origin https://github.com/TU-USUARIO/ecommerce-cicd-workshop.git

# Crear rama main
git branch -M main

# Primer commit
git add .
git commit -m "feat: initial commit with CI/CD setup"

# Push
git push -u origin main
```

## Secrets y Variables

### Configurar Secrets

Los secrets son valores sensibles que no deben estar en el código.

#### Paso 1: Ir a Settings

1. En tu repositorio, clic en "Settings"
2. En el menú lateral, clic en "Secrets and variables" → "Actions"

#### Paso 2: Agregar Secrets

Clic en "New repository secret" y agrega:

**Para Development:**
- Name: `DEV_API_KEY`
- Value: `dev-api-key-12345`

- Name: `DEV_DATABASE_URL`
- Value: `postgresql://user:pass@localhost:5432/ecommerce_dev`

**Para Staging:**
- Name: `STAGING_API_KEY`
- Value: `staging-api-key-67890`

- Name: `STAGING_DATABASE_URL`
- Value: `postgresql://user:pass@staging-db.example.com:5432/ecommerce_staging`

**Para Production:**
- Name: `PROD_API_KEY`
- Value: `prod-api-key-XXXXX`

- Name: `PROD_DATABASE_URL`
- Value: `postgresql://user:pass@prod-db.example.com:5432/ecommerce_prod`

### Configurar Variables

Las variables son valores no sensibles que pueden variar por ambiente.

1. En "Secrets and variables" → "Actions"
2. Clic en la pestaña "Variables"
3. Clic en "New repository variable"

Agregar:
- Name: `PYTHON_VERSION`
- Value: `3.10`

## Environments

Los environments permiten configurar protecciones y secrets específicos por ambiente.

### Crear Environment de Development

1. Settings → Environments
2. Clic en "New environment"
3. Name: `development`
4. Clic en "Configure environment"

Configuración:
- Environment protection rules: (ninguna para dev)
- Environment secrets: Agregar DEV_API_KEY y DEV_DATABASE_URL
- Deployment branches: All branches

### Crear Environment de Staging

1. New environment → Name: `staging`
2. Configuración:
   - Required reviewers: (opcional) Agregar 1 revisor
   - Wait timer: 0 minutes
   - Deployment branches: Selected branches → `main`, `develop`
   - Environment secrets: STAGING_API_KEY, STAGING_DATABASE_URL

### Crear Environment de Production

1. New environment → Name: `production`
2. Configuración:
   - Required reviewers: Agregar 2 revisores
   - Wait timer: 5 minutes (tiempo de espera antes de deployment)
   - Deployment branches: Selected branches → `main` only
   - Environment secrets: PROD_API_KEY, PROD_DATABASE_URL

## Branch Protection

Proteger la rama `main` para asegurar calidad.

### Configurar Branch Protection

1. Settings → Branches
2. Clic en "Add branch protection rule"
3. Branch name pattern: `main`

Configuración recomendada:

✅ **Require a pull request before merging**
- Require approvals: 1
- Dismiss stale pull request approvals when new commits are pushed
- Require review from Code Owners

✅ **Require status checks to pass before merging**
- Require branches to be up to date before merging
- Status checks que deben pasar:
  - `lint`
  - `test`
  - `security`

✅ **Require conversation resolution before merging**

✅ **Require signed commits** (opcional pero recomendado)

✅ **Include administrators**

❌ **Allow force pushes** (deshabilitado)

❌ **Allow deletions** (deshabilitado)

## Pull Requests

### Crear un Pull Request

#### Paso 1: Crear una rama de feature

```bash
# Crear y cambiar a nueva rama
git checkout -b feature/nueva-funcionalidad

# Hacer cambios
# ... editar archivos ...

# Commit
git add .
git commit -m "feat: agregar nueva funcionalidad"

# Push
git push origin feature/nueva-funcionalidad
```

#### Paso 2: Abrir PR en GitHub

1. Ve a tu repositorio en GitHub
2. Verás un banner "Compare & pull request" → Clic
3. Base: `main` ← Compare: `feature/nueva-funcionalidad`
4. Título: Descriptivo (ej: "feat: Agregar cálculo de envío")
5. Descripción: Explicar los cambios
6. Reviewers: Asignar revisores
7. Labels: Agregar labels apropiados (feature, bug, etc.)
8. Clic en "Create pull request"

### Template de PR

Crea `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Descripción
<!-- Describe los cambios realizados -->

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## Checklist
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] Code review solicitado
- [ ] CI/CD pasa exitosamente

## Screenshots (si aplica)
<!-- Agregar capturas de pantalla -->

## Notas adicionales
<!-- Información adicional para los revisores -->
```

### Revisar un PR

Como revisor:

1. Ve al PR
2. Pestaña "Files changed"
3. Revisar cambios línea por línea
4. Agregar comentarios haciendo clic en el número de línea
5. Cuando termines:
   - "Approve" si está bien
   - "Request changes" si necesita modificaciones
   - "Comment" para comentarios sin aprobar/rechazar

### Merge del PR

Una vez aprobado y con CI pasando:

1. Clic en "Merge pull request"
2. Opciones de merge:
   - **Create a merge commit**: Mantiene historial completo
   - **Squash and merge**: Combina commits en uno (recomendado)
   - **Rebase and merge**: Reaplica commits sobre main
3. Confirmar merge
4. Eliminar rama (opcional pero recomendado)

## Comandos Útiles

```bash
# Ver status de workflows
gh run list

# Ver detalles de un workflow
gh run view <run-id>

# Re-ejecutar un workflow fallido
gh run rerun <run-id>

# Ver logs de un workflow
gh run view <run-id> --log

# Crear un release
gh release create v1.0.0 --title "Release 1.0.0" --notes "Primera versión"
```

## Troubleshooting

### Workflow no se ejecuta

- Verificar que el archivo YAML esté en `.github/workflows/`
- Verificar sintaxis YAML (usar yamllint)
- Verificar que el trigger (on:) sea correcto

### Secrets no funcionan

- Verificar que el nombre del secret sea exacto (case-sensitive)
- Verificar que el secret esté en el scope correcto (repo o environment)
- Los secrets no se muestran en logs (aparecen como ***)

### Tests fallan en CI pero pasan localmente

- Verificar versión de Python
- Verificar dependencias (requirements.txt actualizado)
- Verificar variables de entorno
- Ejecutar tests con mismo comando que CI: `pytest --cov=src`
