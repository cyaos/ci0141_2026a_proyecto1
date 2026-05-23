<template>
  <div class="overflow-auto h-full">
    <table class="w-full text-sm">
      <thead class="sticky top-0 bg-surface text-xs text-text-dim uppercase tracking-wider">
        <tr class="border-b border-border">
          <th class="text-left px-4 py-2 w-16">id</th>
          <th class="text-left px-4 py-2">jugador / videojuego</th>
          <th class="text-left px-4 py-2">temporada</th>
          <th class="text-left px-4 py-2 w-24">posicion</th>
          <th class="text-left px-4 py-2 w-24">puntaje</th>
          <th class="text-left px-4 py-2 w-24">pj / pg</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows"
            :key="row.id_ranking"
            class="border-b border-border/50 hover:bg-surface-2 cursor-pointer"
            @click="drawer.openEdit('rankings', row)">
          <td class="px-4 py-2 text-text-dim">
            {{ row.id_ranking.toString().padStart(2, "0") }}
          </td>
          <td class="px-4 py-2">
            <template v-if="row.nombre_usuario">
              {{ row.nombre_usuario }} <span class="text-text-dim">· {{ row.videojuego }}</span>
            </template>
            <template v-else>
              <span class="text-text-dim">jugador #{{ row.id_jugador }} · juego #{{ row.id_videojuego }}</span>
            </template>
          </td>
          <td class="px-4 py-2 text-text-muted">{{ row.temporada }}</td>
          <td class="px-4 py-2 text-text-muted">{{ row.posicion }}</td>
          <td class="px-4 py-2 text-accent">{{ row.puntaje }}</td>
          <td class="px-4 py-2 text-text-muted">{{ row.partidas_jugadas }} / {{ row.partidas_ganadas }}</td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="6" class="px-4 py-12 text-center text-text-dim">sin rankings</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useEntitiesStore } from '../../stores/entities';
import { useEnginesStore } from '../../stores/engines';
import { useDrawerStore } from '../../stores/drawer';

const entities = useEntitiesStore();
const engines = useEnginesStore();
const drawer = useDrawerStore();

const rows = computed(() => entities.rankings[engines.activeEngine] || []);
</script>
