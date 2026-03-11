# Índice de Navegación del Taller

## 🗺️ Guía de Navegación

Este taller contiene múltiples archivos de documentación. Usa este índice para encontrar rápidamente lo que necesitas.

---

## 📚 Documentación Principal

### 1. [README.md](README.md) - **EMPIEZA AQUÍ**
**Propósito**: Guía principal paso a paso del taller completo (2 horas)

**Contenido**:
- Introducción y objetivos
- Requisitos previos
- Guía paso a paso completa:
  - Paso 1: Setup (30 min)
  - Paso 2: Tests Básicos (30 min)
  - Paso 3: GitHub Actions (30 min)
  - Paso 4: Ejercicio Práctico (30 min)
- Troubleshooting
- Recursos adicionales

**Cuándo usar**: Cuando empieces el taller y durante todo el proceso.

---

### 2. [GUIA_GITHUB.md](GUIA_GITHUB.md)
**Propósito**: Guía detallada específica para GitHub y GitHub Actions

**Contenido**:
- Cómo crear un repositorio en GitHub
- Cómo subir código a GitHub
- Cómo ver y entender GitHub Actions
- Cómo hacer cambios y ver CI en acción
- Solución de problemas específicos de GitHub

**Cuándo usar**: Durante el Paso 3 (GitHub Actions) o cuando tengas dudas sobre GitHub.

---

### 3. [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md)
**Propósito**: Referencia rápida de todos los comandos

**Contenido**:
- Comandos de Python y pip
- Comandos de pytest
- Comandos de Git
- Comandos de GitHub
- Flujo de trabajo típico
- Comandos de debugging
- Comandos de limpieza

**Cuándo usar**: Como referencia rápida cuando olvides un comando.

---

### 4. [RESUMEN_TALLER.md](RESUMEN_TALLER.md)
**Propósito**: Resumen ejecutivo del taller completo

**Contenido**:
- Información general
- Objetivos de aprendizaje
- Estructura del proyecto
- Conceptos clave
- Funciones y tests implementados
- Checklist de completación
- Métricas del taller

**Cuándo usar**: Para tener una vista general o al finalizar el taller.

---

## 🎯 Ejercicios

### 5. [ejercicios/ejercicio_guiado.md](ejercicios/ejercicio_guiado.md)
**Propósito**: Ejercicio práctico paso a paso

**Contenido**:
- Objetivo del ejercicio
- Descripción detallada
- Paso a paso con tiempos estimados
- Checkpoints de validación
- Criterios de auto-evaluación
- Pistas y ayudas

**Cuándo usar**: Durante el Paso 4 (Ejercicio Práctico).

---

### 6. [ejercicios/solucion_ejercicio.py](ejercicios/solucion_ejercicio.py)
**Propósito**: Solución completa del ejercicio

**Contenido**:
- Código completo de la función
- Tests completos
- Explicación detallada de la solución
- Mejores prácticas aplicadas

**Cuándo usar**: Solo después de intentar el ejercicio por tu cuenta.

---

## 📁 Código Fuente

### 7. [src/transformations.py](src/transformations.py)
**Propósito**: Funciones de transformación de datos

**Contenido**:
- `calcular_total_venta()`: Multiplica precio por cantidad
- `aplicar_descuento()`: Aplica descuento porcentual
- Validaciones y manejo de errores
- Docstrings completos

**Cuándo usar**: Para entender las funciones que vas a testear.

---

### 8. [tests/test_basico.py](tests/test_basico.py)
**Propósito**: Tests unitarios de las funciones

**Contenido**:
- 10 tests completos
- Comentarios explicativos extensos
- Ejemplos del patrón AAA
- Tests de excepciones

**Cuándo usar**: Para aprender cómo escribir tests.

---

## ⚙️ Configuración

### 9. [.github/workflows/tests.yml](.github/workflows/tests.yml)
**Propósito**: Workflow de GitHub Actions

**Contenido**:
- Configuración de CI
- Triggers (push, pull_request)
- Steps del workflow
- Comentarios explicativos

**Cuándo usar**: Para entender cómo funciona CI.

---

### 10. [requirements.txt](requirements.txt)
**Propósito**: Dependencias del proyecto

**Contenido**:
- pytest==7.4.0

**Cuándo usar**: Al instalar dependencias con `pip install -r requirements.txt`.

---

### 11. [pytest.ini](pytest.ini)
**Propósito**: Configuración de pytest

**Contenido**:
- Directorio de tests
- Opciones por defecto

**Cuándo usar**: Pytest lo usa automáticamente.

---

### 12. [.gitignore](.gitignore)
**Propósito**: Archivos a ignorar en Git

**Contenido**:
- Cache de Python
- Entornos virtuales
- Archivos de IDE

**Cuándo usar**: Git lo usa automáticamente.

---

## 📊 Datos

### 13. [data/transactions.csv](data/transactions.csv)
**Propósito**: Datos de ejemplo para testing

