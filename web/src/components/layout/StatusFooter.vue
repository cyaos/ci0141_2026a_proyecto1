<template>
  <footer class="h-8 border-t border-border bg-surface flex items-center px-4 text-xs">
    <div class="flex items-center gap-4">
      <div v-for="s in engines.statuses" :key="s.key" class="flex items-center gap-1.5">
        <StatusDot :active="s.active" />
        <span>{{ s.name }}</span>
        <span :class="s.active ? 'text-text-primary' : 'text-danger'">{{ s.active ? 'OK' : 'OFF' }}</span>
      </div>
    </div>

    <span class="text-text-dim mx-4">·</span>

    <div class="flex items-center gap-4 text-text-dim">
      <span>
        Protocol:
        <span :class="recovery.hasProtocol ? 'text-accent' : ''">
          {{ recovery.protocol || '—' }}
        </span>
      </span>
      <span>WAL: <span class="text-text-primary">{{ recovery.walCount }}</span></span>
      <span>
        TXN:
        <span :class="recovery.isActive ? 'text-accent' : ''">
          {{ recovery.currentTid || '—' }}
        </span>
      </span>
    </div>

    <div class="ml-auto text-text-dim">
      {{ entities.loading ? 'cargando…' : 'listo' }}
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useEnginesStore } from '../../stores/engines';
import { useEntitiesStore } from '../../stores/entities';
import { useRecoveryStore } from '../../stores/recovery';
import StatusDot from '../primitives/StatusDot.vue';

const engines = useEnginesStore();
const entities = useEntitiesStore();
const recovery = useRecoveryStore();
</script>
