from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import jugadores, rankings, engines
from api.deps import get_manager, shutdown

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    get_manager()
    yield
    shutdown()

app = FastAPI(
    title="DBClient UCR API",
    description="Stateless REST API wrapping DB connections",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(engines.router)
app.include_router(jugadores.router)
app.include_router(rankings.router)

@app.get("/")
def liveness_probe():
    return {"service": "dbclient-ucr", "stage": 1}