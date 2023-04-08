import asyncio
from collections import defaultdict

from pydantic.typing import List, Dict
from sqlalchemy import select
from strawberry.types import Info

from src.graphql.db.session import get_session
from src.graphql.db.utils import getOne, getAll
from src.graphql.scalars.recipe_scalar import (
    AssociatedRecipes,
    NEI_Base_Recipe,
    NEI_Fluid,
    NEI_GT_Recipe,
    NEI_Item,
    NEI_Recipe_Dimensions,
    SidebarItem,
)
import src.graphql.models.recipe_models_autogen as rma


# TODO:
# Actually follow graphql design philosophy lol
# (currently the whole resource is grabbed regardless of what the user asks)


def _prepORMDict(item, rename={}, exclude=[], include={}):
    d = dict(item.__dict__)
    d.pop('_sa_instance_state')

    for k, v in rename.items():
        d[v] = d.pop(k)
    for k in exclude:
        d.pop(k)
    d.update(include)
    
    return d


async def _getNEIItemInputs(session, rec_id) -> List[NEI_Item]:
    stmt = select(rma.Item, rma.RecipeItemGroup.item_inputs_key, rma.ItemGroupItemStacks.item_stacks_stack_size) \
        .join(rma.ItemGroupItemStacks, rma.ItemGroupItemStacks.item_stacks_item_id == rma.Item.id) \
        .join(rma.RecipeItemGroup, rma.RecipeItemGroup.item_inputs_id == rma.ItemGroupItemStacks.item_group_id) \
        .filter(rma.RecipeItemGroup.recipe_id == rec_id)

    rows = await session.execute(stmt)
    item_inputs = []
    for r in rows:
        itemORM, position, stack_size = r
        item_inputs.append(
            NEI_Item(**_prepORMDict(
                itemORM,
                include={'stack_size': stack_size, 'position': position, 'input': True},
            ))
        )
    
    return item_inputs


async def _getNEIFluidInputs(session, rec_id) -> List[NEI_Fluid]:
    stmt = select(rma.Fluid, rma.RecipeFluidGroup.fluid_inputs_key, rma.FluidGroupFluidStacks.fluid_stacks_amount) \
        .join(rma.FluidGroupFluidStacks, rma.FluidGroupFluidStacks.fluid_stacks_fluid_id == rma.Fluid.id) \
        .join(rma.RecipeFluidGroup, rma.RecipeFluidGroup.fluid_inputs_id == rma.FluidGroupFluidStacks.fluid_group_id) \
        .filter(rma.RecipeFluidGroup.recipe_id == rec_id)

    rows = await session.execute(stmt)
    fluid_inputs = []
    for r in rows:
        fluidORM, position, liters = r
        fluid_inputs.append(
            NEI_Fluid(**_prepORMDict(
                fluidORM,
                include={'liters': liters, 'position': position, 'input': True},
            ))
        )
    
    return fluid_inputs


async def _getNEIItemOutputs(session, rec_id) -> List[NEI_Item]:
    stmt = select(rma.Item, rma.RecipeItemOutputs) \
            .join(rma.RecipeItemOutputs, rma.RecipeItemOutputs.item_outputs_value_item_id == rma.Item.id) \
            .filter(rma.RecipeItemOutputs.recipe_id == rec_id)

    rows = await session.execute(stmt)
    item_outputs = []
    for r in rows:
        itemORM, itemOutputsORM = r
        findict = _prepORMDict(itemORM)
        findict.update(_prepORMDict(
            itemOutputsORM,
            exclude=['recipe_id', 'item_outputs_value_item_id'],
            rename={
                'item_outputs_value_stack_size': 'stack_size',
                'item_outputs_value_probability': 'output_probability',
                'item_outputs_key': 'position',
            },
            include={
                'input': False,
            }
        ))
        item_outputs.append(
            NEI_Item(**findict)
        )
    
    return item_outputs


async def _getNEIFluidOutputs(session, rec_id) -> List[NEI_Fluid]:
    stmt = select(rma.Fluid, rma.RecipeFluidOutputs) \
            .join(rma.RecipeFluidOutputs, rma.RecipeFluidOutputs.fluid_outputs_value_fluid_id == rma.Fluid.id) \
            .filter(rma.RecipeFluidOutputs.recipe_id == rec_id)

    rows = await session.execute(stmt)
    fluid_outputs = []
    for r in rows:
        fluidORM, fluidOutputsORM = r
        findict = _prepORMDict(fluidORM)
        findict.update(_prepORMDict(
            fluidOutputsORM,
            exclude=['recipe_id', 'fluid_outputs_value_fluid_id'],
            rename={
                'fluid_outputs_value_amount': 'liters',
                'fluid_outputs_value_probability': 'output_probability',
                'fluid_outputs_key': 'position',
            },
            include={
                'input': False,
            }
        ))
        fluid_outputs.append(
            NEI_Fluid(**findict)
        )
    
    return fluid_outputs


async def _getNEIRecipe(session, rec_id) -> NEI_Base_Recipe:
    construction_dict = dict(recipe_id=rec_id)

    awaitables = [
        _getNEIItemInputs(session, rec_id),
        _getNEIFluidInputs(session, rec_id),
        _getNEIItemOutputs(session, rec_id),
        _getNEIFluidOutputs(session, rec_id),
    ]
    results = await asyncio.gather(*awaitables)

    construction_dict['input_items'] = results[0]
    construction_dict['input_fluids'] = results[1]
    construction_dict['output_items'] = results[2]
    construction_dict['output_fluids'] = results[3]

    return NEI_Base_Recipe(**construction_dict)


