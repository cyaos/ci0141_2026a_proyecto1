from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool
from api.deps import get_engine
from api.schemas import serialize_row, JugadorCreate, JugadorUpdate
from api import recovery_state

router = APIRouter(prefix="/api/{engine}/jugadores", tags=["jugadores"])


def _serialize_or_404(jugador: dict | None, id_jugador: int) -> dict:
  if jugador is None:
    raise HTTPException(status_code=404, detail=f"Jugador {id_jugador} no encontrado.")
  return serialize_row(jugador)


def _sql_literal(value) -> str:
  """Convierte un valor Python a literal SQL para construir queries."""
  if value is None:
    return 'NULL'
  if isinstance(value, bool):
    return 'TRUE' if value else 'FALSE'
  if isinstance(value, (int, float)):
    return str(value)
  return "'" + str(value).replace("'", "''") + "'"


async def _via_protocolo(verb: str, sql: str) -> dict:
  """Ejecuta DML vía el protocolo de recuperación activo y retorna la fila resultante."""
  state = recovery_state.get_state()
  tid = await state.ensure_tx()
  pg = await state.get_pg()
  before, after = await state.recovery_mgr.activo.on_write(tid, verb, "postgres", sql, pg)
  fila = None
  if after:
    fila = after[0]
  elif before:
    fila = before[0]
  else:
    # Caso bufferizado (No-Undo): retornar un placeholder con los datos enviados
    fila = {"buffered": True, "tid": tid, "protocolo": state.recovery_mgr.protocolo_activo()}
  return serialize_row(fila)


@router.get("")
def list_jugadores(engine: str) -> list[dict]:
  conexion = get_engine(engine)
  jugadores = conexion.listar_jugadores()
  return [serialize_row(jugador) for jugador in jugadores]


@router.post("")
async def insert_jugador(engine: str, body: JugadorCreate) -> dict:
  state = recovery_state.get_state()
  if engine == "postgres" and state.current_tid is not None:
    sql = (
      f"INSERT INTO jugadores (nombre_usuario, pais, fecha_registro) "
      f"VALUES ({_sql_literal(body.nombre_usuario)}, "
      f"{_sql_literal(body.pais)}, "
      f"{_sql_literal(body.fecha_registro)})"
    )
    return await _via_protocolo("INSERT", sql)

  # Camino normal (sin TX activa): comportamiento original síncrono
  def _exec():
    conexion = get_engine(engine)
    return conexion.insertar_jugador(
      nombre_usuario=body.nombre_usuario,
      pais=body.pais,
      fecha_registro=body.fecha_registro,
    )

  jugador = await run_in_threadpool(_exec)
  return serialize_row(jugador)


@router.patch("/{id_jugador}")
async def update_jugador(engine: str, id_jugador: int, body: JugadorUpdate) -> dict:
  state = recovery_state.get_state()
  if engine == "postgres" and state.current_tid is not None:
    sql = (
      f"UPDATE jugadores SET "
      f"nombre_usuario = {_sql_literal(body.nombre_usuario)}, "
      f"pais = {_sql_literal(body.pais)} "
      f"WHERE id_jugador = {int(id_jugador)}"
    )
    return await _via_protocolo("UPDATE", sql)

  def _exec():
    conexion = get_engine(engine)
    return conexion.actualizar_jugador(
      id_jugador=id_jugador,
      nombre_usuario=body.nombre_usuario,
      pais=body.pais,
    )

  jugador = await run_in_threadpool(_exec)
  return _serialize_or_404(jugador, id_jugador)


@router.delete("/{id_jugador}")
async def delete_jugador(engine: str, id_jugador: int) -> dict:
  state = recovery_state.get_state()
  if engine == "postgres" and state.current_tid is not None:
    # Borrado simple por la PK (el adapter sync borra antes en partidas/rankings)
    sql = f"DELETE FROM jugadores WHERE id_jugador = {int(id_jugador)}"
    return await _via_protocolo("DELETE", sql)

  def _exec():
    conexion = get_engine(engine)
    return conexion.eliminar_jugador(id_jugador)

  jugador = await run_in_threadpool(_exec)
  return _serialize_or_404(jugador, id_jugador)
