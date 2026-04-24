CREATE TABLE destinos (
    id_destino SERIAL PRIMARY KEY,
    nombre_destino VARCHAR(100) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    codigo_iata VARCHAR(3) UNIQUE NOT NULL, 
    estado_operativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE vuelos (
    id_vuelo SERIAL PRIMARY KEY,
    numero_vuelo VARCHAR(20) UNIQUE NOT NULL,
    id_destino INT REFERENCES destinos(id_destino),
    aerolinea VARCHAR(100) NOT NULL,
    precio_base DECIMAL(10, 2) NOT NULL,
    fecha_salida TIMESTAMP NOT NULL,
    capacidad_total INT NOT NULL,
    asientos_disponibles INT NOT NULL,
    modelo_avion VARCHAR(100) NOT NULL
);