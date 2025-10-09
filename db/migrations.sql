-- Galpones y pozas
CREATE TABLE IF NOT EXISTS galpones (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) UNIQUE NOT NULL,
  descripcion TEXT
);

CREATE TABLE IF NOT EXISTS pozas (
  id SERIAL PRIMARY KEY,
  galpon_id INT REFERENCES galpones(id) ON DELETE CASCADE,
  nombre VARCHAR(100) NOT NULL,
  tipo VARCHAR(50) DEFAULT 'reproductores', -- reproductores, destete, engorde, reemplazo
  capacidad INT DEFAULT 0
);

-- Reproductores (stock actual por poza)
CREATE TABLE IF NOT EXISTS reproductores (
  id SERIAL PRIMARY KEY,
  galpon_id INT REFERENCES galpones(id),
  poza_id INT REFERENCES pozas(id),
  sexo VARCHAR(10),
  hembras INT DEFAULT 0,
  machos INT DEFAULT 0,
  fecha_ingreso DATE,
  origen VARCHAR(50)
);

-- Partos
CREATE TABLE IF NOT EXISTS partos (
  id SERIAL PRIMARY KEY,
  galpon_id INT REFERENCES galpones(id),
  poza_id INT REFERENCES pozas(id),
  fecha DATE,
  nacidos_hembras INT DEFAULT 0,
  nacidos_machos INT DEFAULT 0,
  muertos INT DEFAULT 0,
  observaciones TEXT
);

-- Destetes
CREATE TABLE IF NOT EXISTS destetes (
  id SERIAL PRIMARY KEY,
  parto_id INT REFERENCES partos(id),
  fecha DATE,
  destetados_hembras INT DEFAULT 0,
  destetados_machos INT DEFAULT 0,
  muertos INT DEFAULT 0,
  galpon_destino INT,
  poza_destino INT,
  observaciones TEXT
);

-- Movimientos
CREATE TABLE IF NOT EXISTS movimientos (
  id SERIAL PRIMARY KEY,
  fecha TIMESTAMP DEFAULT now(),
  tipo VARCHAR(50),
  origen_galpon INT,
  origen_poza INT,
  destino_galpon INT,
  destino_poza INT,
  hembras INT DEFAULT 0,
  machos INT DEFAULT 0,
  notas TEXT
);

-- Ventas
CREATE TABLE IF NOT EXISTS ventas (
  id SERIAL PRIMARY KEY,
  fecha DATE,
  tipo VARCHAR(50), -- destetados, engorde, descarte, reproductor
  hembras_vendidas INT DEFAULT 0,
  machos_vendidos INT DEFAULT 0,
  precio_unitario NUMERIC DEFAULT 0,
  costo_total NUMERIC DEFAULT 0
);

-- Notificaciones (básico)
CREATE TABLE IF NOT EXISTS notificaciones (
  id SERIAL PRIMARY KEY,
  titulo TEXT,
  mensaje TEXT,
  prioridad VARCHAR(20) DEFAULT 'media',
  fecha_creacion TIMESTAMP DEFAULT now(),
  leida BOOLEAN DEFAULT FALSE
);
