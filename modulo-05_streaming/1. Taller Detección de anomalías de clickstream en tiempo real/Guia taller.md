# 🚀 Lab: Detección de Anomalías en Tiempo Real en Clickstream con Amazon Managed Service for Apache Flink

Este laboratorio es parte del taller **Amazon Managed Service for Apache Flink Workshop**. El objetivo es construir una canalización (pipeline) de procesamiento de streaming para detectar anomalías en datos de clickstream (comportamiento de usuarios) utilizando el algoritmo **Random Cut Forest (RCF)** sobre Apache Flink.

## Tabla de Contenidos
- [Descripción del Escenario](#descripción-del-escenario)
- [Arquitectura](#arquitectura)
- [Requisitos Previos](#requisitos-previos)
- [Instrucciones Paso a Paso](#instrucciones-paso-a-paso)
  - [1. Configuración de Infraestructura](#1-configuración-de-infraestructura)
  - [2. Generación de Datos (Data Producer)](#2-generación-de-datos-data-producer)
  - [3. Despliegue de la Aplicación Flink](#3-despliegue-de-la-aplicación-flink)
  - [4. Ejecución y Monitoreo](#4-ejecución-y-monitoreo)
  - [5. Verificación de Resultados](#5-verificación-de-resultados)
- [Limpieza de Recursos](#limpieza-de-recursos)
- [Referencias](#referencias)

---

## Descripción del Escenario

Los sitios web modernos generan millones de eventos de "clickstream" (vistas de página, clics en botones, errores, etc.). Detectar anomalías en estos flujos en tiempo real (por ejemplo, un aumento repentino de errores 404 o una caída drástica en las compras) es crítico para la operatividad del negocio.

En este laboratorio utilizaremos **Amazon Managed Service for Apache Flink** para procesar estos datos y aplicar el algoritmo **Random Cut Forest (RCF)**. RCF es un algoritmo no supervisado diseñado para detectar puntos de datos que divergen del patrón normal sin necesidad de etiquetado previo.

---

## Arquitectura

El flujo de datos propuesto es el siguiente:

1.  **Fuente (Source):** Un script en Python genera eventos de clickstream simulados y los inyecta en un **Amazon Kinesis Data Stream** (`InputStream`).
2.  **Procesamiento:** La aplicación de **Apache Flink** consume el stream, agrega los datos y calcula un `ANOMALY_SCORE`.
3.  **Destino (Sink):** Los resultados (incluyendo el score de anomalía) se envían a otro **Kinesis Data Stream** (`OutputStream`) para su consumo posterior (ej. Lambda, OpenSearch o Dashboard).

```mermaid
graph LR
    A[Generador de Datos<br>(Python Script)] -->|PutRecord| B[Kinesis Data Stream<br>(Input)]
    B -->|Consumer| C[Amazon Managed Service<br>for Apache Flink]
    C -->|RCF Algorithm| D[Kinesis Data Stream<br>(Output)]
    D -->|Consumo| E[Lambda / OpenSearch]
```
##  Requisitos Previos
Antes de comenzar, asegúrate de tener:

Cuenta de AWS: Acceso a la consola de AWS con permisos de Administrador o PowerUser.

Entorno de Desarrollo: AWS Cloud9 (recomendado) o AWS CLI configurado en local.

Java & Maven: Necesario si vas a compilar el código fuente de la aplicación Flink.

Python 3.x: Para ejecutar los scripts de generación de datos.

##  Instrucciones Paso a Paso
1. Configuración de Infraestructura
Si el taller no provee una plantilla de CloudFormation, crea los recursos manualmente:

Ve a la consola de Amazon Kinesis.

Crea dos Kinesis Data Streams:

ClickstreamInput (Source)

ClickstreamOutput (Sink)

Crea un S3 Bucket (ej. flink-app-artifacts-<tu-nombre>) para almacenar el código compilado (JAR).

##  2. Generación de Datos (Data Producer)
Utiliza el script producer.py provisto en los materiales del taller para simular tráfico.

Instala la librería boto3 si no la tienes:

Bash
pip install boto3
Ejecuta el productor apuntando al stream de entrada:

Bash
python producer.py --stream ClickstreamInput --region us-east-1
Nota: Mantén esta terminal abierta enviando datos durante todo el laboratorio.

3. Despliegue de la Aplicación Flink
Compilación: Navega al directorio del código Java (java-getting-started) y compila el proyecto:

Bash
mvn clean package
Carga: Sube el archivo .jar resultante (ubicado en la carpeta /target) a tu bucket de S3.

Creación de la App:

Ve a la consola de Amazon Managed Service for Apache Flink.

Selecciona Create streaming application.

Elige Apache Flink como motor.

En Code location, selecciona el bucket y el objeto .jar que acabas de subir.

4. Ejecución y Configuración
Configura las propiedades de ejecución (Runtime Properties) para conectar los streams:

En la configuración de la aplicación, añade un Group ID: FlinkAppProperties.

Añade los pares Key-Value:

InputStreamName: ClickstreamInput

OutputStreamName: ClickstreamOutput

Region: us-east-1

Asegúrate de que el Rol de IAM asociado tenga permisos de lectura/escritura en Kinesis y acceso al bucket S3.

Presiona Run para iniciar la aplicación.

5. Verificación de Resultados
Una vez que la aplicación pase al estado Running:

Revisa la pestaña Monitoring en la consola de Flink para verificar que hay métricas de BytesReceived y RecordsWritten.

Para inspeccionar los datos de salida, ejecuta el script consumidor:

Bash
python consumer.py --stream ClickstreamOutput --region us-east-1
Analiza la salida JSON. Busca el campo anomaly_score:

Valores cercanos a 0 indican tráfico normal.

Valores altos indican anomalías detectadas por el algoritmo RCF.

Limpieza de Recursos
Para evitar costos innecesarios, elimina los recursos en el siguiente orden al finalizar:

Detener la aplicación Flink (Stop Application).

Eliminar la aplicación Flink.

Eliminar los streams de Kinesis (ClickstreamInput, ClickstreamOutput).

Vaciar y eliminar el bucket de S3.

