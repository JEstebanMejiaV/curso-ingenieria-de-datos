# Taller: Calidad de Datos (Data Quality) y Auditoría

## Objetivo

Implementar reglas automáticas para validar la integridad de las transacciones de e-commerce y auditar los accesos (y bloqueos) generados por las políticas de Lake Formation de la Fase 3.

---

## Requisitos previos del alumno

- Tener la tabla `transacciones_clientes` catalogada.
- Haber ejecutado consultas exitosas y bloqueadas en Athena durante el taller de Lake Formation.

---

## Parte 1: Implementación de Reglas de Calidad de Datos (AWS Glue Data Quality)

En lugar de escribir scripts complejos, se usarael lenguaje declarativo de **Glue Data Quality** (basado en Deequ) para evaluar si los datos de e-commerce cumplen con las reglas de negocio.

### 1.1. Crear el conjunto de reglas (Ruleset)

1. Ingresar a la consola de **AWS Glue**.
2. En el panel izquierdo, bajo **Data Catalog**, seleccionar **Data Quality**.
3. Hacer clic en **Create ruleset**.
4. Completar:
   - **Name:** `reglas_calidad_ecommerce`
5. En **Target**, seleccionar:
   - Base de datos: `ecommerce_db`
   - Tabla: `transacciones_clientes`
6. En el editor de reglas (**Data quality rules**), pegar el siguiente código.

> Estas reglas validan que no haya montos negativos, que el ID sea único, que los métodos de pago sean válidos y que los emails no estén vacíos.

```plaintext
Rules = [
    IsComplete "id_transaccion",
    IsUnique "id_transaccion",
    IsComplete "email_cliente",
    ColumnValues "monto_total" > 0,
    ColumnValues "metodo_pago" in ["Tarjeta de Credito", "PayPal", "Transferencia"],
    ColumnLength "pais_origen" = 2
]
```

7. Hacer clic en **Save ruleset**.

### 1.2. Ejecutar la evaluación de calidad

1. En la pestaña del ruleset recién creado, hacer clic en **Run**.
2. En **IAM Role**, seleccionar el rol de servicio de Glue que usan en su entorno (por ejemplo, `AWSGlueServiceRole`).
3. En **Data quality results output** (opcional pero recomendado), configurar una ruta en S3 para guardar resultados, por ejemplo:

```text
s3://data-lake-gobierno-[id-alumno]/data-quality-results/
```

4. Hacer clic en **Run**.

> El proceso tomará aproximadamente **1 a 2 minutos**.

### 1.3. Analizar los resultados

1. Una vez que el estado cambie a **Completed**, ir a la pestaña **Data quality runs**.
2. Seleccionar la ejecución.
3. Revisar el dashboard de resultados:
   - Qué reglas pasaron (**Passed**)
   - Qué reglas fallaron (**Failed**)

#### Prueba de fallo (opcional)


- Subir un nuevo `.csv` con una fila donde `monto_total = -50.00`.
- Volver a ejecutar la evaluación del ruleset.
- Verificar que la regla `ColumnValues "monto_total" > 0` falle.

---

## Parte 2: Auditoría de Acceso a los Datos (AWS CloudTrail)

El control de acceso de Lake Formation es insuficiente si no podemos demostrar a un equipo de seguridad (o a auditores) quién intentó acceder a qué datos.

### 2.1. Rastrear eventos en CloudTrail

1. Abrir la consola de **AWS CloudTrail**.
2. En el panel izquierdo, ir a **Event history**.
3. Cambiar el filtro de búsqueda (**Lookup attributes**) de **Read-only** a **Event name**.
4. En la barra de búsqueda, escribir:

```text
GetDataAccess
```

> `GetDataAccess` es el evento que registra cuando **Lake Formation** otorga o deniega credenciales temporales a Athena.

### 2.2. Analizar un evento de acceso exitoso

1. Buscar en la lista un evento `GetDataAccess` asociado al rol `Rol_Analista_Datos` (de la Fase 3).
2. Hacer clic en el nombre del evento para abrir el JSON del evento.
3. Pedir a los alumnos que identifiquen estos campos clave:

- `userIdentity.arn`: muestra exactamente **quién** hizo la consulta.
- `requestParameters.table.name`: muestra que la tabla consultada fue `transacciones_clientes`.

### 2.3. Configurar auditoría directamente en Athena (opcional pero potente)

Consultar los logs de CloudTrail usando SQL en Athena.

1. En **CloudTrail > Event history**, hacer clic en **Create Athena table** (arriba a la derecha).
2. Seleccionar el bucket S3 donde CloudTrail guarda los logs (si está configurado en el entorno de Skill Builder).
3. Ir a **Athena** y ejecutar la siguiente consulta para identificar intentos de acceso:

```sql
SELECT 
    useridentity.arn, 
    eventsource, 
    eventname, 
    errormessage, 
    eventtime 
FROM cloudtrail_logs 
WHERE eventname = 'GetDataAccess' 
ORDER BY eventtime DESC 
LIMIT 10;
```

---
