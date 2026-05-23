<template>
  <aside class="w-60 border-r border-border bg-surface flex flex-col h-full overflow-y-auto">
    <!-- Conexiones -->
    <div class="pt-4 pb-2 px-4 flex items-center justify-between">
      <span class="field-label">Conexiones</span>
      <span class="text-xs text-text-dim">{{ engines.statuses.length }}</span>
    </div>
    <div class="flex flex-col mb-6">
      <ConnectionRow 
        v-for="status in engines.statuses" 
        :key="status.key"
        :status="status"
        :active="status.key === engines.activeEngine"
        @select="engines.setActive"
      />
    </div>

    <!-- Transacciones -->
    <div class="px-4 pb-2 flex items-center gap-2">
      <span class="field-label">Transacciones</span>
      <span class="pill stage-2">stage 2</span>
    </div>
    <div class="px-4 text-xs text-text-dim italic mb-6">
      Disponible al implementar BEGIN / COMMIT / ROLLBACK.
    </div>

    <!-- Spacer and Footer -->
    <div class="mt-auto p-4 border-t border-border/50 text-xs text-text-dim flex flex-col gap-1">
      <div>CI-0141 · Stage 1</div>
      <div>CRUD parity · M1′ layout</div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useEnginesStore } from '../../stores/engines';
import ConnectionRow from './ConnectionRow.vue';

const engines = useEnginesStore();
</script>
