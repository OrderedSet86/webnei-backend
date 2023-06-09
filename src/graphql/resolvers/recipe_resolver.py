import asyncio

from typing import List, Dict
from strawberry.types import Info

from src.graphql.db.asyncpg import connectionHandler, _PreparedQueryConnectionHandler
from src.graphql.scalars.recipe_scalar import (
    AssociatedRecipes,
    NEI_All_Dimensions,
    NEI_Base_Recipe,
    NEI_Fluid,
    NEI_GT_Recipe,
    NEI_Item,
    NEI_Recipe_Dimensions,
    SidebarItem,
)


# NOTE: Leave the SQLA comments in if you work on this code
# They are used for fast development of queries. You can compile them using
# compileQueries.ipynb in the root of the repo.

# TODO:
# Actually follow graphql design philosophy lol
# (currently the whole resource is grabbed regardless of what the user asks)


preparedQueryConnectionHandler = _PreparedQueryConnectionHandler({
    '_getNEIItemInputs': 5,
    '_getNEIItemOutputs': 5,
    '_getNEIFluidInputs': 5,
    '_getNEIFluidOutputs': 5,
    '_getNEIRecipeTypeInfo': 5,
    '_getNEIGTRecipe': 2,
    'getNSidebarRecipes': 2,
    'getNSidebarRecipesContains': 2,
    'getNSidebarRecipesRegex': 2,
})


def _prepStrawberryDictFromRecord(item, rename={}, exclude=[], include={}):
    d = dict(item)
    for k, v in rename.items():
        d[v] = d.pop(k)
    for k in exclude:
        d.pop(k)
    d.update(include)
    
    return d


async def _getData(method, *args):
    await preparedQueryConnectionHandler.loadPools()
    stmt, index = await preparedQueryConnectionHandler.getPreparedStatement(method)
    rows = await stmt.fetch(*args)
    await preparedQueryConnectionHandler.releasePreparedStatement(method, index)
    return rows


async def _getNEIItemInputs(rec_id) -> List[NEI_Item]:
    # stmt = select(rma.Item, rma.RecipeItemGroup.item_inputs_key, rma.ItemGroupItemStacks.item_stacks_stack_size) \
    #     .join(rma.ItemGroupItemStacks, rma.ItemGroupItemStacks.item_stacks_item_id == rma.Item.id) \
    #     .join(rma.RecipeItemGroup, rma.RecipeItemGroup.item_inputs_id == rma.ItemGroupItemStacks.item_group_id) \
    #     .filter(rma.RecipeItemGroup.recipe_id == rec_id)

    rows = await _getData('_getNEIItemInputs', rec_id)
    item_inputs = [
        NEI_Item(**_prepStrawberryDictFromRecord(
            r,
            rename={
                'item_stacks_stack_size': 'stack_size',
                'item_inputs_key': 'position',
            },
            include={'input': True},
        ))
        for r in rows
    ]
    
    return item_inputs


async def _getNEIFluidInputs(rec_id) -> List[NEI_Fluid]:
    # stmt = select(rma.Fluid, rma.RecipeFluidGroup.fluid_inputs_key, rma.FluidGroupFluidStacks.fluid_stacks_amount) \
    #     .join(rma.FluidGroupFluidStacks, rma.FluidGroupFluidStacks.fluid_stacks_fluid_id == rma.Fluid.id) \
    #     .join(rma.RecipeFluidGroup, rma.RecipeFluidGroup.fluid_inputs_id == rma.FluidGroupFluidStacks.fluid_group_id) \
    #     .filter(rma.RecipeFluidGroup.recipe_id == rec_id)

    rows = await _getData('_getNEIFluidInputs', rec_id)
    fluid_inputs = [
        NEI_Fluid(**_prepStrawberryDictFromRecord(
            r,
            rename={
                'fluid_stacks_amount': 'liters',
                'fluid_inputs_key': 'position',
            },
            include={'input': True},
        ))
        for r in rows
    ]
    
    return fluid_inputs


async def _getNEIItemOutputs(rec_id) -> List[NEI_Item]:
    # stmt = select(rma.Item, rma.RecipeItemOutputs) \
    #         .join(rma.RecipeItemOutputs, rma.RecipeItemOutputs.item_outputs_value_item_id == rma.Item.id) \
    #         .filter(rma.RecipeItemOutputs.recipe_id == rec_id)

    rows = await _getData('_getNEIItemOutputs', rec_id)
    item_outputs = [
        NEI_Item(**_prepStrawberryDictFromRecord(
            r,
            exclude=['recipe_id', 'item_outputs_value_item_id'],
            rename={
                'item_outputs_value_stack_size': 'stack_size',
                'item_outputs_value_probability': 'output_probability',
                'item_outputs_key': 'position',
            },
            include={
                'input': False,
            },
        ))
        for r in rows
    ]
    
    return item_outputs


