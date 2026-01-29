## **HU3: Modelo Relacional (Estructura y Transacciones)**

> **\"Como ingeniero, quiero diseñar el modelo relacional que represente
> los datos transaccionales de pedidos, entregas y clientes.\"**

*Tecnología seleccionada: PostgreSQL (Implementación recomendada en la
nube: Amazon RDS). Esta elección se basa en la necesidad de cumplimiento
de propiedades ACID (Atomicidad, Consistencia, Aislamiento y
Durabilidad), asegurando que cada transacción de pedido sea exacta y
auditable.*

##  [**[Diagrama Entidad-Relación (ERD)]{.underline}**](https://drive.google.com/file/d/1qj5zoT-hKjnihCOaAIXEkyPOzshEL9FM/view?usp=sharing)

**El modelo sigue una Arquitectura de Estrella Simplificada, optimizada
para la integridad transaccional y la facilidad de consultas (Joins)
analíticas.**

  -------------- ---------------------- ----------------- ----------------
  **Tabla**      **Descripción**        **Llave Primaria  **Dependencias
                                        (PK)**            (FK)**

  **Clientes**   **Almacena el perfil   **id_cliente**    **Ninguna**
                 maestro del cliente                      
                 (nombre, zona,                           
                 tipo).**                                 

  **Catálogo**   **Maestro de productos **id_producto**   **Ninguna**
                 con precios y tipos de                   
                 entrega.**                               

  **Pedidos**    **Tabla de hechos que  **id_pedido**     **id_cliente,
                 registra la                              id_producto**
                 transacción                              
                 comercial.**                             

  **Entregas**   **Datos operativos de  **id_pedido**     **id_pedido**
                 última milla                             
                 (conductor, vehículo,                    
                 tiempos).**                              
  -------------- ---------------------- ----------------- ----------------

## **Descripción de Relaciones de Negocio**

![](media/image1.png){width="6.046875546806649in"
height="4.944938757655293in"}

###  **Relación Clientes ⮕ Pedidos**

- **Cardinalidad:** Uno a Muchos (1:N).

- **Definición Técnica:** La tabla pedidos hereda el id_cliente como
  llave foránea.

- **Lógica de Negocio:** Un cliente puede generar múltiples órdenes de
  compra, pero cada pedido es único y debe estar vinculado
  obligatoriamente a un cliente registrado para evitar \"pedidos
  huérfanos\".

###  **Relación Catálogo ⮕ Pedidos**

- **Cardinalidad:** Uno a Muchos (1:N).

- **Definición Técnica:** Relaciona el id_producto del catálogo con la
  transacción en pedidos.

- **Lógica de Negocio:** Permite estandarizar los precios y categorías.
  Un pedido solo puede procesar productos existentes en el inventario
  oficial de LogiData.

###  **Relación Pedidos ⮕ Entregas**

- **Cardinalidad:** Uno a Uno (1:1).

- **Definición Técnica:** El id_pedido actúa simultáneamente como PK y
  FK en la tabla de entregas.

- **Lógica de Negocio:** Cada pedido genera una única hoja de ruta de
  entrega. Esta separación permite que la tabla de pedidos se mantenga
  ligera, mientras que la de entregas gestiona la complejidad operativa
  (conductores y vehículos).

##  **Pilares de Integridad del Diseño**

- **Llaves Primarias (PK):** (Icono Llave Dorada). Garantizan la
  unicidad de los registros; no pueden existir dos pedidos con el mismo
  ID.

- **Llaves Foráneas (FK):** (Icono Llave Blanca). Actúan como puentes de
  integridad; impiden, por ejemplo, que se cree una entrega para un
  pedido que no ha sido registrado previamente.

- **Constraints (Restricciones):** Se implementaron validaciones de tipo
  CHECK para asegurar que zonas y estados (CREADO, ENTREGADO, etc.)
  cumplan estrictamente con los valores permitidos por el negocio.

