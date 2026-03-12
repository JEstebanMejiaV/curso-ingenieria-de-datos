#!/bin/bash

# Script para ejecutar el ETL localmente con datos de muestra
# Autor: Equipo de Ingeniería de Datos LogiData
# Fecha: 2025-01-15

echo "=========================================="
echo "ETL KPIs LogiData - Ejecución Local"
echo "=========================================="
echo ""

# Verificar que Python está instalado
if ! command -v python &> /dev/null; then
    echo "Error: Python no está instalado"
    exit 1
fi

# Verificar que las dependencias están instaladas
echo "Verificando dependencias..."
python -c "import pyspark" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: PySpark no está instalado"
    echo "Ejecuta: pip install -r requirements.txt"
    exit 1
fi

# Configurar variables de entorno
export SPARK_ENV=dev
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Fecha de ejecución (por defecto: ayer)
RUN_DATE=${1:-$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)}

echo "Fecha de ejecución: $RUN_DATE"
echo "Ambiente: dev"
echo "Modo: incremental"
echo "Datos: locales (../Datos/)"
echo ""

# Crear directorios de salida si no existen
mkdir -p output/curated
mkdir -p output/mart
mkdir -p output/quarantine
mkdir -p logs

echo "Ejecutando ETL..."
echo ""

# Ejecutar el ETL
python jobs/etl_kpis_delivery.py \
  --env dev \
  --run-date "$RUN_DATE" \
  --mode incremental \
  --input-local

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "ETL completado exitosamente!"
    echo "=========================================="
    echo ""
    echo "Resultados generados en:"
    echo "  - output/curated/orders_enriched/"
    echo "  - output/curated/deliveries_enriched/"
    echo "  - output/mart/kpis_daily/"
    echo "  - output/mart/kpis_by_store/"
    echo "  - output/mart/kpis_by_driver/"
    echo ""
    
    # Mostrar resumen de archivos generados
    echo "Archivos generados:"
    find output -name "*.parquet" -type f | head -10
    echo ""
else
    echo ""
    echo "=========================================="
    echo "Error en la ejecución del ETL"
    echo "=========================================="
    echo ""
    echo "Revisa los logs en: logs/etl_kpis.log"
    exit 1
fi
