<template>
  <header class="h-12 border-b border-border bg-surface flex items-center justify-between px-4">
    <div class="flex items-center gap-6">
      <h1 class="font-bold flex items-center gap-2">
        <span class="text-accent">DB</span>
        <span class="text-text-primary">Client UCR</span>
        <span class="text-text-dim text-xs font-normal">/ stage 1</span>
      </h1>

      <div class="flex items-center gap-3">
        <span class="field-label">PROTOCOLO</span>
        <div class="flex items-center gap-2">
          <button
            class="pill"
            :class="recovery.protocol === 'no_undo_no_redo' ? 'stage-2-active' : 'stage-2'"
            :disabled="recovery.switching"
            @click="select('no_undo_no_redo')"
          >No-Undo/No-Redo</button>
          <button
            class="pill"
            :class="recovery.protocol === 'no_undo_redo' ? 'stage-2-active' : 'stage-2'"
            :disabled="recovery.switching"
            @click="select('no_undo_redo')"
          >No-Undo/Redo</button>
          <button
            class="pill"
            :class="recovery.protocol === 'undo_no_redo' ? 'stage-2-active' : 'stage-2'"
            :disabled="recovery.switching"
            @click="select('undo_no_redo')"
          >Undo/No-Redo</button>
          <button
            class="pill"
            :class="recovery.protocol === 'undo_redo' ? 'stage-2-active' : 'stage-2'"
            :disabled="recovery.switching"
            @click="select('undo_redo')"
          >Undo/Redo</button>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <span class="text-xs text-accent font-mono">{{ recovery.currentTid || '—' }}</span>

      <button
        class="btn"
        :class="recovery.isActive ? 'btn-primary' : 'stage-2'"
        :disabled="!recovery.isActive"
        @click="commit"
      >✓ Commit</button>

      <button
        class="btn"
        :class="recovery.isActive ? 'btn-danger' : 'stage-2'"
        :disabled="!recovery.isActive"
        @click="abort"
      >✗ Abort</button>

      <button
        class="btn"
        :class="recovery.isActive ? 'btn-primary' : 'stage-2'"
        :disabled="!recovery.isActive"
        @click="simular"
      >Simular fallo</button>

    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue';
import { useRecoveryStore } from '../../stores/recovery';
import { useEntitiesStore } from '../../stores/entities';
import { useEnginesStore } from '../../stores/engines';
import type { ProtocolName } from '../../lib/types';

const recovery = useRecoveryStore();
const entities = useEntitiesStore();
const engines = useEnginesStore();

async function select(name: ProtocolName) {
  await recovery.selectProtocol(name);
  recovery.fetchWal();
  entities.refresh(engines.activeEngine);
}

async function commit() {
  await recovery.commit();
  entities.refresh(engines.activeEngine);
}

async function abort() {
  await recovery.abort();
  entities.refresh(engines.activeEngine);
}

async function simular() {
  const report = await recovery.simulateFailure();
  if (report) {
    await entities.refresh(engines.activeEngine);
    const detalle = [
      `Protocolo: ${report.protocolo}`,
      `Estado: ${report.estado}`,
      `TIDs UNDO: ${report.tids_undo.length ? report.tids_undo.join(', ') : '—'}`,
      `TIDs REDO: ${report.tids_redo.length ? report.tids_redo.join(', ') : '—'}`,
      `Ops UNDO: ${report.ops_undo.length}, Ops REDO: ${report.ops_redo.length}`,
    ].join('\n');
    window.alert(`Recuperación ejecutada:\n\n${detalle}`);
  }
}

onMounted(() => recovery.startPolling());
onBeforeUnmount(() => recovery.stopPolling());
</script>
