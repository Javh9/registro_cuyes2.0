-- Tabla animales
CREATE TABLE IF NOT EXISTS animales (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    sexo VARCHAR(10) NOT NULL CHECK (sexo IN ('macho', 'hembra')),
    fecha_nacimiento DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'vendido', 'muerto', 'descarte')),
    etapa_productiva VARCHAR(20) DEFAULT 'destete' CHECK (etapa_productiva IN ('reproductor', 'lactancia', 'destete', 'reemplazo', 'engorde')),
    clasificacion VARCHAR(20),
    poza_id INTEGER REFERENCES pozas(id),
    madre_id INTEGER REFERENCES animales(id),
    padre_id INTEGER REFERENCES animales(id),
    peso_actual DECIMAL(8,2) DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- Tabla partos
CREATE TABLE IF NOT EXISTS partos (
    id SERIAL PRIMARY KEY,
    hembra_id INTEGER REFERENCES animales(id),
    poza_id INTEGER REFERENCES pozas(id),
    fecha_parto DATE NOT NULL,
    machos_nacidos INTEGER DEFAULT 0,
    hembras_nacidas INTEGER DEFAULT 0,
    muertos_nacimiento INTEGER DEFAULT 0,
    observaciones TEXT,
    estado VARCHAR(20) DEFAULT 'lactancia' CHECK (estado IN ('lactancia', 'destetado', 'cerrado')),
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Tabla destetes
CREATE TABLE IF NOT EXISTS destetes (
    id SERIAL PRIMARY KEY,
    parto_id INTEGER REFERENCES partos(id),
    fecha_destete DATE NOT NULL,
    machos_destetados INTEGER DEFAULT 0,
    hembras_destetadas INTEGER DEFAULT 0,
    muertos_destete INTEGER DEFAULT 0,
    peso_promedio DECIMAL(8,2),
    destino VARCHAR(20) CHECK (destino IN ('reemplazo', 'engorde', 'venta_directa')),
    poza_destino_id INTEGER REFERENCES pozas(id),
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Tabla movimientos_animales
CREATE TABLE IF NOT EXISTS movimientos_animales (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER REFERENCES animales(id),
    desde_poza_id INTEGER REFERENCES pozas(id),
    hacia_poza_id INTEGER REFERENCES pozas(id),
    motivo TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT NOW()
);