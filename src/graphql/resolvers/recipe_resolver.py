import asyncio
import time

from typing import List, Dict
from strawberry.types import Info

from src.graphql.db.asyncpg import connectionHandler
from src.graphql.scalars.recipe_scalar import (
    AssociatedRecipes,
    NEI_Base_Recipe,
    NEI_Fluid,
    NEI_GT_Recipe,
    NEI_Item,
    NEI_Recipe_Dimensions,
    SidebarItem,
)


# TODO:
# Actually follow graphql design philosophy lol
# (currently the whole resource is grabbed regardless of what the user asks)


def _prepORMDict(item, rename={}, exclude=[], include={}, apgRecord=False):
    if apgRecord:
        d = dict(item)
    if not apgRecord:
        d = dict(item.__dict__)
        d.pop('_sa_instance_state')

    for k, v in rename.items():
        d[v] = d.pop(k)
    for k in exclude:
        d.pop(k)
    d.update(include)
    
    return d


async def _getNEIItemInputs(rec_id) -> List[NEI_Item]:
    # stmt = select(rma.Item, rma.RecipeItemGroup.item_inputs_key, rma.ItemGroupItemStacks.item_stacks_stack_size) \
    #     .join(rma.ItemGroupItemStacks, rma.ItemGroupItemStacks.item_stacks_item_id == rma.Item.id) \
    #     .join(rma.RecipeItemGroup, rma.RecipeItemGroup.item_inputs_id == rma.ItemGroupItemStacks.item_group_id) \
    #     .filter(rma.RecipeItemGroup.recipe_id == rec_id)

    stmt = f"""
    SELECT item.id, item.image_file_path, item.internal_name, item.item_damage, item.item_id, item.localized_name, item.max_damage, item.max_stack_size, item.mod_id, item.nbt, item.tooltip, item.unlocalized_name, recipe_item_group.item_inputs_key, item_group_item_stacks.item_stacks_stack_size 
    FROM item 
    JOIN item_group_item_stacks ON item_group_item_stacks.item_stacks_item_id = item.id 
    JOIN recipe_item_group ON recipe_item_group.item_inputs_id = item_group_item_stacks.item_group_id
    WHERE recipe_item_group.recipe_id = '{rec_id}';
    """

    pool = await connectionHandler.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(stmt)

    item_inputs = [
        NEI_Item(**_prepORMDict(
            r,
            rename={
                'item_stacks_stack_size': 'stack_size',
                'item_inputs_key': 'position',
            },
            include={'input': True},
            apgRecord=True,
        ))
        for r in rows
    ]
    
    return item_inputs


async def _getNEIFluidInputs(rec_id) -> List[NEI_Fluid]:
    # stmt = select(rma.Fluid, rma.RecipeFluidGroup.fluid_inputs_key, rma.FluidGroupFluidStacks.fluid_stacks_amount) \
    #     .join(rma.FluidGroupFluidStacks, rma.FluidGroupFluidStacks.fluid_stacks_fluid_id == rma.Fluid.id) \
    #     .join(rma.RecipeFluidGroup, rma.RecipeFluidGroup.fluid_inputs_id == rma.FluidGroupFluidStacks.fluid_group_id) \
    #     .filter(rma.RecipeFluidGroup.recipe_id == rec_id)

    stmt = f"""
    SELECT fluid.id, fluid.density, fluid.fluid_id, fluid.gaseous, fluid.image_file_path, fluid.internal_name, fluid.localized_name, fluid.luminosity, fluid.mod_id, fluid.nbt, fluid.temperature, fluid.unlocalized_name, fluid.viscosity, recipe_fluid_group.fluid_inputs_key, fluid_group_fluid_stacks.fluid_stacks_amount
    FROM fluid
    JOIN fluid_group_fluid_stacks ON fluid_group_fluid_stacks.fluid_stacks_fluid_id = fluid.id 
    JOIN recipe_fluid_group ON recipe_fluid_group.fluid_inputs_id = fluid_group_fluid_stacks.fluid_group_id
    WHERE recipe_fluid_group.recipe_id = '{rec_id}';
    """

    pool = await connectionHandler.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(stmt)

    fluid_inputs = [
        NEI_Fluid(**_prepORMDict(
            r,
            rename={
                'fluid_stacks_amount': 'liters',
                'fluid_inputs_key': 'position',
            },
            include={'input': True},
            apgRecord=True,
        ))
        for r in rows
    ]
    
    return fluid_inputs


