from typing import List

from sqlalchemy import select
from sqlalchemy.engine.row import Row

from src.graphql.db.session import get_session


async def getAll(model, filter=None):
    async with get_session() as session:
        # Return type is List[model]
        base_stmt = select(model)
        if filter is not None:
            assert isinstance(filter, dict)
            base_stmt = base_stmt.filter_by(**filter)
        
        result = (await session.execute(base_stmt)).scalars().all()
        return result


async def getOne(model, filter=None):
    async with get_session() as session:
        # Return type is model
        base_stmt = select(model).limit(1)
        if filter is not None:
            assert isinstance(filter, dict)
            base_stmt = base_stmt.filter_by(**filter)
        
        result = (await session.execute(base_stmt)).scalar()
        return result
