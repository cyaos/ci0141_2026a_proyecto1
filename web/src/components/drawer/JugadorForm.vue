<template>
  <form @submit.prevent="submit" class="flex-1 flex flex-col h-full overflow-hidden">
    <div class="space-y-4 px-5 py-4 overflow-auto flex-1">
      <div>
        <label class="field-label block mb-1">nombre_usuario</label>
        <input v-model="form.nombre_usuario" type="text" class="field-input" :disabled="submitting" />
      </div>

      <div>
        <label class="field-label block mb-1">pais</label>
        <input v-model="form.pais" type="text" class="field-input" :disabled="submitting" />
      </div>

      <div v-if="drawer.mode === 'create'">
        <label class="field-label block mb-1">fecha_registro</label>
        <input v-model="form.fecha_registro" type="date" class="field-input" :disabled="submitting" />
      </div>

      <div v-if="drawer.mode === 'edit'" class="mt-4 pt-4 border-t border-border/50 text-xs text-text-dim flex justify-between">
        <span>id_jugador</span>
        <span>{{ editing?.id_jugador }}</span>
      </div>

      <p v-if="error" class="text-danger text-xs mt-4">{{ error }}</p>
    </div>

    <div class="h-14 border-t border-border bg-surface-2 px-5 flex items-center shrink-0">
      <template v-if="drawer.mode === 'edit'">
        <template v-if="confirmingDelete">
          <button type="button" class="btn btn-danger mr-2" :disabled="submitting" @click="remove">confirmar eliminación</button>
          <button type="button" class="btn btn-ghost" :disabled="submitting" @click="confirmingDelete = false">cancelar</button>
        </template>
        <template v-else>
          <button type="button" class="btn btn-danger" :disabled="submitting" @click="confirmingDelete = true">eliminar</button>
        </template>
      </template>

      <div class="ml-auto flex items-center gap-2">
        <button type="button" class="btn btn-ghost" :disabled="submitting" @click="drawer.close()">cancelar</button>
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          {{ drawer.mode === 'create' ? 'insertar' : 'guardar' }}
        </button>
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useDrawerStore } from '../../stores/drawer';
import { useEnginesStore } from '../../stores/engines';
import { useEntitiesStore } from '../../stores/entities';
import type { Jugador } from '../../lib/types';

const drawer = useDrawerStore();
const engines = useEnginesStore();
const entities = useEntitiesStore();

const editing = drawer.editing as Jugador | null;
const form = reactive({
  nombre_usuario: editing?.nombre_usuario ?? "",
  pais: editing?.pais ?? "",
  fecha_registro: editing?.fecha_registro ?? new Date().toISOString().slice(0, 10),
});
const submitting = ref(false);
const error = ref<string | null>(null);
const confirmingDelete = ref(false);

async function submit() {
  if (!form.nombre_usuario.trim() || !form.pais.trim()) {
    error.value = "nombre_usuario y pais son requeridos.";
    return;
  }
  
  submitting.value = true;
  error.value = null;
  
  try {
    if (drawer.mode === 'create') {
      await entities.createJugador(engines.activeEngine, {
        nombre_usuario: form.nombre_usuario,
        pais: form.pais,
        fecha_registro: form.fecha_registro,
      });
    } else {
      if (!editing) throw new Error("No hay jugador en edición");
      await entities.updateJugador(engines.activeEngine, editing.id_jugador, {
        nombre_usuario: form.nombre_usuario,
        pais: form.pais,
      });
    }
    drawer.close();
  } catch (e: any) {
    error.value = e.message || "Error al guardar";
  } finally {
    submitting.value = false;
  }
}

async function remove() {
  if (!editing) return;
  submitting.value = true;
  error.value = null;
  
  try {
    await entities.deleteJugador(engines.activeEngine, editing.id_jugador);
    drawer.close();
  } catch (e: any) {
    error.value = e.message || "Error al eliminar";
    confirmingDelete.value = false;
  } finally {
    submitting.value = false;
  }
}
</script>
