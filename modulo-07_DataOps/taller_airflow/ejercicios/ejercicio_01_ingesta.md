# Ejercicio 01: DAG de Ingesta de Eventos Web

## 🎯 Objetivo

Crear un DAG de Apache Airflow desde cero que ingeste datos de eventos web desde archivos CSV y los cargue a PostgreSQL. Este ejercicio te permitirá aplicar los conceptos fundamentales de Airflow aprendidos en el taller.

## 📋 Contexto

Tu equipo de análisis necesita procesar eventos de navegación web de usuarios para entender mejor su comportamiento en el sitio de e-commerce. Los eventos se generan diariamente en archivos CSV y deben ser cargados a la base de datos para análisis posteriores.

## 🎓 Conceptos a Aplicar

- Definición de DAGs con configuración básica
- Uso de PythonOperator o TaskFlow API (@task)
- Encadenamiento de tareas con dependencias
- Lectura de archivos CSV
- Carga de datos a PostgreSQL
- Manejo de errores y reintentos
- Documentación de DAGs

## 📊 Datos de Entrada

Se te proporciona un archivo CSV con eventos web: `data/raw/web_events.csv`

**Estructura del archivo:**
```csv
event_id,user_id,event_type,page_url,timestamp,session_id
evt_001,usr_123,page_view,/products/laptop,2024-01-15 10:30:00,sess_abc
evt_002,usr_456,add_to_cart,/products/mouse,2024-01-15 10:31:15,sess_def
evt_003,usr_123,purchase,/checkout,2024-01-15 10:35:00,sess_abc
```

**Columnas:**
- `event_id`: Identificador único del evento
- `user_id`: Identificador del usuario
- `event_type`: Tipo de evento (page_view, add_to_cart, purchase, etc.)
- `page_url`: URL de la página donde ocurrió el evento
- `timestamp`: Fecha y hora del evento
- `session_id`: Identificador de la sesión del usuario

## 📝 Requisitos

### 1. Configuración del DAG

Crea un DAG con las siguientes características:

- **dag_id**: `ejercicio_01_ingesta_eventos_web`
- **schedule_interval**: `@daily` (ejecutar diariamente)
- **start_date**: `datetime(2024, 1, 1)`
- **catchup**: `False`
- **tags**: `['ejercicio', 'ingesta', 'eventos_web']`
- **default_args**:
  - `owner`: Tu nombre
  - `retries`: 2
  - `retry_delay`: `timedelta(minutes=5)`

### 2. Tareas Requeridas

Tu DAG debe incluir las siguientes tareas en orden:

#### Tarea 1: `check_source_file`
- Verificar que el archivo CSV de eventos web existe
- Si no existe, la tarea debe fallar con un mensaje claro
- Imprimir la ruta del archivo y su tamaño

