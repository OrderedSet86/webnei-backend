import asyncio
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
            statement_cache_size=0,
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


class _PreparedQueryConnectionHandler:
    """
    asyncpg only supports prepared queries with a connection,
    and the prepared queries only last as long as the connection lifetime.

    This class takes in a configuration of:
    {
        str: int,
        ...
    }
    where the strings are the namespaces for connection "pools", and the ints are the max size of the pool.
    
    Unfortunately the default asyncpg pool implementation does release prepared queries, so I need to manually
    do pool management :)

    When using this class, run `loadPools` once before trying to use the pools.
    """
    def __init__(self, config):
        self._queries_by_namespace = {
            '_getNEIItemInputs': f"""
                SELECT item.id, item.image_file_path, item.internal_name, item.item_damage, item.item_id, item.localized_name, item.max_damage, item.max_stack_size, item.mod_id, item.nbt, item.tooltip, item.unlocalized_name, recipe_item_group.item_inputs_key, item_group_item_stacks.item_stacks_stack_size 
                FROM item 
                JOIN item_group_item_stacks ON item_group_item_stacks.item_stacks_item_id = item.id 
                JOIN recipe_item_group ON recipe_item_group.item_inputs_id = item_group_item_stacks.item_group_id
                WHERE recipe_item_group.recipe_id = $1;
                """,
        }

        self._config = config
        self._loadingPools = asyncio.Lock()
        self._poolsLoaded = False

        # Confirm all namespaces have associated SQL queries for prepared queries
        assert all(namespace in self._queries_by_namespace for namespace in config.keys())

        self._pools = {x: [] for x in config.keys()} # Not accessed after initialization
        self._semaphores = {namespace: asyncio.BoundedSemaphore(value=count) for namespace, count in config.items()}
        
        self.prepared_queries = {namespace: [] for namespace in config.keys()}

    async def _createConnection(self):
        return await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            statement_cache_size=0, # disable automated prepared query management
        )
    
    # Public functions
    async def loadPools(self):
        async with self._loadingPools:
            if self._poolsLoaded:
                return

            # Create connections for each namespace
            for namespace, max_size in self._config.items():
                awaitables = [self._createConnection() for _ in range(max_size)]
                self._pools[namespace] = await asyncio.gather(*awaitables)
            
            # Load prepared queries into each connection
            for namespace, connections in self._pools.items():
                awaitables = [connection.prepare(self._queries_by_namespace[namespace]) for connection in connections]
                self.prepared_queries[namespace] = await asyncio.gather(*awaitables)
            
            self._poolsLoaded = True

    async def getPreparedStatement(self, namespace):
        await self._semaphores[namespace].acquire() # Decrement semaphore count or block if unavailable
        index = self._semaphores[namespace]._value # Not technically "safe" but good enough
        return self.prepared_queries[namespace][index]

    async def releasePreparedStatement(self, namespace):
        self._semaphores[namespace].release()

    async def __aexit__(self):
        for namespace, connections in self._pools.items():
            for connection in connections:
                await connection.close()

