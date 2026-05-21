<template>
  <div class="h-full flex flex-col">
    <TopToolbar />
    <div class="flex-1 flex overflow-hidden">
      <Sidebar />
      <EntityPanel />
    </div>
    <StatusFooter />
    <Drawer />

    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="translate-y-4 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-4 opacity-0"
    >
      <div v-if="engines.lastError"
           class="fixed bottom-12 right-4 bg-surface border border-danger
                  px-4 py-2 text-sm text-danger z-50 shadow-lg">
        {{ engines.lastError }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, watch } from "vue";
import { useEnginesStore } from "./stores/engines";
import { useEntitiesStore } from "./stores/entities";
import TopToolbar from "./components/layout/TopToolbar.vue";
import Sidebar from "./components/layout/Sidebar.vue";
import StatusFooter from "./components/layout/StatusFooter.vue";
import EntityPanel from "./components/tables/EntityPanel.vue";
import Drawer from "./components/drawer/Drawer.vue";

const engines = useEnginesStore();
const entities = useEntitiesStore();

onMounted(async () => {
  engines.startPolling();
  await engines.refresh();
  if (engines.active?.active) {
    entities.refresh(engines.activeEngine);
  }
});

onBeforeUnmount(() => engines.stopPolling());

watch(() => engines.lastError, (msg) => {
  if (msg) window.setTimeout(() => engines.clearError(), 4000);
});
</script>
