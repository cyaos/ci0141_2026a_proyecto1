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
        return await self._client[db][coll].find(filter_q).to_list(length=100)

    async def execute_command(self, db: str, command: dict):
        await self.connect()
        return await self._client[db].command(command)