#### Tarea 2: `create_table`
- Crear la tabla `raw.web_events` en PostgreSQL si no existe
- Estructura de la tabla:
  ```sql
  CREATE TABLE IF NOT EXISTS raw.web_events (
      event_id VARCHAR(50) PRIMARY KEY,
      user_id VARCHAR(50),
      event_type VARCHAR(50),
      page_url VARCHAR(500),
      timestamp TIMESTAMP,
      session_id VARCHAR(50),
      loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

#### Tarea 3: `load_events`
- Leer el archivo CSV de eventos web
- Validar que el archivo no esté vacío
- Cargar los datos a la tabla `raw.web_events`
- Imprimir el número de registros cargados

#### Tarea 4: `validate_load`
- Verificar que los datos se cargaron correctamente
- Contar registros en la tabla `raw.web_events`
- Comparar con el número de registros del CSV
- Imprimir resumen de la carga

#### Tarea 5: `log_completion`
- Registrar la ejecución exitosa en la tabla `audit.pipeline_executions`
- Incluir: dag_id, execution_date, status, records_processed
- Imprimir mensaje de finalización exitosa

### 3. Dependencias entre Tareas

Establece las dependencias usando el operador `>>`:

```
check_source_file >> create_table >> load_events >> validate_load >> log_completion
```

### 4. Documentación

- Incluye un docstring al inicio del archivo explicando el propósito del DAG
- Documenta cada tarea con comentarios claros
- Usa `doc_md` en el DAG para incluir documentación

## ✅ Criterios de Evaluación

Tu solución será evaluada según los siguientes criterios:

### Funcionalidad (40 puntos)
- [ ] El DAG se carga correctamente en Airflow sin errores (10 pts)
- [ ] Todas las tareas se ejecutan en el orden correcto (10 pts)
- [ ] Los datos se cargan correctamente a PostgreSQL (10 pts)
- [ ] Las validaciones funcionan apropiadamente (10 pts)

### Código (30 puntos)
- [ ] Uso correcto de TaskFlow API o PythonOperator (10 pts)
- [ ] Manejo apropiado de errores y excepciones (10 pts)
- [ ] Código limpio, legible y bien estructurado (10 pts)

### Configuración (20 puntos)
- [ ] Configuración correcta del DAG (schedule, start_date, etc.) (10 pts)
- [ ] Dependencias entre tareas correctamente definidas (10 pts)

### Documentación (10 puntos)
- [ ] Docstrings y comentarios claros (5 pts)
- [ ] Mensajes de log informativos (5 pts)

**Total: 100 puntos**

## 🚀 Pasos para Completar el Ejercicio

1. **Crear el archivo del DAG**
   ```bash
   touch dags/ejercicio_01_ingesta_eventos_web.py
   ```

2. **Implementar el DAG**
   - Importa las librerías necesarias
   - Define la configuración del DAG
   - Implementa cada tarea según los requisitos
   - Establece las dependencias

3. **Generar datos de prueba**
   ```bash
   python scripts/generate_web_events.py
   ```

4. **Probar el DAG**
   - Verifica que el DAG aparece en la UI de Airflow
   - Activa el DAG
   - Ejecuta manualmente (trigger)
   - Revisa los logs de cada tarea

5. **Validar resultados**
   ```sql
   -- Verificar datos cargados
   SELECT COUNT(*) FROM raw.web_events;
   SELECT * FROM raw.web_events LIMIT 10;
   
   -- Verificar auditoría
   SELECT * FROM audit.pipeline_executions 
   WHERE dag_id = 'ejercicio_01_ingesta_eventos_web';
   ```

## 💡 Consejos

- **Usa las utilidades del taller**: Aprovecha las funciones en `utils/db_utils.py` para conectarte a PostgreSQL
- **Prueba incrementalmente**: Implementa una tarea a la vez y prueba antes de continuar
- **Revisa los ejemplos**: Consulta `01_dag_basico_ingesta.py` como referencia
- **Maneja errores**: Usa try-except para capturar y manejar errores apropiadamente
- **Logs informativos**: Usa print() o logging para generar mensajes útiles
- **Valida datos**: Verifica que los datos tengan el formato esperado antes de cargar

## 🔍 Preguntas de Reflexión

Después de completar el ejercicio, reflexiona sobre:

1. ¿Qué pasaría si el archivo CSV no existe cuando se ejecuta el DAG?
2. ¿Cómo manejarías archivos CSV con millones de registros?
3. ¿Qué mejoras podrías hacer para hacer el DAG más robusto?
4. ¿Cómo implementarías carga incremental en lugar de reemplazar todos los datos?
5. ¿Qué otras validaciones de calidad podrías agregar?

## 📚 Recursos Adicionales

- [Documentación de Airflow - TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html)
- [Documentación de Airflow - DAG Configuration](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html)
- `docs/CONCEPTOS_AIRFLOW.md` - Conceptos clave del taller
- `docs/COMANDOS_UTILES.md` - Comandos útiles para debugging

## ✨ Bonus (Opcional)

Si terminas el ejercicio básico, intenta agregar:

1. **Validación de esquema**: Verifica que el CSV tenga las columnas esperadas
2. **Manejo de duplicados**: Evita cargar eventos duplicados (basado en event_id)
3. **Particionamiento por fecha**: Carga solo eventos del día correspondiente
4. **Notificaciones**: Envía un mensaje cuando la carga se complete o falle
5. **Métricas**: Calcula y registra estadísticas sobre los eventos cargados

---

**¡Buena suerte! 🚀**

Si tienes dudas, consulta la solución de referencia en `ejercicios/soluciones/ejercicio_01_solucion.py`
