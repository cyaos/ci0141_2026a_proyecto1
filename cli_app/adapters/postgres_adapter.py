"""Postgres adapter using asyncpg."""
import asyncpg
from typing import Any, Optional
import asyncio


class PostgresAdapter:
    def __init__(self, uri: str):
        self.uri = uri
        self._conn: Optional[asyncpg.Connection] = None
        self._lock = asyncio.Lock()

    async def connect(self):
        if self._conn is None:
            self._conn = await asyncpg.connect(self.uri)
        return self._conn

    async def _reconnect(self):
        # best-effort cleanup and create a fresh connection
        try:
            if self._conn:
                await self._conn.close()
        except Exception:
            pass
        self._conn = None
        await self.connect()

    async def begin_transaction(self):
        """Start a DB transaction on the underlying connection and return the Transaction object."""
        await self.connect()
        try:
            tx = self._conn.transaction()
            await tx.start()
            return tx
        except Exception:
            # try one reconnect and retry
            await self._reconnect()
            tx = self._conn.transaction()
            await tx.start()
            return tx

    async def commit_transaction(self, tx):
        """Commit a Transaction object returned by begin_transaction."""
        await tx.commit()

    async def rollback_transaction(self, tx):
        """Rollback a Transaction object returned by begin_transaction."""
        await tx.rollback()

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def execute(self, query: str, *args) -> Any:
        await self.connect()
        async with self._lock:
            try:
                return await self._conn.fetch(query, *args)
            except Exception:
                # try one reconnect and retry the query
                await self._reconnect()
                return await self._conn.fetch(query, *args)

    async def execute_non_query(self, query: str, *args) -> str:
        await self.connect()
        async with self._lock:
            try:
                return await self._conn.execute(query, *args)
            except Exception:
                await self._reconnect()
                return await self._conn.execute(query, *args)

    async def begin(self):
        await self.connect()
        return await self._conn.transaction()

