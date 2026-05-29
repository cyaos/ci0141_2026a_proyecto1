<template>
  <section class="border-t border-border bg-surface flex flex-col" style="height:260px">
    <div class="flex items-center gap-3 px-4 py-2 border-b border-border shrink-0">
      <span class="field-label">BITÁCORA WAL</span>
      <span class="text-text-dim text-xs">({{ recovery.filteredWal.length }} / {{ recovery.walEntries.length }} entradas)</span>

      <div class="flex items-center gap-2 ml-4">
        <span class="field-label">TID</span>
        <input
          v-model="recovery.walFilterTid"
          class="field-input w-28 text-xs"
          placeholder="T1a2b3c4d"
        />
      </div>

      <div class="flex items-center gap-2">
        <span class="field-label">DESDE</span>
        <input
          v-model="recovery.walFilterSince"
          type="datetime-local"
          class="field-input text-xs"
        />
      </div>

      <div class="flex items-center gap-2">
        <span class="field-label">HASTA</span>
        <input
          v-model="recovery.walFilterUntil"
          type="datetime-local"
          class="field-input text-xs"
        />
      </div>

      <button class="pill ml-auto" @click="recovery.fetchWal()">Actualizar</button>
    </div>

    <div class="flex-1 overflow-y-auto font-mono text-xs">
      <div v-if="recovery.walLoading" class="px-4 py-3 text-text-dim">Cargando…</div>
      <div v-else-if="recovery.filteredWal.length === 0" class="px-4 py-3 text-text-dim">
        Sin entradas{{ recovery.walFilterTid || recovery.walFilterSince ? ' para los filtros aplicados' : '' }}.
      </div>
      <table v-else class="w-full">
        <thead class="sticky top-0 bg-surface border-b border-border">
          <tr class="text-left text-text-dim">
            <th class="px-3 py-1 w-24">TID</th>
            <th class="px-3 py-1 w-20">OP</th>
            <th class="px-3 py-1 w-20">MOTOR</th>
            <th class="px-3 py-1 w-20">TABLA</th>
            <th class="px-3 py-1">QUERY</th>
            <th class="px-3 py-1 w-32">BEFORE</th>
            <th class="px-3 py-1 w-32">AFTER</th>
            <th class="px-3 py-1 w-40">TIMESTAMP</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(entry, i) in recovery.filteredWal"
            :key="i"
            class="border-b border-border hover:bg-surface-2/50"
            :class="rowClass(entry.op)"
          >
            <td class="px-3 py-1 text-accent">{{ entry.tid }}</td>
            <td class="px-3 py-1 font-bold" :class="opClass(entry.op)">{{ entry.op }}</td>
            <td class="px-3 py-1 text-text-dim">{{ entry.engine || '—' }}</td>
            <td class="px-3 py-1 text-text-dim">{{ entry.table || '—' }}</td>
            <td class="px-3 py-1 text-text-primary truncate max-w-xs" :title="entry.query">
              {{ entry.query || '—' }}
            </td>
            <td class="px-3 py-1 text-text-dim">
              <span v-if="entry.before && entry.before.length">
                {{ JSON.stringify(entry.before[0]).slice(0, 40) }}
              </span>
              <span v-else>—</span>
            </td>
            <td class="px-3 py-1 text-text-dim">
              <span v-if="entry.after && entry.after.length">
                {{ JSON.stringify(entry.after[0]).slice(0, 40) }}
              </span>
              <span v-else>—</span>
            </td>
            <td class="px-3 py-1 text-text-dim">{{ entry.timestamp.slice(0, 19).replace('T', ' ') }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRecoveryStore } from '../../stores/recovery';

const recovery = useRecoveryStore();

function opClass(op: string) {
  if (op === 'COMMIT') return 'text-accent';
  if (op === 'ABORT' || op === 'FAILURE_SIMULATED') return 'text-danger';
  if (op === 'BEGIN') return 'text-text-dim';
  return 'text-text-primary';
}

function rowClass(op: string) {
  if (op === 'FAILURE_SIMULATED') return 'bg-danger/5';
  if (op === 'COMMIT') return 'bg-accent/5';
  return '';
}
</script>
