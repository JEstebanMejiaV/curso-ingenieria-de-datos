# Bases de Datos Relacionales y NoSQL

HU3: Diseño e Implementación del Modelo Relacional (PostgreSQL)

Objetivo: Modelar los datos transaccionales (Clientes, Catálogo, Pedidos, Entregas) asegurando integridad referencial.

Paso 1: Definición del Esquema (DDL)
Debes crear 4 tablas principales. Utiliza el esquema proporcionado en la página 2 y 3 del documento para definir los tipos de datos correctos:

Tabla Clientes:

Definir id_cliente como Primary Key (PK) (tipo VARCHAR).

Asegurar que el campo zona acepte los valores permitidos: Norte, Sur, Oriente, Occidente, Centro.

Asegurar que tipo_cliente acepte: Retail, Farmacéutico, Supermercado, etc..

Tabla Catalogo:

Definir id_producto como PK.

Configurar precio como FLOAT y tipo_entrega como VARCHAR (validar valores: Same Day, Next Day, etc.).

Tabla Pedidos:

Definir id_pedido como PK.

Crear Foreign Keys (FK):


id_cliente referenciando a Clientes(id_cliente).


id_producto referenciando a Catalogo(id_producto).

El campo fecha debe ser TIMESTAMP (UTC-agnóstico).

Tabla Entregas:


Nota Importante: Esta tabla solo contiene pedidos no cancelados.

Definir id_pedido como FK referenciando a Pedidos(id_pedido).

Incluir campos para logística: conductor y vehiculo.

Paso 2: Script de Creación (SQL)
Escribe un script .sql que ejecute las sentencias CREATE TABLE en el orden correcto para evitar errores de llaves foráneas:

Crear Clientes y Catalogo (Tablas maestras).

Crear Pedidos (Tabla transaccional dependiente).

Crear Entregas (Tabla dependiente de Pedidos).

Paso 3: Carga de Datos de Prueba (DML)
El documento indica que AceleraTI entrega archivos CSV (clientes.csv, pedidos.csv, etc.).

Desarrolla un script (en Python con Pandas o SQL COPY) para ingestar estos CSVs en tu base de datos local o instancia RDS de prueba.


Validación: Ejecuta un COUNT(*) en cada tabla para verificar que coincida con los volúmenes esperados (~300 clientes, ~2000 pedidos).

HU4: Diseño del Modelo NoSQL (Datos IoT)

Objetivo: Almacenar datos de alta velocidad provenientes de sensores IoT (Temperatura, Ubicación).

Paso 1: Selección del Motor y Estrategia
Dado que la plataforma es en AWS, DynamoDB es la opción nativa recomendada, aunque MongoDB también es válido.

Análisis del dato: Son series de tiempo por vehículo. Necesitas consultas rápidas por vehículo y rango de fechas.

Paso 2: Diseño de la Tabla (Ejemplo DynamoDB)
Diseña la tabla Sensores optimizada para patrones de acceso de lectura/escritura intensiva:


Partition Key (PK): id_vehiculo (Permite distribuir la carga por camión).


Sort Key (SK): timestamp (Permite ordenar eventos cronológicamente y consultar rangos de tiempo).

Atributos:

latitud (Number)

longitud (Number)

temperatura (Number)


evento (String: "OK" o "TEMP_CRITICA").

Paso 3: Carga de Datos NoSQL (Scripting)
Utiliza el archivo sensores.csv provisto (que simula 10,000 eventos).

Crea un script (Python con boto3 para DynamoDB o pymongo para MongoDB) que:

Lea el CSV fila por fila.

Convierta cada fila en un objeto JSON.

Inserte el documento en la base de datos NoSQL.

Tip: Para DynamoDB, usa BatchWriteItem para optimizar costos y velocidad.

Entregables Finales para estas HU
Según la tabla de evaluación:

Documento de Diseño (modelo_datos_logidata.pdf):

Diagrama Entidad-Relación (DER) del modelo SQL.

Diagrama o descripción JSON del modelo NoSQL.

Justificación de los tipos de datos elegidos.

Código Fuente:

Scripts SQL (schema.sql).

