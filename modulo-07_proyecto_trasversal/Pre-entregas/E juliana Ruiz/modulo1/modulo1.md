## **HU1: Arquitectura de una Plataforma Moderna**

> **\"Como ingeniero de datos, quiero comprender la arquitectura de una
> plataforma de datos moderna para estructurar la solución de
> LogiData.\"**

### [**[Diagrama de Arquitectura General]{.underline}**](https://drive.google.com/file/d/14CW2ryk5ZomgpJgNMGr-O28Tea5Cilnx/view?usp=sharing)

Para LogiData, la arquitectura sigue el patrón de **Arquitectura de
Medallón** integrada con flujos de **Streaming** y **Batch**.

**Flujo General:**

1.  **Entrada:** Los archivos CSV (Pedidos, Clientes, Catálogo) y los
    eventos de sensores IoT entran al ecosistema.

2.  **Tratamiento:** Los datos pasan de un estado \"sucio\" (**Raw**) a
    uno \"limpio\" (**Silver**) y finalmente \"listivo para negocio\"
    (**Gold**).

3.  **Transversalidad:** El monitoreo, la seguridad y la calidad
    envuelven todo el proceso para asegurar que el dato sea confiable.

## **HU2: Definición de Servicios AWS**

> **\"Como ingeniero, quiero definir los servicios AWS que usaré en la
> plataforma.\"**

###  **Documento Técnico Base: Componentes y Flujo.**

### **1. Ingesta y Almacenamiento**

- **Amazon S3:** Actuará como **Data Lake**. Se usara buckets para
  separar las capas (Bronze/Silver/Gold).

- [**Amazon Kinesis Data Firehose:** Para capturar los eventos de los
  sensores en tiempo real y depositarlos automáticamente en S3 sin
  gestionar servidores.]{.mark}

#### **2. Procesamiento** 

- **AWS Glue (ETL Jobs):** Utilizaremos **PySpark** para las
  transformaciones Batch pesadas.

- **AWS Lambda:** Para el procesamiento \"micro\" y rápido de los
  sensores. Si un sensor reporta una temperatura critica, la Lambda
  reacciona al instante.

#### **3. Catalogación y Consulta** 

- **AWS Glue Data Catalog:** El inventario central de metadatos.

- **Amazon Athena:** Para que el equipo de datos pueda hacer consultas
  SQL sobre S3 y presentar informes.

#### **4. Orquestación y Gobernanza** 

- [**Apache Airflow (en Amazon ECS/Fargate):** programará los Glue Jobs
  y validará que cada paso se cumpla en el orden correcto.]{.mark}

- **AWS IAM:** Aplicación de políticas de \"Privilegio Mínimo\" para que
  cada servicio solo acceda a lo que le corresponde.

#### **5. Calidad y Monitoreo** 

- [**AWS Glue Data Quality:** Para definir las \"Expectativas\" (ej. el
  monto de un pedido no puede ser negativo).]{.mark}

- [**Amazon CloudWatch:** Centralización de logs y alarmas para saber si
  un proceso falló antes de que el cliente se queje.]{.mark}
