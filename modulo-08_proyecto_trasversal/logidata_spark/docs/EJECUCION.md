# Guía de Ejecución - ETL KPIs LogiData

## Tabla de Contenidos
1. [Preparación del Entorno](#preparación-del-entorno)
2. [Ejecución Local](#ejecución-local)
3. [Ejecución en AWS Glue](#ejecución-en-aws-glue)
4. [Ejecución en EMR](#ejecución-en-emr)
5. [Modos de Ejecución](#modos-de-ejecución)
6. [Troubleshooting](#troubleshooting)

---

## Preparación del Entorno

### 1. Requisitos Previos

#### Software Necesario
```bash
# Python 3.8+
python --version

# Java 8 o 11 (requerido por Spark)
java -version

# AWS CLI (para S3)
aws --version
```

#### Instalación de Dependencias
```bash
# Clonar el repositorio
cd modulo-08_proyecto_trasversal/logidata_spark

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de AWS

#### Configurar Credenciales
```bash
# Opción 1: AWS CLI
aws configure
# Ingresar: Access Key ID, Secret Access Key, Region

# Opción 2: Variables de entorno
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Opción 3: Perfil específico
export AWS_PROFILE=logidata-dev
```

#### Verificar Acceso a S3
```bash
# Listar buckets
aws s3 ls

# Verificar acceso al bucket del proyecto
aws s3 ls s3://logidata-dev-raw/
```

### 3. Configuración del Proyecto

#### Variables de Entorno
```bash
# Crear archivo .env
cat > .env << EOF
SPARK_ENV=dev
AWS_PROFILE=logidata-dev
RUN_DATE=2025-01-15
EOF

# Cargar variables
source .env
```

---

## Ejecución Local

### Modo 1: Con Datos Locales (Desarrollo)

```bash
# Ejecutar con datos de muestra locales
python jobs/etl_kpis_delivery.py \
  --env dev \
  --run-date 2025-01-15 \
  --mode incremental \
  --input-local
```

**Ventajas**:
- No requiere acceso a S3
- Más rápido para desarrollo
- Ideal para pruebas

**Limitaciones**:
- Datos limitados
- No refleja volumen real

### Modo 2: Con Datos en S3

```bash
# Ejecutar con datos en S3
python jobs/etl_kpis_delivery.py \
  --env dev \
  --run-date 2025-01-15 \
  --mode incremental
```

**Ventajas**:
- Datos reales
- Prueba completa del flujo

**Requisitos**:
- Credenciales AWS configuradas
- Datos disponibles en S3

### Modo 3: Procesamiento Full

```bash
# Reprocesar todo el histórico
python jobs/etl_kpis_delivery.py \
  --env dev \
  --mode full
```

**Uso**: Cuando se cambia la lógica de KPIs y se necesita reprocesar todo.

### Modo 4: Backfill (Rango de Fechas)

```bash
# Reprocesar últimos 7 días
python jobs/etl_kpis_delivery.py \
  --env prod \
  --mode backfill \
  --start-date 2025-01-08 \
  --end-date 2025-01-15
```

**Uso**: Recuperar datos faltantes o corregir errores en un período.

---

## Ejecución en AWS Glue

### 1. Preparación

#### Subir Código a S3
```bash
# Crear bucket para código
aws s3 mb s3://logidata-code

# Subir job principal
aws s3 cp jobs/etl_kpis_delivery.py s3://logidata-code/jobs/

# Subir módulos
aws s3 sync src/ s3://logidata-code/src/
aws s3 sync quality/ s3://logidata-code/quality/

# Subir configuración
aws s3 cp config/prod.yaml s3://logidata-code/config/
```

#### Crear Rol IAM
```bash
# Crear rol con políticas necesarias
aws iam create-role \
  --role-name LogiDataGlueRole \
  --assume-role-policy-document file://trust-policy.json

# Adjuntar políticas
aws iam attach-role-policy \
  --role-name LogiDataGlueRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole

aws iam attach-role-policy \
  --role-name LogiDataGlueRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### 2. Crear Job en Glue

```bash
# Crear job
aws glue create-job \
  --name logidata-kpis-etl \
  --role LogiDataGlueRole \
  --command '{
    "Name": "glueetl",
    "ScriptLocation": "s3://logidata-code/jobs/etl_kpis_delivery.py",
    "PythonVersion": "3"
  }' \
  --default-arguments '{
    "--extra-py-files": "s3://logidata-code/src.zip,s3://logidata-code/quality.zip",
    "--additional-python-modules": "pyyaml==6.0",
    "--TempDir": "s3://logidata-temp/",
    "--enable-metrics": "",
    "--enable-continuous-cloudwatch-log": "true"
  }' \
  --max-capacity 10 \
  --timeout 120
```

### 3. Ejecutar Job

```bash
# Ejecución manual
aws glue start-job-run \
  --job-name logidata-kpis-etl \
  --arguments '{
    "--env": "prod",
    "--run-date": "2025-01-15",
    "--mode": "incremental"
  }'

# Obtener estado
aws glue get-job-run \
  --job-name logidata-kpis-etl \
  --run-id jr_xxxxxxxxxxxxx
```

### 4. Programar Ejecución

```bash
# Crear trigger diario (ejecuta a las 2 AM UTC)
aws glue create-trigger \
  --name logidata-kpis-daily \
  --type SCHEDULED \
  --schedule "cron(0 2 * * ? *)" \
  --actions JobName=logidata-kpis-etl,Arguments='{"--env":"prod","--mode":"incremental"}' \
  --start-on-creation
```

---

## Ejecución en EMR

### 1. Crear Cluster EMR

```bash
# Crear cluster
aws emr create-cluster \
  --name "LogiData ETL Cluster" \
  --release-label emr-6.10.0 \
  --applications Name=Spark \
  --ec2-attributes KeyName=my-key,SubnetId=subnet-xxxxx \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles \
  --log-uri s3://logidata-logs/emr/
```

### 2. Subir Código

```bash
# Empaquetar código
zip -r logidata_spark.zip src/ quality/ config/

# Subir a S3
aws s3 cp logidata_spark.zip s3://logidata-code/
aws s3 cp jobs/etl_kpis_delivery.py s3://logidata-code/jobs/
```

### 3. Ejecutar Job

```bash
# Agregar step al cluster
aws emr add-steps \
  --cluster-id j-XXXXXXXXXXXXX \
  --steps Type=Spark,Name="LogiData KPIs ETL",\
ActionOnFailure=CONTINUE,\
Args=[--deploy-mode,cluster,\
--master,yarn,\
--conf,spark.sql.shuffle.partitions=200,\
--py-files,s3://logidata-code/logidata_spark.zip,\
s3://logidata-code/jobs/etl_kpis_delivery.py,\
--env,prod,\
--run-date,2025-01-15,\
--mode,incremental]

# Verificar estado
aws emr describe-step \
  --cluster-id j-XXXXXXXXXXXXX \
  --step-id s-XXXXXXXXXXXXX
```

---

## Modos de Ejecución

### Incremental (Recomendado)

**Cuándo usar**: Ejecución diaria normal

**Características**:
- Procesa solo la fecha especificada
- Sobrescribe la partición correspondiente
- Más rápido y eficiente

**Ejemplo**:
```bash
python jobs/etl_kpis_delivery.py \
  --env prod \
  --run-date 2025-01-15 \
  --mode incremental
```

### Full

**Cuándo usar**: 
- Primera carga
- Cambios en lógica de KPIs
- Correcciones masivas

**Características**:
- Reprocesa todo el histórico
- Más lento y costoso
- Sobrescribe todas las particiones

**Ejemplo**:
```bash
python jobs/etl_kpis_delivery.py \
  --env prod \
  --mode full
```

### Backfill

**Cuándo usar**:
- Recuperar datos faltantes
- Corregir errores en un período
- Reprocesar después de fix

**Características**:
- Procesa rango de fechas
- Ejecuta incremental por cada fecha
- Permite recuperación selectiva

**Ejemplo**:
```bash
python jobs/etl_kpis_delivery.py \
  --env prod \
  --mode backfill \
  --start-date 2025-01-01 \
  --end-date 2025-01-15
```

---

## Troubleshooting

### Error: "Partition not found"

**Causa**: No existen datos para la fecha especificada

**Solución**:
```bash
# Verificar particiones disponibles
aws s3 ls s3://logidata-prod-raw/pedidos/ --recursive | grep event_date

# Ajustar fecha de ejecución
python jobs/etl_kpis_delivery.py --run-date 2025-01-14
```

### Error: "Schema mismatch"

**Causa**: Cambio en estructura de datos de entrada

**Solución**:
1. Verificar diccionario de datos
2. Actualizar schemas en `readers.py`
3. Ejecutar con datos de muestra para validar

### Error: "Out of Memory"

**Causa**: Volumen de datos muy grande

**Solución**:
```python
# Ajustar configuración de Spark
spark.conf.set("spark.sql.shuffle.partitions", "400")
spark.conf.set("spark.executor.memory", "16g")
```

### Performance Lento

**Diagnóstico**:
```bash
# Ver logs de Spark
tail -f logs/etl_kpis.log

# Verificar métricas en Spark UI
# http://localhost:4040
```

**Optimizaciones**:
1. Aumentar `spark.sql.shuffle.partitions`
2. Habilitar broadcast joins para tablas pequeñas
3. Usar cache para DataFrames reutilizados
4. Particionar datos de entrada

### Error: "AWS Credentials not found"

**Solución**:
```bash
# Verificar configuración
aws configure list

# Verificar variables de entorno
echo $AWS_ACCESS_KEY_ID
echo $AWS_PROFILE

# Reconfigurar
aws configure --profile logidata-prod
```

---

## Monitoreo

### Logs

```bash
# Ver logs locales
tail -f logs/etl_kpis.log

# Ver logs en CloudWatch (Glue)
aws logs tail /aws-glue/jobs/logidata-kpis-etl --follow

# Ver logs en S3 (EMR)
aws s3 ls s3://logidata-logs/emr/j-XXXXX/steps/
```

### Métricas

```bash
# Verificar outputs generados
aws s3 ls s3://logidata-prod-mart/kpis_delivery_daily/event_date=2025-01-15/

# Contar registros
aws athena start-query-execution \
  --query-string "SELECT COUNT(*) FROM mart.kpis_delivery_daily WHERE event_date='2025-01-15'"
```

---

## Próximos Pasos

1. **Integración con Airflow**: Automatizar ejecución diaria
2. **Great Expectations**: Agregar validaciones de calidad
3. **Alertas**: Configurar notificaciones en CloudWatch
4. **Dashboard**: Visualizar KPIs en QuickSight
5. **Optimización**: Tuning de performance para producción
