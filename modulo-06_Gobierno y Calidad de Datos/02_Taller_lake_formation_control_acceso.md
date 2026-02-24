# Taller: Control de Acceso con Lake Formation (Caso E-commerce)

## Objetivo

Transicionar el gobierno de datos de IAM a Lake Formation, ocultando la Información de Identificación Personal (PII) a los analistas de datos y restringiendo su visibilidad únicamente a las transacciones de un país específico.

---

## Parte 1: Toma de Control y Revocación de Permisos Heredados

Antes de aplicar la nueva seguridad, cada alumno debe deshabilitar el acceso global que AWS Glue otorga por defecto.

### 1.1. Designar al Administrador del Data Lake

1. Ingresar a la consola de **AWS Lake Formation**.
2. En el panel de navegación izquierdo, bajo **Permissions**, seleccionar **Administrative roles and tasks**.
3. En la sección **Data lake administrators**, hacer clic en **Choose administrators**.
4. Seleccionar el rol federado que están usando actualmente (usualmente `AWSReservedSSO_...` o `TeamRole`) y hacer clic en **Save**.

### 1.2. Deshabilitar el control exclusivo de IAM

1. En el panel izquierdo, ir a **Data catalog > Settings**.
2. Desmarcar las dos casillas:
   - **Use only IAM access control for new databases**
   - **Use only IAM access control for new tables in new databases**
3. Hacer clic en **Save**.

### 1.3. Revocar permisos de `IAMAllowedPrincipals`

1. Ir a **Data catalog > Databases**.
2. Seleccionar la base de datos `ecommerce_db`.
3. En el menú superior derecho **Actions**, seleccionar **Edit permissions**.
4. Seleccionar el grupo `IAMAllowedPrincipals` y hacer clic en **Revoke**.
5. Ir a **Data catalog > Tables**.
6. Seleccionar la tabla `transacciones_clientes`.
7. En la pestaña inferior **Permissions**, marcar la fila de `IAMAllowedPrincipals` y hacer clic en **Revoke**.

---

## Parte 2: Registro de la Ubicación de los Datos en S3

Lake Formation necesita saber dónde están los datos físicos para poder gobernar el acceso a ellos.

### 2.1. Registrar la ruta de S3

1. En el panel izquierdo, ir a **Register and ingest > Data lake locations**.
2. Hacer clic en **Register location**.
3. En **Amazon S3 path**, examinar y seleccionar la ruta exacta del bucket de la capa Curated (ejemplo: `s3://data-lake-gobierno-[id-alumno]/curated/transacciones/`).
4. En **IAM role**, dejar el valor por defecto: `AWSServiceRoleForLakeFormationDataAccess`.
5. Hacer clic en **Register location**.

---

## Parte 3: Aplicación de Seguridad Granular (Columna y Fila)

Configurarán los permisos para un rol de consumidor de datos. Asumiremos que previamente crearon (o se les aprovisionó) un rol en IAM llamado `Rol_Analista_Datos`.

### 3.1. Seguridad a Nivel de Columna (Ocultar PII)

**Objetivo:** El analista no debe ver los nombres ni los correos de los clientes.

1. En el panel izquierdo, ir a **Permissions > Data lake permissions** y hacer clic en **Grant**.
2. **Principals:** Seleccionar **IAM users and roles**, y elegir `Rol_Analista_Datos`.
3. **LF-Tags or catalog resources:** Seleccionar **Named data catalog resources**.
4. Elegir la base de datos `ecommerce_db` y la tabla `transacciones_clientes`.
5. **Table permissions:** Marcar únicamente la opción **Select**.
6. **Data permissions:**
   - Seleccionar **Column-based access**.
   - Elegir **Exclude columns**.
   - Seleccionar explícitamente las columnas `nombre_cliente` y `email_cliente`.
7. Hacer clic en **Grant**.

### 3.2. Seguridad a Nivel de Fila (Data Filters)

**Objetivo:** El analista solo debe tener acceso a las ventas generadas en Panamá.

1. En el panel izquierdo, ir a **Data catalog > Data filters** y hacer clic en **Create new filter**.
2. Completar:
   - **Filter name:** `filtro_ventas_panama`
   - **Target database:** `ecommerce_db`
   - **Target table:** `transacciones_clientes`
3. **Column-level access:** Seleccionar **Include all columns** (esto se combinará con la exclusión del paso anterior).
4. **Row filter expression:** Escribir exactamente la siguiente expresión SQL:

```sql
pais_origen = 'PA'
```

5. Guardar el filtro.
6. Ir nuevamente a **Permissions > Data lake permissions > Grant**.
7. Seleccionar el `Rol_Analista_Datos`, la base de datos y la tabla.
8. En **Table permissions**, marcar **Select**.
9. En **Data permissions**, elegir **Row-based access**, seleccionar el filtro `filtro_ventas_panama` recién creado, y hacer clic en **Grant**.

---

## Parte 4: Validación de la Arquitectura en Amazon Athena

El paso final es comprobar que las reglas se aplican correctamente al consultar los datos reales.

### 4.1. Configurar la sesión del Analista

1. Asuman el rol `Rol_Analista_Datos` (o utilicen las credenciales de ese usuario en su entorno).
2. Navegar a la consola de **Amazon Athena**.
3. Asegurarse de que el entorno de Athena tiene un bucket de resultados configurado en **Settings**.

### 4.2. Ejecutar y Verificar

En el editor de consultas, ejecutar:

```sql
SELECT * FROM ecommerce_db.transacciones_clientes LIMIT 100;
```

#### Verificaciones esperadas

- **Verificación de Columnas:** Validar en los resultados que las columnas `nombre_cliente` y `email_cliente` no aparecen por ninguna parte.
- **Verificación de Filas:** Revisar la columna `pais_origen`. El 100% de los registros devueltos debe mostrar el valor `'PA'`.

#### Prueba de fallo esperado

Ejecutar:

```sql
SELECT *
FROM ecommerce_db.transacciones_clientes
WHERE pais_origen = 'CO';
```

**Resultado esperado:** La consulta debe ejecutarse exitosamente, pero devolver **0 resultados**, demostrando que Lake Formation filtra los datos antes de que el motor de Athena pueda interactuar con ellos.

---

