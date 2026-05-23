<template>
  <div class="overflow-auto h-full">
    <table class="w-full text-sm">
      <thead class="sticky top-0 bg-surface text-xs text-text-dim uppercase tracking-wider">
        <tr class="border-b border-border">
          <th class="text-left px-4 py-2 w-16">id</th>
          <th class="text-left px-4 py-2">nombre_usuario</th>
          <th class="text-left px-4 py-2">pais</th>
          <th class="text-left px-4 py-2 w-40">fecha_registro</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows"
            :key="row.id_jugador"
            class="border-b border-border/50 hover:bg-surface-2 cursor-pointer"
            @click="drawer.openEdit('jugadores', row)">
          <td class="px-4 py-2 text-text-dim">
            {{ row.id_jugador.toString().padStart(2, "0") }}
          </td>
          <td class="px-4 py-2">{{ row.nombre_usuario }}</td>
          <td class="px-4 py-2 text-text-muted">{{ row.pais }}</td>
          <td class="px-4 py-2 text-text-muted">{{ row.fecha_registro }}</td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="4" class="px-4 py-12 text-center text-text-dim">sin jugadores</td>
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

const rows = computed(() => entities.jugadores[engines.activeEngine] || []);
</script>
