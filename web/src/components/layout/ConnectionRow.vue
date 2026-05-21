<template>
  <button 
    class="w-full text-left py-2 px-4 border-l-2 hover:bg-surface-2 transition-colors"
    :class="active ? 'border-accent' : 'border-transparent'"
    @click="$emit('select', status.key)"
  >
    <div class="flex items-center gap-2">
      <StatusDot :active="status.active" />
      <span>{{ status.name }}</span>
    </div>
    <div class="text-xs text-text-dim pl-4">
      {{ status.host }}:{{ status.port }}
      <span v-if="!status.active" class="text-danger">· offline</span>
    </div>
  </button>
</template>

<script setup lang="ts">
import type { EngineStatus, EngineKey } from '../../lib/types';
import StatusDot from '../primitives/StatusDot.vue';

defineProps<{
  status: EngineStatus;
  active: boolean;
}>();

defineEmits<{
  (e: 'select', key: EngineKey): void
}>();
</script>
