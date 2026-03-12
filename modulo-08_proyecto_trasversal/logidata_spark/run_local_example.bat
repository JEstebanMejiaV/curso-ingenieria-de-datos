@echo off
REM Script para ejecutar el ETL localmente con datos de muestra (Windows)
REM Autor: Equipo de Ingeniería de Datos LogiData
REM Fecha: 2025-01-15

echo ==========================================
echo ETL KPIs LogiData - Ejecucion Local
echo ==========================================
echo.

REM Verificar que Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no esta instalado
    exit /b 1
)

REM Verificar que las dependencias estan instaladas
echo Verificando dependencias...
python -c "import pyspark" >nul 2>&1
if errorlevel 1 (
    echo Error: PySpark no esta instalado
    echo Ejecuta: pip install -r requirements.txt
    exit /b 1
)

REM Configurar variables de entorno
set SPARK_ENV=dev
set PYTHONPATH=%PYTHONPATH%;%CD%\src

REM Fecha de ejecucion (por defecto: ayer)
if "%1"=="" (
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (
        set RUN_DATE=2025-01-15
    )
) else (
    set RUN_DATE=%1
)

echo Fecha de ejecucion: %RUN_DATE%
echo Ambiente: dev
echo Modo: incremental
echo Datos: locales (../Datos/)
echo.

REM Crear directorios de salida si no existen
if not exist output\curated mkdir output\curated
if not exist output\mart mkdir output\mart
if not exist output\quarantine mkdir output\quarantine
if not exist logs mkdir logs

echo Ejecutando ETL...
echo.

REM Ejecutar el ETL
python jobs\etl_kpis_delivery.py --env dev --run-date %RUN_DATE% --mode incremental --input-local

REM Verificar resultado
if errorlevel 1 (
    echo.
    echo ==========================================
    echo Error en la ejecucion del ETL
    echo ==========================================
    echo.
    echo Revisa los logs en: logs\etl_kpis.log
    exit /b 1
) else (
    echo.
    echo ==========================================
    echo ETL completado exitosamente!
    echo ==========================================
    echo.
    echo Resultados generados en:
    echo   - output\curated\orders_enriched\
    echo   - output\curated\deliveries_enriched\
    echo   - output\mart\kpis_daily\
    echo   - output\mart\kpis_by_store\
    echo   - output\mart\kpis_by_driver\
    echo.
)
