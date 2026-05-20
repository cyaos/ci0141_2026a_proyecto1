# Registro de uso de IA — CI-0141 Proyecto 1

Este documento registra el uso de herramientas de inteligencia artificial durante el desarrollo del proyecto, conforme a la **Sección 1 de la especificación**:

> *"El uso de herramientas de inteligencia artificial o la copia de código sin la referencia explícita correspondiente constituye fraude académico y será tratado con las sanciones que establece el Reglamento de la Universidad de Costa Rica."*

## Herramienta utilizada

- **Asistente**: Claude Code (Anthropic), modelo Claude Opus 4.7.
- **Modalidad**: asistencia interactiva en línea de comandos, con revisión manual de cada cambio antes de su incorporación al repositorio.

## Convenciones del registro

Cada entrada documenta:

- **Fecha**: cuándo ocurrió la interacción.
- **Solicitud**: la petición textual o resumida hecha al asistente.
- **Resultado**: qué generó el asistente.
- **Archivos afectados**: rutas relativas modificadas o creadas.
- **Revisión**: validación humana realizada (lectura, pruebas, modificaciones aplicadas, decisiones rechazadas).

## Bitácora

### 2026-05-20 — Diseño de la UI (entrevista de requisitos)

- **Solicitud**: definir el diseño de alto nivel para el cliente web (paleta, tipografía, layout, patrones de formulario). Sesión guiada por el skill `frontend-design` mediante preguntas estructuradas.
- **Resultado**: definición conjunta del esquema de diseño "P1 Operator Console" — monoespaciado Geist Mono, fondo `#0A0A0A`, acento verde ácido `#A3E635`, layout tipo consola operativa con sidebar de motores, tabla central y drawer lateral para formularios.
- **Archivos afectados**: ninguno todavía (decisiones documentadas).
- **Revisión**: el estudiante respondió cada pregunta del asistente y validó cada decisión antes de avanzar a la siguiente.

### 2026-05-20 — Scaffolding de configuración del frontend

- **Solicitud**: generar los archivos de configuración del frontend en `web/` (no componentes funcionales): Tailwind, Vite, TypeScript, entrada HTML, hojas de tokens, bootstrap de la app.
- **Resultado**: contenido para `web/tailwind.config.js` (paleta P1 + Geist Mono + escala tipográfica), `web/index.html` (entry de Vite + Google Fonts), `web/src/env.d.ts` (shim de tipos para `*.vue` y `vite/client`), `web/src/styles/globals.css` (capas Tailwind + variables CSS + clases `.panel`/`.btn`/`.input`/`.label`/`.chip`), `web/src/main.ts` (bootstrap Vue + Pinia), `web/src/App.vue` (placeholder mínimo). Corrección del script `build` en `package.json` (`vue-tsc -b` → `vue-tsc --noEmit`) porque no hay project references.
- **Archivos afectados**: `web/tailwind.config.js`, `web/index.html`, `web/src/env.d.ts`, `web/src/styles/globals.css`, `web/src/main.ts`, `web/src/App.vue`, `web/package.json`.
- **Revisión**: el estudiante solicitó explícitamente que la generación se registrara como uso de IA. Validación pendiente vía `npm install && npm run dev`.

---

## Plantilla para nuevas entradas

```markdown
### YYYY-MM-DD — Título breve

- **Solicitud**: …
- **Resultado**: …
- **Archivos afectados**: …
- **Revisión**: …
```
