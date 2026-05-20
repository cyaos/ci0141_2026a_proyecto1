from api.schemas import JugadorUpdate
from src.api.routes import jugadores
from fastapi import APIRouter, HTTPException
from api.deps import get_engine
from api.schemas import serialize_row, RankingCreate, RankingUpdate

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
def insert_ranking(engine: str, body: RankingCreate) -> dict:
  conexion = get_engine(engine)
  ranking = conexion.insertar_ranking(
    id_jugador=body.id_jugador,
    id_videojuego=body.id_videojuego,
    temporada=body.temporada,
    posicion=body.posicion,
    puntaje=body.puntaje
  )
  return serialize_row(ranking)

@router.patch("/{id_ranking}")
def update_ranking(engine: str, id_ranking: int, body: RankingUpdate) -> dict:
  conexion = get_engine(engine)
  ranking = conexion.actualizar_ranking(
    id_ranking=id_ranking,
    posicion=body.posicion,
    puntaje=body.puntaje,
    partidas_jugadas=body.partidas_jugadas,
    partidas_ganadas=body.partidas_ganadas
  )
  return _serialize_or_404(ranking, id_ranking)

@router.delete("/{id_ranking}")
def delete_ranking(engine: str, id_ranking: int) -> dict:
  conexion = get_engine(engine)
  ranking = conexion.eliminar_ranking(id_ranking)
  return _serialize_or_404(ranking, id_ranking)
