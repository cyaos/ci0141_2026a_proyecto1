<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="drawer.open" 
        class="fixed inset-0 bg-bg/60 backdrop-blur-sm z-40"
        @click="drawer.close()"
      ></div>
    </Transition>

    <!-- Drawer panel -->
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition-transform duration-200 ease-in"
      leave-from-class="translate-x-0"
      leave-to-class="translate-x-full"
    >
      <div 
        v-if="drawer.open"
        class="fixed top-0 right-0 h-full w-[420px] bg-surface border-l-2 border-accent z-50 flex flex-col"
      >
        <div class="px-5 py-4 border-b border-border bg-surface-2 flex flex-col gap-1">
          <span class="field-label">{{ drawer.mode === 'create' ? 'insertar' : 'editar' }} · {{ drawer.entity === 'jugadores' ? 'jugador' : 'ranking' }}</span>
          <div class="text-xs text-text-dim uppercase tracking-wider">
            motor: <span class="text-accent">{{ engines.active?.name || 'ninguno' }}</span>
          </div>
        </div>

        <div class="flex-1 overflow-hidden flex flex-col">
          <JugadorForm v-if="drawer.entity === 'jugadores'" :key="drawer.openSeq" />
          <RankingForm v-else :key="drawer.openSeq" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useDrawerStore } from '../../stores/drawer';
import { useEnginesStore } from '../../stores/engines';
import JugadorForm from './JugadorForm.vue';
import RankingForm from './RankingForm.vue';

const drawer = useDrawerStore();
const engines = useEnginesStore();
</script>
