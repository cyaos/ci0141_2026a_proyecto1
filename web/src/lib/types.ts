export type EngineKey = "postgres" | "mongo";

export interface EngineStatus {
  key: EngineKey;
  name: string;
  host: string;
  port: number;
  active: boolean;
  error: string | null;
}

export interface Jugador {
  id_jugador: number;
  nombre_usuario: string;
  pais: string;
  fecha_registro: string;
}

export interface Ranking {
  id_ranking: number;
  id_jugador?: number;
  id_videojuego?: number;
  nombre_usuario?: string;
  videojuego?: string;
  temporada: string;
  posicion: number;
  puntaje: number;
  partidas_jugadas: number;
  partidas_ganadas: number;
}

export interface JugadorCreate {
  nombre_usuario: string;
  pais: string;
  fecha_registro: string;
}

export interface JugadorUpdate {
  nombre_usuario: string;
  pais: string;
}

export interface RankingCreate {
  id_jugador: number;
  id_videojuego: number;
  temporada: string;
  posicion: number;
  puntaje: number;
}

export interface RankingUpdate {
  posicion: number;
  puntaje: number;
  partidas_jugadas: number;
  partidas_ganadas: number;
}

export type EntityName = "jugadores" | "rankings";