Scripts de carga inicial (load_data.py).


# Bodegas de datos
HU12: Diseño del Modelo Dimensional (Analista BI)
Descripción: Como analista BI, quiero diseñar un modelo dimensional para analizar el cumplimiento de entregas por zona y tiempos.

Tarea 12.1: Definición de Granularidad y Procesos de Negocio

Establecer el grano de la tabla de hechos: ¿Una fila representa una orden de envío, un ítem dentro del envío o un intento de entrega?.

Validar que el grano elegido permita responder preguntas sobre tiempos de retraso y cumplimiento por zona.

Tarea 12.2: Diseño de la Matriz de Bus (Bus Matrix)

Identificar las dimensiones conformadas (que se compartirán con otros procesos como Ventas o Inventario).

Definir la relación entre Dim_Tiempo, Dim_Zona (Geografía) y el Hecho de Entregas.

Tarea 12.3: Definición de Estrategia SCD (Slowly Changing Dimensions)

Decisión Crítica: Analizar la Dim_Zona o Dim_Cliente. Si un cliente se muda o una zona cambia de región administrativa, ¿debemos preservar la historia de sus entregas anteriores en la zona vieja?

Opción A (SCD Tipo 1): Sobrescribir. Se pierde el rastro histórico de la zona anterior.

Opción B (SCD Tipo 2): Crear una nueva fila con claves subrogadas y fechas de vigencia (Fecha_Inicio, Fecha_Fin, Activo). Esto permite reportar la entrega histórica en la zona correcta en ese momento.

Entregable: Documento de mapeo indicando qué atributos son Tipo 1 y cuáles Tipo 2.

Tarea 12.4: Clasificación de Medidas (Facts)

Definir las medidas en la Fact_Entregas:


Días de Retraso: Medida aditiva o semi-aditiva (promediable).

Cumplimiento (Flag): 1 si cumplió, 0 si no (para calcular % de éxito).

Asegurar que las fechas (Fecha Promesa vs. Fecha Real) se modelen como Role-Playing Dimensions apuntando a Dim_Tiempo.

HU13: Implementación DDL y Preparación de Datos (Ingeniero de Datos)
Descripción: Como ingeniero, quiero preparar los datos para consumo analítico (DDL y Staging).

Tarea 13.1: Creación de Claves Subrogadas (Surrogate Keys)

Diseñar la lógica para generar claves sintéticas (ej. ID_Zona_SK) en lugar de usar las claves primarias del sistema operacional (ERP), para aislar el DW de cambios en la fuente.

Tarea 13.2: Scripting DDL de Dimensiones (Esquema en Estrella)

Escribir el CREATE TABLE para Dim_Tiempo, Dim_Geografia/Zona y Dim_Transportadora.


Implementación SCD: Si en la HU12 se decidió SCD Tipo 2 para la Zona, incluir columnas de auditoría en el DDL: Row_Effective_Date, Row_Expiration_Date y Is_Current.

Desnormalizar jerarquías (País -> Región -> Zona) en una sola tabla ancha para mejorar el rendimiento de lectura (Star Schema).

Tarea 13.3: Scripting DDL de Tabla de Hechos

Crear la Fact_Entregas asegurando la integridad referencial (Foreign Keys) hacia las tablas de dimensiones creadas.

Incluir las claves de fecha para los diferentes roles (Fecha Envío, Fecha Entrega).

Tarea 13.4: Carga Inicial de Dimensiones "Dummy"

Insertar registros para manejar valores nulos o desconocidos (ej. ID -1 = "Sin Información") para mantener la integridad referencial en el modelo estrella.

Nuevas Historias de Usuario Sugeridas (Basadas en el PPT)
Para completar el ciclo de desarrollo de una Bodega de Datos robusta, te sugiero agregar estas historias:

HU14: Desarrollo de Procesos ETL/ELT para Carga de Datos
Como Ingeniero de Datos, Quiero desarrollar los pipelines de extracción y transformación, Para poblar el modelo dimensional desde las fuentes transaccionales.

Tareas:

Implementar la lógica de limpieza y normalización antes de cargar al DW.

