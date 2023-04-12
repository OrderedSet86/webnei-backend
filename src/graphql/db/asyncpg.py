import asyncpg

import load_env
from src.graphql.core.config import settings


class _ConnectionHandler:
    def __init__(self):
        self._pool = None
    
    def __exit__(self):
        self.close_pool()
    
    async def _createAsyncpgPool(self):
        return await asyncpg.create_pool(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            max_size=10,
        )

    async def get_pool(self):
        if self._pool is None:
            self._pool = await self._createAsyncpgPool()
        return self._pool

    async def close_pool(self):
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

connectionHandler = _ConnectionHandler()