async def _getNEIFluidOutputs(rec_id) -> List[NEI_Fluid]:
    # stmt = select(rma.Fluid, rma.RecipeFluidOutputs) \
    #         .join(rma.RecipeFluidOutputs, rma.RecipeFluidOutputs.fluid_outputs_value_fluid_id == rma.Fluid.id) \
    #         .filter(rma.RecipeFluidOutputs.recipe_id == rec_id)

    rows = await _getData('_getNEIFluidOutputs', rec_id)
    fluid_outputs = [
        NEI_Fluid(**_prepStrawberryDictFromRecord(
            r,
            exclude=['recipe_id', 'fluid_outputs_value_fluid_id'],
            rename={
                'fluid_outputs_value_amount': 'liters',
                'fluid_outputs_value_probability': 'output_probability',
                'fluid_outputs_key': 'position',
            },
            include={
                'input': False,
            },
        ))
        for r in rows
    ]

    return fluid_outputs


async def _getNEIRecipeTypeInfo(rec_id):
    # stmt = select(rma.RecipeType) \
    #        .join(rma.Recipe, rma.Recipe.recipe_type_id == rma.RecipeType.id) \
    #        .filter(rma.Recipe.id == rec_id)

    rows = await _getData('_getNEIRecipeTypeInfo', rec_id)
    rowdict = _prepStrawberryDictFromRecord(
        rows[0],
        rename={'type': 'recipe_type'}
    )
    icon_id = rowdict.pop('icon_id')
    recipe_type = rowdict.pop('recipe_type')
    for single_type in ['item', 'fluid']:
        for direction in ['input', 'output']:
            rowdict[f'{single_type}_{direction}_dims'] = NEI_Recipe_Dimensions(
                height = rowdict.pop(f'{single_type}_{direction}_dimension_height'),
                width = rowdict.pop(f'{single_type}_{direction}_dimension_width'),
            )
    findict = {
        'recipe_type': recipe_type,
        'icon_id': icon_id,
        'dimensions': NEI_All_Dimensions(**rowdict),
    }

    return findict


async def _getNEIRecipe(rec_id) -> NEI_Base_Recipe:
    construction_dict = dict(recipe_id=rec_id)

    awaitables = [
        _getNEIItemInputs(rec_id),
        _getNEIFluidInputs(rec_id),
        _getNEIItemOutputs(rec_id),
        _getNEIFluidOutputs(rec_id),
        _getNEIRecipeTypeInfo(rec_id),
    ]
    results = await asyncio.gather(*awaitables)

    construction_dict['input_items'] = results[0]
    construction_dict['input_fluids'] = results[1]
    construction_dict['output_items'] = results[2]
    construction_dict['output_fluids'] = results[3]
    construction_dict.update(results[4])

    return NEI_Base_Recipe(**construction_dict)


async def _getNEIGTRecipe(rec_id) -> NEI_GT_Recipe:
    # stmt = select(rma.RecipeType, rma.GregTechRecipe) \
    #     .join(rma.Recipe, rma.RecipeType.id == rma.Recipe.recipe_type_id) \
    #     .join(rma.GregTechRecipe, rma.GregTechRecipe.recipe_id == rma.Recipe.id) \
    #     .filter(and_(rma.Recipe.id == rec_id))

    findict = {}
    findict['base_recipe'] = await _getNEIRecipe(rec_id)

    rows = await _getData('_getNEIGTRecipe', rec_id)

    findict.update(**_prepStrawberryDictFromRecord(
        rows[0],
        rename={
            'type': 'localized_machine_name',
            'duration': 'duration_ticks',
        },
        exclude = [
            'id',
        ],
    ))

    gt_recipe = NEI_GT_Recipe(**findict)
    
    return gt_recipe


async def getNEIGTRecipe(recipe_id, info: Info) -> NEI_GT_Recipe:
    # This is used by the query schema, don't delete it :)
    recipe = await _getNEIGTRecipe(recipe_id)
    
    return recipe


def preProcessSearch(search: str) -> str:
    # Avoids SQL injection and/or unintended consequences
    # For "contains" searches I'm doing LIKE, so _, \, % are reserved characters
    # (Need to insert escapes for them)
    reserved = ['_', '\\', '%']
    buf = ['%']
    for char in search:
        if char in reserved:
            buf.extend(['\\', f'{char}'])
        else:
            buf.append(char)
    buf.append('%')
    return ''.join(buf)


