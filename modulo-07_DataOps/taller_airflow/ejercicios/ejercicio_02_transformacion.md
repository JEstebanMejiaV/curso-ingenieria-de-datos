# Ejercicio 02: Transformación y Análisis RFM

## 🎯 Objetivo

Modificar un DAG existente para agregar transformaciones avanzadas y validaciones de calidad. Este ejercicio te permitirá aplicar conceptos de transformación de datos, cálculo de métricas de negocio (RFM) y validación de calidad en Airflow.

## 📋 Contexto

El equipo de marketing necesita segmentar clientes usando el análisis RFM (Recency, Frequency, Monetary) para personalizar campañas. Tu tarea es extender el DAG de transformaciones existente para calcular estas métricas y agregar validaciones de calidad robustas.

## 🎓 Conceptos a Aplicar

- Modificación de DAGs existentes
- Transformaciones complejas de datos
- Cálculo de métricas de negocio (RFM)
- Validaciones de calidad de datos
- Uso de XCom para compartir datos entre tareas
- Flujos condicionales con BranchPythonOperator
- Manejo de errores y logging avanzado

## 📊 Análisis RFM

El análisis RFM es una técnica de segmentación de clientes basada en tres dimensiones:

- **Recency (R)**: ¿Qué tan reciente fue la última compra del cliente?
  - Menor número de días = Mayor valor
  - Escala: 1-5 (5 = compra muy reciente)

- **Frequency (F)**: ¿Con qué frecuencia compra el cliente?
  - Mayor número de transacciones = Mayor valor
  - Escala: 1-5 (5 = compra muy frecuente)

- **Monetary (M)**: ¿Cuánto dinero ha gastado el cliente?
  - Mayor gasto total = Mayor valor
  - Escala: 1-5 (5 = gasto muy alto)

**Score RFM**: Combinación de los tres valores (ej: "555" = mejor cliente, "111" = cliente en riesgo)

## 📝 Requisitos

### 1. DAG Base

Parte del DAG existente: `02_dag_transformaciones.py`

Tu tarea es **agregar nuevas tareas** al DAG sin modificar las existentes.

### 2. Nuevas Tareas a Implementar

#### Tarea 6: `calculate_rfm_metrics`

Calcula las métricas RFM para cada cliente basándose en sus transacciones.

**Cálculos requeridos:**

```python
# Para cada cliente:
# 1. Recency: Días desde la última compra hasta hoy
recency_days = (fecha_actual - fecha_ultima_compra).days

# 2. Frequency: Número total de transacciones
frequency = count(transacciones)

# 3. Monetary: Suma total gastada
monetary = sum(amount)

# 4. Scores RFM (1-5):
# - Dividir clientes en 5 quintiles para cada métrica
# - Asignar score 5 a los mejores, 1 a los peores
# - Para Recency: menor días = mejor (invertir escala)
# - Para Frequency y Monetary: mayor valor = mejor

# 5. RFM Score: Concatenar los tres scores
rfm_score = f"{r_score}{f_score}{m_score}"  # Ej: "543"

# 6. Segmento: Clasificar según RFM score
# - "Champions": RFM >= 444
# - "Loyal": RFM >= 334 y < 444
# - "Potential": RFM >= 224 y < 334
# - "At Risk": RFM >= 114 y < 224
# - "Lost": RFM < 114
```

**Tabla de salida:** `analytics.customer_rfm`

