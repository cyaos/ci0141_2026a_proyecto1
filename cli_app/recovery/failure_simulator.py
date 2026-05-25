"""Simulación de fallos: abandona una transacción sin commit ni abort."""
from datetime import datetime, timezone
import wal as wal_module


async def simular_fallo(tid: str, tx_manager) -> None:
    """
    Registra un fallo simulado en el WAL para la transacción indicada.
    No llama a commit() ni abort(): la transacción queda interrumpida,
    dejando el WAL con BEGIN + operaciones pero sin COMMIT.
    Esto permite demostrar la recuperación ante fallos.
    """
    await wal_module.append({
        'tid': tid,
        'op': 'FAILURE_SIMULATED',
        'timestamp': datetime.now(timezone.utc).isoformat(),
    })
    # Eliminamos la TX del gestor sin registrar COMMIT/ABORT
    # para simular que el proceso cayó abruptamente.
    if hasattr(tx_manager, '_txs'):
        tx_manager._txs.pop(tid, None)
