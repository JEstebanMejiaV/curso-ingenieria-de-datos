# Workshop: Pipeline de Streaming en Tiempo Real con Amazon MSK

## Objetivo
Crear un clúster de Apache Kafka gestionado (Amazon MSK), configurar una máquina cliente (EC2) y desarrollar scripts en Python para producir y consumir datos simulados en tiempo real.


## Costos y advertencia
Este taller usa recursos que no siempre son gratuitos (MSK, y opcionalmente Flink Studio/Analytics). El costo por una sesión corta suele ser bajo, pero **es crítico borrar todos los recursos al finalizar** (ver sección “Limpieza final”).

---

## Prerrequisitos
- Cuenta de AWS activa
- Conocimientos básicos de la consola de AWS
- Key Pair (.pem) creada en EC2 para conectarte por SSH
- Permisos para crear y borrar: VPC/Security Groups, MSK, EC2, S3, Firehose, Lambda, Kinesis Analytics (Studio), IAM roles/policies (o permisos para adjuntarlas)

---

## Arquitectura lógica

Componentes y ubicación:

- **Subred pública**
  - EC2 (cliente Kafka) con IP pública para SSH
- **Subredes privadas**
  - Brokers de MSK
  - Lambda (con ENIs en la VPC)
  - (Opcional) Flink Studio con *Networking* en VPC

Conectividad de salida:
- Subredes privadas salen a Internet a través del **NAT Gateway** (ubicado en una subred pública).
- Esto permite que **Lambda** y **Flink Studio** llamen APIs de AWS (por ejemplo Firehose, CloudWatch, Glue).

---

# Parte 1: MSK + EC2 + Python Producer/Consumer

## Conceptos clave de red

### ¿Por qué subredes privadas?
Por seguridad. En una subred privada los recursos **no tienen IP pública**, por lo que **nadie desde Internet puede iniciar conexiones directas** hacia ellos. Esta es la zona típica para servicios backend, datos y procesamiento, como **MSK** y **Lambda**.

### ¿Qué es un NAT Gateway?
Un NAT Gateway permite que recursos **en subredes privadas** puedan **iniciar conexiones salientes** hacia Internet o hacia servicios públicos de AWS, sin permitir tráfico entrante desde Internet.

Sin NAT Gateway, una Lambda dentro de VPC puede quedarse sin salida y fallar al invocar servicios como Firehose, Glue o endpoints públicos, resultando en **timeouts**.

---

## Paso 1: Configuración de red y seguridad
Para que Kafka funcione, el productor y consumidor deben poder comunicarse con el clúster.

1) Ve a la consola de **VPC**.  
2) Usaremos la **VPC por defecto** para este taller.  
3) Ve a **Security Groups** y selecciona **Create security group**:
- **Name**: `msk-workshop-sg`
- **Description**: Permitir tráfico Kafka para el workshop
- **VPC**: tu VPC por defecto

4) **Inbound rules**:
- **Type**: `All traffic` (solo para simplificar el workshop)
- **Source**: el mismo Security Group que estás creando (Self reference)
  - En la UI suele aparecer como “Custom” y luego eliges el SG `msk-workshop-sg` o su ID.

5) Clic en **Create**.

**Nota (producción):** abrirías únicamente los puertos necesarios (por ejemplo 9092/9094/9098 según el modo de conexión) y restringirías el origen (CIDR o SGs específicos).

---

## Paso 2: Crear el clúster de MSK
1) Ve a la consola de **Amazon MSK**  
2) Clic en **Create cluster**  
3) Selecciona **Custom create** (para controlar costos)

Configuración sugerida (económica para el workshop):
- **Cluster name**: `mi-data-stream`
- **Cluster type**: `Provisioned`
- **Apache Kafka version**: recomendada por AWS (por ejemplo 3.5.1 o superior)
- **Brokers**
  - **Broker type**: `kafka.t3.small`
  - **Number of zones**: `2`
  - **Brokers per zone**: `1`
  - **Storage**: `10 GiB` por broker (mínimo)
- **Configuration**: Default
- **Networking**
  - **VPC**: la VPC por defecto
  - **Subnets**: selecciona 2 subnets diferentes
  - **Security groups**: `msk-workshop-sg`
- **Security**
  - **Access control methods**: habilita `Unauthenticated access` (solo para el workshop)
  - **Encryption**: `Plaintext` dentro del clúster

4) Clic en **Create cluster**

Espera a que el clúster pase a estado **Active**.

---

