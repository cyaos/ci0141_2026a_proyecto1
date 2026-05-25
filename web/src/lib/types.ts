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

export type ProtocolName =
  | "no_undo_no_redo"
  | "no_undo_redo"
  | "undo_no_redo"
  | "undo_redo";

export interface RecoveryStatus {
  protocol: ProtocolName | string;
  current_tid: string | null;
  wal_count: number;
  protocolos_disponibles: string[];
}

export interface WalEntry {
  tid: string;
  op: string;
  engine?: string;
  query?: string;
  before?: any[];
  after?: any[];
  table?: string;
  timestamp: string;
}

export interface FailureReport {
  protocolo: string;
  estado: string;
  tids_undo: string[];
  tids_redo: string[];
  ops_undo: any[];
  ops_redo: any[];
}
