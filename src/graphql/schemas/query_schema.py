from typing import List

import strawberry
from strawberry.types import Info

from src.graphql.resolvers.recipe_resolver import (
    getNEIGTRecipe,
    getNEIRecipesThatMakeSingleId,
    getNEIRecipesThatUseSingleId,
    getNSidebarRecipes,   
)
from src.graphql.scalars.recipe_scalar import (
    AssociatedRecipes,
    NEI_GT_Recipe,
    SidebarItem,
)


@strawberry.type
class Query:
    @strawberry.field
    async def getGTRecipeByRecipeId(self, info: Info, recipe_id: str) -> NEI_GT_Recipe:
        # TODO: Support non GT recipes
        user_dict = await getNEIGTRecipe(recipe_id, info)
        return user_dict

    @strawberry.field
    async def getNSidebarItems(self, info: Info, limit: int, search: str, mode: str) -> List[SidebarItem]:
        user_dict = await getNSidebarRecipes(limit, search, mode, info)
        return user_dict

    @strawberry.field
    async def getRecipesThatMakeSingleId(self, info: Info, item_id: str) -> AssociatedRecipes:
        # Supports items and fluids
        user_dict = await getNEIRecipesThatMakeSingleId(item_id, info)
        return user_dict 

    @strawberry.field
    async def getRecipesThatUseSingleId(self, info: Info, item_id: str) -> AssociatedRecipes:
        # Supports items and fluids
        user_dict = await getNEIRecipesThatUseSingleId(item_id, info)
        print(f"getRecipesThatUseSingleID returned this many GT recipes: {len(user_dict.GTRecipes)}")
        print(f"getRecipesThatUseSingleID returned this many Other recipes: {len(user_dict.OtherRecipes)}")
        return user_dict 