async def _getNEIItemOutputs(rec_id) -> List[NEI_Item]:
    # stmt = select(rma.Item, rma.RecipeItemOutputs) \
    #         .join(rma.RecipeItemOutputs, rma.RecipeItemOutputs.item_outputs_value_item_id == rma.Item.id) \
    #         .filter(rma.RecipeItemOutputs.recipe_id == rec_id)

    stmt = f"""
    SELECT item.id, item.image_file_path, item.internal_name, item.item_damage, item.item_id, item.localized_name, item.max_damage, item.max_stack_size, item.mod_id, item.nbt, item.tooltip, item.unlocalized_name, recipe_item_outputs.recipe_id, recipe_item_outputs.item_outputs_value_probability, recipe_item_outputs.item_outputs_value_stack_size, recipe_item_outputs.item_outputs_key, recipe_item_outputs.item_outputs_value_item_id 
    FROM item
    JOIN recipe_item_outputs ON recipe_item_outputs.item_outputs_value_item_id = item.id
    WHERE recipe_item_outputs.recipe_id = '{rec_id}';
    """

    pool = await connectionHandler.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(stmt)

    item_outputs = [
        NEI_Item(**_prepORMDict(
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
            apgRecord=True
        ))
        for r in rows
    ]
    
    return item_outputs


async def _getNEIFluidOutputs(rec_id) -> List[NEI_Fluid]:
    # stmt = select(rma.Fluid, rma.RecipeFluidOutputs) \
    #         .join(rma.RecipeFluidOutputs, rma.RecipeFluidOutputs.fluid_outputs_value_fluid_id == rma.Fluid.id) \
    #         .filter(rma.RecipeFluidOutputs.recipe_id == rec_id)

    stmt = f"""
    SELECT fluid.id, fluid.density, fluid.fluid_id, fluid.gaseous, fluid.image_file_path, fluid.internal_name, fluid.localized_name, fluid.luminosity, fluid.mod_id, fluid.nbt, fluid.temperature, fluid.unlocalized_name, fluid.viscosity, recipe_fluid_outputs.recipe_id, recipe_fluid_outputs.fluid_outputs_value_amount, recipe_fluid_outputs.fluid_outputs_value_probability, recipe_fluid_outputs.fluid_outputs_key, recipe_fluid_outputs.fluid_outputs_value_fluid_id 
    FROM fluid JOIN recipe_fluid_outputs ON recipe_fluid_outputs.fluid_outputs_value_fluid_id = fluid.id 
    WHERE recipe_fluid_outputs.recipe_id = '{rec_id}'
    """

    pool = await connectionHandler.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(stmt)

    fluid_outputs = [
        NEI_Fluid(**_prepORMDict(
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
            apgRecord=True,
        ))
        for r in rows
    ]

    return fluid_outputs


async def _getNEIRecipe(rec_id) -> NEI_Base_Recipe:
    construction_dict = dict(recipe_id=rec_id)

    awaitables = [
        _getNEIItemInputs(rec_id),
        _getNEIFluidInputs(rec_id),
        _getNEIItemOutputs(rec_id),
        _getNEIFluidOutputs(rec_id),
    ]
    results = await asyncio.gather(*awaitables)

    construction_dict['input_items'] = results[0]
    construction_dict['input_fluids'] = results[1]
    construction_dict['output_items'] = results[2]
    construction_dict['output_fluids'] = results[3]

    return NEI_Base_Recipe(**construction_dict)


