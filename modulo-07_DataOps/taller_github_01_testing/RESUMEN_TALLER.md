# Resumen Ejecutivo del Taller

## 📊 Información General

- **Nombre**: Taller de Testing y GitHub Actions - Introducción Práctica

## 🎯 Objetivos de Aprendizaje

Al completar este taller, serás capaz de:

1. ✅ Escribir tests unitarios básicos con pytest
2. ✅ Usar el patrón AAA (Arrange-Act-Assert)
3. ✅ Testear excepciones y validaciones
4. ✅ Configurar GitHub Actions para CI
5. ✅ Interpretar resultados de CI en GitHub
6. ✅ Aplicar TDD (Test-Driven Development) básico

## 📁 Estructura del Proyecto

```
taller_github_01_testing/
├── src/
│   └── transformations.py          # 2 funciones simples
├── tests/
│   └── test_basico.py              # 11 tests
├── data/
│   ├── transactions.csv            # 25 transacciones
│   └── README.md
├── ejercicios/
│   ├── ejercicio_guiado.md         # Ejercicio paso a paso
│   └── solucion_ejercicio.py       # Solución completa
├── .github/workflows/
│   └── tests.yml                   # Workflow de CI
├── README.md                       # Guía principal
├── GUIA_GITHUB.md                  # Guía de GitHub
├── COMANDOS_RAPIDOS.md             # Referencia de comandos
└── requirements.txt                # Solo pytest
```

## ⏱️ Distribución del Tiempo

| Paso | Actividad | Duración |
|------|-----------|----------|
| 1 | Setup y Configuración | 30 min |
| 2 | Tests Básicos con Pytest | 30 min |
| 3 | GitHub Actions y CI | 30 min |
| 4 | Ejercicio Práctico | 30 min |

## 🔑 Conceptos Clave

### Testing
- **Test Unitario**: Verifica una función individual
- **Patrón AAA**: Arrange (preparar), Act (ejecutar), Assert (verificar)
- **Assertion**: Verificación de que algo es verdadero
- **pytest.raises**: Verificar que se lanza una excepción

### CI/CD
- **CI (Continuous Integration)**: Ejecutar tests automáticamente
- **GitHub Actions**: Herramienta de CI/CD de GitHub
- **Workflow**: Archivo YAML que define qué hacer
- **Job**: Conjunto de pasos a ejecutar
- **Step**: Acción individual en un job


## 📝 Funciones Implementadas

### 1. calcular_total_venta
```python
calcular_total_venta(precio: float, cantidad: int) -> float
```
- Multiplica precio por cantidad
- Valida que precio >= 0 y cantidad >= 1

### 2. aplicar_descuento
```python
aplicar_descuento(monto: float, porcentaje_descuento: float) -> float
```
- Aplica descuento porcentual
- Valida que monto >= 0 y descuento entre 0-100

### 3. categorizar_cliente (Ejercicio)
```python
categorizar_cliente(total_compras: float) -> str
```
- Categoriza clientes: bronce, plata, oro, platino
- Valida que total_compras >= 0

## 🧪 Tests Implementados

### Tests de calcular_total_venta (5 tests)
- ✅ Caso básico (2 productos de $100)
- ✅ Un solo producto
- ✅ Precios decimales
- ✅ Rechazo de precio negativo
- ✅ Rechazo de cantidad cero

### Tests de aplicar_descuento (6 tests)
- ✅ Descuento del 10%
- ✅ Sin descuento (0%)
- ✅ Descuento completo (100%)
- ✅ Rechazo de monto negativo
- ✅ Rechazo de descuento > 100%

### Tests de categorizar_cliente (11 tests - Ejercicio)
- ✅ Categoría bronce (mínimo y máximo)
- ✅ Categoría plata (mínimo, medio, máximo)
- ✅ Categoría oro (mínimo, medio, máximo)
- ✅ Categoría platino (mínimo y alto)
- ✅ Rechazo de valor negativo

**Total: 22 tests**

## 🚀 Workflow de GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - Checkout código
      - Setup Python 3.9
      - Instalar dependencias
      - Ejecutar pytest
```

**Triggers**: Se ejecuta en cada push y pull request a main

## 📚 Archivos de Documentación

| Archivo | Propósito |
|---------|-----------|
| README.md | Guía principal paso a paso |
| GUIA_GITHUB.md | Guía específica de GitHub |
| COMANDOS_RAPIDOS.md | Referencia de comandos |
| RESUMEN_TALLER.md | Este archivo |
| ejercicios/ejercicio_guiado.md | Ejercicio práctico |
| ejercicios/solucion_ejercicio.py | Solución del ejercicio |


### Proyecto
- [ ] Todos los tests pasan localmente
- [ ] El código está en GitHub
- [ ] GitHub Actions muestra ✅ verde
- [ ] Implementé la función categorizar_cliente
- [ ] Escribí tests para categorizar_cliente

## 🎓 Habilidades Adquiridas
c)

### Tutoriales Recomendados
- [Real Python - Testing](https://realpython.com/pytest-python-testing/)
- [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)
- [Test-Driven Development](https://testdriven.io/)

