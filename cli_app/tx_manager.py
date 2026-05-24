"""Transaction manager that assigns TIDs and coordinates WAL + adapters."""
import uuid
import asyncio
from typing import Dict, Any, Optional
from wal import append


class TxContext:
    def __init__(self, tid: str):
        self.tid = tid
        self.operations = []  # list of dicts: {op, before, after, engine, query}
        # adapter transactions: engine -> {"adapter": adapter_obj, "tx": tx_obj}
        self.adapter_txs: Dict[str, Dict[str, object]] = {}


class TxManager:
    def __init__(self):
        self._txs: Dict[str, TxContext] = {}
        self._lock = asyncio.Lock()

    async def begin(self) -> str:
        async with self._lock:
            tid = "T" + uuid.uuid4().hex[:8]
            self._txs[tid] = TxContext(tid)
            await append({"tid": tid, "op": "BEGIN"})
            return tid

    async def log_op(self, tid: str, op: str, engine: str, before: Any, after: Any, query: str):
        ctx = self._txs.get(tid)
        if ctx is None:
            raise RuntimeError("Unknown TID")
        entry = {"tid": tid, "op": op, "engine": engine, "before": before, "after": after, "query": query}
        ctx.operations.append(entry)
        await append(entry)

    async def attach_adapter_tx(self, tid: str, engine: str, adapter: object, tx_obj: object):
        ctx = self._txs.get(tid)
        if ctx is None:
            raise RuntimeError("Unknown TID")
        ctx.adapter_txs[engine] = {"adapter": adapter, "tx": tx_obj}

    def get_adapter_tx(self, tid: str, engine: str):
        ctx = self._txs.get(tid)
        if ctx is None:
            return None
        return ctx.adapter_txs.get(engine)

    async def commit(self, tid: str):
        async with self._lock:
            ctx = self._txs.pop(tid, None)
            if ctx is None:
                raise RuntimeError("Unknown TID")
            await append({"tid": tid, "op": "COMMIT"})
            # commit any attached adapter transactions
            errors = []
            for engine, info in ctx.adapter_txs.items():
                adapter = info.get("adapter")
                txobj = info.get("tx")
                try:
                    # adapter is expected to expose commit_transaction(txobj)
                    if hasattr(adapter, "commit_transaction"):
                        await adapter.commit_transaction(txobj)
                    else:
                        # if txobj itself has commit (e.g., asyncpg Transaction), call it
                        if hasattr(txobj, "commit"):
                            await txobj.commit()
                except Exception as e:
                    # collect errors to report after attempting others
                    errors.append(f"{engine}: {e}")
            if errors:
                raise RuntimeError("Errors during commit: " + "; ".join(errors))

    async def abort(self, tid: str):
        async with self._lock:
            ctx = self._txs.pop(tid, None)
            if ctx is None:
                raise RuntimeError("Unknown TID")
            await append({"tid": tid, "op": "ABORT"})
            # rollback any attached adapter transactions
            errors = []
            for engine, info in ctx.adapter_txs.items():
                adapter = info.get("adapter")
                txobj = info.get("tx")
                try:
                    if hasattr(adapter, "rollback_transaction"):
                        await adapter.rollback_transaction(txobj)
                    else:
                        if hasattr(txobj, "rollback"):
                            await txobj.rollback()
                except Exception as e:
                    errors.append(f"{engine}: {e}")
            if errors:
                raise RuntimeError("Errors during abort: " + "; ".join(errors))

