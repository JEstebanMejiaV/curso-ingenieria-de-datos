# Ejercicios Prácticos - Taller 2

## 🎯 Ejercicio 1: Configurar Pipeline Completo de CI

**Objetivo**: Implementar un pipeline de CI con lint, tests y security.

**Pasos**:

1. Crear el workflow `.github/workflows/ci.yml`
2. Configurar 3 jobs: lint, test, security
3. Agregar caching de dependencias
4. Ejecutar tests en Python 3.8, 3.9 y 3.10
5. Subir reporte de cobertura como artifact

**Validación**:
- [ ] El workflow se ejecuta en push y PR
- [ ] Los 3 jobs se ejecutan en paralelo
- [ ] El caching funciona (segunda ejecución más rápida)
- [ ] Los artifacts se suben correctamente

**Solución**: Ver `.github/workflows/ci.yml` en el repositorio

---

## 🎯 Ejercicio 2: Implementar Deployment a Múltiples Ambientes

**Objetivo**: Configurar deployment automático a dev, staging y prod.

**Pasos**:

1. Crear 3 environments en GitHub: development, staging, production
2. Configurar secrets por ambiente
3. Crear workflows de deployment para cada ambiente
4. Configurar protecciones:
   - Dev: Sin protección
   - Staging: 1 aprobación
   - Prod: 2 aprobaciones + 5 min wait

**Validación**:
- [ ] Deployment a dev es automático
- [ ] Staging requiere aprobación
- [ ] Prod requiere 2 aprobaciones y espera 5 minutos
- [ ] Los secrets se usan correctamente

**Solución**: Ver `.github/workflows/cd-*.yml` en el repositorio

---

## 🎯 Ejercicio 3: Configurar Versionado Automático

**Objetivo**: Implementar versionado semántico y releases automáticos.

**Pasos**:

1. Crear workflow `.github/workflows/release.yml`
2. Configurar bump automático de versión
3. Generar changelog automático
4. Crear GitHub Release con notas

**Validación**:
- [ ] Al hacer merge a main, se crea un tag nuevo
- [ ] El changelog se genera automáticamente
- [ ] Se crea un GitHub Release
- [ ] La versión sigue semantic versioning

**Solución**: Ver `.github/workflows/release.yml` en el repositorio

---

## 🎯 Ejercicio 4: Implementar Quality Gates

**Objetivo**: Configurar quality gates que bloqueen PRs de baja calidad.

**Pasos**:

1. Crear workflow `.github/workflows/quality-gate.yml`
2. Verificar cobertura mínima del 70%
3. Verificar complejidad ciclomática < 10
4. Verificar code style con Black y Flake8
5. Generar resumen en el PR

**Validación**:
- [ ] El workflow se ejecuta solo en PRs
- [ ] Falla si cobertura < 70%
- [ ] Falla si hay problemas de style
- [ ] Muestra resumen en el PR

**Solución**: Ver `.github/workflows/quality-gate.yml` en el repositorio

---

## 🎯 Ejercicio 5: Configurar Análisis de Seguridad

**Objetivo**: Implementar análisis de seguridad automático.

**Pasos**:

1. Configurar Dependabot en `.github/dependabot.yml`
2. Crear workflow de security scan
3. Ejecutar Bandit para SAST
4. Ejecutar Safety para dependencias
5. Configurar CodeQL

**Validación**:
- [ ] Dependabot crea PRs automáticos
- [ ] Bandit detecta problemas de seguridad
- [ ] Safety verifica vulnerabilidades
- [ ] CodeQL analiza el código

**Solución**: Ver `.github/workflows/security.yml` y `.github/dependabot.yml`

---

## 🎯 Ejercicio 6: Implementar Branch Protection

**Objetivo**: Proteger la rama main con reglas estrictas.

**Pasos**:

1. Ir a Settings → Branches
2. Crear branch protection rule para `main`
3. Requerir PR antes de merge
4. Requerir 1 aprobación
5. Requerir que pasen los checks de CI
6. Requerir que las conversaciones estén resueltas

**Validación**:
- [ ] No se puede hacer push directo a main
- [ ] Se requiere PR
- [ ] Se requiere aprobación
- [ ] CI debe pasar antes de merge

**Solución**: Ver GUIA_GITHUB.md sección "Branch Protection"

---

## 🎯 Ejercicio 7: Crear PR Template

**Objetivo**: Estandarizar la creación de Pull Requests.

**Pasos**:

1. Crear `.github/PULL_REQUEST_TEMPLATE.md`
2. Incluir secciones:
   - Descripción
   - Tipo de cambio
   - Checklist
   - Screenshots (si aplica)
