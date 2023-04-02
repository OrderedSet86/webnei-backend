from typing import List

from sqlalchemy import select
from sqlalchemy.engine.row import Row


async def getAll(session, model, filter=None) -> List[Row]:
    base_stmt = select(model)
    if filter is not None:
        assert isinstance(filter, dict)
        base_stmt = base_stmt.filter_by(**filter)
    
    result = (await session.execute(base_stmt)).scalars().all()
    return result


async def getOne(session, model, filter=None):
    base_stmt = select(model).limit(1)
    if filter is not None:
        assert isinstance(filter, dict)
        base_stmt = base_stmt.filter_by(**filter)
    
    result = (await session.execute(base_stmt)).scalar()
    return result
