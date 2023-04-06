from typing import List, Dict

import strawberry
from strawberry.types import Info

from src.graphql.resolvers.recipe_resolver import (
    getNEIGTRecipe,
    getNEIRecipesThatMakeSingleId,
    # getNEIRecipesThatUseSingleId,
    getNSidebarRecipes,   
)
from src.graphql.scalars.recipe_scalar import (
    AssociatedRecipes,
    NEI_Base_Recipe,
    NEI_GT_Recipe,
    SidebarItem,
)


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
    async def getGTRecipeByRecipeId(self, info: Info, recipe_id: str) -> NEI_GT_Recipe:
        # TODO: Support non GT recipes
        user_dict = await getNEIGTRecipe(recipe_id, info)
        return user_dict

    @strawberry.field
    async def getNSidebarItems(self, info: Info, limit: int) -> List[SidebarItem]:
        user_dict = await getNSidebarRecipes(limit, info)
        return user_dict

    @strawberry.field
    async def getRecipesThatMakeSingleId(self, info: Info, item_id: str) -> AssociatedRecipes:
        # Supports items and fluids
        user_dict = await getNEIRecipesThatMakeSingleId(item_id, info)
        return user_dict 

    # @strawberry.field
    # async def getRecipesThatUseSingleId(self, info: Info, item_id: str) -> Dict["GT": List[NEI_GT_Recipe], "Other": List[NEI_Base_Recipe]]:
    #     # Supports items and fluids
    #     user_dict = await getNEIRecipesThatUseSingleId(item_id, info)
    #     return user_dict 