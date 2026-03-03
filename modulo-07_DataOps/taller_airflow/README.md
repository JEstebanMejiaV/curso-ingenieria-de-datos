# Taller de Apache Airflow - Módulo 07: DataOps

## Introducción

Bienvenido al taller de Apache Airflow, parte del módulo 07_DataOps del curso de Ingeniería de Datos. Este taller te enseñará a orquestar pipelines de datos usando Apache Airflow, una de las herramientas más populares para la automatización y monitoreo de workflows de datos en entornos de producción.

Apache Airflow es una plataforma de código abierto que permite programar, monitorear y gestionar workflows complejos de procesamiento de datos. En este taller, aprenderás a construir DAGs (Directed Acyclic Graphs) que representan pipelines de datos end-to-end, desde la ingesta hasta la transformación y validación de calidad.

### Caso de Uso: Sistema de Análisis de Ventas E-commerce

A lo largo del taller trabajaremos con un escenario realista de análisis de datos de ventas para una plataforma de e-commerce. Construirás pipelines que:

- Ingestan datos de transacciones, productos y clientes desde archivos CSV
- Transforman y enriquecen los datos aplicando lógica de negocio
- Calculan métricas agregadas para análisis de ventas
- Validan la calidad de los datos en cada etapa
- Coordinan múltiples procesos con dependencias complejas
- Manejan reprocesamiento de datos históricos

## Objetivos de Aprendizaje

Al completar este taller, serás capaz de:

1. **Configurar y ejecutar** un entorno de Airflow localmente usando Docker
2. **Crear DAGs básicos** para ingesta de datos desde archivos CSV a bases de datos
3. **Implementar transformaciones** de datos con dependencias entre tareas
4. **Integrar validaciones de calidad** usando Great Expectations
5. **Usar sensores** para coordinar pipelines con dependencias externas
6. **Manejar backfills** para procesar datos históricos
7. **Orquestar jobs Spark** desde Airflow
8. **Implementar monitoreo y alertas** para pipelines de producción
9. **Aplicar mejores prácticas** de DataOps en pipelines reales

## Requisitos Previos

### Conocimientos

- Python básico (funciones, clases, manejo de archivos)
- SQL básico (SELECT, INSERT, JOIN)
- Conceptos de bases de datos relacionales
- Familiaridad con línea de comandos
- Conocimientos básicos de Docker (deseable)

### Software Necesario

- **Docker Desktop** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git** para clonar el repositorio
- **Editor de código** (VS Code, PyCharm, o similar)
- Al menos **8 GB de RAM** disponible para Docker
- Al menos **10 GB de espacio en disco**

### Verificación de Requisitos

Verifica que tienes Docker y Docker Compose instalados:

```bash
docker --version
docker-compose --version
```

## Estructura del Taller

```
taller_airflow/
├── dags/                          # DAGs de Airflow
│   ├── 01_dag_basico_ingesta.py
│   ├── 02_dag_transformaciones.py
│   ├── 03_dag_calidad.py
│   ├── 04_dag_sensores.py
│   ├── 05_dag_backfill.py
│   ├── 06_dag_spark_integration.py
│   ├── 07_dag_great_expectations.py
│   ├── 08_dag_completo_produccion.py
│   └── utils/                     # Utilidades compartidas
│       ├── db_utils.py
│       └── validation_utils.py
├── data/                          # Datos de ejemplo
│   ├── raw/                       # Datos sin procesar
│   ├── processed/                 # Datos transformados
│   └── analytics/                 # Datos agregados
├── docs/                          # Documentación de referencia
│   ├── COMANDOS_UTILES.md
│   ├── CONCEPTOS_AIRFLOW.md
│   └── ARQUITECTURA.md
├── ejercicios/                    # Ejercicios prácticos
│   ├── ejercicio_01_ingesta.md
│   ├── ejercicio_02_transformacion.md
│   ├── ejercicio_03_pipeline_completo.md
│   └── soluciones/                # Soluciones de referencia
├── logs/                          # Logs de Airflow
├── plugins/                       # Plugins personalizados
├── scripts/                       # Scripts de utilidad
│   ├── init_db.sql
│   └── generate_sample_data.py
├── spark_jobs/                    # Jobs de Spark
├── docker-compose.yml             # Configuración de Docker
├── .env                           # Variables de entorno
├── requirements.txt               # Dependencias Python
└── README.md                      # Este archivo
```

## Guía de Setup

### Paso 1: Clonar el Repositorio

Si aún no lo has hecho, clona el repositorio del curso:

```bash
git clone <url-del-repositorio>
cd modulo-07_DataOps/taller_airflow
```

### Paso 2: Configurar Variables de Entorno

El archivo `.env` contiene la configuración necesaria para Airflow. Ya está preconfigurado con valores por defecto para desarrollo local.

### Paso 3: Inicializar Airflow

Ejecuta el siguiente comando para inicializar la base de datos de Airflow y crear el usuario administrador:

```bash
docker-compose up airflow-init
```

Este comando:
- Crea la base de datos de metadatos de Airflow
- Inicializa los esquemas necesarios
- Crea un usuario administrador (usuario: `airflow`, contraseña: `airflow`)

### Paso 4: Levantar los Servicios de Airflow

Una vez completada la inicialización, levanta todos los servicios:

```bash
docker-compose up -d
```

Este comando inicia:
- **PostgreSQL**: Base de datos para metadatos y datos del taller
- **Redis**: Message broker para el executor
- **Airflow Webserver**: Interfaz web (puerto 8080)
- **Airflow Scheduler**: Programador de DAGs
- **Airflow Worker**: Ejecutor de tareas

### Paso 5: Verificar que los Servicios Están Corriendo

Verifica el estado de los contenedores:

```bash
docker-compose ps
```

Todos los servicios deben estar en estado "running" o "healthy".

### Paso 6: Acceder a la Interfaz Web

Abre tu navegador y accede a:

```
http://localhost:8080
```

Credenciales de acceso:
- **Usuario**: `airflow`
- **Contraseña**: `airflow`

### Paso 7: Generar Datos de Ejemplo

Ejecuta el script para generar datos sintéticos de ejemplo:

```bash
docker-compose exec airflow-worker python /opt/airflow/scripts/generate_sample_data.py
```

Este script genera:
- 1000 clientes
- 100 productos en 10 categorías
- 10,000 transacciones distribuidas en 30 días
- Anomalías intencionales para practicar validaciones

### Paso 8: Inicializar la Base de Datos

Crea los esquemas y tablas necesarios:

```bash
docker-compose exec postgres psql -U airflow -d airflow -f /opt/airflow/scripts/init_db.sql
```

### Paso 9: Activar los DAGs

En la interfaz web de Airflow:
1. Ve a la página principal (DAGs)
2. Verás la lista de DAGs del taller
3. Activa los DAGs usando el toggle a la izquierda de cada uno
4. Los DAGs comenzarán a ejecutarse según su configuración de schedule

## Progresión del Taller

El taller está diseñado para aprendizaje progresivo. Sigue este orden:

### Nivel 1: Fundamentos (DAGs 01-02)
1. **DAG 01: Ingesta Básica** - Aprende los conceptos fundamentales de Airflow
2. **DAG 02: Transformaciones** - Entiende el encadenamiento de tareas y uso de XCom

### Nivel 2: Calidad y Coordinación (DAGs 03-04)
3. **DAG 03: Validación de Calidad** - Implementa validaciones y flujos condicionales
4. **DAG 04: Sensores** - Coordina pipelines con dependencias externas

### Nivel 3: Avanzado (DAGs 05-07)
5. **DAG 05: Backfill** - Maneja procesamiento de datos históricos
6. **DAG 06: Integración Spark** - Orquesta jobs de procesamiento distribuido
7. **DAG 07: Great Expectations** - Integra validaciones avanzadas de calidad

### Nivel 4: Producción (DAG 08)
8. **DAG 08: Pipeline Completo** - Aplica todas las mejores prácticas en un pipeline production-ready

## Ejercicios Prácticos

Después de completar los DAGs de ejemplo, practica con los ejercicios en el directorio `ejercicios/`:

1. **Ejercicio 1**: Crear un DAG de ingesta desde cero
2. **Ejercicio 2**: Modificar un DAG existente para agregar transformaciones
3. **Ejercicio 3**: Diseñar un pipeline completo end-to-end

Cada ejercicio incluye:
- Descripción del objetivo
- Requisitos específicos
- Criterios de evaluación
- Solución de referencia (en `ejercicios/soluciones/`)

## Documentación de Referencia

Consulta los siguientes documentos para profundizar:

- **[COMANDOS_UTILES.md](docs/COMANDOS_UTILES.md)**: Comandos de Docker, Airflow CLI, y troubleshooting
- **[CONCEPTOS_AIRFLOW.md](docs/CONCEPTOS_AIRFLOW.md)**: Glosario y explicación de conceptos clave
- **[ARQUITECTURA.md](docs/ARQUITECTURA.md)**: Arquitectura del taller y diagramas

## Comandos Útiles

### Docker Compose

```bash
# Levantar servicios
docker-compose up -d

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f airflow-scheduler

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (limpieza completa)
docker-compose down -v

# Reiniciar un servicio específico
docker-compose restart airflow-scheduler
```

### Airflow CLI

```bash
# Listar DAGs
docker-compose exec airflow-worker airflow dags list

# Ejecutar un DAG manualmente
docker-compose exec airflow-worker airflow dags trigger <dag_id>

# Ver estado de un DAG
docker-compose exec airflow-worker airflow dags state <dag_id> <execution_date>

# Listar tareas de un DAG
docker-compose exec airflow-worker airflow tasks list <dag_id>

# Probar una tarea específica
docker-compose exec airflow-worker airflow tasks test <dag_id> <task_id> <execution_date>
```

### PostgreSQL

```bash
# Conectarse a la base de datos
docker-compose exec postgres psql -U airflow -d airflow

# Ejecutar query desde línea de comandos
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT * FROM raw.transactions LIMIT 5;"
```

## Troubleshooting

### Los servicios no inician

1. Verifica que Docker Desktop esté corriendo
2. Asegúrate de tener suficiente RAM asignada a Docker (mínimo 8 GB)
3. Revisa los logs: `docker-compose logs`

### No puedo acceder a la interfaz web

1. Verifica que el webserver esté corriendo: `docker-compose ps`
2. Espera 1-2 minutos después de iniciar los servicios
3. Intenta acceder a `http://127.0.0.1:8080` en lugar de `localhost:8080`

### Los DAGs no aparecen en la UI

1. Verifica que los archivos estén en el directorio `dags/`
2. Revisa los logs del scheduler: `docker-compose logs airflow-scheduler`
3. Verifica que no haya errores de sintaxis en los DAGs

### Error de conexión a la base de datos

1. Verifica que el servicio postgres esté corriendo
2. Revisa las credenciales en el archivo `.env`
3. Reinicia los servicios: `docker-compose restart`

## Recursos Adicionales

- [Documentación oficial de Apache Airflow](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Great Expectations Documentation](https://docs.greatexpectations.io/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)

## Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa la sección de Troubleshooting en este README
2. Consulta `docs/COMANDOS_UTILES.md` para comandos de debugging
3. Revisa los logs de los servicios con `docker-compose logs`
4. Consulta con el instructor del curso

