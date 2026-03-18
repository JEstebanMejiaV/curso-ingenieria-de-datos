# Índice del Taller 2: CI/CD Avanzado y Deployment

## 📚 Documentación Principal

### 🎯 Comenzar Aquí
- **[README.md](README.md)** - Guía principal del taller con todas las secciones

### 📖 Guías Detalladas
- **[GUIA_GITHUB.md](GUIA_GITHUB.md)** - Configuración de GitHub (Secrets, Environments, Branch Protection)
- **[RESUMEN_TALLER.md](RESUMEN_TALLER.md)** - Resumen completo de conceptos y arquitectura
- **[EJERCICIOS.md](EJERCICIOS.md)** - 10 ejercicios prácticos + ejercicio integrador
- **[COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md)** - Referencia rápida de comandos

## 🗂️ Estructura del Proyecto

```
taller_github_02_cicd/
│
├── 📄 README.md                    # Guía principal del taller
├── 📄 GUIA_GITHUB.md              # Guía de configuración de GitHub
├── 📄 RESUMEN_TALLER.md           # Resumen y conceptos clave
├── 📄 EJERCICIOS.md               # Ejercicios prácticos
├── 📄 COMANDOS_RAPIDOS.md         # Referencia de comandos
├── 📄 INDICE.md                   # Este archivo
│
├── 📁 src/                        # Código fuente
│   ├── __init__.py
│   ├── transformations.py         # Funciones de transformación
│   └── config.py                  # Configuración por ambientes
│
├── 📁 tests/                      # Tests unitarios
│   ├── __init__.py
│   └── test_transformations.py    # Tests de transformaciones
│
├── 📁 config/                     # Configuraciones por ambiente
│   ├── dev.yaml                   # Configuración desarrollo
│   ├── staging.yaml               # Configuración staging
│   └── prod.yaml                  # Configuración producción
│
├── 📁 .github/                    # GitHub Actions workflows
│   ├── workflows/
│   │   ├── ci.yml                 # Pipeline de CI
│   │   ├── cd-dev.yml             # Deployment a dev
│   │   ├── cd-staging.yml         # Deployment a staging
│   │   ├── cd-prod.yml            # Deployment a prod
│   │   ├── release.yml            # Versionado automático
│   │   ├── coverage.yml           # Análisis de cobertura
│   │   ├── security.yml           # Análisis de seguridad
│   │   └── quality-gate.yml       # Quality gates
│   ├── dependabot.yml             # Configuración Dependabot
│   └── changelog-config.json      # Configuración changelog
│
├── 📁 scripts/                    # Scripts de utilidad
│   └── bump_version.py            # Script de versionado
│
├── 📄 requirements.txt            # Dependencias de producción
├── 📄 requirements-dev.txt        # Dependencias de desarrollo
├── 📄 pytest.ini                  # Configuración de pytest
└── 📄 .gitignore                  # Archivos ignorados por git
```

## 🎓 Ruta de Aprendizaje Recomendada

### Nivel 1: Fundamentos (1-2 horas)
1. Leer [README.md](README.md) - Sección 1: Pipeline de CI/CD Completo
2. Implementar workflow básico de CI
3. Ejecutar tests localmente
4. Ver [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md) para referencia

### Nivel 2: Deployment (1-2 horas)
1. Leer [README.md](README.md) - Sección 2: Deployment Automatizado
2. Configurar environments en GitHub (ver [GUIA_GITHUB.md](GUIA_GITHUB.md))
3. Implementar workflows de deployment
4. Configurar secrets por ambiente

### Nivel 3: Versionado (45 min)
1. Leer [README.md](README.md) - Sección 3: Versionado y Releases
2. Implementar versionado automático
3. Crear primer release
4. Entender semantic versioning

### Nivel 4: Calidad y Seguridad (45 min)
1. Leer [README.md](README.md) - Sección 4: Calidad y Seguridad
2. Configurar Dependabot
3. Implementar security scan
4. Configurar quality gates

### Nivel 5: Práctica (2-3 horas)
1. Completar [EJERCICIOS.md](EJERCICIOS.md) - Ejercicios 1-10
2. Realizar ejercicio integrador final
3. Revisar [RESUMEN_TALLER.md](RESUMEN_TALLER.md) para consolidar

## 📊 Workflows Implementados

### CI (Continuous Integration)
- **ci.yml**: Pipeline principal con lint, tests y security
- **coverage.yml**: Análisis de cobertura de código
- **quality-gate.yml**: Quality gates para PRs
- **security.yml**: Análisis de seguridad (Bandit, Safety, CodeQL)

