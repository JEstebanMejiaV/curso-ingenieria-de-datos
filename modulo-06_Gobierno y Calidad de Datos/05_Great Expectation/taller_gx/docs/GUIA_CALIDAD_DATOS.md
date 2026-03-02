# Guía Completa: Calidad de Datos con Great Expectations

## Índice
1. [Introducción a la Calidad de Datos](#introducción)
2. [Las 6 Dimensiones de Calidad](#dimensiones)
3. [Implementación con Great Expectations](#implementación)
4. [Data Docs y Reportes](#data-docs)
5. [Casos de Uso Reales](#casos-de-uso)
6. [Mejores Prácticas](#mejores-prácticas)

---

## Introducción a la Calidad de Datos {#introducción}

### ¿Qué es la Calidad de Datos?

La calidad de datos es el grado en que los datos cumplen con los requisitos de uso previstos. Datos de alta calidad son:
- **Precisos**: Reflejan la realidad correctamente
- **Completos**: Contienen toda la información necesaria
- **Consistentes**: Son coherentes a través del tiempo y sistemas
- **Oportunos**: Están disponibles cuando se necesitan
- **Válidos**: Cumplen con reglas de negocio definidas
- **Únicos**: No contienen duplicados innecesarios

### ¿Por qué es importante?

**Impacto en el Negocio**:
- Decisiones incorrectas basadas en datos erróneos
- Pérdida de confianza en los sistemas de datos
- Costos operacionales por corrección de errores
- Incumplimiento regulatorio
- Pérdida de oportunidades de negocio

**Estadísticas**:
- El 88% de las empresas reportan que datos de mala calidad afectan sus resultados
- Se estima que la mala calidad de datos cuesta a las empresas un promedio del 15-25% de sus ingresos
- El 40% de las iniciativas de negocio fallan por problemas de calidad de datos

---

## Las 6 Dimensiones de Calidad {#dimensiones}

### 1. Completitud (Completeness)

**Definición**: Mide si todos los valores requeridos están presentes.

**Pregunta clave**: ¿Faltan datos donde no deberían faltar?

**Ejemplos de problemas**:
- Campos obligatorios con valores NULL
- Registros incompletos
- Datos faltantes en columnas críticas

**Cómo medirlo**:
```
Completitud = (Valores presentes / Total de valores esperados) × 100%
```

**Expectativas GX**:
```python
# Verificar que no haya nulos
gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id")

# Verificar porcentaje mínimo de completitud
gx.expectations.ExpectColumnValuesToNotBeNull(
    column="email",
    mostly=0.95  # Al menos 95% completo
)
```

**Impacto de negocio**:
- Análisis incompletos o sesgados
- Imposibilidad de contactar clientes
- Reportes con información faltante

---

### 2. Validez (Validity)

**Definición**: Los datos cumplen con las reglas de formato, tipo y dominio esperados.

**Pregunta clave**: ¿Los valores están dentro de los rangos permitidos?

**Ejemplos de problemas**:
- Edades negativas
- Fechas futuras en registros históricos
- Categorías no válidas
- Formatos incorrectos (emails, teléfonos)

**Cómo medirlo**:
```
Validez = (Valores válidos / Total de valores) × 100%
```

**Expectativas GX**:
```python
# Validar rangos numéricos
gx.expectations.ExpectColumnValuesToBeBetween(
    column="age",
    min_value=0,
    max_value=120
)

# Validar dominio de valores
gx.expectations.ExpectColumnValuesToBeInSet(
    column="status",
    value_set=["active", "inactive", "pending"]
)

# Validar formato con regex
gx.expectations.ExpectColumnValuesToMatchRegex(
    column="email",
    regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)
```

**Impacto de negocio**:
- Procesos downstream que fallan
- Cálculos incorrectos
- Violación de reglas de negocio

---

### 3. Precisión (Accuracy)

**Definición**: Los datos reflejan correctamente la realidad que representan.

**Pregunta clave**: ¿Los datos son correctos y representan la verdad?

**Ejemplos de problemas**:
- Direcciones incorrectas
- Precios desactualizados
- Información de contacto errónea

**Cómo medirlo**:
```
Precisión = (Valores correctos / Total de valores) × 100%
```

**Nota**: La precisión es difícil de medir automáticamente ya que requiere comparación con una fuente de verdad externa.

**Expectativas GX**:
```python
# Comparar con valores de referencia
gx.expectations.ExpectColumnValuesToBeInSet(
    column="country_code",
    value_set=["US", "CA", "MX", ...]  # Lista de códigos ISO válidos
)

# Validar relaciones lógicas
gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(
    column_A="end_date",
    column_B="start_date"
)
```

**Impacto de negocio**:
- Envíos a direcciones incorrectas
- Facturación errónea
- Pérdida de confianza del cliente

---

### 4. Consistencia (Consistency)

**Definición**: Los datos son coherentes entre diferentes campos, registros o sistemas.

**Pregunta clave**: ¿Los datos relacionados tienen sentido juntos?

**Ejemplos de problemas**:
- Formatos de fecha inconsistentes
- Unidades de medida mezcladas
- Convenciones de nombres diferentes
- Datos contradictorios entre sistemas

**Cómo medirlo**:
```
Consistencia = (Registros consistentes / Total de registros) × 100%
```

**Expectativas GX**:
```python
# Consistencia de tipos
gx.expectations.ExpectColumnValuesToBeOfType(
    column="price",
    type_="float64"
)

# Consistencia de formato
gx.expectations.ExpectColumnValuesToMatchRegex(
    column="phone",
    regex=r"^\+\d{1,3}-\d{3}-\d{3}-\d{4}$"
)

# Consistencia entre columnas
gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(
    column_A="total_price",
    column_B="unit_price"
)
```

**Impacto de negocio**:
- Dificultad para integrar datos
- Reportes confusos o contradictorios
- Errores en análisis agregados

---

### 5. Unicidad (Uniqueness)

**Definición**: No existen duplicados donde no deberían existir.

**Pregunta clave**: ¿Hay registros duplicados que deberían ser únicos?

**Ejemplos de problemas**:
- IDs duplicados
- Registros de clientes duplicados
- Transacciones procesadas múltiples veces

**Cómo medirlo**:
```
Unicidad = (Valores únicos / Total de valores) × 100%
```

**Expectativas GX**:
```python
# Verificar unicidad completa
gx.expectations.ExpectColumnValuesToBeUnique(
    column="order_id"
)

# Verificar unicidad de combinaciones
gx.expectations.ExpectCompoundColumnsToBeUnique(
    column_list=["customer_id", "order_date", "product_id"]
)
```

**Impacto de negocio**:
- Doble facturación
- Métricas infladas
- Violación de restricciones de integridad
- Confusión en identificación de entidades

---

### 6. Puntualidad (Timeliness)

**Definición**: Los datos están actualizados y disponibles cuando se necesitan.

**Pregunta clave**: ¿Los datos son recientes y relevantes?

**Ejemplos de problemas**:
- Datos obsoletos
- Retrasos en actualización
- Fechas futuras en datos históricos

**Cómo medirlo**:
```
Puntualidad = (Registros actualizados / Total de registros) × 100%
```

**Expectativas GX**:
```python
# Verificar que las fechas no sean futuras
gx.expectations.ExpectColumnValuesToBeBetween(
    column="transaction_date",
    min_value="2020-01-01",
    max_value=datetime.now().strftime("%Y-%m-%d")
)

# Verificar frescura de datos
gx.expectations.ExpectColumnMaxToBeBetween(
    column="last_updated",
    min_value=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
    max_value=datetime.now().strftime("%Y-%m-%d")
)
```

**Impacto de negocio**:
- Decisiones basadas en información desactualizada
- Oportunidades perdidas
- Reportes irrelevantes

---

## Implementación con Great Expectations {#implementación}

### Flujo de Trabajo Recomendado

1. **Identificar dimensiones críticas** para tu caso de uso
2. **Definir umbrales aceptables** por dimensión
3. **Crear expectativas** en Great Expectations
4. **Automatizar validaciones** en pipelines
5. **Monitorear y ajustar** basado en resultados

### Ejemplo: Suite Completa de Calidad

```python
import great_expectations as gx

context = gx.get_context(mode="file")

# Crear suite maestra
suite = context.suites.add(
    gx.ExpectationSuite(name="calidad_datos_completa")
)

# COMPLETITUD
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="customer_id",
        meta={"dimension": "Completitud", "criticidad": "Alta"}
    )
)

# VALIDEZ
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="price",
        min_value=0.01,
        max_value=10000,
        meta={"dimension": "Validez", "criticidad": "Alta"}
    )
)

# CONSISTENCIA
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeOfType(
        column="quantity",
        type_="int64",
        meta={"dimension": "Consistencia", "criticidad": "Media"}
    )
)

# UNICIDAD
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeUnique(
        column="order_id",
        meta={"dimension": "Unicidad", "criticidad": "Alta"}
    )
)

# PUNTUALIDAD
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="order_date",
        min_value="2020-01-01",
        max_value=datetime.now().strftime("%Y-%m-%d"),
        meta={"dimension": "Puntualidad", "criticidad": "Media"}
    )
)

suite.save()
```

---

## Data Docs y Reportes {#data-docs}

### ¿Qué son los Data Docs?

Los Data Docs son páginas HTML interactivas generadas automáticamente que:
- Documentan todas tus expectativas
- Muestran resultados de validaciones
- Incluyen gráficos y estadísticas
- Son fáciles de compartir con stakeholders

### Generar Data Docs

```python
# Generar documentación
context.build_data_docs()

# Abrir en navegador
context.open_data_docs()
```

### Estructura de Data Docs

```
data_docs/
├── index.html                    # Página principal
├── expectations/                 # Documentación de expectativas
│   └── suite_name.html
├── validations/                  # Resultados de validaciones
│   └── validation_result.html
└── static/                       # Assets (CSS, JS, imágenes)
```

### Personalización de Data Docs

Los Data Docs se pueden personalizar editando `great_expectations.yml`:

```yaml
data_docs_sites:
  local_site:
    class_name: SiteBuilder
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/data_docs/local_site/
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
```

---

## Casos de Uso Reales {#casos-de-uso}

### Caso 1: E-commerce - Validación de Pedidos

**Contexto**: Plataforma de e-commerce con 10,000 pedidos diarios

**Dimensiones críticas**:
1. **Completitud**: Todos los pedidos deben tener customer_id, product_id, price
2. **Validez**: Precios > 0, cantidades entre 1-100
3. **Unicidad**: order_id debe ser único
4. **Puntualidad**: Fechas de pedido no pueden ser futuras

**Impacto**:
- Reducción del 40% en pedidos con errores
- Ahorro de 20 horas/semana en corrección manual
- Mejora en satisfacción del cliente

### Caso 2: Finanzas - Validación de Transacciones

**Contexto**: Banco procesando 1M transacciones diarias

**Dimensiones críticas**:
1. **Precisión**: Montos deben coincidir con registros bancarios
2. **Consistencia**: Formatos de cuenta estandarizados
3. **Unicidad**: transaction_id único
4. **Puntualidad**: Transacciones procesadas en <24h

**Impacto**:
- Detección temprana de fraudes
- Cumplimiento regulatorio mejorado
- Reducción de disputas de clientes

### Caso 3: Healthcare - Validación de Registros Médicos

**Contexto**: Hospital con 50,000 pacientes

**Dimensiones críticas**:
1. **Completitud**: Información crítica del paciente completa
2. **Validez**: Códigos de diagnóstico válidos (ICD-10)
3. **Consistencia**: Formatos de fecha estandarizados
4. **Precisión**: Alergias y medicamentos correctos

**Impacto**:
- Mejora en seguridad del paciente
- Cumplimiento HIPAA
- Reducción de errores médicos

---

## Mejores Prácticas {#mejores-prácticas}

### 1. Priorización de Dimensiones

No todas las dimensiones tienen la misma importancia para cada caso de uso:

| Caso de Uso | Dimensiones Críticas |
|-------------|---------------------|
| E-commerce | Validez, Completitud, Unicidad |
| Finanzas | Precisión, Consistencia, Puntualidad |
| Analytics | Completitud, Consistencia |
| IoT/Sensores | Puntualidad, Validez |

### 2. Definición de Umbrales

Establece umbrales realistas basados en tu contexto:

```python
# Ejemplo: Permitir hasta 5% de valores nulos en campos no críticos
gx.expectations.ExpectColumnValuesToNotBeNull(
    column="optional_field",
    mostly=0.95  # 95% de completitud mínima
)
```

### 3. Documentación de Reglas

Usa el campo `meta` para documentar:

```python
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="age",
        min_value=0,
        max_value=120,
        meta={
            "dimension": "Validez",
            "criticidad": "Alta",
            "regla_negocio": "Edad debe estar entre 0 y 120 años",
            "owner": "equipo_datos",
            "fecha_creacion": "2026-03-01"
        }
    )
)
```

### 4. Automatización

Integra validaciones en tus pipelines:

```python
# En tu pipeline de datos
def process_data(df):
    # 1. Validar datos de entrada
    validation_result = validate_input_data(df)
    
    if not validation_result.success:
        send_alert("Datos de entrada inválidos")
        return None
    
    # 2. Procesar datos
    df_processed = transform_data(df)
    
    # 3. Validar datos de salida
    validation_result_output = validate_output_data(df_processed)
    
    if not validation_result_output.success:
        send_alert("Datos de salida inválidos")
        return None
    
    return df_processed
```

### 5. Monitoreo Continuo

Establece dashboards para monitorear:
- Tendencias de calidad en el tiempo
- Dimensiones que más fallan
- Impacto de cambios en pipelines
- Tiempo de resolución de problemas

### 6. Cultura de Calidad de Datos

- **Ownership**: Asigna responsables por cada dataset
- **Training**: Capacita al equipo en calidad de datos
- **Comunicación**: Comparte resultados con stakeholders
- **Mejora continua**: Revisa y actualiza expectativas regularmente

---

## Recursos Adicionales

### Documentación Oficial
- [Great Expectations Docs](https://docs.greatexpectations.io/)
- [Galería de Expectations](https://greatexpectations.io/expectations/)

### Libros Recomendados
- "Data Quality: The Accuracy Dimension" - Jack E. Olson
- "The Data Warehouse Toolkit" - Ralph Kimball

### Frameworks Complementarios
- **dbt**: Para transformaciones con tests
- **Apache Griffin**: Para calidad de datos en big data
- **Soda**: Alternativa a Great Expectations

---

**Última actualización**: Marzo 2026
**Versión**: 1.0
