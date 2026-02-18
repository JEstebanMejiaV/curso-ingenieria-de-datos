# Workshop: Pipeline de Streaming en Tiempo Real con Amazon MSK

## Objetivo

Construir una arquitectura de *streaming* robusta usando una **VPC personalizada**, con:

- **Amazon MSK (Apache Kafka gestionado)** en subredes privadas
- **EC2** como cliente Kafka en subred pública (para acceso por SSH)
- **AWS Lambda** dentro de la VPC consumiendo desde MSK
- **Amazon Kinesis Data Firehose** entregando a **Amazon S3**
- **(Opcional) Kinesis Data Analytics Studio (Apache Flink)** para analítica en tiempo real

La pieza clave del taller es la **salida a Internet desde subredes privadas** vía **NAT Gateway**, para que componentes como Lambda puedan invocar servicios administrados (por ejemplo Firehose, CloudWatch, Glue) sin exponer recursos a Internet.

---

## Duración estimada

- **Infraestructura (MSK provisionado):** 20 a 30 min de creación del clúster
- **Cliente + pruebas:** 20 a 40 min
- **Serverless + validación:** 20 a 40 min
- **Flink Studio (opcional):** 30 a 60 min

---

## Costos y advertencia

Este taller usa recursos con costo por hora:

- **MSK Cluster:** aprox. **USD 0.05 a 0.10 por hora** (según región, broker, almacenamiento).
- **NAT Gateway:** aprox. **USD 0.045 por hora** **más** tráfico.
- **EC2:** `t2.micro` (posible Free Tier) o `t3.micro`/`t3.small` según necesidad.

**IMPORTANTE:** Para evitar cobros sorpresa, al final:
- **borra el NAT Gateway**
- **libera la Elastic IP**
- luego limpia el resto (ver sección **Limpieza final**)

---

## Prerrequisitos

- Cuenta de AWS con permisos para crear VPC, MSK, EC2, Lambda, Firehose, S3.
- Acceso a consola AWS y a una terminal local con SSH.
- **Key Pair** (archivo `.pem`) para conectarte a EC2.
- Tu IP pública para permitir SSH (recomendado usar “My IP” en el Security Group).

---

## Convenciones del taller (nombres sugeridos)

| Recurso | Nombre sugerido |
|---|---|
| VPC | `msk-vpc` |
| Security Group unificado | `msk-seguridad-total` |
| MSK cluster | `mi-data-stream` |
| EC2 client | `kafka-client` |
| Topic Kafka | `sensor-data` |
| Bucket S3 | `msk-datalake-<tu-nombre>` |
| Firehose delivery stream | `msk-delivery-stream` |
| Lambda | `KafkaToFirehose` |

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

# Parte 1: Infraestructura de Red y MSK

## 1. Conceptos clave de red

### ¿Por qué subredes privadas?
Por seguridad. En una subred privada los recursos **no tienen IP pública**, por lo que **nadie desde Internet puede iniciar conexiones directas** hacia ellos. Esta es la zona típica para servicios backend, datos y procesamiento, como **MSK** y **Lambda**.

### ¿Qué es un NAT Gateway?
Un NAT Gateway permite que recursos **en subredes privadas** puedan **iniciar conexiones salientes** hacia Internet o hacia servicios públicos de AWS, sin permitir tráfico entrante desde Internet.

Sin NAT Gateway, una Lambda dentro de VPC puede quedarse sin salida y fallar al invocar servicios como Firehose, Glue o endpoints públicos, resultando en **timeouts**.

---

## 2. Paso 1: Crear VPC personalizada (VPC + NAT Gateway)

1) Ve a la consola de **VPC**  
2) Clic en **Create VPC** y selecciona **VPC and more**  
3) Configuración exacta:

- **Name tag:** `msk-vpc`
- **IPv4 CIDR:** `10.0.0.0/16`
- **Number of Availability Zones (AZs):** `2`
- **Number of public subnets:** `2`
- **Number of private subnets:** `2`
- **NAT gateways:** `1 in 1 AZ`
- **VPC endpoints:** `None`

4) Clic en **Create VPC**