## Paso 3: Configurar la máquina cliente (EC2)
Mientras se crea el clúster, prepara una instancia EC2 para actuar como productor y consumidor.

1) Ve a la consola de **EC2**  
2) **Launch instance**:
- **Name**: `kafka-client`
- **AMI**: Amazon Linux 2023
- **Instance type**: `t2.micro` (free tier eligible, si aplica)
- **Key pair**: selecciona tu `.pem`
- **Network settings**
  - **VPC**: la misma del clúster MSK
  - **Security group**: `msk-workshop-sg`

3) Lanza la instancia y conéctate por SSH:

```bash
ssh -i "tu-llave.pem" ec2-user@<IP_PUBLICA_DE_TU_EC2>
```

4) Instala dependencias en la EC2 (ejecuta uno por uno):

```bash
# Actualizar sistema
sudo dnf update -y

# Instalar Java (requisito para herramientas Kafka)
sudo dnf install java-17-amazon-corretto -y

# Instalar Python y Pip
sudo dnf install python3-pip -y

# Librería Kafka para Python
pip3 install kafka-python-ng

# Descargar herramientas de Apache Kafka para crear topics
wget https://archive.apache.org/dist/kafka/3.5.1/kafka_2.12-3.5.1.tgz
tar -xzf kafka_2.12-3.5.1.tgz
```

---

## Paso 4: Obtener bootstrap servers y crear topics
Cuando el clúster MSK esté **Active**:

1) En MSK, entra a tu clúster `mi-data-stream`  
2) Clic en **View client information**  
3) Copia el valor bajo **Plaintext (Bootstrap servers)**. Se verá similar a:

```
b-1.midatastream.xxxxx.c2.kafka.us-east-1.amazonaws.com:9092,b-2.midatastream.xxxxx.c2.kafka.us-east-1.amazonaws.com:9092
```

4) En tu EC2 (SSH), guarda la cadena en una variable de entorno:

```bash
export BS="<PEGA_AQUI_TUS_BOOTSTRAP_SERVERS>"
# Ejemplo:
# export BS="b-1.xxxx:9092,b-2.xxxx:9092"
```

### 4.1 Crear topic `sensor-data`
```bash
cd ~/kafka_2.12-3.5.1/bin

./kafka-topics.sh --create --bootstrap-server "$BS" \
  --replication-factor 2 --partitions 2 --topic sensor-data
```

Si no hay error, el topic quedó creado.

---

## Paso 5: Ingeniería de datos (Python)
Crearemos dos scripts en tu carpeta home (`cd ~`). Los scripts leen la cadena de conexión desde la variable `BS`.

### 5.A Productor `producer.py`
Crea el archivo:

```bash
cd ~
nano producer.py
```

Pega el siguiente contenido:

```python
import json
import os
import time
import random
from kafka import KafkaProducer

TOPIC_NAME = "sensor-data"

def get_bootstrap_servers() -> list[str]:
    bs = os.getenv("BS", "").strip()
    if not bs:
        raise SystemExit("ERROR: Define la variable de entorno BS con tus bootstrap servers.")
    return [x.strip() for x in bs.split(",") if x.strip()]

def json_serializer(data: dict) -> bytes:
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(
    bootstrap_servers=get_bootstrap_servers(),
    value_serializer=json_serializer,
)

print("Iniciando simulador de sensor (Ctrl+C para detener)")

try:
    while True:
        data = {
            "sensor_id": random.randint(1, 5),
            "temperature": round(random.uniform(20.0, 35.0), 2),
            "humidity": random.randint(30, 80),
            "timestamp": time.time(),
        }

        producer.send(TOPIC_NAME, data)
        print(f"Enviado: {data}")

        time.sleep(1)
except KeyboardInterrupt:
    print("Deteniendo productor.")
finally:
    producer.close()
```

Guarda y sal.

---

### 5.B Consumidor `consumer.py`
Crea el archivo:

```bash
cd ~
nano consumer.py
```

Pega el siguiente contenido:

```python
import json
import os
from kafka import KafkaConsumer

TOPIC_NAME = "sensor-data"

def get_bootstrap_servers() -> list[str]:
    bs = os.getenv("BS", "").strip()
    if not bs:
        raise SystemExit("ERROR: Define la variable de entorno BS con tus bootstrap servers.")
    return [x.strip() for x in bs.split(",") if x.strip()]

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=get_bootstrap_servers(),
    auto_offset_reset="earliest",
    group_id="monitor-group-1",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

print("Escuchando datos del sensor (Ctrl+C para detener)")

for message in consumer:
    datos = message.value

    # lógica simple de procesamiento
    if datos.get("temperature", 0) > 30.0:
        alert = "ALERTA: alta temperatura"
    else:
        alert = "Normal"

    print(f"Sensor {datos.get('sensor_id')}: {datos.get('temperature')}°C - {alert}")
```