### CD (Continuous Deployment)
- **cd-dev.yml**: Deployment automático a desarrollo
- **cd-staging.yml**: Deployment a staging con aprobación
- **cd-prod.yml**: Deployment a producción con múltiples aprobaciones

### Release Management
- **release.yml**: Versionado automático y creación de releases

### Maintenance
- **dependabot.yml**: Actualizaciones automáticas de dependencias

## 🎯 Objetivos de Aprendizaje por Sección

### Sección 1: Pipeline de CI/CD
- ✅ Configurar workflows de GitHub Actions
- ✅ Implementar jobs paralelos
- ✅ Usar caching para optimizar
- ✅ Generar artifacts y reportes

### Sección 2: Deployment
- ✅ Configurar múltiples ambientes
- ✅ Usar secrets de forma segura
- ✅ Implementar aprobaciones
- ✅ Configurar rollback automático

### Sección 3: Versionado
- ✅ Entender semantic versioning
- ✅ Automatizar bump de versión
- ✅ Generar changelog automático
- ✅ Crear GitHub Releases

### Sección 4: Calidad y Seguridad
- ✅ Configurar análisis de cobertura
- ✅ Implementar security scanning
- ✅ Configurar Dependabot
- ✅ Establecer quality gates

## 🔗 Enlaces Rápidos

### Documentación
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Herramientas
- [pytest](https://docs.pytest.org/)
- [Black](https://black.readthedocs.io/)
- [Flake8](https://flake8.pycqa.org/)
- [Bandit](https://bandit.readthedocs.io/)

### Recursos Adicionales
- [12 Factor App](https://12factor.net/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub CLI](https://cli.github.com/)

## 💡 Tips para el Taller

### Para Instructores
1. Comenzar con demo en vivo del pipeline completo
2. Explicar cada sección antes de que los estudiantes la implementen
3. Hacer pausas para Q&A después de cada sección
4. Revisar los ejercicios en grupo
5. Compartir mejores prácticas de la industria

### Para Estudiantes
1. Leer toda la documentación antes de empezar
2. Hacer commits frecuentes con mensajes descriptivos
3. Probar localmente antes de hacer push
4. No tener miedo de experimentar
5. Pedir ayuda cuando sea necesario

### Troubleshooting Común
- **Workflows no se ejecutan**: Verificar sintaxis YAML
- **Secrets no funcionan**: Verificar nombres exactos (case-sensitive)
- **Tests fallan en CI**: Verificar versión de Python y dependencias
- **Deployment falla**: Verificar permisos y secrets por ambiente

## 📞 Soporte

Si tienes preguntas o encuentras problemas:

1. Revisa [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md) para comandos útiles
2. Consulta [GUIA_GITHUB.md](GUIA_GITHUB.md) para configuración de GitHub
3. Revisa la sección de Troubleshooting en cada documento
4. Consulta con el instructor o compañeros

## ✅ Checklist de Completitud

Usa este checklist para verificar tu progreso:

### Configuración Inicial
- [ ] Repositorio creado en GitHub
- [ ] Código clonado localmente
- [ ] Entorno virtual configurado
- [ ] Dependencias instaladas

### Sección 1: CI/CD
- [ ] Workflow de CI implementado
- [ ] Tests ejecutándose correctamente
- [ ] Lint configurado
- [ ] Security scan funcionando

### Sección 2: Deployment
- [ ] 3 environments configurados
- [ ] Secrets configurados por ambiente
- [ ] Workflows de deployment creados
- [ ] Aprobaciones configuradas

### Sección 3: Versionado
- [ ] Workflow de release implementado
- [ ] Versionado automático funcionando
- [ ] Changelog generándose
- [ ] Releases creándose en GitHub

### Sección 4: Calidad
- [ ] Coverage configurado
- [ ] Dependabot activo
- [ ] Security scan automático
- [ ] Quality gates implementados

### Ejercicios
- [ ] Ejercicios 1-10 completados
- [ ] Ejercicio integrador completado
- [ ] Documentación revisada

## 🎉 Próximos Pasos

Después de completar este taller:

1. **Taller 3**: Integración con Airflow (si disponible)
2. **Proyecto Real**: Aplicar lo aprendido en un proyecto personal
3. **Certificación**: Considerar certificaciones de GitHub Actions
4. **Comunidad**: Compartir tu experiencia y aprender de otros

---

**¡Éxito en tu aprendizaje de CI/CD!** 🚀