Desarrollar la lógica de "Lookups" para resolver las Claves Subrogadas de las dimensiones durante la carga de hechos.

Manejar la carga incremental para SCD Tipo 2 (detectar cambios vs. inserciones nuevas).

HU15: Configuración de Capacidades OLAP (Cubos/Semántica)
Como Analista de Datos, Quiero configurar jerarquías de navegación y agregaciones, Para permitir a los usuarios hacer Drill-down y Roll-up en los reportes.

Tareas:

Definir la jerarquía de tiempo (Año -> Trimestre -> Mes -> Día) para permitir Roll-up automático de métricas.

Configurar la jerarquía geográfica (País -> Ciudad -> Zona) para permitir operaciones de Drill-down.

Pre-calcular agregaciones comunes (ej. Total Entregas por Mes) para optimizar tiempos de respuesta.

HU16: Optimización de Rendimiento del Modelo
Como Arquitecto de Datos, Quiero aplicar estrategias de indexación y particionamiento, Para asegurar que las consultas sobre grandes volúmenes de datos respondan en segundos.

Tareas:

Evaluar si se requiere particionamiento de la Fact_Entregas (por ejemplo, por Año/Mes).

Crear índices bitmap en las claves foráneas de las dimensiones si la cardinalidad es baja, o B-Tree si es alta.

Validar que el modelo estrella esté optimizado para reducir el número de JOINs necesarios en tiempo de consulta.

# Data Lake

HU5: Construir un Data Lake en S3 que reciba datos crudos desde distintas fuentes
1) Diseño de la estructura del Data Lake (raw y curated)

Tarea 1.1: Definir convención de nombres y layout de paths en S3

Salida: documento corto con naming + estructura.

Propuesta de layout:

s3://<lake-bucket>/raw/<source>/<dataset>/ingest_date=YYYY-MM-DD/part-*.json|csv|parquet

s3://<lake-bucket>/curated/<domain>/<dataset>/event_date=YYYY-MM-DD/part-*.parquet

s3://<lake-bucket>/quarantine/<source>/<dataset>/... (errores)

s3://<lake-bucket>/_system/metadata/... (checkpoints, manifests)

DoD: layout aprobado y documentado (incluye ejemplo real por dataset).

Tarea 1.2: Definir particionado mínimo por zona

Raw: ingest_date (siempre), opcional source_system

Curated: por fecha de evento (event_date) o year/month/day según caso

DoD: criterios de particionado escritos y aplicables por dataset.

2) Provisionamiento de S3 con seguridad y escalabilidad

Tarea 2.1: Crear bucket(s) y prefijos con controles base

Versioning (recomendado), bloqueo de acceso público, políticas de bucket.

DoD: bucket creado con “public access block” y versioning configurado.

Tarea 2.2: Cifrado y llaves

SSE-KMS para raw/curated, key policy alineada a roles de ingesta/ETL/consulta.

DoD: objetos quedan cifrados; roles autorizados pueden leer/escribir.

Tarea 2.3: Lifecycle y costos

Reglas para transición de raw a IA/Glacier según retención (ej. 30/90/365 días).

DoD: lifecycle activo y documentado con rationale de costos.

Tarea 2.4: Auditoría y logging

CloudTrail Data Events (si aplica), S3 server access logs (opcional), métricas.

DoD: trazabilidad habilitada para operaciones críticas (write/delete/list).

3) Scripts de ingesta en Python (a zona raw)

Tarea 3.1: Especificación de “contrato de ingesta” por fuente

Campos mínimos de metadata: source, dataset, ingest_ts, batch_id, schema_version.

Formatos esperados, compresión, tamaño objetivo de archivos.

DoD: contrato escrito para al menos 2 datasets piloto.

Tarea 3.2: Construir framework de ingesta (Python)

Componentes:

Cargador por fuente (conectores)

Normalizador de nombres/encoding

Escritura a S3 con layout estándar

Registro de manifest/checkpoint (para idempotencia)

DoD: repo con estructura clara (src/, configs/, tests/, README), ejecución local y parametrizable.

Tarea 3.3: Idempotencia y re-ejecución segura