---

## Paso 6: Ejecución
Lo ideal es abrir **dos terminales** conectadas a la misma EC2 (duplica tu sesión SSH).

Terminal 1 (consumidor):
```bash
python3 consumer.py
```

Terminal 2 (productor):
```bash
python3 producer.py
```

Resultado esperado:
- En la Terminal 2 verás mensajes “Enviado: {...}”
- En la Terminal 1 verás los datos llegando en tiempo real y la evaluación simple de alerta

---

# Parte 2: Persistencia serverless en S3 y analytics con Flink

## Prerrequisitos (continuación)
- Clúster MSK activo
- Instancia EC2 `kafka-client` activa
- Variable `BS` configurada en la EC2

---

## Paso 1: Generador de clickstream (nuevo productor)
1) Conéctate a tu EC2 por SSH  
2) Instala `boto3` (lo usaremos más adelante):

```bash
pip3 install boto3
```

### 1.1 Crear topic `clickstream`
```bash
cd ~/kafka_2.12-3.5.1/bin

./kafka-topics.sh --create --bootstrap-server "$BS" \
  --replication-factor 2 --partitions 2 --topic clickstream
```

### 1.2 Script `clickstream_producer.py`
Crea el archivo:

```bash
cd ~
nano clickstream_producer.py
```

Pega el siguiente contenido:

```python
import json
import os
import time
import random
from kafka import KafkaProducer

TOPIC_NAME = "clickstream"

def get_bootstrap_servers() -> list[str]:
    bs = os.getenv("BS", "").strip()
    if not bs:
        raise SystemExit("ERROR: Define la variable de entorno BS con tus bootstrap servers.")
    return [x.strip() for x in bs.split(",") if x.strip()]

def json_serializer(data: dict) -> bytes:
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(
    bootstrap_servers=get_bootstrap_servers(),
    value_serializer=json_serializer,
)

urls = ["/home", "/products/shoes", "/products/hats", "/cart", "/checkout", "/login"]
browsers = ["Chrome", "Firefox", "Safari", "Edge"]

print("Iniciando simulación de Clickstream (Ctrl+C para detener)")

try:
    while True:
        data = {
            "user_id": f"user_{random.randint(1, 100)}",
            "url": random.choice(urls),
            "browser": random.choice(browsers),
            "response_time_ms": random.randint(20, 500),
            "status": random.choices([200, 404, 500], weights=[90, 5, 5])[0],
            "ts": int(time.time()),
        }

        producer.send(TOPIC_NAME, data)
        print(f"Click: {data['user_id']} - {data['url']}")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Deteniendo productor.")
finally:
    producer.close()
```

Ejecuta el productor:
```bash
python3 clickstream_producer.py
```

Déjalo corriendo en una terminal.

---

## Paso 2: Data Lake serverless (MSK - Lambda - Firehose - S3)
Este patrón persiste mensajes de Kafka en S3 sin administrar servidores para consumidores.

### 2.1 Crear bucket S3 y Firehose
1) **S3**: crea un bucket (nombre único global), por ejemplo:
- `msk-datalake-<tu-nombre>-workshop`

2) **Amazon Data Firehose**:
- Clic en **Create Firehose stream**
- **Source**: `Direct PUT`
- **Destination**: `Amazon S3`
- **Stream name**: `msk-delivery-stream`
- **Destination settings**: selecciona tu bucket S3
- Clic en **Create**

---

### 2.2 Crear la función Lambda
La Lambda actuará como puente. Leerá de MSK y escribirá en Firehose.

1) Ve a **Lambda** y crea una función:
- **Name**: `KafkaToFirehose`
- **Runtime**: `Python 3.11`
- **Role**: crea un rol nuevo con permisos básicos de Lambda

2) Permisos del rol:
- Adjunta `AWSLambdaMSKExecutionRole` (lectura desde MSK)
- Adjunta `AmazonKinesisFirehoseFullAccess` (escritura en Firehose)

3) Networking (crítico):
- Configura la Lambda en la **misma VPC**, **subnets** y **security group** que el MSK para que pueda conectarse al clúster.

---

### 2.3 Código de la Lambda
En la pestaña **Code**, pega este código y ajusta el nombre del Delivery Stream si cambiaste el valor:

