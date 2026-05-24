"""MongoDB adapter using motor."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, Optional


class MongoAdapter:
    def __init__(self, uri: str, database: Optional[str] = None):
        self.uri = uri
        self._client: Optional[AsyncIOMotorClient] = None
        self.database = database

    async def connect(self):
        if self._client is None:
            self._client = AsyncIOMotorClient(self.uri)
        return self._client

    async def close(self):
        if self._client:
            self._client.close()
            self._client = None

    async def execute_find(self, db: str, coll: str, filter_q: dict):
        await self.connect()
        try:
            return await self._client[db][coll].find(filter_q).to_list(length=100)
        except Exception:
            # try reconnect once
            try:
                await self.close()
            except Exception:
                pass
            await self.connect()
            return await self._client[db][coll].find(filter_q).to_list(length=100)

    async def execute_command(self, db: str, command: dict):
        await self.connect()
        try:
            return await self._client[db].command(command)
        except Exception:
            try:
                await self.close()
            except Exception:
                pass
            await self.connect()
            return await self._client[db].command(command)

    # ----- Helpers that capture before/after images for WAL -----
    async def insert_with_images(self, db: str, coll: str, docs):
        """Insert docs and return (inserted_ids, after_rows)."""
        await self.connect()
        try:
            docs_list = docs if isinstance(docs, list) else [docs]
            res = await self._client[db][coll].insert_many(docs_list)
            after = await self._client[db][coll].find({"_id": {"$in": res.inserted_ids}}).to_list(length=100)
            return res.inserted_ids, after
        except Exception:
            try:
                await self.close()
            except Exception:
                pass
            await self.connect()
            res = await self._client[db][coll].insert_many(docs if isinstance(docs, list) else [docs])
            after = await self._client[db][coll].find({"_id": {"$in": res.inserted_ids}}).to_list(length=100)
            return res.inserted_ids, after

    async def update_with_images(self, db: str, coll: str, flt: dict, upd: dict):
        """Capture before image, apply update_many, capture after image. Returns (before, after, result)."""
        await self.connect()
        try:
            before = await self._client[db][coll].find(flt).to_list(length=100)
            res = await self._client[db][coll].update_many(flt, upd)
            after = await self._client[db][coll].find(flt).to_list(length=100)
            return before, after, res
        except Exception:
            try:
                await self.close()
            except Exception:
                pass
            await self.connect()
            before = await self._client[db][coll].find(flt).to_list(length=100)
            res = await self._client[db][coll].update_many(flt, upd)
            after = await self._client[db][coll].find(flt).to_list(length=100)
            return before, after, res

    async def delete_with_images(self, db: str, coll: str, flt: dict):
        """Capture before image, apply delete_many, return (before, after(empty), result)."""
        await self.connect()
        try:
            before = await self._client[db][coll].find(flt).to_list(length=100)
            res = await self._client[db][coll].delete_many(flt)
            after = []
            return before, after, res
        except Exception:
            try:
                await self.close()
            except Exception:
                pass
            await self.connect()
            before = await self._client[db][coll].find(flt).to_list(length=100)
            res = await self._client[db][coll].delete_many(flt)
            after = []
            return before, after, res