Esto crea automáticamente:
- Internet Gateway para subredes públicas
- NAT Gateway para salida desde subredes privadas (con Elastic IP asociada)

---

## 3. Paso 2: Security Group “Espejo” (unificado)

Crearemos un solo Security Group para permitir comunicación interna entre EC2, MSK y Lambda.

1) Ve a **Security Groups**  
2) Clic en **Create security group**

- **Name:** `msk-seguridad-total`
- **Description:** Seguridad unificada para MSK, EC2 y Lambda
- **VPC:** selecciona `msk-vpc`

### Inbound rules

1) **SSH**
- Type: `SSH`
- Source: `My IP`

2) **Tráfico interno completo**
- Type: `All traffic`
- Source: `Custom`
- En la barra, selecciona el **ID del mismo Security Group** que estás creando (self-reference)

Esto habilita que los componentes dentro del SG se hablen sin bloqueos.

### Outbound rules
- Deja el default: `All traffic` hacia `0.0.0.0/0`

3) Clic en **Create**

---

## 4. Paso 3: Crear el clúster de MSK

1) Ve a la consola de **Amazon MSK**  
2) Clic en **Create cluster** y elige **Custom create**

Configuración:

- **Cluster name:** `mi-data-stream`
- **Cluster type:** `Provisioned`

### Brokers
- Type: `kafka.t3.small` (económico)
- Zones: `2`
- Brokers per zone: `1`

### Networking
- VPC: `msk-vpc`
- Subnets: selecciona **las 2 private subnets**
- Security groups: `msk-seguridad-total`

### Security (solo laboratorio)
- Access control: `Unauthenticated access`
- Encryption: `Plaintext`

3) Clic en **Create cluster**  
La creación puede tardar ~20 minutos.

**Nota de seguridad:** *Unauthenticated + Plaintext* es solo para laboratorio. En producción usa TLS, autenticación (IAM/SASL o SCRAM) y control de acceso.

---

## 5. Paso 4: Crear la máquina cliente (EC2)

1) Consola de **EC2**  
2) **Launch instance**

Configuración:

- **Name:** `kafka-client`
- **AMI:** Amazon Linux 2023
- **Instance type:** `t2.micro` o `t3.micro`
- **Key pair:** tu archivo `.pem`

### Network settings (Edit)
- VPC: `msk-vpc`
- Subnet: selecciona una **public subnet** (debe decir “Public” en el nombre)
- Auto-assign Public IP: `Enable`
- Security group: `msk-seguridad-total`

3) Lanza la instancia

---

# Parte 2: Configuración del Cliente y Scripts

## 6. Paso 5: Preparar la EC2

Conéctate por SSH usando la IP pública de la EC2:

```bash
ssh -i "tu-llave.pem" ec2-user@<IP_PUBLICA>
```

Actualiza e instala dependencias:

```bash
sudo dnf update -y
sudo dnf install java-17-amazon-corretto -y
sudo dnf install python3-pip -y

pip3 install kafka-python-ng boto3
```

Descarga Kafka (binarios) y extrae:

```bash
wget https://archive.apache.org/dist/kafka/3.5.1/kafka_2.12-3.5.1.tgz
tar -xzf kafka_2.12-3.5.1.tgz
```

---

## 7. Paso 6: Conexión y creación de topics

### 7.1 Obtener Bootstrap Servers
En MSK, ve a **Client information** y copia:

- **Bootstrap servers (Plaintext)**

Asegúrate de:
- usar el endpoint de **Kafka** (no Zookeeper)
- incluir puerto `:9092`
- no tener espacios

En EC2:

```bash
export BS="b-1.midatastream.xxxx.amazonaws.com:9092,b-2.midatastream.xxxx.amazonaws.com:9092"
```

### 7.2 Prueba rápida de conectividad
Usa `nc` para probar el puerto 9092 a un broker:

```bash
# Instala netcat si no está
sudo dnf install -y nc

# Prueba contra un broker
nc -zv b-1.midatastream.xxxx.amazonaws.com 9092
```

