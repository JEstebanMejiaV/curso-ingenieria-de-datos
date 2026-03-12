# Definición de KPIs - LogiData

## Resumen Ejecutivo

Este documento define los KPIs (Key Performance Indicators) calculados por el ETL de Spark para medir el cumplimiento y eficiencia de las entregas de LogiData S.A.S.

## KPIs Principales

### 1. OTD (On-Time Delivery Rate)

**Definición**: Porcentaje de entregas realizadas dentro del SLA (Service Level Agreement) prometido al cliente.

**Fórmula**:
```
OTD Rate = (Entregas a tiempo / Total de entregas) × 100
```

**Criterio de "A Tiempo"**:
Una entrega se considera "a tiempo" si:
- `fecha_entrega_real <= fecha_entrega_prometida`

**SLA por Tipo de Entrega**:
| Tipo de Entrega | SLA (horas) |
|----------------|-------------|
| Express        | 4           |
| Same Day       | 8           |
| Next Day       | 24          |
| Standard       | 48          |

**Umbrales de Alerta**:
- **Crítico**: OTD < 85% (producción) / 70% (desarrollo)
- **Warning**: OTD < 90% (producción) / 80% (desarrollo)
- **Objetivo**: OTD >= 95%

**Granularidad**:
- Diaria
- Por zona/tienda
- Por conductor

**Uso**:
- Monitoreo de cumplimiento de promesas al cliente
- Identificación de zonas o conductores con bajo desempeño
- Evaluación de proveedores de transporte

---

### 2. Lead Time

**Definición**: Tiempo total transcurrido desde que se crea el pedido hasta que se entrega al cliente.

**Fórmula**:
```
Lead Time = fecha_entrega_real - fecha_pedido
```

**Unidad**: Horas

**Métricas Derivadas**:
- **Promedio** (avg_lead_time_hours): Lead time promedio del período
- **Mínimo** (min_lead_time_hours): Lead time más corto
- **Máximo** (max_lead_time_hours): Lead time más largo

**Umbrales**:
- **Máximo razonable**: 30 días (720 horas)
- **Warning**: > 36 horas (producción) / > 48 horas (desarrollo)

**Granularidad**:
- Diaria
- Por zona/tienda
- Por conductor

**Uso**:
- Optimización de procesos logísticos
- Identificación de cuellos de botella
- Comparación con competencia

---

### 3. Pickup Time

**Definición**: Tiempo transcurrido desde que se asigna un conductor hasta que recoge el pedido.

**Fórmula**:
```
Pickup Time = fecha_recogida - fecha_asignacion
```

**Unidad**: Minutos

**Métricas Derivadas**:
- **Promedio** (avg_pickup_time_minutes): Pickup time promedio

**Umbrales**:
- **Objetivo**: < 30 minutos
- **Warning**: > 60 minutos

**Granularidad**:
- Diaria
- Por conductor

**Uso**:
- Evaluación de eficiencia de conductores
- Optimización de asignaciones
- Identificación de problemas operativos

---

### 4. First Attempt Success Rate

**Definición**: Porcentaje de entregas exitosas en el primer intento.

**Fórmula**:
```
First Attempt Rate = (Entregas con 1 intento / Total de entregas) × 100
```

**Criterio**:
Una entrega es exitosa en el primer intento si:
- `intentos = 1`
- `estado_entrega = "ENTREGADO"`

**Umbrales**:
- **Objetivo**: >= 90%
- **Warning**: < 85%

**Granularidad**:
- Diaria
- Por conductor

**Uso**:
- Reducción de costos operativos (reintentos son costosos)
- Mejora de satisfacción del cliente
- Evaluación de calidad de direcciones

---

### 5. Eficiencia por Conductor

**Definición**: Número promedio de entregas completadas por hora de trabajo.

**Fórmula**:
```
Deliveries per Hour = Total entregas / Horas trabajadas
```

**Nota**: Actualmente se asume una jornada de 8 horas. En futuras versiones se calculará con datos reales de jornada.

**Umbrales**:
- **Objetivo**: >= 3 entregas/hora
- **Warning**: < 2 entregas/hora

**Granularidad**:
- Diaria
- Por conductor

