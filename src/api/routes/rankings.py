from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool
from api.deps import get_engine
from api.schemas import serialize_row, RankingCreate, RankingUpdate
from api import recovery_state
from api.routes.jugadores import _sql_literal, _via_protocolo

router = APIRouter(prefix="/api/{engine}/rankings", tags=["rankings"])


def _serialize_or_404(ranking: dict | None, id_ranking: int) -> dict:
  if ranking is None:
    raise HTTPException(status_code=404, detail=f"Ranking {id_ranking} no encontrado.")
  return serialize_row(ranking)


@router.get("")
def list_rankings(engine: str) -> list[dict]:
  conexion = get_engine(engine)
  rankings = conexion.listar_rankings()
  return [serialize_row(ranking) for ranking in rankings]


@router.post("")
async def insert_ranking(engine: str, body: RankingCreate) -> dict:
  state = recovery_state.get_state()
  if engine == "postgres" and state.current_tid is not None:
    sql = (
      f"INSERT INTO rankings (id_jugador, id_videojuego, temporada, posicion, puntaje, "
      f"partidas_jugadas, partidas_ganadas) VALUES ("
      f"{int(body.id_jugador)}, {int(body.id_videojuego)}, "
      f"{_sql_literal(body.temporada)}, {int(body.posicion)}, {int(body.puntaje)}, 0, 0)"
    )
    return await _via_protocolo("INSERT", sql)

  def _exec():
    conexion = get_engine(engine)
    return conexion.insertar_ranking(
      id_jugador=body.id_jugador,
      id_videojuego=body.id_videojuego,
      temporada=body.temporada,
      posicion=body.posicion,
      puntaje=body.puntaje,
    )

  ranking = await run_in_threadpool(_exec)
  return serialize_row(ranking)


@router.patch("/{id_ranking}")
async def update_ranking(engine: str, id_ranking: int, body: RankingUpdate) -> dict:
  state = recovery_state.get_state()
  if engine == "postgres" and state.current_tid is not None:
    sql = (
      f"UPDATE rankings SET "
      f"posicion = {int(body.posicion)}, "
      f"puntaje = {int(body.puntaje)}, "
      f"partidas_jugadas = {int(body.partidas_jugadas)}, "
      f"partidas_ganadas = {int(body.partidas_ganadas)}, "
      f"fecha_actualizacion = CURRENT_TIMESTAMP "
      f"WHERE id_ranking = {int(id_ranking)}"
    )
    return await _via_protocolo("UPDATE", sql)

  def _exec():
    conexion = get_engine(engine)
    return conexion.actualizar_ranking(
      id_ranking=id_ranking,
      posicion=body.posicion,
      puntaje=body.puntaje,
      partidas_jugadas=body.partidas_jugadas,
      partidas_ganadas=body.partidas_ganadas,
    )

  ranking = await run_in_threadpool(_exec)
  return _serialize_or_404(ranking, id_ranking)


@router.delete("/{id_ranking}")
async def delete_ranking(engine: str, id_ranking: int) -> dict:
  state = recovery_state.get_state()
  if engine == "postgres" and state.current_tid is not None:
    sql = f"DELETE FROM rankings WHERE id_ranking = {int(id_ranking)}"
    return await _via_protocolo("DELETE", sql)

  def _exec():
    conexion = get_engine(engine)
    return conexion.eliminar_ranking(id_ranking)

  ranking = await run_in_threadpool(_exec)
  return _serialize_or_404(ranking, id_ranking)
