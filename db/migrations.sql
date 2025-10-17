-- =============================================
-- MIGRACIONES BÁSICAS - SISTEMA GRANJA CUYES
-- =============================================

-- Tabla galpones (PRIMERO - no depende de nadie)
CREATE TABLE IF NOT EXISTS galpones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    capacidad INTEGER NOT NULL,
    ubicacion VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla pozas (SEGUNDO - depende de galpones)
CREATE TABLE IF NOT EXISTS pozas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('reproductora', 'lactancia', 'destete', 'engorde', 'reemplazo')),
    capacidad INTEGER NOT NULL,
    galpon_id INTEGER REFERENCES galpones(id),
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla partos_simplificada (TERCERO - depende de galpones y pozas)
CREATE TABLE IF NOT EXISTS partos_simplificada (
    id SERIAL PRIMARY KEY,
    galpon_id INTEGER REFERENCES galpones(id),
    poza_id INTEGER REFERENCES pozas(id),
    fecha_parto DATE NOT NULL,
    nacidos_vivos INTEGER DEFAULT 0,
    muertos_nacimiento INTEGER DEFAULT 0,
    numero_parto INTEGER NOT NULL,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- 🆕 TABLA MORTALIDAD GENERAL UNIFICADA (REEMPLAZA mortalidad_lactancia)
CREATE TABLE IF NOT EXISTS mortalidad_general (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo_cuy VARCHAR(20) NOT NULL CHECK (tipo_cuy IN ('reproductor', 'lactante', 'destete', 'reemplazo', 'engorde_destete', 'engorde_descarte')),
    galpon_id INTEGER REFERENCES galpones(id),
    poza_id INTEGER REFERENCES pozas(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    causa VARCHAR(100) NOT NULL,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Tabla destetes_simplificada (SIN PESO)
CREATE TABLE IF NOT EXISTS destetes_simplificada (
    id SERIAL PRIMARY KEY,
    galpon_id INTEGER REFERENCES galpones(id),
    poza_origen_id INTEGER REFERENCES pozas(id),
    fecha_destete DATE NOT NULL,
    machos_destetados INTEGER DEFAULT 0,
    hembras_destetadas INTEGER DEFAULT 0,
    muertos_destete INTEGER DEFAULT 0,
    reemplazo_machos INTEGER DEFAULT 0,
    reemplazo_hembras INTEGER DEFAULT 0,
    engorde_machos INTEGER DEFAULT 0,
    engorde_hembras INTEGER DEFAULT 0,
    venta_directa_machos INTEGER DEFAULT 0,
    venta_directa_hembras INTEGER DEFAULT 0,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Tabla control_engorde
CREATE TABLE IF NOT EXISTS control_engorde (
    id SERIAL PRIMARY KEY,
    tipo_engorde VARCHAR(20) NOT NULL CHECK (tipo_engorde IN ('destete', 'descarte')),
    galpon_id INTEGER REFERENCES galpones(id),
    poza_id INTEGER REFERENCES pozas(id),
    fecha_control DATE NOT NULL,
    peso_promedio DECIMAL(8,2),
    listo_venta BOOLEAN DEFAULT FALSE,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Tabla ventas
CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    fecha_venta DATE NOT NULL,
    cliente VARCHAR(200),
    tipo_producto VARCHAR(20) NOT NULL CHECK (tipo_producto IN ('engorde_destete', 'engorde_descarte', 'destete_directo')),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Tabla gastos
CREATE TABLE IF NOT EXISTS gastos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('alimentacion', 'medicamentos', 'mantenimiento', 'mano_obra', 'transporte','otros')),
    descripcion VARCHAR(200) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    proveedor VARCHAR(100),
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- MIGRACIÓN DE DATOS EXISTENTES
-- =============================================

-- 🚨 MIGRAR DATOS EXISTENTES de mortalidad_lactancia a mortalidad_general
INSERT INTO mortalidad_general (fecha, tipo_cuy, galpon_id, poza_id, cantidad, causa, observaciones, fecha_creacion)
SELECT 
    fecha, 
    'lactante' as tipo_cuy, 
    galpon_id, 
    poza_id, 
    cantidad, 
    causa, 
    observaciones, 
    fecha_creacion
FROM mortalidad_lactancia;

-- 🗑️ ELIMINAR TABLA ANTIGUA (después de migrar)
DROP TABLE IF EXISTS mortalidad_lactancia;

-- =============================================
-- INSERTAR DATOS BÁSICOS PARA PRUEBAS
-- =============================================

-- Galpones de ejemplo
INSERT INTO galpones (nombre, capacidad, ubicacion) VALUES 
('Galpón Principal', 100, 'Zona A'),
('Galpón Secundario', 50, 'Zona B')
ON CONFLICT DO NOTHING;

-- Pozas de ejemplo
INSERT INTO pozas (nombre, tipo, capacidad, galpon_id) VALUES
('Poza A', 'reproductora', 10, 1),
('Poza B', 'reproductora', 10, 1),
('Poza C', 'lactancia', 15, 1),
('Poza D', 'destete', 20, 2),
('Poza E', 'engorde', 25, 2)
ON CONFLICT DO NOTHING;

-- =============================================
-- ÍNDICES BÁSICOS
-- =============================================

CREATE INDEX IF NOT EXISTS idx_pozas_galpon_id ON pozas(galpon_id);
CREATE INDEX IF NOT EXISTS idx_partos_poza ON partos_simplificada(poza_id);
CREATE INDEX IF NOT EXISTS idx_partos_fecha ON partos_simplificada(fecha_parto);
CREATE INDEX IF NOT EXISTS idx_mortalidad_tipo ON mortalidad_general(tipo_cuy);
CREATE INDEX IF NOT EXISTS idx_mortalidad_fecha ON mortalidad_general(fecha);

-- =============================================
-- MENSAJE FINAL
-- =============================================

DO $$ 
BEGIN
    RAISE NOTICE '✅ Base de datos configurada correctamente';
    RAISE NOTICE '🆕 Tabla mortalidad_general creada (unificada)';
    RAISE NOTICE '📊 Tablas creadas: galpones, pozas, partos_simplificada, mortalidad_general, destetes_simplificada, control_engorde, ventas, gastos';
    RAISE NOTICE '🔄 Datos de mortalidad_lactancia migrados a mortalidad_general';
END $$;