3. Probar creando un PR

**Validación**:
- [ ] Al crear PR, el template aparece automáticamente
- [ ] El template es claro y útil
- [ ] Incluye checklist de validación

**Solución**: Ver `.github/PULL_REQUEST_TEMPLATE.md` en el repositorio

---

## 🎯 Ejercicio 8: Implementar Rollback Automático

**Objetivo**: Configurar rollback automático en caso de fallo en producción.

**Pasos**:

1. Modificar `.github/workflows/cd-prod.yml`
2. Agregar step de backup antes de deployment
3. Agregar smoke tests después de deployment
4. Agregar step de rollback si falla

**Validación**:
- [ ] Se crea backup antes de deployment
- [ ] Se ejecutan smoke tests
- [ ] Si falla, se ejecuta rollback
- [ ] Se notifica al equipo

**Solución**: Ver `.github/workflows/cd-prod.yml` en el repositorio

---

## 🎯 Ejercicio 9: Optimizar Performance del Pipeline

**Objetivo**: Reducir el tiempo de ejecución del pipeline.

**Pasos**:

1. Agregar caching de dependencias
2. Ejecutar jobs en paralelo
3. Usar matrix strategy para tests
4. Cancelar workflows redundantes

**Validación**:
- [ ] Primera ejecución: ~5 minutos
- [ ] Segunda ejecución con cache: ~2 minutos
- [ ] Jobs se ejecutan en paralelo
- [ ] Workflows redundantes se cancelan

**Solución**: Ver `.github/workflows/ci.yml` con optimizaciones

---

## 🎯 Ejercicio 10: Monitoreo y Alertas

**Objetivo**: Configurar notificaciones de deployment.

**Pasos**:

1. Agregar step de notificación en workflows
2. Configurar notificación a Slack (o email)
3. Incluir información del deployment
4. Diferenciar entre éxito y fallo

**Validación**:
- [ ] Se envía notificación en cada deployment
- [ ] La notificación incluye ambiente y versión
- [ ] Se diferencia éxito de fallo
- [ ] El equipo recibe las notificaciones

**Solución**: Agregar steps de notificación en workflows de CD

---

## 📝 Ejercicio Integrador Final

**Objetivo**: Implementar un feature completo siguiendo todo el flujo de CI/CD.

**Escenario**: Agregar funcionalidad de "Cupones de Descuento"

**Pasos**:

1. Crear rama `feature/cupones-descuento`
2. Implementar función `aplicar_cupon(pedido, codigo_cupon)`
3. Escribir tests unitarios (cobertura >= 80%)
4. Asegurar que pase lint y security
5. Crear PR con template completo
6. Esperar aprobación y CI
7. Merge a main
8. Verificar deployment a dev
9. Crear tag RC para staging
10. Aprobar y verificar staging
11. Crear release para producción
12. Aprobar y verificar producción

**Validación**:
- [ ] Feature implementado correctamente
- [ ] Tests con cobertura >= 80%
- [ ] CI pasa en todos los checks
- [ ] PR aprobado y mergeado
- [ ] Deployment exitoso a los 3 ambientes
- [ ] Release creado con changelog

**Tiempo estimado**: 2-3 horas

---

## 🏆 Desafíos Adicionales

### Desafío 1: Multi-Region Deployment
Configurar deployment a múltiples regiones (US, EU, LATAM)

### Desafío 2: Blue-Green Deployment
Implementar estrategia de blue-green deployment

### Desafío 3: Canary Deployment
Implementar deployment gradual (canary)

### Desafío 4: Feature Flags
Integrar sistema de feature flags

### Desafío 5: Performance Testing
Agregar tests de performance al pipeline

---

## 📊 Rúbrica de Evaluación

| Criterio | Puntos | Descripción |
|----------|--------|-------------|
| Pipeline CI completo | 15 | Lint, tests, security funcionando |
| Deployment multi-ambiente | 15 | Dev, staging, prod configurados |
| Versionado automático | 10 | Semantic versioning y releases |
| Quality gates | 10 | Cobertura, complejidad, style |
| Security | 10 | Bandit, Safety, CodeQL |
| Branch protection | 10 | Reglas configuradas correctamente |
| Documentation | 10 | README, GUIA_GITHUB completos |
| PR template | 5 | Template útil y completo |
| Rollback | 5 | Rollback automático funciona |
| Optimización | 10 | Pipeline optimizado |
| **Total** | **100** | |

**Aprobación**: >= 70 puntos
**Excelencia**: >= 90 puntos
