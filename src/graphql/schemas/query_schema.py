import strawberry
from strawberry.types import Info

from src.graphql.resolvers.recipe_resolver import get_recipe
from src.graphql.scalars.recipe_scalar import NEI_GT_Recipe


@strawberry.type
class Query:

    # @strawberry.field
    # async def users(self, info:Info) -> typing.List[User]:
    #     """ Get all users """
    #     users_data_list = await get_users(info)
    #     return users_data_list

    # @strawberry.field
    # async def user(self, info:Info, user_id: int) -> User:
    #     """ Get user by id """
    #     user_dict = await get_user(user_id, info)
    #     return user_dict

    # @strawberry.field
    # async def stickynotes(self, info:Info) -> typing.List[StickyNotes]:
    #     """ Get all stickynotes """
    #     stickynotes_data_list = await get_stickynotes(info)
    #     return stickynotes_data_list

    # @strawberry.field
    # async def stickynote(self, info:Info, stickynote_id: int) -> StickyNotes:
    #     """ Get stickynote by id """
    #     stickynote_dict = await get_stickynote(stickynote_id, info)
    #     return stickynote_dict
    
    @strawberry.field
    async def recipe(self, info: Info, recipe_id: str) -> NEI_GT_Recipe:
        """ Get recipe by id """
        # TODO: Support non GT recipes
        user_dict = await get_recipe(recipe_id, info)
        return user_dict
