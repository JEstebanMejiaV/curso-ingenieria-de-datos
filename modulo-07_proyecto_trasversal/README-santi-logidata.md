\# LogiData S.A.S. - Proyecto de Ingeniería de Datos



\*\*Estudiante:\*\* Santiago (Santi)  

\*\*Repositorio:\*\* curso-ingenieria-de-datos  

\*\*Rama de trabajo:\*\* feature/santi-proyecto-logidata



\## Descripción

Plataforma moderna de datos en AWS para LogiData S.A.S., empresa colombiana de logística inteligente. Integra flujos batch y streaming, aplicando principios de gobernanza, automatización y calidad de datos.



\## Estructura del Proyecto

docs/               # Documentación de arquitectura y modelos

src/                # Código fuente

├── ingest/       # Módulo 3: Carga inicial al Data Lake

├── processing/   # Módulo 4: ETL con PySpark

├── streaming/    # Módulo 5: Procesamiento en tiempo real

├── airflow\_dags/ # Módulo 6: Orquestación con Airflow

└── tests/        # Validaciones y pruebas

terraform/          # Módulo 8: Infraestructura como código

dashboards/         # Módulo 8: Configuraciones QuickSight



\## Módulos del Proyecto

\- \[ ] \*\*Módulo 1:\*\* Arquitectura AWS y servicios

\- \[ ] \*\*Módulo 2:\*\* Bases de Datos (PostgreSQL + DynamoDB)

\- \[ ] \*\*Módulo 3:\*\* Data Lake (S3 + Glue Catalog)

\- \[ ] \*\*Módulo 4:\*\* Procesamiento Batch (PySpark)

\- \[ ] \*\*Módulo 5:\*\* Procesamiento Streaming (Kinesis)

\- \[ ] \*\*Módulo 6:\*\* DataOps (Airflow + Great Expectations)

\- \[ ] \*\*Módulo 7:\*\* Data Warehouse (Modelo Dimensional)

\- \[ ] \*\*Módulo 8:\*\* DevOps + Dashboards (Terraform + QuickSight)



\## Datos

Los archivos CSV proporcionados por AceleraTI (`clientes.csv`, `pedidos.csv`, `entregas.csv`, `sensores.csv`, `catalogo.csv`, `diccionario\_datos.csv`) se encuentran en la carpeta `data/` local, ignorada por Git por seguridad y tamaño.

