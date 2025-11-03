# 🚀 Ingeniería de Datos – AceleraTI 2025

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-Data%20Engineering-orange.svg)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4.svg)](https://www.terraform.io/)
[![Airflow](https://img.shields.io/badge/Orchestration-Apache%20Airflow-lightblue.svg)](https://airflow.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Repositorio oficial del curso **Ingeniería de Datos – AceleraTI 2025**, diseñado para formar profesionales capaces de diseñar, automatizar y escalar soluciones modernas de datos en la nube con foco en pipelines distribuidos, modelado, gobernanza y operaciones de datos.  
📄 [Programa oficial del curso (PDF)](https://acelerati.co/hubfs/TRI%20-%202025/Programa/AceleraTI%20-%20Programa%20Ingenier%C3%ADa%20de%20datos.pdf?hsLang=es-co)

---

## 🎯 Objetivo

Desarrollar las habilidades técnicas y prácticas para construir **arquitecturas de datos escalables**, seguras y confiables en la nube, comprendiendo el ciclo completo de un pipeline moderno: desde la ingesta hasta la visualización y automatización en producción.


---

## 🧩 Estructura del curso

Duración: **160 horas (4.5 meses)**  
Modalidad: **Virtual en vivo**  
Metodología: **Teoría + práctica + proyecto transversal**

### Módulos principales
1. **Fundamentos de ingeniería de datos y cloud**
2. **Bases de datos relacionales y NoSQL**
3. **Arquitectura de datos y Data Lakes**
4. **Procesamiento distribuido con Apache Spark**
5. **Streaming y datos en tiempo real**
6. **DataOps y automatización con Airflow / GitHub Actions**
7. **Modelado de datos y bodegas analíticas**
8. **Infraestructura y DevOps con AWS y Terraform**
9. **Gobernanza, calidad y validación (Great Expectations)**
10. **Proyecto final integrador**

---

## 🧰 Stack tecnológico

| Categoría | Tecnologías |
|------------|--------------|
| **Lenguajes** | Python, SQL, Bash |
| **Bases de Datos** | PostgreSQL, MongoDB, DynamoDB |
| **Procesamiento** | Apache Spark (PySpark), Kafka, Kinesis |
| **Orquestación** | Apache Airflow, Prefect, GitHub Actions |
| **Infraestructura Cloud** | AWS (S3, Glue, Redshift, Lambda, Lake Formation, DataZone) |
| **Infraestructura como código (IaC)** | Terraform |
| **Visualización** | Amazon QuickSight |
| **Data Quality / Tests** | Great Expectations |

---

## 📁 Estructura del repositorio

```bash
ingenieria-de-datos-acelerati/
│
├── modulo-01_fundamentos/
├── modulo-02_bases_datos/
├── modulo-03_data_lake/
├── modulo-04_spark/
├── modulo-05_streaming/
├── modulo-06_dataops/
├── modulo-07_modelado/
├── modulo-08_infraestructura/
├── modulo-09_gobernanza/
├── modulo-10_proyecto_final/
│
├── docs/                 # Documentación del curso y guías adicionales
├── notebooks/            # Ejemplos prácticos y laboratorios
├── terraform/            # Plantillas IaC para AWS
├── airflow_dags/         # Flujos de orquestación (ETL/ELT)
└── README.md
```

## 💻 Cómo usar este repositorio

1. Clona el proyecto
```bash
git clone https://github.com/tu-usuario/ingenieria-de-datos.git
cd ingenieria-de-datos-
```
2. Crea y activa un entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```
3. Instala dependencias
```bash
pip install -r requirements.txt
```
4. Ejecuta ejemplos o notebooks
Cada módulo tiene su propio README.md con pasos específicos, datasets de ejemplo y scripts asociados.

---

## 🧪 Buenas prácticas
- Usa ramas tipo feature/tu-nombre o moduleX/experiment.

- Realiza commits descriptivos y claros.

- Usa black o ruff para mantener el formato del código.

- Añade docstrings y logging a tus scripts.

- Implementa tests unitarios donde aplique (pytest recomendado).

---

## 📘 Proyecto final
- El curso culmina con un proyecto integral donde se construye una arquitectura de datos moderna completa:

- Ingesta batch y streaming.

- Limpieza, transformación y modelado.

- Validación con Great Expectations.

- Orquestación y despliegue automatizado.

- Exposición de insights mediante QuickSight o dashboards BI.

---

## 📄 Licencia
Este repositorio se distribuye bajo licencia MIT.
Consulta el archivo LICENSE para más información.

---