Si esto falla:
- revisa que EC2 esté en la VPC correcta
- revisa el Security Group “espejo”
- revisa que el clúster MSK esté en estado ACTIVE
- confirma que copiaste bootstrap servers correctos

### 7.3 Crear el topic `sensor-data`

```bash
cd ~/kafka_2.12-3.5.1/bin

./kafka-topics.sh --create --bootstrap-server "$BS"   --replication-factor 2 --partitions 2 --topic sensor-data
```

Verifica:

```bash
./kafka-topics.sh --list --bootstrap-server "$BS"
./kafka-topics.sh --describe --bootstrap-server "$BS" --topic sensor-data
```

---

## 8. Scripts de prueba: productor y consumidor (Python)

Crea un archivo `producer.py`:

```python
import json
import random
import time
from datetime import datetime

from kafka import KafkaProducer

BOOTSTRAP_SERVERS = ["YOUR_BS_HERE"]
TOPIC = "sensor-data"

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

sensor_ids = ["A-001", "A-002", "B-010", "C-777"]

try:
    while True:
        msg = {
            "ts": datetime.utcnow().isoformat(),
            "sensor_id": random.choice(sensor_ids),
            "temp_c": round(random.uniform(18.0, 35.0), 2),
            "status": "OK",
        }
        producer.send(TOPIC, msg)
        producer.flush()
        print("Sent:", msg)
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    producer.close()
```

Crea un archivo `consumer.py`:

```python
import json
from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = ["YOUR_BS_HERE"]
TOPIC = "sensor-data"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="workshop-consumer",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

try:
    for msg in consumer:
        print("Received:", msg.value)
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

Reemplaza `YOUR_BS_HERE` en ambos scripts por tu lista real.

Ejecuta en dos terminales:

- Terminal 1:
```bash
python3 consumer.py
```

- Terminal 2:
```bash
python3 producer.py
```

---

# Parte 3: Serverless Avanzado (Lambda + Firehose + S3)

Aquí el NAT Gateway es crítico: la Lambda está en subred privada y necesita salida para invocar Firehose.

## 9. Paso 7: Preparar destinos (S3 y Firehose)

### 9.1 S3
Crea un bucket:

- `msk-datalake-<tu-nombre>`

### 9.2 Firehose
Crea un delivery stream:

- Nombre: `msk-delivery-stream`
- Source: **Direct PUT**
- Destination: **S3**
- Bucket: tu bucket creado arriba

---

## 10. Paso 8: Lambda con acceso a Internet (vía NAT)

### 10.1 Crear función
- Nombre: `KafkaToFirehose`
- Runtime: **Python 3.11**

### 10.2 Permisos (IAM role)
Asigna un rol con políticas administradas:

- `AWSLambdaMSKExecutionRole`
- `AmazonKinesisFirehoseFullAccess`

(En un escenario real, lo ideal es una política mínima con `firehose:PutRecordBatch` solo para el stream específico.)

### 10.3 Configuración de VPC (clave)
En Lambda:

1) **Configuration**  
2) **VPC**  
3) **Edit**  
4) Selecciona:

- VPC: `msk-vpc`
- Subnets: **solo las private subnets**
- Security Group: `msk-seguridad-total`

### 10.4 Código Lambda

```python
import base64
import boto3

firehose = boto3.client("firehose")
DELIVERY_STREAM = "msk-delivery-stream"

def lambda_handler(event, context):
    records_map = event.get("records", {})
    batch_for_firehose = []

    for _, messages in records_map.items():
        for msg in messages:
            try:
                payload = base64.b64decode(msg["value"]).decode("utf-8")
                if not payload.endswith("\n"):
                    payload += "\n"
                batch_for_firehose.append({"Data": payload})
            except Exception as e:
                print(f"Error decodificando: {e}")

    if batch_for_firehose:
        firehose.put_record_batch(
            DeliveryStreamName=DELIVERY_STREAM,
            Records=batch_for_firehose,
        )
        print(f"Enviados {len(batch_for_firehose)} eventos a Firehose.")

    return {"statusCode": 200}
