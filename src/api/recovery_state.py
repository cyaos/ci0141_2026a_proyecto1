"""Estado global compartido para los protocolos de recuperación en el backend."""
import os
import sys
from typing import Optional

# Agregar cli_app al FINAL del path (no al inicio) para evitar que
# cli_app/connections.py se imponga sobre el paquete src/connections/.
_CLI_APP_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'cli_app')
)
if _CLI_APP_PATH not in sys.path:
    sys.path.append(_CLI_APP_PATH)

import wal as wal_module
from tx_manager import TxManager
from recovery.recovery_manager import RecoveryManager, NOMBRES_VALIDOS
from recovery.failure_simulator import simular_fallo as _simular_fallo
from adapters.postgres_adapter import PostgresAdapter
from adapters.mongo_adapter import MongoAdapter


PG_URI = "postgresql://admin:admin123@localhost:5432/distributed_client_db"
MONGO_URI = "mongodb://localhost:27018"


class RecoveryState:
    """Mantiene el RecoveryManager, los adaptadores async y la TX activa."""

    def __init__(self):
        self.recovery_mgr = RecoveryManager()
        self.tx_mgr = TxManager()
        self.current_tid: Optional[str] = None
        self._pg_adapter: Optional[PostgresAdapter] = None
        self._mongo_adapter: Optional[MongoAdapter] = None

    async def get_pg(self) -> PostgresAdapter:
        if self._pg_adapter is None:
            self._pg_adapter = PostgresAdapter(PG_URI)
        await self._pg_adapter.connect()
        return self._pg_adapter

    async def get_mongo(self) -> MongoAdapter:
        if self._mongo_adapter is None:
            self._mongo_adapter = MongoAdapter(MONGO_URI)
        await self._mongo_adapter.connect()
        return self._mongo_adapter

    async def ensure_tx(self) -> str:
        """Garantiza que hay una TX abierta; la inicia si no existe."""
        if self.current_tid is None:
            self.current_tid = await self.tx_mgr.begin()
        return self.current_tid

    async def cerrar_tx_actual(self, commit: bool = True) -> Optional[str]:
        """Cierra la TX activa (commit o abort) si existe."""
        if self.current_tid is None:
            return None
        tid = self.current_tid
        try:
            if commit:
                await self.recovery_mgr.activo.on_commit(tid)
                await self.tx_mgr.commit(tid)
            else:
                await self.recovery_mgr.activo.on_abort(tid)
                await self.tx_mgr.abort(tid)
        except Exception:
            pass
        self.current_tid = None
        return tid

    def wal_count(self) -> int:
        try:
            return len(wal_module.query())
        except Exception:
            return 0


_state: Optional[RecoveryState] = None


def get_state() -> RecoveryState:
    global _state
    if _state is None:
        _state = RecoveryState()
    return _state


# Re-exports para que las rutas no tengan que tocar el path
__all__ = [
    "RecoveryState",
    "get_state",
    "wal_module",
    "NOMBRES_VALIDOS",
    "_simular_fallo",
]
