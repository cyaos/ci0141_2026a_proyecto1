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
      <span>Protocol: —</span>
      <span>WAL: —</span>
      <span>TXN: —</span>
    </div>

    <div class="ml-auto text-text-dim">
      {{ entities.loading ? 'cargando…' : 'listo' }}
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useEnginesStore } from '../../stores/engines';
import { useEntitiesStore } from '../../stores/entities';
import StatusDot from '../primitives/StatusDot.vue';

const engines = useEnginesStore();
const entities = useEntitiesStore();
</script>
