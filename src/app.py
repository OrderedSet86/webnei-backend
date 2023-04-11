import logging
import orjson
import strawberry
from fastapi import FastAPI
from fastapi_utils.timing import add_timing_middleware
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

# from src.graphql.schemas.mutation_schema import Mutation
from src.graphql.schemas.query_schema import Query


schema = strawberry.Schema(
    query=Query,
    mutation=None,
    config=StrawberryConfig(auto_camel_case=True)
)

def create_app():

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    app = FastAPI()
    add_timing_middleware(app, record=logger.info, prefix="app", exclude="untimed")
    graphql_app = GraphQLRouter(schema)
    graphql_app.encode_json = orjson.dumps
    app.include_router(graphql_app, prefix="/graphql")

    return app