```python
import base64
import boto3

firehose = boto3.client("firehose")
DELIVERY_STREAM = "msk-delivery-stream"

def lambda_handler(event, context):
    # Kafka envía eventos en lotes (batches)
    records_map = event.get("records", {})
    batch_for_firehose = []

    # Iterar sobre particiones y mensajes
    for _, messages in records_map.items():
        for msg in messages:
            # MSK envía el payload en base64
            payload = base64.b64decode(msg["value"]).decode("utf-8")

            # Firehose a S3 suele escribir mejor con delimitador por línea
            batch_for_firehose.append({"Data": payload + "\n"})

    if batch_for_firehose:
        firehose.put_record_batch(
            DeliveryStreamName=DELIVERY_STREAM,
            Records=batch_for_firehose,
        )
        print(f"Enviados {len(batch_for_firehose)} eventos a S3 vía Firehose")

    return {"statusCode": 200}
```

Clic en **Deploy**.

---

### 2.4 Activar el trigger de MSK en Lambda
1) En la Lambda, **Add trigger**  
2) Selecciona **MSK**  
3) Elige tu clúster  
4) **Topic name**: `clickstream`  
5) **Starting position**: `Latest`  
6) Clic en **Add**

El trigger puede tardar unos minutos en quedar **Enabled**.

**Prueba:**
- Con el `clickstream_producer.py` corriendo, revisa el bucket S3 en 1 a 2 minutos
- Deberías ver prefijos por fecha (año/mes/día) y archivos con JSON por línea

---

## Paso 3: Analytics en tiempo real con Amazon Managed Flink (Studio)
Objetivo: detectar anomalías o incrementos de errores (404/500) por URL en ventanas de tiempo.

1) Ve a **Amazon Kinesis**  
2) **Analytics applications** y luego **Studio**  
3) **Create Studio notebook**:
- **Name**: `ClickstreamAnalytics`
- **Permissions**: crea un rol nuevo
- **Glue Database**: crea una nueva llamada `msk_analytics`
- Clic en **Create**

4) Entra al notebook y abre **Configuration**
- **Networking**: selecciona la **misma VPC**, **subnets** y **security group** del MSK
- Clic en **Update**

5) Clic en **Run** (puede tardar varios minutos)  
6) Clic en **Open in Apache Zeppelin**

### 3.1 Zeppelin: Flink SQL (3 párrafos)
#### Párrafo 1: Conexión a Kafka (DDL)
Reemplaza `properties.bootstrap.servers` con tu cadena real.

```sql
%flink.ssql

CREATE TABLE clickstream_raw (
    user_id STRING,
    url STRING,
    browser STRING,
    response_time_ms INT,
    status INT,
    ts BIGINT,
    proc_time AS PROCTIME()
) WITH (
    'connector' = 'kafka',
    'topic' = 'clickstream',
    'properties.bootstrap.servers' = 'b-1.xxxxx:9092,b-2.xxxxx:9092',
    'properties.group.id' = 'flink-group',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'json'
);
```

#### Párrafo 2: Consulta simple
```sql
%flink.ssql(type=update)
SELECT * FROM clickstream_raw;
```

#### Párrafo 3: Agregación por ventana
Conteo de errores (status >= 400) por URL cada 10 segundos.

```sql
%flink.ssql(type=update)

SELECT
    url,
    COUNT(*) AS error_count,
    TUMBLE_END(proc_time, INTERVAL '10' SECOND) AS window_end
FROM clickstream_raw
WHERE status >= 400
GROUP BY
    url,
    TUMBLE(proc_time, INTERVAL '10' SECOND);
```

---

# Limpieza final (extremadamente importante)
Para evitar cargos innecesarios, elimina recursos en este orden sugerido:

1) Kinesis Analytics (Studio)
- Detén y borra el Notebook / aplicación

2) Firehose
- Borra el Delivery Stream `msk-delivery-stream`

3) S3
- Vacía y borra el bucket del workshop

4) Lambda
- Borra la función `KafkaToFirehose` (y revisa roles/policies si deseas limpiar IAM)

5) EC2
- Termina la instancia `kafka-client`

6) MSK
- Borra el clúster `mi-data-stream`

---

## Notas finales
- La regla “All traffic” en el Security Group se usa solo para simplificar el workshop. No es un patrón recomendado en producción.
- Si encuentras errores de conexión, valida que MSK, EC2, Lambda y Flink estén en la misma VPC y subnets compatibles, y que el Security Group permita el tráfico necesario.
