CREATE TABLE IF NOT EXISTS estudiantes (
    id SERIAL PRIMARY KEY,
    carne VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    nota_actual NUMERIC(5,2) NOT NULL
);

INSERT INTO estudiantes (carne, nombre, nota_actual)
VALUES
('C23913', 'Elizabeth Huang', 88.00),
('C67890', 'Luis Mora', 75.50),
('A11111', 'María Solano', 91.25);