**Contenido**:
- 25 transacciones de e-commerce
- Columnas: transaction_id, amount, quantity, date, status

**Cuándo usar**: Para entender el contexto de los datos.

---

### 14. [data/README.md](data/README.md)
**Propósito**: Documentación del esquema de datos

**Contenido**:
- Descripción de columnas
- Ejemplos de registros
- Reglas de validación

**Cuándo usar**: Para entender la estructura de los datos.

---

## 🗺️ Flujo de Navegación Recomendado

### Para Principiantes (Primera Vez)

1. **Empieza aquí**: [README.md](README.md)
2. **Sigue el Paso 1**: Setup y Configuración
3. **Revisa el código**: [src/transformations.py](src/transformations.py)
4. **Revisa los tests**: [tests/test_basico.py](tests/test_basico.py)
5. **Sigue el Paso 2**: Tests Básicos
6. **Consulta comandos**: [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md) (si olvidas algo)
7. **Sigue el Paso 3**: GitHub Actions
8. **Consulta guía GitHub**: [GUIA_GITHUB.md](GUIA_GITHUB.md) (si tienes dudas)
9. **Sigue el Paso 4**: Ejercicio Práctico
10. **Haz el ejercicio**: [ejercicios/ejercicio_guiado.md](ejercicios/ejercicio_guiado.md)
11. **Revisa solución**: [ejercicios/solucion_ejercicio.py](ejercicios/solucion_ejercicio.py) (solo si te atascas)
12. **Revisa resumen**: [RESUMEN_TALLER.md](RESUMEN_TALLER.md)

### Para Referencia Rápida

- **Olvidé un comando**: [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md)
- **Problema con GitHub**: [GUIA_GITHUB.md](GUIA_GITHUB.md) → Sección 6
- **Problema con pytest**: [README.md](README.md) → Sección Troubleshooting
- **¿Qué aprendí?**: [RESUMEN_TALLER.md](RESUMEN_TALLER.md)

### Para Repaso

1. [RESUMEN_TALLER.md](RESUMEN_TALLER.md) - Vista general
2. [tests/test_basico.py](tests/test_basico.py) - Ejemplos de tests
3. [.github/workflows/tests.yml](.github/workflows/tests.yml) - Configuración CI

---

## 🔍 Búsqueda Rápida por Tema

### Testing
- Conceptos básicos: [README.md](README.md) → Paso 2
- Ejemplos de tests: [tests/test_basico.py](tests/test_basico.py)
- Comandos pytest: [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md) → Sección Pytest

### GitHub Actions
- Guía completa: [GUIA_GITHUB.md](GUIA_GITHUB.md)
- Configuración: [.github/workflows/tests.yml](.github/workflows/tests.yml)
- Paso a paso: [README.md](README.md) → Paso 3

### Git
- Comandos básicos: [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md) → Sección Git
- Flujo de trabajo: [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md) → Flujo de Trabajo Típico
- Problemas: [GUIA_GITHUB.md](GUIA_GITHUB.md) → Sección 6

### Ejercicio
- Instrucciones: [ejercicios/ejercicio_guiado.md](ejercicios/ejercicio_guiado.md)
- Solución: [ejercicios/solucion_ejercicio.py](ejercicios/solucion_ejercicio.py)

---

## 📱 Versión Imprimible

Si quieres imprimir documentación para tener a mano:

**Esencial** (imprimir):
1. [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md) - 1 página
2. [README.md](README.md) → Solo checkpoints - 1 página

**Opcional** (tener en pantalla):
- [GUIA_GITHUB.md](GUIA_GITHUB.md)
- [ejercicios/ejercicio_guiado.md](ejercicios/ejercicio_guiado.md)

---

## 💡 Tips de Navegación

1. **Usa Ctrl+F** (o Cmd+F en Mac) para buscar dentro de cada archivo
2. **Sigue los enlaces**: Todos los archivos están interconectados
3. **Marca tu progreso**: Usa los checkpoints en cada paso
4. **Consulta cuando necesites**: No memorices, consulta la documentación
5. **Practica**: La mejor forma de aprender es haciendo

---

## 🆘 ¿Perdido?

Si no sabes dónde estás o qué hacer:

1. **Vuelve al README**: [README.md](README.md)
2. **Revisa el resumen**: [RESUMEN_TALLER.md](RESUMEN_TALLER.md)
3. **Consulta este índice**: Estás aquí 😊

---

## 📞 Soporte

Si después de revisar toda la documentación aún tienes dudas:

1. Revisa la sección de Troubleshooting en [README.md](README.md)
2. Consulta problemas específicos de GitHub en [GUIA_GITHUB.md](GUIA_GITHUB.md)
3. Pregunta al instructor del curso

---

**¡Buena suerte con el taller!** 🚀

Recuerda: Esta documentación está aquí para ayudarte. No dudes en consultarla tantas veces como necesites.