```

---

## 11. Paso 9: Activar el trigger (MSK)

En Lambda:

1) **Add trigger**
2) Elige **MSK**
3) Selecciona:
- tu clúster `mi-data-stream`
- topic `sensor-data`

Si la red está bien:
- el trigger debe pasar a **Enabled** en 1 a 2 minutos
- la Lambda empezará a recibir eventos

---

## 12. Validar entrega en S3

1) Ejecuta el `producer.py` desde EC2 durante 1 a 3 minutos  
2) En S3, en tu bucket, deberías ver objetos creados por Firehose

Opcional: descarga un archivo y verifica que el contenido sea JSON por línea.

---

# Parte 4 (Opcional): Analytics con Flink Studio (Kinesis Data Analytics Studio)

Objetivo: ejecutar analítica en tiempo real sobre el stream.

**Punto de red:** para conectarse a Glue/servicios administrados y mantener metadatos, el Notebook suele requerir conectividad similar a Lambda:
- subredes privadas
- NAT Gateway

## 13. Crear el Notebook

1) Ve a **Kinesis Data Analytics Studio**  
2) Crea un **Notebook** (Apache Flink)

## 14. Configuración de Networking (clave)

En **Configuration** del Notebook:

- VPC: `msk-vpc`
- Subnets: selecciona **private subnets**
- Security Group: `msk-seguridad-total`

## 15. SQL de ejemplo (Flink SQL)

Este ejemplo crea una tabla que lee desde Kafka (MSK) y hace una agregación simple.

> Nota: Los conectores disponibles varían por versión/entorno del Notebook. Ajusta propiedades según tu runtime.

```sql
CREATE TABLE sensor_stream (
  sensor_id STRING,
  temp_c DOUBLE,
  ts STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'sensor-data',
  'properties.bootstrap.servers' = '<TU_BS>',
  'properties.group.id' = 'flink-sql',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json'
);

SELECT
  sensor_id,
  AVG(temp_c) AS avg_temp
FROM sensor_stream
GROUP BY sensor_id;
```

---

# Troubleshooting (rápido)

## Timeouts desde EC2 hacia MSK
- Confirma que `BS` apunta a bootstrap servers **Plaintext** `:9092`
- Confirma que MSK está ACTIVE
- Revisa `nc -zv <broker> 9092`
- Revisa que EC2 está en la **misma VPC** que MSK
- Revisa que el Security Group tiene la regla de self-reference (All traffic desde el mismo SG)

## Trigger MSK en Lambda no se habilita
- Confirma que Lambda está en **private subnets**
- Confirma que existe **NAT Gateway** y que las subredes privadas tienen ruta a NAT
- Confirma que Lambda usa `msk-seguridad-total`
- Revisa logs de CloudWatch para errores de permisos o red

## Firehose no entrega a S3
- Revisa permisos del rol de Firehose
- Revisa el delivery stream (errores en Monitoring)
- Verifica que Lambda imprime “Enviados X eventos”
- Asegura que agregas salto de línea para facilidad de lectura (ya incluido)

---

# Limpieza final (Checklist anti-cobros)

Sigue este orden para evitar recursos huérfanos:

1) **Lambda**
- Borra el trigger de MSK
- Borra la función `KafkaToFirehose`

2) **Kinesis Data Analytics Studio** (si lo creaste)
- Detén y borra el Notebook

3) **NAT Gateway**
- VPC Console - NAT Gateways - borra el NAT (cobra por hora)

4) **Elastic IP**
- VPC Console - Elastic IPs - **Release** la IP asociada al NAT

5) **Firehose y S3**
- Borra `msk-delivery-stream`
- Vacía y borra el bucket `msk-datalake-<tu-nombre>`

6) **EC2**
- Termina la instancia `kafka-client`

7) **MSK**
- Borra el clúster `mi-data-stream`

8) **VPC**
- Finalmente borra `msk-vpc` (limpia subnets, route tables y SGs asociados)

---

## Resultado esperado

Al finalizar, deberías tener:

- Mensajes enviados desde EC2 a Kafka (MSK)
- Lambda consumiendo del topic `sensor-data`
- Firehose entregando a S3, con registros legibles (JSON por línea)
- (Opcional) consultas en Flink Studio sobre el stream
