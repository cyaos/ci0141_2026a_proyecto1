from typing import Literal, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel

EngineName = Literal["postgres", "mongo"]

class JugadorCreate(BaseModel):
    nombre_usuario: str
    pais: str
    fecha_registro: str

class JugadorUpdate(BaseModel):
    nombre_usuario: str
    pais: str

class RankingCreate(BaseModel):
    id_jugador: int
    id_videojuego: int
    temporada: str
    posicion: int
    puntaje: int

class RankingUpdate(BaseModel):
    posicion: int
    puntaje: int
    partidas_jugadas: int
    partidas_ganadas: int

class EngineStatus(BaseModel):
    key: str
    name: str
    host: str
    port: int
    active: bool
    error: Optional[str] = None

def serialize_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, dict):
        return {key: serialize_value(nested_value) for key, nested_value in value.items()}
    elif isinstance(value, list):
        return [serialize_value(list_item) for list_item in value]
    return value

def serialize_row(row: dict) -> dict:
    return serialize_value(row)
