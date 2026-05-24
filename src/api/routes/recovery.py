"""Endpoints para protocolos de recuperación y simulación de fallos."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api import recovery_state


router = APIRouter(prefix="/api/recovery", tags=["recovery"])


class ProtocolBody(BaseModel):
    name: str


class StatusResponse(BaseModel):
    protocol: str
    current_tid: Optional[str]
    wal_count: int
    protocolos_disponibles: list[str]


class FailureReport(BaseModel):
    protocolo: str
    estado: str
    tids_undo: list[str]
    tids_redo: list[str]
    ops_undo: list[dict]
    ops_redo: list[dict]


@router.get("/status", response_model=StatusResponse)
async def get_status():
    state = recovery_state.get_state()
    return StatusResponse(
        protocol=state.recovery_mgr.protocolo_activo(),
        current_tid=state.current_tid,
        wal_count=state.wal_count(),
        protocolos_disponibles=list(recovery_state.NOMBRES_VALIDOS),
    )


@router.post("/protocol", response_model=StatusResponse)
async def set_protocol(body: ProtocolBody):
    state = recovery_state.get_state()
    # Si hay una TX abierta, la cerramos (commit) antes de cambiar de protocolo.
    await state.cerrar_tx_actual(commit=True)
    ok = state.recovery_mgr.seleccionar(body.name)
    if not ok:
        raise HTTPException(
            status_code=400,
            detail=f"Protocolo desconocido. Disponibles: {list(recovery_state.NOMBRES_VALIDOS)}",
        )
    # Abrir TX fresca con el nuevo protocolo activo
    await state.ensure_tx()
    return await get_status()


@router.post("/simulate_failure", response_model=FailureReport)
async def simulate_failure():
    state = recovery_state.get_state()
    if state.current_tid is None:
        # No hay TX activa: abrir una vacía solo para registrar el fallo
        await state.ensure_tx()

    tid = state.current_tid
    await recovery_state._simular_fallo(tid, state.tx_mgr)
    state.current_tid = None

    # Recuperación automática usando el WAL
    pg = await state.get_pg()
    entries = recovery_state.wal_module.query()
    reporte = await state.recovery_mgr.activo.recover(entries, {"postgres": pg})

    return FailureReport(
        protocolo=reporte.protocolo,
        estado=reporte.estado_final,
        tids_undo=reporte.tids_con_undo,
        tids_redo=reporte.tids_con_redo,
        ops_undo=reporte.operaciones_undo,
        ops_redo=reporte.operaciones_redo,
    )


@router.post("/commit", response_model=StatusResponse)
async def commit_current():
    """Confirma la TX activa (flush del buffer en protocolos No-Undo)."""
    state = recovery_state.get_state()
    await state.cerrar_tx_actual(commit=True)
    return await get_status()


@router.post("/abort", response_model=StatusResponse)
async def abort_current():
    """Aborta la TX activa (UNDO en protocolos Undo)."""
    state = recovery_state.get_state()
    await state.cerrar_tx_actual(commit=False)
    return await get_status()


@router.post("/begin", response_model=StatusResponse)
async def begin_tx():
    """Abre una transacción manualmente."""
    state = recovery_state.get_state()
    if state.current_tid is None:
        await state.ensure_tx()
    return await get_status()


@router.get("/wal")
async def get_wal():
    """Retorna todas las entradas del WAL."""
    return recovery_state.wal_module.query()
