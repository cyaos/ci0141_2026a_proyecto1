import { defineStore } from 'pinia';
import type { EntityName, Jugador, Ranking } from '../lib/types';

interface State {
  open: boolean;
  entity: EntityName;
  mode: "create" | "edit";
  editing: Jugador | Ranking | null;
  openSeq: number;
}

export const useDrawerStore = defineStore('drawer', {
  state: (): State => ({
    open: false,
    entity: "jugadores",
    mode: "create",
    editing: null,
    openSeq: 0,
  }),
  actions: {
    openCreate(entity: EntityName) {
      this.editing = null;
      this.mode = "create";
      this.entity = entity;
      this.openSeq++;
      this.open = true;
    },
    openEdit(entity: EntityName, row: Jugador | Ranking) {
      this.editing = row;
      this.mode = "edit";
      this.entity = entity;
      this.openSeq++;
      this.open = true;
    },
    close() {
      this.editing = null;
      this.open = false;
    }
  }
});
