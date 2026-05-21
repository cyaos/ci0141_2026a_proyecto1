import { defineStore } from 'pinia';
import { api } from '../lib/api';
import type { EngineKey, EntityName, Jugador, Ranking, JugadorCreate, JugadorUpdate, RankingCreate, RankingUpdate } from '../lib/types';

interface State {
  jugadores: Record<EngineKey, Jugador[]>;
  rankings: Record<EngineKey, Ranking[]>;
  activeTab: EntityName;
  loading: boolean;
  lastError: string | null;
}

export const useEntitiesStore = defineStore('entities', {
  state: (): State => ({
    jugadores: { postgres: [], mongo: [] },
    rankings: { postgres: [], mongo: [] },
    activeTab: "jugadores",
    loading: false,
    lastError: null,
  }),
  actions: {
    setTab(tab: EntityName) {
      this.activeTab = tab;
    },
    async refresh(engine: EngineKey) {
      this.loading = true;
      this.lastError = null;
      try {
        if (this.activeTab === "jugadores") {
          this.jugadores[engine] = await api.listJugadores(engine);
        } else {
          this.rankings[engine] = await api.listRankings(engine);
        }
      } catch (err: any) {
        this.lastError = err.message || "Error al obtener datos";
      } finally {
        this.loading = false;
      }
    },
    async createJugador(engine: EngineKey, payload: JugadorCreate) {
      this.loading = true;
      this.lastError = null;
      try {
        await api.createJugador(engine, payload);
        await this.refresh(engine);
      } catch (err: any) {
        this.lastError = err.message || "Error al crear jugador";
        throw err;
      } finally {
        this.loading = false;
      }
    },
    async updateJugador(engine: EngineKey, id: number, payload: JugadorUpdate) {
      this.loading = true;
      this.lastError = null;
      try {
        await api.updateJugador(engine, id, payload);
        await this.refresh(engine);
      } catch (err: any) {
        this.lastError = err.message || "Error al actualizar jugador";
        throw err;
      } finally {
        this.loading = false;
      }
    },
    async deleteJugador(engine: EngineKey, id: number) {
      this.loading = true;
      this.lastError = null;
      try {
        await api.deleteJugador(engine, id);
        await this.refresh(engine);
      } catch (err: any) {
        this.lastError = err.message || "Error al eliminar jugador";
        throw err;
      } finally {
        this.loading = false;
      }
    },
    async createRanking(engine: EngineKey, payload: RankingCreate) {
      this.loading = true;
      this.lastError = null;
      try {
        await api.createRanking(engine, payload);
        await this.refresh(engine);
      } catch (err: any) {
        this.lastError = err.message || "Error al crear ranking";
        throw err;
      } finally {
        this.loading = false;
      }
    },
    async updateRanking(engine: EngineKey, id: number, payload: RankingUpdate) {
      this.loading = true;
      this.lastError = null;
      try {
        await api.updateRanking(engine, id, payload);
        await this.refresh(engine);
      } catch (err: any) {
        this.lastError = err.message || "Error al actualizar ranking";
        throw err;
      } finally {
        this.loading = false;
      }
    },
    async deleteRanking(engine: EngineKey, id: number) {
      this.loading = true;
      this.lastError = null;
      try {
        await api.deleteRanking(engine, id);
        await this.refresh(engine);
      } catch (err: any) {
        this.lastError = err.message || "Error al eliminar ranking";
        throw err;
      } finally {
        this.loading = false;
      }
    }
  }
});