Estrategia recomendada:

batch_id determinístico (por ventana/archivo)

manifest en /_system/metadata/manifests/

evitar duplicados al reintentar

DoD: re-ejecutar un batch no duplica datos (validado con prueba).

Tarea 3.4: Manejo de errores y “quarantine”

Regla: registros/archivos inválidos van a quarantine/ con motivo y timestamp.

DoD: se generan evidencias en quarantine/ + log; el pipeline no “traga” errores silenciosamente.

Tarea 3.5: Logging y métricas operativas

Logs estructurados (JSON), conteos: leídos, escritos, rechazados, duración.

DoD: logs consumibles por CloudWatch y con correlación por batch_id.

Tarea 3.6: Conectores iniciales (mínimo 2 fuentes)

Ejemplos típicos: SFTP/FTPS, API REST, BD (RDS), archivos locales, Salesforce, SAP (según contexto).

DoD: cada conector tiene config, prueba y ejemplo de ejecución.

4) Orquestación mínima (para escalar y operar)

Tarea 4.1: Definir modo de ejecución

Opciones: cron en container, AWS Lambda, AWS Glue Python Shell, ECS, Step Functions.

DoD: decisión tomada y documentada con pros/contras.

Tarea 4.2: Scheduler y reintentos

Política de reintento, backoff, alertas en fallas repetidas.

DoD: existe ejecución programada y se puede forzar un run manual.

HU6: Catalogar la información en AWS Glue para habilitar consultas gobernadas
1) Modelado de catálogo (Glue Databases y Tables)

Tarea 1.1: Definir bases de datos Glue por zona y dominio

Ejemplo: dl_raw, dl_curated, o por dominio curated_finance, curated_collections.

DoD: naming y criterio definidos y aplicados a piloto.

Tarea 1.2: Definir “table standards”

Ubicación S3, formato (ideal: Parquet en curated), particiones, owners.

DoD: plantilla de definición de tabla lista (campos, particiones, parámetros).

2) Población del Glue Catalog

Tarea 2.1: Crear Glue Crawlers para raw (controlado)

Clasificadores si hay CSV con delimitadores particulares o JSON complejo.

DoD: crawler crea tablas raw y detecta particiones ingest_date.

Tarea 2.2: Crear tablas curated preferiblemente por definición explícita

En curated conviene definir schema “a mano” (IaC o scripts) para evitar drift.

DoD: tablas curated con schema estable y particiones correctas.

Tarea 2.3: Estrategia de evolución de esquema

Versionado: schema_version, reglas de compatibilidad, columnas nuevas.

DoD: procedimiento escrito + prueba con columna nueva sin romper consultas.

3) Gobierno de acceso para “consultas gobernadas”

Tarea 3.1: Definir modelo de permisos

Por rol (Analyst, Engineer, Admin) y por zona (raw restringido, curated abierto parcial).

DoD: matriz de permisos (quién ve qué datasets y con qué nivel).

Tarea 3.2: Implementar control de acceso

Recomendación (si buscas gobierno real): Lake Formation con permisos por tabla/columna y, si aplica, filtros por filas.

Alternativa mínima: IAM + políticas en S3 + Athena Workgroups.

DoD: un usuario/rol de analista consulta curated y no accede raw (validación real).

Tarea 3.3: Tags de gobernanza

LF-Tags (si usas Lake Formation) para acceso por clasificación (PII, confidencial, público).

DoD: al menos 1 dataset etiquetado y con permisos basados en tags.

4) Validación de consultas y operación

Tarea 4.1: Configurar Athena para consulta gobernada

Workgroup con límites, cifrado de resultados, ubicación controlada.

DoD: consultas de ejemplo ejecutan en curated y registran resultados en bucket designado.

Tarea 4.2: Suite de consultas de calidad

Conteos por partición, nulos en claves, duplicados en IDs.

DoD: set de queries guardadas (o script) que valida el dataset.

Tarea 4.3: Observabilidad

Alarmas por falla de crawler, fallas de ETL, crecimiento anómalo de particiones.

DoD: al menos 2 alarmas activas con notificación.