[[Carga de
datos]{.underline}](https://drive.google.com/drive/folders/1kSbDwHVRhxrW3hAbF-YKXI9XWfaVqa0M?usp=sharing).

![](media/image2.png){width="6.267716535433071in"
height="3.2777777777777777in"}

## **HU 4: Modelo NO Relacional**

> **\"Como ingeniero, quiero definir un modelo NoSQL para los datos de
> sensores IoT. \"**

*Tecnología seleccionada: Mongo está diseñado para escribir miles de
documentos por segundo sin afectar el rendimiento y tendremos datos
**masivos y cambiantes,** como los sensores generan miles de datos por
segundo .*

> ![](media/image3.png){width="4.473958880139983in"
> height="2.5193886701662294in"}
>
> [**[Carga de
> datos]{.underline}**](https://drive.google.com/drive/folders/1kSbDwHVRhxrW3hAbF-YKXI9XWfaVqa0M?usp=sharing)
>
> ![](media/image4.png){width="6.267716535433071in"
> height="2.6527777777777777in"}

  ------------- --------------- ------------------------------------------
  **Campo**     **Tipo de Dato  **Descripción y Uso**
                (BSON)**        

  \_id          objectId        Llave Primaria única. MongoDB la genera
                                automáticamente para asegurar que ningún
                                evento se repita.

  evento        string          Texto. Almacena etiquetas como \"OK\",
                                \"Alerta\" o el tipo de reporte del
                                sensor.

  latitud       double          Número Decimal. Almacena la coordenada GPS
                                con alta precisión.

  longitud      double          Número Decimal. Almacena la coordenada GPS
                                necesaria para el rastreo.

  temperatura   double          Número Decimal. Crucial para la cadena de
                                frío; permite medir grados exactos (ej.
                                4.5°C).

  timestamp     string          Fecha/Hora. Aunque es texto, sigue el
                                formato ISO-8601 para ordenar los eventos
                                cronológicamente.

  vehiculo      string          Texto. Es el identificador del camión (ej.
                                \"V-001\") que vincula este dato con la
                                tabla de entregas.
  ------------- --------------- ------------------------------------------

### 

### 

### 

### **¿Por qué usamos estos tipos en LogiData?**

1.  **Double vs Integer:** Usamos double porque las coordenadas y la
    temperatura nunca son números enteros exactos; necesitamos los
    decimales para saber la ubicación real del camión**.**

2.  **ObjectId:** Es mucho más eficiente que un número normal porque
    incluye información sobre *cuándo* se creó el registro, lo que
    acelera las búsquedas masivas**.**

3.  **Flexibilidad:** Si mañana decides agregar un sensor de
    \"Humedad\", MongoDB te permitirá guardarlo como un nuevo campo sin
    tener que reconstruir toda la base de datos, algo que en PostgreSQL
    sería mucho más complejo.

    **Justificación Técnica: LogiData S.A.S.**

  -----------------------------------------------------------------------------
  **Tecnología**   **Pilar Técnico**  **Ventaja Estratégica para el Negocio**
  ---------------- ------------------ -----------------------------------------
  PostgreSQL       Integridad         Garantiza que la \"Informacion\" (pedidos
                   Referencial y ACID y facturas) nunca tenga descuadres. No
                                      permite vender a clientes inexistentes ni
                                      productos fuera de catálogo.

  MongoDB          Escalabilidad      Soporta el \"ruido\" de 10,000 eventos
                   Horizontal y       IoT por ráfaga sin bloquear el sistema.
                   Esquema Flexible   Permite agregar nuevos tipos de sensores
                                      (humedad, vibración) sin detener la
                                      operación.

  AWS S3           Almacenamiento de  Es 10 veces más barato que las bases
                   Bajo Costo         activas. Funciona como un Data Lake
                   (FinOps)           centralizado donde el analista hace Big
                                      Data sin poner lenta la aplicación móvil.
  -----------------------------------------------------------------------------
