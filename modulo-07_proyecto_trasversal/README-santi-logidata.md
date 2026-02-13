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


## Arquitectura AWS - LogiData S.A.S.

```mermaid
flowchart TB
    subgraph GOBIERNO["Capa de Gobierno y Orquestación (DataOps)"]
        SF[("AWS Step Functions<br/>Orquestación Workflows<br/>• DAGs programados<br/>• Dependencias ETL<br/>• Monitoreo pipelines")]
        GC[("AWS Glue Catalog<br/>Metadatos & Esquemas<br/>• Tablas automáticas<br/>• Particiones S3<br/>• Lineage de datos")]
        LF[("AWS Lake Formation<br/>Gobernanza & Seguridad<br/>• Control de acceso<br/>• Políticas de datos<br/>• Catalogación unificada")]
    end

    subgraph DATALAKE["Data Lake S3"]
        direction TB
        S3[(("Amazon S3<br/>Data Lake"))]
        RAW["Raw Zone<br/>(CSV crudos)"]
        CURATED["Curated Zone<br/>(datos limpios)"]
        ANALYTICS["Analytics Zone<br/>(consumo BI)"]
    end

    subgraph FUENTES["Fuentes de Datos"]
        CSV["Fuentes CSV<br/>(AceleraTI)<br/>• clientes.csv<br/>• pedidos.csv<br/>• entregas.csv<br/>• sensores.csv<br/>• catalogo.csv"]
        RDS[("Amazon RDS<br/>PostgreSQL")]
        DYNAMO[("Amazon DynamoDB<br/>Sensores IoT")]
    end

    subgraph PROCESAMIENTO["Procesamiento"]
        GLUE["AWS Glue<br/>PySpark ETL<br/>• Limpieza<br/>• Transformaciones<br/>• KPIs batch"]
        KINESIS["Amazon Kinesis<br/>Data Streams<br/>• Sensores IoT<br/>• Tiempo real<br/>• Anomalías temperatura"]
    end

    subgraph CONSUMO["Consumo Analítico"]
        REDSHIFT[("Amazon Redshift<br/>Data Warehouse<br/>• Modelo estrella<br/>• Fact_Entregas<br/>• Dimensiones: Tiempo, Zona, Cliente")]
        QS["Amazon QuickSight<br/>Dashboards & KPIs<br/>• Cumplimiento entregas<br/>• Tiempos por zona<br/>• Anomalías temperatura"]
    end

    %% Flujos de datos principales
    CSV --> RAW
    RDS --> RAW
    DYNAMO --> RAW
    
    RAW --> GLUE
    RAW --> KINESIS
    
    GLUE --> CURATED
    KINESIS --> ANALYTICS
    
    CURATED --> REDSHIFT
    REDSHIFT --> QS
    
    %% Gobierno y orquestación (líneas punteadas)
    SF -.-> GLUE
    SF -.-> KINESIS
    GC -.-> S3
    GC -.-> GLUE
    LF -.-> S3
    
    %% Estilos
    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef storage fill:#3F8624,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef database fill:#2E27AD,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef analytics fill:#E73585,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef governance fill:#9B59B6,stroke:#232F3E,stroke-width:2px,color:#fff
    
    class S3 storage
    class RDS,DYNAMO,REDSHIFT database
    class GLUE,KINESIS,QS analytics
    class GC,LF,SF governance
