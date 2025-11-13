## Caso: Diseño Arquitectura Datos: ECOBanco 3000
### Contexto general

Eres miembro del equipo de Ingeniería de Datos del Banco ECOBanco 3000, una entidad financiera con operaciones en varios países de América Latina. El banco está ejecutando una transformación digital para unificar sus datos, mejorar la toma de decisiones y reducir los tiempos de entrega de reportes y modelos analíticos.

El reto surge porque cada unidad del negocio produce y consume datos de manera independiente, lo que ha generado duplicidad, inconsistencias y falta de trazabilidad.

Tu equipo debe diseñar una arquitectura y un modelo de gobierno que atienda las necesidades de tres áreas estratégicas, con diferentes tipos de fuentes y requisitos.

## Análisis de comportamiento de clientes
## Problema:
El área de Inteligencia Comercial desea entender los patrones de uso de productos financieros (cuentas, tarjetas, créditos, inversiones) para diseñar estrategias de retención.
Actualmente, los analistas dependen de los ingenieros de datos para generar consultas y reportes, lo cual causa cuellos de botella.

### Evaluación de riesgo crediticio
### Problema:
El área de Ciencia de Riesgos desarrolla modelos de probabilidad de incumplimiento (PD) y pérdida esperada (LGD).
Necesita construir features a partir de datos históricos limpios y consistentes, pero la información proviene de distintos sistemas legados y APIs externas con formatos heterogéneos.


### Detección de fraude en tiempo real
### Problema:
El equipo de Prevención de Fraude requiere detectar operaciones sospechosas en tiempo real a partir de eventos de tarjetas, transferencias y banca móvil.
El sistema actual procesa los datos con retraso, lo que impide actuar de manera oportuna.

---

## Fuentes de datos

### Historial de Transacciones de Tarjeta (API JSON de tercero y bases PostgreSQL internas)

La API externa requiere token de servicio y proporciona endpoints tanto de transmisión en tiempo real como de extracción masiva, sin limitaciones de tasa. Las bases de datos internas PostgreSQL, heredadas de múltiples sistemas de producción, presentan duplicidad e inconsistencias en campos clave como device_id y merchant_id. Los registros se entregan en formato JSON con eventos que incluyen montos, ubicación, tipo de comercio, resultado de autorización y dispositivo utilizado. El flujo de eventos alcanza entre 2.000 y 5.000 transacciones por segundo y se replica a un data lake mediante microbatches. Los datos están parcialmente pseudonimizados, con tokenización de PAN y políticas de retención de 13 meses.

### Buró de Crédito (API XML de tercero)

El buró ofrece información crediticia consolidada mediante una API XML autenticada con mTLS y clave API. El servicio está limitado a 300 solicitudes por minuto y dispone de una ventana de mantenimiento nocturna. Los reportes contienen cuentas activas, consultas recientes, morosidad y comportamiento de pago. La latencia varía entre 200 y 800 milisegundos. Los datos son altamente confidenciales y requieren trazabilidad SOX y cumplimiento PCI DSS. Los resultados deben almacenarse temporalmente y auditarse antes de ser usados en modelos. Las coincidencias por nombre o documento pueden no ser exactas.

### Archivos de Nómina e Ingresos (SFTP mensual – CSV)

Los empleadores y aliados financieros envían mensualmente archivos CSV mediante SFTP autenticado por clave rotativa. Los archivos contienen datos de ingresos, descuentos y antigüedad laboral de los solicitantes de crédito. Los formatos y codificaciones varían según el emisor, lo que genera problemas de column drift y montos con separadores inconsistentes. Los archivos suelen recibirse con retrasos de hasta cinco días. Los datos se validan mediante reconciliación automática y se transforman a un esquema estándar antes de ser cargados en la capa Silver del data lake. Por incluir PII, se aplica cifrado y retención máxima de 18 meses.

### Denuncias de Fraude y Casos (MongoDB interno con adjuntos)

El sistema de atención de fraude almacena reportes de casos en una base MongoDB accesible sólo desde la red interna. Los documentos BSON incluyen descripciones textuales, etiquetas de tipo de fraude, nivel de confianza y evidencias adjuntas (imágenes o capturas de chat). Los registros se actualizan en línea y pueden consumirse mediante change streams. El esquema es flexible y carece de estandarización en las etiquetas, lo que complica el entrenamiento de modelos de clasificación. Los datos contienen PII y evidencia sensible, por lo que están sujetos a políticas de acceso restringido y anonimización para fines analíticos.

### Geolocalización de Dispositivos (SDK móvil – JSON streaming)

Los datos de ubicación provienen del SDK de la aplicación. Cada registro contiene device_id, coordenadas GPS, precisión, fuente y timestamp. La frecuencia de muestreo es adaptativa según la actividad del usuario, con latencias promedio de 200 a 600 milisegundos. Aunque los datos son valiosos para detección de fraude, presentan saltos y errores de precisión superiores a 100 metros en interiores. La información de geolocalización sólo puede retenerse durante 90 días, según las políticas de privacidad y consentimiento explícito de los usuarios.