```sql
CREATE TABLE analytics.customer_rfm (
    customer_id VARCHAR(50) PRIMARY KEY,
    recency_days INTEGER,
    frequency INTEGER,
    monetary DECIMAL(12,2),
    r_score INTEGER,
    f_score INTEGER,
    m_score INTEGER,
    rfm_score VARCHAR(3),
    segment VARCHAR(50),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tarea 7: `validate_rfm_metrics`

Valida que las métricas RFM calculadas sean correctas.

**Validaciones requeridas:**

1. **Validar rangos de scores**:
   - r_score, f_score, m_score deben estar entre 1 y 5
   - rfm_score debe tener exactamente 3 dígitos

2. **Validar valores numéricos**:
   - recency_days >= 0
   - frequency >= 1 (al menos una transacción)
   - monetary > 0

3. **Validar segmentos**:
   - segment debe ser uno de: Champions, Loyal, Potential, At Risk, Lost
   - Verificar que la asignación de segmento sea consistente con rfm_score

4. **Validar completitud**:
   - Todos los clientes con transacciones deben tener métricas RFM
   - No debe haber valores nulos en columnas críticas

**Retornar:** Diccionario con resultados de validación

#### Tarea 8: `branch_on_rfm_quality`

BranchPythonOperator que decide el flujo basado en validaciones.

**Lógica de decisión:**
- Si todas las validaciones pasan → `generate_rfm_report`
- Si alguna validación falla → `handle_rfm_validation_failure`

#### Tarea 9: `generate_rfm_report`

Genera un reporte resumen de la segmentación RFM.

**Reporte debe incluir:**
- Número de clientes por segmento
- Valor promedio por segmento (monetary)
- Frecuencia promedio por segmento
- Recency promedio por segmento
- Top 10 clientes (por RFM score)

**Guardar en:** `analytics.rfm_summary_report`

#### Tarea 10: `handle_rfm_validation_failure`

Maneja el caso cuando las validaciones RFM fallan.

**Acciones:**
- Registrar detalles de validaciones fallidas
- Crear registro en tabla de auditoría
- Imprimir mensaje de error detallado

#### Tarea 11: `log_rfm_completion`

Registra la finalización del proceso RFM (se ejecuta siempre).

**Usar trigger_rule:** `'none_failed_min_one_success'`

### 3. Dependencias entre Tareas

Integrar las nuevas tareas con el DAG existente:

```
[Tareas existentes del DAG 02] >> calculate_rfm_metrics
calculate_rfm_metrics >> validate_rfm_metrics
validate_rfm_metrics >> branch_on_rfm_quality
branch_on_rfm_quality >> [generate_rfm_report, handle_rfm_validation_failure]
[generate_rfm_report, handle_rfm_validation_failure] >> log_rfm_completion
```

### 4. Configuración Adicional

- Agregar tag: `'rfm'` al DAG
- Configurar retries: 2 para las nuevas tareas
- Usar XCom para compartir resultados de validación

## ✅ Criterios de Evaluación

Tu solución será evaluada según los siguientes criterios:

### Funcionalidad (40 puntos)
- [ ] Cálculo correcto de métricas RFM (Recency, Frequency, Monetary) (10 pts)
- [ ] Asignación correcta de scores RFM (1-5) usando quintiles (10 pts)
- [ ] Segmentación correcta de clientes según RFM score (10 pts)
- [ ] Validaciones de calidad funcionan apropiadamente (10 pts)

### Transformaciones (25 puntos)
- [ ] Uso correcto de pandas para cálculos RFM (10 pts)
- [ ] Implementación correcta de quintiles para scoring (10 pts)
- [ ] Generación correcta del reporte resumen (5 pts)

### Flujo y Control (20 puntos)
- [ ] BranchPythonOperator implementado correctamente (10 pts)
- [ ] Manejo apropiado de casos de éxito y fallo (5 pts)
- [ ] Trigger rules configurados correctamente (5 pts)

### Código y Documentación (15 puntos)
- [ ] Código limpio y bien estructurado (5 pts)
- [ ] Uso apropiado de XCom (5 pts)
- [ ] Documentación clara con docstrings (5 pts)

**Total: 100 puntos**

## 🚀 Pasos para Completar el Ejercicio

1. **Copiar el DAG base**
   ```bash
   cp dags/02_dag_transformaciones.py dags/ejercicio_02_transformacion_rfm.py
   ```

2. **Modificar el DAG**
   - Cambiar dag_id a `'ejercicio_02_transformacion_rfm'`
   - Agregar tag `'rfm'`
   - Mantener todas las tareas existentes

3. **Implementar nuevas tareas**
   - Implementa cada tarea según los requisitos
   - Usa las funciones de `utils/` cuando sea apropiado
   - Agrega logging informativo

4. **Establecer dependencias**
   - Conecta las nuevas tareas con las existentes
   - Verifica el flujo en el Graph View de Airflow

5. **Probar el DAG**
   - Verifica que el DAG se carga sin errores
   - Ejecuta el DAG completo
   - Revisa los logs de cada tarea nueva
   - Verifica los datos en las tablas de salida

6. **Validar resultados**
   ```sql
   -- Ver métricas RFM
   SELECT * FROM analytics.customer_rfm LIMIT 10;
   
   -- Ver distribución de segmentos
   SELECT segment, COUNT(*) as customers
   FROM analytics.customer_rfm
   GROUP BY segment
   ORDER BY customers DESC;
   
   -- Ver top clientes
   SELECT customer_id, rfm_score, segment, monetary
   FROM analytics.customer_rfm
   ORDER BY rfm_score DESC
   LIMIT 10;
   
   -- Ver reporte resumen
   SELECT * FROM analytics.rfm_summary_report;
   ```

## 💡 Consejos

- **Entiende RFM primero**: Asegúrate de entender bien cómo funciona el análisis RFM antes de implementar
- **Usa pandas.qcut()**: Para dividir en quintiles fácilmente
- **Invierte Recency**: Recuerda que menor recency es mejor, así que invierte la escala
- **Prueba cálculos**: Valida manualmente algunos cálculos RFM antes de confiar en el código
- **Maneja edge cases**: ¿Qué pasa si un cliente tiene solo 1 transacción?
- **Logs detallados**: Imprime estadísticas intermedias para debugging

## 🔍 Ejemplo de Cálculo RFM

```python
# Ejemplo con 3 clientes:

# Cliente A:
# - Última compra: hace 5 días
# - Transacciones: 10
# - Total gastado: $5,000

# Cliente B:
# - Última compra: hace 30 días
# - Transacciones: 3
# - Total gastado: $500

# Cliente C:
# - Última compra: hace 90 días
# - Transacciones: 1
# - Total gastado: $100

# Después de calcular quintiles:
# Cliente A: R=5, F=5, M=5 → RFM="555" → Segment="Champions"
# Cliente B: R=3, F=3, M=3 → RFM="333" → Segment="Potential"
# Cliente C: R=1, F=1, M=1 → RFM="111" → Segment="Lost"
```

## 📚 Recursos Adicionales

- [Análisis RFM - Explicación](https://en.wikipedia.org/wiki/RFM_(market_research))
- [Pandas qcut() - Documentación](https://pandas.pydata.org/docs/reference/api/pandas.qcut.html)
- [Airflow BranchPythonOperator](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html#branching)
- `02_dag_transformaciones.py` - DAG base de referencia
- `03_dag_calidad.py` - Ejemplo de validaciones y branching

## ✨ Bonus (Opcional)

Si terminas el ejercicio básico, intenta agregar:

1. **Análisis temporal**: Compara RFM del mes actual vs mes anterior
2. **Alertas automáticas**: Identifica clientes que cambiaron de segmento
3. **Visualización**: Genera gráficos de distribución de segmentos
4. **Predicción**: Identifica clientes en riesgo de churn (Lost o At Risk)
5. **Recomendaciones**: Sugiere acciones de marketing por segmento

## 🧪 Casos de Prueba

Valida tu implementación con estos casos:

1. **Cliente nuevo** (1 transacción, hace 1 día, $100):
   - Recency: Alto (R=5)
   - Frequency: Bajo (F=1)
   - Monetary: Bajo (M=1)
   - Segmento esperado: "Potential" o "At Risk"

2. **Cliente leal** (50 transacciones, hace 2 días, $10,000):
   - Recency: Alto (R=5)
   - Frequency: Alto (F=5)
   - Monetary: Alto (M=5)
   - Segmento esperado: "Champions"

3. **Cliente perdido** (5 transacciones, hace 180 días, $500):
   - Recency: Bajo (R=1)
   - Frequency: Medio (F=2-3)
   - Monetary: Medio (M=2-3)
   - Segmento esperado: "Lost"

---

**¡Buena suerte! 🚀**

Si tienes dudas, consulta la solución de referencia en `ejercicios/soluciones/ejercicio_02_solucion.py`
