<template>
  <header class="h-12 border-b border-border bg-surface flex items-center justify-between px-4">
    <div class="flex items-center gap-6">
      <h1 class="font-bold flex items-center gap-2">
        <span class="text-accent">DB</span>
        <span class="text-text-primary">Client UCR</span>
        <span class="text-text-dim text-xs font-normal">/ stage 1</span>
      </h1>
      
      <div class="flex items-center gap-3">
        <span class="field-label">PROTOCOLO</span>
        <div class="flex items-center gap-2">
          <button class="pill stage-2" disabled title="Disponible en Stage 2">No-Undo/No-Redo</button>
          <button class="pill stage-2" disabled title="Disponible en Stage 2">No-Undo/Redo</button>
          <button class="pill stage-2" disabled title="Disponible en Stage 2">Undo/No-Redo</button>
          <button class="pill stage-2" disabled title="Disponible en Stage 2">Undo/Redo</button>
        </div>
      </div>
    </div>

    <div>
      <button class="btn stage-2" disabled>Simular fallo</button>
    </div>
  </header>
</template>
