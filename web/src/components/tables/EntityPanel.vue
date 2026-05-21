<template>
  <div class="flex-1 flex flex-col h-full overflow-hidden">
    <!-- Tab strip -->
    <div class="h-12 border-b border-border bg-surface px-4 flex items-center justify-between">
      <div class="flex h-full gap-6">
        <button 
          class="h-full relative font-medium uppercase text-xs tracking-wider flex items-center gap-2"
          :class="entities.activeTab === 'jugadores' ? 'text-text-primary' : 'text-text-dim hover:text-text-primary transition-colors'"
          @click="selectTab('jugadores')"
        >
          jugadores
          <span class="text-text-muted font-normal">{{ entities.jugadores[engines.activeEngine]?.length || 0 }}</span>
          <div v-if="entities.activeTab === 'jugadores'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-accent"></div>
        </button>
        <button 
          class="h-full relative font-medium uppercase text-xs tracking-wider flex items-center gap-2"
          :class="entities.activeTab === 'rankings' ? 'text-text-primary' : 'text-text-dim hover:text-text-primary transition-colors'"
          @click="selectTab('rankings')"
        >
          rankings
          <span class="text-text-muted font-normal">{{ entities.rankings[engines.activeEngine]?.length || 0 }}</span>
          <div v-if="entities.activeTab === 'rankings'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-accent"></div>
        </button>
      </div>
      
      <div class="flex items-center gap-4">
        <div class="text-xs text-text-dim uppercase tracking-wider">
          motor activo: <span class="text-accent">{{ engines.active?.name || 'ninguno' }}</span>
        </div>
        <button 
          class="btn btn-primary"
          :disabled="!engines.active?.active"
          @click="drawer.openCreate(entities.activeTab)"
        >
          + nuevo
        </button>
      </div>
    </div>
    
    <!-- Table content -->
    <div class="flex-1 overflow-hidden relative">
      <JugadoresTable v-if="entities.activeTab === 'jugadores'" />
      <RankingsTable v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { useEnginesStore } from '../../stores/engines';
import { useEntitiesStore } from '../../stores/entities';
import { useDrawerStore } from '../../stores/drawer';
import type { EntityName } from '../../lib/types';
import JugadoresTable from './JugadoresTable.vue';
import RankingsTable from './RankingsTable.vue';

const engines = useEnginesStore();
const entities = useEntitiesStore();
const drawer = useDrawerStore();

function selectTab(tab: EntityName) {
  entities.setTab(tab);
  entities.refresh(engines.activeEngine);
}

watch(() => engines.activeEngine, (next) => {
  entities.refresh(next);
});
</script>
