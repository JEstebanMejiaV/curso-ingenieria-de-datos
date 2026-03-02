# Guía Completa: Data Docs en Great Expectations

## Índice
1. [¿Qué son los Data Docs?](#que-son)
2. [Estructura y Componentes](#estructura)
3. [Generación de Data Docs](#generacion)
4. [Personalización](#personalizacion)
5. [Hosting y Distribución](#hosting)
6. [Mejores Prácticas](#mejores-practicas)

---

## ¿Qué son los Data Docs? {#que-son}

Los **Data Docs** son sitios web estáticos generados automáticamente por Great Expectations que documentan:

### Componentes Principales

1. **Expectation Suites**: Documentación de todas las reglas de calidad definidas
2. **Validation Results**: Resultados de ejecuciones de validación
3. **Profiling Results**: Estadísticas descriptivas de los datos
4. **Data Assets**: Información sobre las fuentes de datos

### Beneficios

- **Comunicación**: Facilita compartir resultados con stakeholders no técnicos
- **Transparencia**: Documenta automáticamente todas las reglas de calidad
- **Trazabilidad**: Historial de validaciones y cambios
- **Colaboración**: Punto central de referencia para el equipo

---

## Estructura y Componentes {#estructura}

### Estructura de Directorios

```
gx/uncommitted/data_docs/
├── local_site/
│   ├── index.html                    # Página principal
│   ├── expectations/                 # Suites de expectativas
│   │   ├── suite_1.html
│   │   └── suite_2.html
│   ├── validations/                  # Resultados de validaciones
│   │   ├── validation_1.html
│   │   └── validation_2.html
│   └── static/                       # Assets (CSS, JS, imágenes)
│       ├── styles/
│       ├── images/
│       └── fonts/
```

### Página Principal (index.html)

Muestra:
- Lista de todas las Expectation Suites
- Últimas validaciones ejecutadas
- Estadísticas generales de calidad
- Enlaces a documentación detallada

### Páginas de Expectation Suites

Documentan:
- Todas las expectativas en la suite
- Descripción de cada expectativa
- Metadatos (owner, criticidad, etc.)
- Historial de cambios

### Páginas de Validation Results

Muestran:
- Estado general (Pass/Fail)
- Resultados por expectativa
- Estadísticas detalladas
- Valores inesperados encontrados
- Gráficos y visualizaciones

---

## Generación de Data Docs {#generacion}

### Método Básico

```python
import great_expectations as gx

# Crear contexto
context = gx.get_context(mode="file")

# Generar Data Docs
context.build_data_docs()

# Abrir en navegador
context.open_data_docs()
```

### Generación Después de Validación

```python
# Ejecutar validación
validation_result = validation_definition.run(
    batch_parameters={"dataframe": df}
)

# Generar Data Docs automáticamente
context.build_data_docs()
```

### Generación Programática

```python
# Generar solo para una suite específica
context.build_data_docs(
    site_names=["local_site"],
    resource_identifiers=[
        {
            "expectation_suite_name": "mi_suite"
        }
    ]
)
```

---

## Personalización {#personalizacion}

### Configuración en great_expectations.yml

```yaml
data_docs_sites:
  local_site:
    class_name: SiteBuilder
    show_how_to_buttons: true
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/data_docs/local_site/
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
      show_cta_footer: true
```

### Personalizar Estilos CSS

Crear archivo `custom_styles.css`:

```css
/* Personalizar colores */
:root {
    --primary-color: #1E88E5;
    --success-color: #43A047;
    --error-color: #E53935;
}

/* Personalizar header */
.ge-header {
    background-color: var(--primary-color);
    padding: 20px;
}

/* Personalizar cards */
.ge-card {
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

### Agregar Logo Personalizado

```yaml
data_docs_sites:
  local_site:
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
      site_section_builders:
        expectations:
          header: "Reglas de Calidad de Datos"
          logo:
            path: "static/images/company_logo.png"
            alt_text: "Company Logo"
```

---

## Hosting y Distribución {#hosting}

### Opción 1: Local (Desarrollo)

```python
# Generar y abrir localmente
context.build_data_docs()
context.open_data_docs()
```

**Ubicación**: `gx/uncommitted/data_docs/local_site/`

### Opción 2: Amazon S3

```yaml
data_docs_sites:
  s3_site:
    class_name: SiteBuilder
    store_backend:
      class_name: TupleS3StoreBackend
      bucket: my-data-docs-bucket
      prefix: data_docs/
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
```

```python
# Generar y subir a S3
context.build_data_docs(site_names=["s3_site"])
```

### Opción 3: Google Cloud Storage

```yaml
data_docs_sites:
  gcs_site:
    class_name: SiteBuilder
    store_backend:
      class_name: TupleGCSStoreBackend
      project: my-project
      bucket: my-data-docs-bucket
      prefix: data_docs/
```

### Opción 4: Azure Blob Storage

```yaml
data_docs_sites:
  azure_site:
    class_name: SiteBuilder
    store_backend:
      class_name: TupleAzureBlobStoreBackend
      container: data-docs
      connection_string: ${AZURE_STORAGE_CONNECTION_STRING}
```

### Opción 5: Servidor Web Interno

```bash
# Copiar archivos a servidor web
cp -r gx/uncommitted/data_docs/local_site/* /var/www/html/data-docs/

# O usar Python simple HTTP server para testing
cd gx/uncommitted/data_docs/local_site/
python -m http.server 8000
```

---

## Mejores Prácticas {#mejores-practicas}

### 1. Automatizar Generación

```python
# En tu pipeline de datos
def run_data_quality_checks(df):
    # Validar
    result = validation_definition.run(
        batch_parameters={"dataframe": df}
    )
    
    # Generar Data Docs automáticamente
    context.build_data_docs()
    
    # Enviar notificación con link
    if not result.success:
        send_notification(
            message="Validación fallida",
            docs_url="https://data-docs.company.com/latest"
        )
    
    return result
```

### 2. Versionamiento

```python
# Incluir timestamp en nombres de validación
from datetime import datetime

validation_name = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

validation_definition = gx.ValidationDefinition(
    data=batch_def,
    suite=suite,
    name=validation_name
)
```

### 3. Organización por Ambiente

```yaml
data_docs_sites:
  dev_site:
    store_backend:
      base_directory: uncommitted/data_docs/dev/
  
  staging_site:
    store_backend:
      base_directory: uncommitted/data_docs/staging/
  
  prod_site:
    store_backend:
      class_name: TupleS3StoreBackend
      bucket: prod-data-docs
```

### 4. Seguridad y Acceso

```python
# Para S3 con autenticación
data_docs_sites:
  secure_s3_site:
    store_backend:
      class_name: TupleS3StoreBackend
      bucket: secure-data-docs
      prefix: data_docs/
      boto3_options:
        region_name: us-east-1
        # Usar IAM roles en producción
```

### 5. Limpieza de Archivos Antiguos

```python
# Script para limpiar validaciones antiguas
import os
import shutil
from datetime import datetime, timedelta

def cleanup_old_validations(days=30):
    validations_dir = "gx/uncommitted/data_docs/local_site/validations/"
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for filename in os.listdir(validations_dir):
        filepath = os.path.join(validations_dir, filename)
        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
        
        if file_time < cutoff_date:
            os.remove(filepath)
            print(f"Eliminado: {filename}")
```

---

## Ejemplos de Uso

### Ejemplo 1: Reporte Diario Automatizado

```python
# script: daily_quality_report.py
import great_expectations as gx
import pandas as pd
from datetime import datetime

def generate_daily_report():
    # Cargar datos del día
    df = pd.read_csv(f"data/sales_{datetime.now().strftime('%Y%m%d')}.csv")
    
    # Validar
    context = gx.get_context(mode="file")
    validation_result = run_validation(context, df)
    
    # Generar Data Docs
    context.build_data_docs()
    
    # Enviar email con link
    send_email(
        to="data-team@company.com",
        subject=f"Reporte de Calidad - {datetime.now().strftime('%Y-%m-%d')}",
        body=f"Estado: {'✅ Aprobado' if validation_result.success else '❌ Rechazado'}",
        docs_url="https://data-docs.company.com/latest"
    )

if __name__ == "__main__":
    generate_daily_report()
```

### Ejemplo 2: Dashboard de Calidad

```python
# Integración con Streamlit
import streamlit as st
import great_expectations as gx

st.title("Dashboard de Calidad de Datos")

context = gx.get_context(mode="file")

# Mostrar últimas validaciones
st.header("Últimas Validaciones")
# ... código para mostrar resultados

# Botón para regenerar Data Docs
if st.button("Regenerar Data Docs"):
    context.build_data_docs()
    st.success("Data Docs actualizados!")
    st.markdown("[Ver Data Docs](file://gx/uncommitted/data_docs/local_site/index.html)")
```

---

**Última actualización**: Marzo 2026
**Versión**: 1.0
