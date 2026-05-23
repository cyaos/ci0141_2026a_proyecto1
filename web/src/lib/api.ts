import type {
  EngineKey,
  EngineStatus,
  Jugador,
  JugadorCreate,
  JugadorUpdate,
  Ranking,
  RankingCreate,
  RankingUpdate
} from './types';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch("/api" + path, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(body.detail || 'API Error', res.status);
  }
  return res.json() as Promise<T>;
}

export const api = {
  status: () => request<EngineStatus[]>('/engines/status'),

  listJugadores: (engine: EngineKey) => request<Jugador[]>(`/${engine}/jugadores`),
  createJugador: (engine: EngineKey, payload: JugadorCreate) => 
    request<Jugador>(`/${engine}/jugadores`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }),
  updateJugador: (engine: EngineKey, id: number, payload: JugadorUpdate) =>
    request<Jugador>(`/${engine}/jugadores/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }),
  deleteJugador: (engine: EngineKey, id: number) =>
    request<Jugador>(`/${engine}/jugadores/${id}`, {
      method: 'DELETE'
    }),

  listRankings: (engine: EngineKey) => request<Ranking[]>(`/${engine}/rankings`),
  createRanking: (engine: EngineKey, payload: RankingCreate) => 
    request<Ranking>(`/${engine}/rankings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }),
  updateRanking: (engine: EngineKey, id: number, payload: RankingUpdate) =>
    request<Ranking>(`/${engine}/rankings/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }),
  deleteRanking: (engine: EngineKey, id: number) =>
    request<Ranking>(`/${engine}/rankings/${id}`, {
      method: 'DELETE'
    })
};