async def _getNEIGTRecipe(rec_id) -> NEI_GT_Recipe:
    # stmt = select(rma.RecipeType, rma.GregTechRecipe) \
    #     .join(rma.Recipe, rma.RecipeType.id == rma.Recipe.recipe_type_id) \
    #     .join(rma.GregTechRecipe, rma.GregTechRecipe.recipe_id == rma.Recipe.id) \
    #     .filter(and_(rma.Recipe.id == rec_id))

    stmt = f"""
    SELECT recipe_type.id, recipe_type.category, recipe_type.fluid_input_dimension_height, recipe_type.fluid_input_dimension_width, recipe_type.fluid_output_dimension_height, recipe_type.fluid_output_dimension_width, recipe_type.icon_info, recipe_type.item_input_dimension_height, recipe_type.item_input_dimension_width, recipe_type.item_output_dimension_height, recipe_type.item_output_dimension_width, recipe_type.shapeless, recipe_type.type, recipe_type.icon_id, greg_tech_recipe.id AS greg_tech_recipe_id, greg_tech_recipe.additional_info, greg_tech_recipe.amperage, greg_tech_recipe.duration, greg_tech_recipe.requires_cleanroom, greg_tech_recipe.requires_low_gravity, greg_tech_recipe.voltage, greg_tech_recipe.voltage_tier, greg_tech_recipe.recipe_id 
    FROM recipe_type 
    JOIN recipe ON recipe_type.id = recipe.recipe_type_id
    JOIN greg_tech_recipe ON greg_tech_recipe.recipe_id = recipe.id
    WHERE recipe.id = '{rec_id}';
    """ 

    findict = {}
    findict['base_recipe'] = await _getNEIRecipe(rec_id)

    pool = await connectionHandler.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(stmt)

    findict.update(**_prepORMDict(
        rows[0],
        rename={
            'type': 'localized_machine_name',
            'duration': 'duration_ticks',
        },
        exclude = [
            'category', # They're all "gregtech"
            'id',
            'greg_tech_recipe_id',
        ],
        apgRecord=True,
    ))
    for single_type in ['item', 'fluid']:
        for direction in ['input', 'output']:
            findict[f'{single_type}_{direction}_dims'] = NEI_Recipe_Dimensions(
                height = findict.pop(f'{single_type}_{direction}_dimension_height'),
                width = findict.pop(f'{single_type}_{direction}_dimension_width'),
            )

    gt_recipe = NEI_GT_Recipe(**findict)
    
    return gt_recipe


async def getNEIGTRecipe(recipe_id, info: Info) -> NEI_GT_Recipe:
    # This is used by the query schema, don't delete it :)
    recipe = await _getNEIGTRecipe(recipe_id)
    
    return recipe


async def getNSidebarRecipes(limit: int, info: Info) -> List[SidebarItem]:
    # stmt = select(rma.Item).limit(limit)
    # async with get_session() as session:
    #     results = (await session.execute(stmt)).scalars().all()

    stmt = f"""
    SELECT item.id, item.image_file_path, item.internal_name, item.item_damage, item.item_id, item.localized_name, item.max_damage, item.max_stack_size, item.mod_id, item.nbt, item.tooltip, item.unlocalized_name 
    FROM item
    ORDER BY item.item_id
    LIMIT {limit}
    """

    pool = await connectionHandler.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(stmt)
    
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

    base_stmt = f"""
    SELECT recipe.id, recipe_type.category 
    FROM recipe_type
    JOIN recipe ON recipe.recipe_type_id = recipe_type.id 
    WHERE recipe.id IN {tuple(recipe_ids)} AND recipe_type.category
    """
    gt_recipes_query = base_stmt + " = 'gregtech'"
    other_recipes_query = base_stmt + "!= 'gregtech'"

    gt_recipes, other_recipes = await asyncio.gather(
        _getGTRecipes(gt_recipes_query), 
        _getOtherRecipes(other_recipes_query),
    )
    output_recipes['GT'] = gt_recipes
    output_recipes['Other'] = other_recipes

    return output_recipes


async def getNEIRecipesThatMakeSingleId(single_id: int, info: Info) -> AssociatedRecipes:
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
        makeOrUse = 'Make',
        GTRecipes = output_recipes['GT'],
        OtherRecipes = output_recipes['Other'],
    )
    
    return output_recipes


async def getNEIRecipesThatUseSingleId(single_id: int, info: Info) -> AssociatedRecipes:
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
        makeOrUse = 'Make',
        GTRecipes = output_recipes['GT'],
        OtherRecipes = output_recipes['Other'],
    )

    return output_recipes
