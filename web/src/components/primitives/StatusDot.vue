<template>
  <span 
    class="inline-block w-2 h-2 rounded-full"
    :class="active ? 'bg-accent shadow-[0_0_8px_rgba(163,230,53,0.5)]' : 'bg-text-dim'"
  ></span>
</template>

<script setup lang="ts">
defineProps<{
  active: boolean;
}>();
</script>