**Uso**:
- Evaluación de productividad
- Identificación de mejores prácticas
- Optimización de rutas

---

## KPIs Secundarios

### 6. Delay Hours

**Definición**: Horas de retraso para entregas que no cumplieron el SLA.

**Fórmula**:
```
Delay Hours = fecha_entrega_real - fecha_entrega_prometida (si > 0)
```

**Uso**:
- Cuantificar magnitud de incumplimientos
- Priorización de mejoras

---

### 7. Total Revenue

**Definición**: Ingresos totales del período.

**Fórmula**:
```
Total Revenue = SUM(monto_total)
```

**Granularidad**:
- Diaria
- Por zona

**Uso**:
- Análisis de rentabilidad
- Correlación con KPIs operativos

---

### 8. Average Order Value (AOV)

**Definición**: Valor promedio de los pedidos.

**Fórmula**:
```
AOV = Total Revenue / Total de pedidos
```

**Uso**:
- Segmentación de clientes
- Estrategias de pricing

---

## Dimensiones de Análisis

Los KPIs se pueden analizar por las siguientes dimensiones:

### Temporal
- **Fecha** (event_date): Día del pedido
- **Día de la semana**: Lunes a Domingo
- **Mes**: Enero a Diciembre
- **Trimestre**: Q1 a Q4

### Geográfica
- **Zona**: Norte, Sur, Oriente, Occidente, Centro
- **Ciudad** (futuro)
- **Región** (futuro)

### Cliente
- **Tipo de cliente**: Retail, Farmacéutico, Supermercado, etc.
- **Segmento** (futuro)

### Producto
- **Categoría**: Categoría del producto
- **Tipo de entrega**: Express, Same Day, Next Day, Standard

### Operacional
- **Conductor**: Identificador del conductor
- **Vehículo**: Identificador del vehículo
- **Estado de entrega**: Entregado, Fallido, etc.

---

## Frecuencia de Actualización

| KPI | Frecuencia | Latencia |
|-----|-----------|----------|
| OTD Rate | Diaria | D+1 |
| Lead Time | Diaria | D+1 |
| Pickup Time | Diaria | D+1 |
| First Attempt Rate | Diaria | D+1 |
| Eficiencia por Conductor | Diaria | D+1 |

**Nota**: D+1 significa que los KPIs del día D se calculan al día siguiente (D+1).

---

## Casos de Uso

### 1. Dashboard Ejecutivo
- OTD Rate (tendencia mensual)
- Total Deliveries (tendencia)
- Average Lead Time (comparación con objetivo)

### 2. Dashboard Operacional
- OTD Rate por zona (heatmap)
- Entregas por conductor (ranking)
- First Attempt Rate (tendencia)

### 3. Alertas Automáticas
- OTD < 85% → Alerta crítica
- Lead Time > 36h → Alerta warning
- Conductor con < 2 entregas/hora → Alerta operacional

### 4. Análisis de Causa Raíz
- Correlación OTD vs Zona
- Correlación Lead Time vs Tipo de Cliente
- Análisis de entregas fallidas por conductor

---

## Limitaciones y Consideraciones

### Datos Faltantes
- **Entregas sin fecha_entrega_real**: No se incluyen en cálculo de Lead Time
- **Entregas sin conductor**: No se incluyen en KPIs por conductor
- **Pedidos cancelados**: Se excluyen del análisis

### Supuestos
- **Jornada laboral**: Se asume 8 horas (futuro: usar datos reales)
- **Zonas horarias**: Todas las fechas en UTC
- **Reintentos**: Se cuenta el número de intentos reportado

### Mejoras Futuras
1. Incorporar datos de GPS para calcular distancias reales
2. Calcular horas trabajadas reales por conductor
3. Agregar KPIs de costo (costo por entrega, costo por km)
4. Implementar predicción de OTD con ML
5. Agregar análisis de sentimiento de clientes

---

## Referencias

- HU7: Transformar pedidos y entregas en PySpark para KPIs de cumplimiento y eficiencia
- Diccionario de Datos: `modulo-08_proyecto_trasversal/Datos/diccionario_datos.csv`
- Configuración: `config/dev.yaml` y `config/prod.yaml`