async def _getNEIGTRecipe(session, rec_id) -> NEI_GT_Recipe:
    stmt = select(rma.GregTechRecipe, rma.RecipeType) \
            .join(rma.Recipe, rma.GregTechRecipe.recipe_id == rma.Recipe.id) \
            .join(rma.RecipeType, rma.Recipe.recipe_type_id == rma.RecipeType.id) \
            .filter(rma.GregTechRecipe.recipe_id == rec_id)

    findict = {}
    findict['base_recipe'] = await _getNEIRecipe(session, rec_id)

    rows = await session.execute(stmt)
    gtRecipeORM, recipeTypeORM = rows.first()
    findict.update(_prepORMDict(
        recipeTypeORM,
        rename={
            'type': 'localized_machine_name',
        },
        exclude = [
            'category', # They're all "gregtech"
            'id'
        ],
    ))
    findict.update(_prepORMDict(
        gtRecipeORM,
        rename = {
            'duration': 'duration_ticks',
        },
        exclude = ['id'],
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
    async with get_session() as session:
        recipe = await _getNEIGTRecipe(session, recipe_id)
    
    return recipe


async def getNSidebarRecipes(limit: int, info: Info) -> List[SidebarItem]:
    async with get_session() as session:
        stmt = select(rma.Item).limit(limit)
        results = (await session.execute(stmt)).scalars().all()
    
    sidebar_recipes = []
    for result in results:
        result = dict(result.__dict__)
        sidebarItem_construction_dict = {
            'item_id': result['id'],
            'image_file_path': result['image_file_path'],
            'localized_name': result['localized_name'],
            'tooltip': result['tooltip'],
        }
        sidebar_recipes.append(SidebarItem(**sidebarItem_construction_dict))
    
    return sidebar_recipes


async def _getAndSplitNEIRecipesByType(session, recipe_ids: List[int]) -> Dict["GT": List[NEI_GT_Recipe], "Other": List[NEI_Base_Recipe]]:
    output_recipes = {
        'GT': [],
        'Other': [],
    }

    base_stmt = select(rma.Recipe.id, rma.RecipeType.category) \
                .join(rma.Recipe, rma.Recipe.recipe_type_id == rma.RecipeType.id) \
                .filter(rma.Recipe.id.in_(recipe_ids)) 
    gt_recipes_query = base_stmt.filter(rma.RecipeType.category == 'gregtech')
    other_recipes_query = base_stmt.filter(rma.RecipeType.category != 'gregtech')

    # Get GT recipes
    rows = (await session.execute(gt_recipes_query))
    awaitables = [_getNEIGTRecipe(session, recipe_id) for recipe_id, _ in rows]
    output_recipes['GT'] = await asyncio.gather(*awaitables)

    # Get non GT recipes
    rows = (await session.execute(other_recipes_query))
    awaitables = [_getNEIRecipe(session, recipe_id) for recipe_id, _ in rows]
    output_recipes['Other'] = await asyncio.gather(*awaitables)

    return output_recipes


async def _determineSingleIdType(session, single_id) -> str:
    if (await getOne(session, rma.Item, dict(id=single_id))):
        return 'Item'
    elif (await getOne(session, rma.Fluid, dict(id=single_id))):
        return 'Fluid'
    else:
        raise ValueError(f"Invalid single_id: {single_id}")


async def getNEIRecipesThatMakeSingleId(single_id: int, info: Info) -> AssociatedRecipes:
    async with get_session() as session:
        # Figure out whether we're dealing with an item or fluid
        single_type = await _determineSingleIdType(session, single_id)

        # Get all associated recipe IDs
        relevant_table = {
            'Item': rma.RecipeItemOutputs,
            'Fluid': rma.RecipeFluidOutputs,
        }[single_type]
        relevant_filter_key = {
            'Item': 'item_outputs_value_item_id',
            'Fluid': 'fluid_outputs_value_fluid_id',
        }[single_type]
        relevant_single_id_column = getattr(relevant_table, relevant_filter_key)

        recipe_ids_query = select(relevant_table.recipe_id).filter(relevant_single_id_column == single_id)
        recipe_ids = (await session.execute(recipe_ids_query)).scalars().all()

        # Construct recipes, filtering by GT / not GT
        output_recipes = await _getAndSplitNEIRecipesByType(session, recipe_ids)

    output_recipes = AssociatedRecipes(
        single_id = single_id,
        makeOrUse = 'Make',
        GTRecipes = output_recipes['GT'],
        OtherRecipes = output_recipes['Other'],
    )
    
    return output_recipes


async def getNEIRecipesThatUseSingleId(single_id: int, info: Info) -> AssociatedRecipes:
    async with get_session() as session:
        # Figure out whether we're dealing with an item or fluid
        single_type = await _determineSingleIdType(session, single_id)

        if single_type == 'Item':
            stmt = select(rma.RecipeItemGroup.recipe_id) \
                .join(rma.ItemGroupItemStacks, rma.RecipeItemGroup.item_inputs_id == rma.ItemGroupItemStacks.item_group_id) \
                .filter(rma.ItemGroupItemStacks.item_stacks_item_id == single_id)
        elif single_type == 'Fluid':
            stmt = select(rma.RecipeFluidGroup.recipe_id) \
                .join(rma.FluidGroupFluidStacks, rma.RecipeFluidGroup.fluid_inputs_id == rma.FluidGroupFluidStacks.fluid_group_id) \
                .filter(rma.FluidGroupFluidStacks.fluid_stacks_fluid_id == single_id)

        recipe_ids = (await session.execute(stmt)).scalars().all()
        output_recipes = await _getAndSplitNEIRecipesByType(session, recipe_ids)

    output_recipes = AssociatedRecipes(
        single_id = single_id,
        makeOrUse = 'Make',
        GTRecipes = output_recipes['GT'],
        OtherRecipes = output_recipes['Other'],
    )

    return output_recipes
