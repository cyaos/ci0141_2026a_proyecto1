# CI-0141 Proyecto 1: Cliente de Bases de Datos Distribuidas

## Descripción

Cliente integrado para motores de bases de datos distribuidas, capaz de conectarse a motores de distinta naturaleza (PostgreSQL y MongoDB), ejecutar operaciones CRUD, y — en su fase completa — registrar una bitácora transaccional tipo Write-Ahead Log (WAL) y simular protocolos de recuperación ante fallos.

## Estado actual

- **Stage 1 (en repositorio)**: cliente CLI + API REST (FastAPI) + UI web (Vue 3) con paridad CRUD sobre las entidades `jugadores` y `rankings` para ambos motores. Cambio de motor activo en caliente. Monitoreo de salud de conexiones por polling.
- **Stage 2 (pendiente)**: transacciones explícitas (BEGIN/COMMIT/ROLLBACK), WAL persistente, los cuatro protocolos de recuperación ante fallos, y simulación de fallos controlados.

## Componentes

```
src/main.py                  Cliente CLI (menú interactivo)
src/connections/             Adaptadores compartidos por CLI y API
src/api/                     FastAPI — REST sobre los adaptadores
web/                         Vue 3 + Vite + Tailwind — UI cliente
database/                    Scripts de inicialización de PostgreSQL y MongoDB
docker-compose.yml           Levanta PostgreSQL, MongoDB y pgAdmin
```

## Requisitos

- Docker + Docker Compose
- Python 3.12+
- Node.js 18+

## Configuración inicial

```bash
# 1. Levantar las bases de datos
docker compose up -d

# 2. Crear entorno Python e instalar dependencias del backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Instalar dependencias del frontend
cd web && npm install && cd ..
```

pgAdmin queda disponible en http://localhost:5050 (`admin@ucr.ac.cr` / `admin123`).

## Ejecución

Tres modalidades, no excluyentes:

### Cliente CLI
```bash
python src/main.py
```

### API REST + UI Web (recomendado)
En dos terminales separadas:

```bash
# Terminal A — API
PYTHONPATH=src .venv/bin/uvicorn api.main:app --reload

# Terminal B — Frontend
cd web && npm run dev
```

UI disponible en http://localhost:5173. Documentación interactiva de la API en http://localhost:8000/docs.

## Notas

- `docker compose up -d` solo ejecuta los scripts de seed la primera vez que el volumen se crea. Para re-sembrar manualmente:
  ```bash
  docker exec -i ci0141_postgres psql -U admin -d distributed_client_db < database/init_postgres.sql
  docker exec -i ci0141_mongodb mongosh --quiet < database/init_mongo.js
  ```
- El uso de IA durante el desarrollo está documentado en [`AI_USAGE.md`](AI_USAGE.md) conforme a la Sección 1 de la especificación.
