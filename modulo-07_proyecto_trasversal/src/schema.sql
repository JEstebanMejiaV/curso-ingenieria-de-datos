-- ============================================================
-- PROYECTO LOGIDATA S.A.S.
-- Esquema Relacional PostgreSQL
-- Módulo 2 - HU3: Modelo Transaccional
-- ============================================================

-- 1. LIMPIEZA PREVIA (para recrear sin errores)
DROP TABLE IF EXISTS entregas CASCADE;
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS catalogo CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

-- 2. TABLA MAESTRA: CLIENTES
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    zona VARCHAR(50) NOT NULL,
    tipo_cliente VARCHAR(50) NOT NULL,
    
    -- Constraints de dominio (validación de valores permitidos)
    CONSTRAINT chk_zona CHECK (zona IN ('Norte', 'Sur', 'Oriente', 'Occidente', 'Centro')),
    CONSTRAINT chk_tipo_cliente CHECK (tipo_cliente IN ('Retail', 'Farmacéutico', 'Supermercado', 'Ecommerce', 'Restaurante'))
);

COMMENT ON TABLE clientes IS 'Tabla maestra de clientes (~300 registros)';
COMMENT ON COLUMN clientes.id_cliente IS 'PK: Identificador único del cliente';
COMMENT ON COLUMN clientes.nombre IS 'Nombre completo del cliente';
COMMENT ON COLUMN clientes.zona IS 'Zona geográfica de operación';
COMMENT ON COLUMN clientes.tipo_cliente IS 'Segmento de negocio';

-- 3. TABLA MAESTRA: CATÁLOGO DE PRODUCTOS
CREATE TABLE IF NOT EXISTS catalogo (
    id_producto VARCHAR(50) PRIMARY KEY,
    categoria VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL CHECK (precio > 0),
    tipo_entrega VARCHAR(50) NOT NULL,
    
    CONSTRAINT chk_tipo_entrega CHECK (tipo_entrega IN ('Same Day', 'Next Day', 'Programada', 'Express'))
);

COMMENT ON TABLE catalogo IS 'Catálogo de productos (~200 registros)';
COMMENT ON COLUMN catalogo.id_producto IS 'PK: Identificador único del producto';
COMMENT ON COLUMN catalogo.categoria IS 'Clasificación del producto';
COMMENT ON COLUMN catalogo.precio IS 'Precio unitario en pesos colombianos';
COMMENT ON COLUMN catalogo.tipo_entrega IS 'Modalidad de entrega disponible';

-- 4. TABLA TRANSACCIONAL: PEDIDOS
CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido VARCHAR(50) PRIMARY KEY,
    id_cliente VARCHAR(50) NOT NULL,
    id_producto VARCHAR(50) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    monto DECIMAL(12, 2) NOT NULL CHECK (monto >= 0),
    estado VARCHAR(50) NOT NULL DEFAULT 'CREADO',
    
    -- Constraints de dominio
    CONSTRAINT chk_estado CHECK (estado IN ('CREADO', 'EN_DESPACHO', 'ENTREGADO', 'CANCELADO')),
    
    -- Foreign Keys con integridad referencial
    CONSTRAINT fk_pedidos_cliente FOREIGN KEY (id_cliente) 
        REFERENCES clientes(id_cliente) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_pedidos_producto FOREIGN KEY (id_producto) 
        REFERENCES catalogo(id_producto) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

-- Índices para optimizar consultas frecuentes
CREATE INDEX idx_pedidos_cliente ON pedidos(id_cliente);
CREATE INDEX idx_pedidos_producto ON pedidos(id_producto);
CREATE INDEX idx_pedidos_fecha ON pedidos(fecha);
CREATE INDEX idx_pedidos_estado ON pedidos(estado);

COMMENT ON TABLE pedidos IS 'Tabla transaccional de pedidos (~2000 registros)';
COMMENT ON COLUMN pedidos.id_pedido IS 'PK: Identificador único del pedido';
COMMENT ON COLUMN pedidos.id_cliente IS 'FK: Cliente que realizó el pedido';
COMMENT ON COLUMN pedidos.id_producto IS 'FK: Producto solicitado';
COMMENT ON COLUMN pedidos.fecha IS 'Fecha y hora del pedido (UTC-agnóstico)';
COMMENT ON COLUMN pedidos.monto IS 'Valor total del pedido';
COMMENT ON COLUMN pedidos.estado IS 'Estado actual del pedido en el flujo logístico';

-- 5. TABLA TRANSACCIONAL: ENTREGAS (solo pedidos no cancelados)
CREATE TABLE IF NOT EXISTS entregas (
    id_pedido VARCHAR(50) PRIMARY KEY,
    hora_programada TIMESTAMP NOT NULL,
    hora_real TIMESTAMP NOT NULL,
    zona VARCHAR(50) NOT NULL,
    conductor VARCHAR(10) NOT NULL,
    vehiculo VARCHAR(10) NOT NULL,
    
    -- Foreign Key con restricción de integridad
    CONSTRAINT fk_entregas_pedido FOREIGN KEY (id_pedido) 
        REFERENCES pedidos(id_pedido) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    
    -- Validación de formatos (expresiones regulares simples)
    CONSTRAINT chk_conductor_formato CHECK (conductor ~ '^C[0-9]{4}$'),
    CONSTRAINT chk_vehiculo_formato CHECK (vehiculo ~ '^V[0-9]{4}$')
);

-- Índices para entregas
CREATE INDEX idx_entregas_zona ON entregas(zona);
CREATE INDEX idx_entregas_conductor ON entregas(conductor);
CREATE INDEX idx_entregas_vehiculo ON entregas(vehiculo);

COMMENT ON TABLE entregas IS 'Entregas físicas (~1800 registros, solo pedidos no cancelados). Relación 1:0..1 opcional con pedidos.';
COMMENT ON COLUMN entregas.id_pedido IS 'PK y FK: Pedido asociado (solo si estado != CANCELADO)';
COMMENT ON COLUMN entregas.hora_programada IS 'Fecha/hora estimada de entrega';
COMMENT ON COLUMN entregas.hora_real IS 'Fecha/hora efectiva de entrega';
COMMENT ON COLUMN entregas.zona IS 'Zona donde se realizó la entrega';
COMMENT ON COLUMN entregas.conductor IS 'Código del conductor (formato: C0001-C0300)';
COMMENT ON COLUMN entregas.vehiculo IS 'Código del vehículo (formato: V0001-V0500)';

-- 6. VISTA DE CONTROL: Pedidos con información de entrega
CREATE OR REPLACE VIEW vw_pedidos_completo AS
SELECT 
    p.id_pedido,
    p.fecha,
    p.monto,
    p.estado,
    c.nombre AS cliente_nombre,
    c.zona AS cliente_zona,
    c.tipo_cliente,
    cat.categoria,
    cat.tipo_entrega,
    e.hora_programada,
    e.hora_real,
    e.conductor,
    e.vehiculo,
    -- Cálculo de métricas de negocio
    CASE 
        WHEN e.hora_real IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (e.hora_real - e.hora_programada))/3600
        ELSE NULL 
    END AS horas_retraso
FROM pedidos p
LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
LEFT JOIN catalogo cat ON p.id_producto = cat.id_producto
LEFT JOIN entregas e ON p.id_pedido = e.id_pedido;

COMMENT ON VIEW vw_pedidos_completo IS 'Vista consolidada de pedidos con datos de cliente, producto y entrega';
