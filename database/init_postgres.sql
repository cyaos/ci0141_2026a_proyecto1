-- Dominio: rankings competitivos de videojuegos
-- Datos MOCK

DROP TABLE IF EXISTS partidas CASCADE;
DROP TABLE IF EXISTS rankings CASCADE;
DROP TABLE IF EXISTS jugadores CASCADE;
DROP TABLE IF EXISTS videojuegos CASCADE;

CREATE TABLE IF NOT EXISTS jugadores (
    id_jugador SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    pais VARCHAR(80) NOT NULL,
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS videojuegos (
    id_videojuego SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL UNIQUE,
    genero VARCHAR(60) NOT NULL,
    plataforma VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS rankings (
    id_ranking SERIAL PRIMARY KEY,
    id_jugador INT NOT NULL REFERENCES jugadores(id_jugador),
    id_videojuego INT NOT NULL REFERENCES videojuegos(id_videojuego),
    temporada VARCHAR(20) NOT NULL,
    posicion INT NOT NULL,
    puntaje INT NOT NULL,
    partidas_jugadas INT NOT NULL DEFAULT 0,
    partidas_ganadas INT NOT NULL DEFAULT 0,
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_jugador, id_videojuego, temporada)
);

CREATE TABLE IF NOT EXISTS partidas (
    id_partida SERIAL PRIMARY KEY,
    id_jugador INT NOT NULL REFERENCES jugadores(id_jugador),
    id_videojuego INT NOT NULL REFERENCES videojuegos(id_videojuego),
    temporada VARCHAR(20) NOT NULL,
    resultado VARCHAR(20) NOT NULL CHECK (resultado IN ('victoria', 'derrota', 'empate')),
    puntos_obtenidos INT NOT NULL,
    fecha_partida TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO jugadores (nombre_usuario, pais, fecha_registro) VALUES
('ShadowCR', 'Costa Rica', '2025-01-12'),
('LunaPixel', 'Costa Rica', '2025-02-08'),
('DragonMX', 'Mexico', '2024-11-21'),
('NovaGT', 'Guatemala', '2025-03-02'),
('ByteHunter', 'Colombia', '2024-09-17'),
('AstraPlay', 'Argentina', '2025-04-04'),
('KiraStorm', 'Chile', '2024-12-10'),
('NeoRacer', 'Panama', '2025-01-30'),
('PixelWolf', 'Peru', '2024-10-05'),
('MangoRush', 'Costa Rica', '2025-05-01');

INSERT INTO videojuegos (titulo, genero, plataforma) VALUES
('Valorant', 'Shooter tactico', 'PC'),
('Rocket League', 'Deportes/arcade', 'Multiplataforma'),
('League of Legends', 'MOBA', 'PC'),
('Fortnite', 'Battle royale', 'Multiplataforma'),
('Super Smash Bros. Ultimate', 'Lucha', 'Nintendo Switch');

INSERT INTO rankings (id_jugador, id_videojuego, temporada, posicion, puntaje, partidas_jugadas, partidas_ganadas) VALUES
(1, 1, '2026-A', 15, 2450, 80, 52),
(2, 1, '2026-A', 22, 2310, 76, 47),
(3, 1, '2026-A', 9, 2680, 91, 63),
(4, 2, '2026-A', 11, 2525, 68, 45),
(5, 2, '2026-A', 18, 2390, 72, 44),
(6, 3, '2026-A', 7, 2755, 88, 61),
(7, 3, '2026-A', 13, 2570, 84, 55),
(8, 4, '2026-A', 25, 2180, 60, 34),
(9, 4, '2026-A', 16, 2435, 73, 46),
(10, 5, '2026-A', 6, 2810, 95, 70),
(1, 2, '2026-A', 30, 2050, 42, 22),
(2, 3, '2026-A', 19, 2365, 79, 49);

INSERT INTO partidas (id_jugador, id_videojuego, temporada, resultado, puntos_obtenidos) VALUES
(1, 1, '2026-A', 'victoria', 25),
(2, 1, '2026-A', 'derrota', -12),
(3, 1, '2026-A', 'victoria', 30),
(4, 2, '2026-A', 'victoria', 22),
(5, 2, '2026-A', 'empate', 5),
(6, 3, '2026-A', 'victoria', 28),
(7, 3, '2026-A', 'derrota', -10),
(8, 4, '2026-A', 'victoria', 20),
(9, 4, '2026-A', 'derrota', -8),
(10, 5, '2026-A', 'victoria', 32);
