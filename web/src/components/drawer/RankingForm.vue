<template>
  <form @submit.prevent="submit" class="flex-1 flex flex-col h-full overflow-hidden">
    <div class="space-y-4 px-5 py-4 overflow-auto flex-1">
      
      <template v-if="drawer.mode === 'create'">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="field-label block mb-1">id_jugador</label>
            <input v-model.number="form.id_jugador" type="number" class="field-input" :disabled="submitting" required />
          </div>
          <div>
            <label class="field-label block mb-1">id_videojuego</label>
            <input v-model.number="form.id_videojuego" type="number" class="field-input" :disabled="submitting" required />
          </div>
        </div>
        <div>
          <label class="field-label block mb-1">temporada</label>
          <input v-model="form.temporada" type="text" class="field-input" :disabled="submitting" required />
        </div>
      </template>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="field-label block mb-1">posicion</label>
          <input v-model.number="form.posicion" type="number" class="field-input" :disabled="submitting" required />
        </div>
        <div>
          <label class="field-label block mb-1">puntaje</label>
          <input v-model.number="form.puntaje" type="number" class="field-input text-accent" :disabled="submitting" required />
        </div>
      </div>

      <div v-if="drawer.mode === 'edit'" class="grid grid-cols-2 gap-3">
        <div>
          <label class="field-label block mb-1">partidas_jugadas</label>
          <input v-model.number="form.partidas_jugadas" type="number" class="field-input" :disabled="submitting" required />
        </div>
        <div>
          <label class="field-label block mb-1">partidas_ganadas</label>
          <input v-model.number="form.partidas_ganadas" type="number" class="field-input" :disabled="submitting" required />
        </div>
      </div>

      <div v-if="drawer.mode === 'edit'" class="mt-4 pt-4 border-t border-border/50 text-xs text-text-dim flex flex-col gap-1">
        <div class="flex justify-between">
          <span>id_ranking</span>
          <span>{{ editing?.id_ranking }}</span>
        </div>
        <div class="flex justify-between" v-if="editing?.id_jugador">
          <span>id_jugador</span>
          <span>{{ editing.id_jugador }}</span>
        </div>
        <div class="flex justify-between" v-if="editing?.id_videojuego">
          <span>id_videojuego</span>
          <span>{{ editing.id_videojuego }}</span>
        </div>
        <div class="flex justify-between" v-if="editing?.temporada">
          <span>temporada</span>
          <span>{{ editing.temporada }}</span>
        </div>
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
import type { Ranking } from '../../lib/types';

const drawer = useDrawerStore();
const engines = useEnginesStore();
const entities = useEntitiesStore();

const editing = drawer.editing as Ranking | null;
const form = reactive({
  id_jugador: editing?.id_jugador ?? 0,
  id_videojuego: editing?.id_videojuego ?? 0,
  temporada: editing?.temporada ?? "",
  posicion: editing?.posicion ?? 0,
  puntaje: editing?.puntaje ?? 0,
  partidas_jugadas: editing?.partidas_jugadas ?? 0,
  partidas_ganadas: editing?.partidas_ganadas ?? 0,
});
const submitting = ref(false);
const error = ref<string | null>(null);
const confirmingDelete = ref(false);

async function submit() {
  if (drawer.mode === 'create' && !form.temporada.trim()) {
    error.value = "Temporada es requerida.";
    return;
  }
  
  submitting.value = true;
  error.value = null;
  
  try {
    if (drawer.mode === 'create') {
      await entities.createRanking(engines.activeEngine, {
        id_jugador: Number(form.id_jugador),
        id_videojuego: Number(form.id_videojuego),
        temporada: form.temporada,
        posicion: Number(form.posicion),
        puntaje: Number(form.puntaje),
      });
    } else {
      if (!editing) throw new Error("No hay ranking en edición");
      await entities.updateRanking(engines.activeEngine, editing.id_ranking, {
        posicion: Number(form.posicion),
        puntaje: Number(form.puntaje),
        partidas_jugadas: Number(form.partidas_jugadas),
        partidas_ganadas: Number(form.partidas_ganadas),
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
    await entities.deleteRanking(engines.activeEngine, editing.id_ranking);
    drawer.close();
  } catch (e: any) {
    error.value = e.message || "Error al eliminar";
    confirmingDelete.value = false;
  } finally {
    submitting.value = false;
  }
}
</script>
