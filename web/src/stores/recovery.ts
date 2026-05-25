import { defineStore } from 'pinia';
import { api } from '../lib/api';
import type { ProtocolName, RecoveryStatus, FailureReport, WalEntry } from '../lib/types';

interface State {
  protocol: string;
  currentTid: string | null;
  walCount: number;
  protocolos: string[];
  pollHandle: number | null;
  lastReport: FailureReport | null;
  lastError: string | null;
  switching: boolean;
  walEntries: WalEntry[];
  walFilterTid: string;
  walFilterSince: string;
  walFilterUntil: string;
  walLoading: boolean;
}

export const useRecoveryStore = defineStore('recovery', {
  state: (): State => ({
    protocol: '',
    currentTid: null,
    walCount: 0,
    protocolos: [],
    pollHandle: null,
    lastReport: null,
    lastError: null,
    switching: false,
    walEntries: [],
    walFilterTid: '',
    walFilterSince: '',
    walFilterUntil: '',
    walLoading: false,
  }),
  getters: {
    isActive: (state) => state.currentTid !== null,
    hasProtocol: (state) => state.protocol !== '',
    filteredWal: (state): WalEntry[] => {
      let entries = state.walEntries;
      const tid = state.walFilterTid.trim();
      const since = state.walFilterSince;
      const until = state.walFilterUntil;
      if (tid) entries = entries.filter(e => e.tid.includes(tid));
      if (since) entries = entries.filter(e => e.timestamp >= since);
      if (until) entries = entries.filter(e => e.timestamp <= until + 'Z');
      return entries;
    },
  },
  actions: {
    _apply(status: RecoveryStatus) {
      this.protocol = status.protocol;
      this.currentTid = status.current_tid;
      this.walCount = status.wal_count;
      this.protocolos = status.protocolos_disponibles;
    },
    async refresh() {
      try {
        const status = await api.recoveryStatus();
        this._apply(status);
      } catch (err: any) {
        this.lastError = err.message || 'Error al consultar estado de recuperación';
      }
    },
    async fetchWal() {
      this.walLoading = true;
      try {
        this.walEntries = await api.getWal();
      } catch (err: any) {
        this.lastError = err.message || 'Error al cargar WAL';
      } finally {
        this.walLoading = false;
      }
    },
    async selectProtocol(name: ProtocolName) {
      this.switching = true;
      this.lastReport = null;
      try {
        const status = await api.setProtocol(name);
        this._apply(status);
      } catch (err: any) {
        this.lastError = err.message || 'Error al seleccionar protocolo';
      } finally {
        this.switching = false;
      }
    },
    async simulateFailure(): Promise<FailureReport | null> {
      try {
        const report = await api.simulateFailure();
        this.lastReport = report;
        await this.refresh();
        await this.fetchWal();
        return report;
      } catch (err: any) {
        this.lastError = err.message || 'Error simulando fallo';
        return null;
      }
    },
    async commit() {
      try {
        const status = await api.commitTx();
        this._apply(status);
        await this.fetchWal();
      } catch (err: any) {
        this.lastError = err.message || 'Error en commit';
      }
    },
    startPolling() {
      if (this.pollHandle !== null) return;
      this.refresh();
      this.fetchWal();
      this.pollHandle = window.setInterval(() => {
        this.refresh();
        this.fetchWal();
      }, 3000);
    },
    stopPolling() {
      if (this.pollHandle !== null) {
        window.clearInterval(this.pollHandle);
        this.pollHandle = null;
      }
    },
    clearReport() {
      this.lastReport = null;
    },
  }
});