async def getNSidebarRecipes(limit: int, search: str, mode: str, info: Info) -> List[SidebarItem]:
    # stmt = select(rma.Item).limit(limit)
    # async with get_session() as session:
    #     results = (await session.execute(stmt)).scalars().all()

    # Mode can be either "contains" or "regex"
    if mode == 'contains':
        if search == '':
            rows = await _getData('getNSidebarRecipes', limit)
        else:
            search = preProcessSearch(search)
            rows = await _getData('getNSidebarRecipesContains', limit, search)
    elif mode == 'regex':
        rows = await _getData('getNSidebarRecipesRegex', limit, search)

    sidebar_recipes = [
        SidebarItem(**{
            'item_id': r['id'],
            'image_file_path': r['image_file_path'],
            'localized_name': r['localized_name'],
            'tooltip': r['tooltip'],
        })
        for r in rows
    ]
    return sidebar_recipes


async def _getGTRecipes(query):
    pool = await connectionHandler.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    awaitables = [_getNEIGTRecipe(record['id']) for record in rows]

    ret = await asyncio.gather(*awaitables)
    return ret


async def _getOtherRecipes(query):
    pool = await connectionHandler.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    awaitables = [_getNEIRecipe(record['id']) for record in rows]

    ret = await asyncio.gather(*awaitables)
    return ret


async def _getAndSplitNEIRecipesByType(recipe_ids: List[int]) -> Dict["GT": List[NEI_GT_Recipe], "Other": List[NEI_Base_Recipe]]:
    output_recipes = {
        'GT': [],
        'Other': [],
    }
    if recipe_ids == []:
        return output_recipes

    # These can't get the prepared statement treatment cause the list is dynamic :(

    if len(recipe_ids) > 1:
        recipe_ids_string = tuple(recipe_ids)
    else:
        # PostgreSQL doesn't like trailing commas
        recipe_ids_string = f"('{recipe_ids[0]}')"

    recipe_limit = 100

    base_stmt = f"""
    SELECT recipe.id, recipe_type.category 
    FROM recipe_type
    JOIN recipe ON recipe.recipe_type_id = recipe_type.id 
    WHERE recipe.id IN {recipe_ids_string} AND recipe_type.category
    """
    gt_recipes_query = base_stmt + f" = 'gregtech'\nLIMIT {recipe_limit}"
    other_recipes_query = base_stmt + f"!= 'gregtech'\nLIMIT {recipe_limit}"


    gt_recipes, other_recipes = await asyncio.gather(
        _getGTRecipes(gt_recipes_query), 
        _getOtherRecipes(other_recipes_query),
    )
    output_recipes['GT'] = gt_recipes
    output_recipes['Other'] = other_recipes

    return output_recipes


async def getNEIRecipesThatMakeSingleId(single_id: str, info: Info) -> AssociatedRecipes:
    # Ignore the fluid/item distinction and just run the SQL queries
    # The tables have a hash index, it's faster to just run them than check the type :)

    item_stmt = f"""
    SELECT recipe_id
    FROM recipe_item_outputs
    WHERE item_outputs_value_item_id = '{single_id}';
    """
    fluid_stmt = f"""
    SELECT recipe_id
    FROM recipe_fluid_outputs
    WHERE fluid_outputs_value_fluid_id = '{single_id}';
    """

    pool = await connectionHandler.get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(item_stmt)
        if len(rows) == 0:
            rows = await conn.fetch(fluid_stmt)

    recipe_ids = [x['recipe_id'] for x in rows]
    output_recipes = await _getAndSplitNEIRecipesByType(recipe_ids)

    output_recipes = AssociatedRecipes(
        single_id = single_id,
        GTRecipes = output_recipes['GT'],
        OtherRecipes = output_recipes['Other'],
    )
    
    return output_recipes


async def getNEIRecipesThatUseSingleId(single_id: str, info: Info) -> AssociatedRecipes:
    # Ignore the fluid/item distinction and just run the SQL queries
    # The tables have a hash index, it's faster to just run them than check the type :)

    item_stmt = f"""
    SELECT recipe_id
    FROM recipe_item_inputs_items
    WHERE item_inputs_items_id = '{single_id}'
    """
    fluid_stmt = f"""
    SELECT recipe_id 
    FROM recipe_fluid_inputs_fluids
    WHERE fluid_inputs_fluids_id = '{single_id}'
    """

    pool = await connectionHandler.get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(item_stmt)
        if len(rows) == 0:
            rows = await conn.fetch(fluid_stmt)
    
    recipe_ids = [x['recipe_id'] for x in rows]
    output_recipes = await _getAndSplitNEIRecipesByType(recipe_ids)

    output_recipes = AssociatedRecipes(
        single_id = single_id,
        GTRecipes = output_recipes['GT'],
        OtherRecipes = output_recipes['Other'],
    )

    return output_recipes
