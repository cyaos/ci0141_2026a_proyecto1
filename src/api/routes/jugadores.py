from fastapi import APIRouter, HTTPException
from api.deps import get_engine
from api.schemas import serialize_row, JugadorCreate, JugadorUpdate

router = APIRouter(prefix="/api/{engine}/jugadores", tags=["jugadores"])


def _serialize_or_404(jugador: dict | None, id_jugador: int) -> dict:
  if jugador is None:
    raise HTTPException(status_code=404, detail=f"Jugador {id_jugador} no encontrado.")
  return serialize_row(jugador)


@router.get("")
def list_jugadores(engine: str) -> list[dict]:
  conexion = get_engine(engine)
  jugadores = conexion.listar_jugadores()
  return [serialize_row(jugador) for jugador in jugadores]

@router.post("")
def insert_jugador(engine: str, body: JugadorCreate) -> dict:
  conexion = get_engine(engine)
  jugador = conexion.insertar_jugador(
    nombre_usuario=body.nombre_usuario,
    pais=body.pais,
    fecha_registro=body.fecha_registro
  )
  return serialize_row(jugador)

@router.patch("/{id_jugador}")
def update_jugador(engine: str, id_jugador: int, body: JugadorUpdate) -> dict:
  conexion = get_engine(engine)
  jugador = conexion.actualizar_jugador(
    id_jugador=id_jugador,
    nombre_usuario=body.nombre_usuario,
    pais=body.pais
  )
  return _serialize_or_404(jugador, id_jugador)

@router.delete("/{id_jugador}")
def delete_jugador(engine: str, id_jugador: int) -> dict:
  conexion = get_engine(engine)
  jugador = conexion.eliminar_jugador(id_jugador)
  return _serialize_or_404(jugador, id_jugador)
