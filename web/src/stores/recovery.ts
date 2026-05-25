import { defineStore } from 'pinia';
import { api } from '../lib/api';
import type { ProtocolName, RecoveryStatus, FailureReport } from '../lib/types';

interface State {
  protocol: string;
  currentTid: string | null;
  walCount: number;
  protocolos: string[];
  pollHandle: number | null;
  lastReport: FailureReport | null;
  lastError: string | null;
  switching: boolean;
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
  }),
  getters: {
    isActive: (state) => state.currentTid !== null,
    hasProtocol: (state) => state.protocol !== '',
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
      } catch (err: any) {
        this.lastError = err.message || 'Error en commit';
      }
    },
    startPolling() {
      if (this.pollHandle !== null) return;
      this.refresh();
      this.pollHandle = window.setInterval(() => this.refresh(), 3000);
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
