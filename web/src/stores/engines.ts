import { defineStore } from 'pinia';
import { api } from '../lib/api';
import type { EngineStatus, EngineKey } from '../lib/types';

interface State {
  statuses: EngineStatus[];
  activeEngine: EngineKey;
  pollHandle: number | null;
  lastError: string | null;
}

export const useEnginesStore = defineStore('engines', {
  state: (): State => ({
    statuses: [],
    activeEngine: "postgres",
    pollHandle: null,
    lastError: null,
  }),
  getters: {
    active: (state) => state.statuses.find(s => s.key === state.activeEngine)
  },
  actions: {
    async refresh() {
      try {
        const next = await api.status();
        this.applyStatuses(next);
      } catch (err: any) {
        this.lastError = err.message || "Error al obtener estado de motores";
      }
    },
    applyStatuses(next: EngineStatus[]) {
      for (const nextStatus of next) {
        const prevStatus = this.statuses.find(s => s.key === nextStatus.key);
        if (prevStatus && prevStatus.active && !nextStatus.active) {
          this.notifyDropped(nextStatus);
        }
      }
      this.statuses = next;

      const activeStatus = this.statuses.find(s => s.key === this.activeEngine);
      if (!activeStatus?.active) {
        const fallback = this.statuses.find(s => s.active);
        if (fallback) {
          this.activeEngine = fallback.key;
        }
      }
    },
    notifyDropped(status: EngineStatus) {
      this.lastError = `Conexión perdida con motor: ${status.name}`;
    },
    setActive(key: EngineKey) {
      const target = this.statuses.find(s => s.key === key);
      if (target?.active) {
        this.activeEngine = key;
      }
    },
    startPolling() {
      if (this.pollHandle !== null) return;
      this.refresh();
      this.pollHandle = window.setInterval(() => {
        this.refresh();
      }, 5000);
    },
    stopPolling() {
      if (this.pollHandle !== null) {
        window.clearInterval(this.pollHandle);
        this.pollHandle = null;
      }
    },
    clearError() {
      this.lastError = null;
    }
  }
});
