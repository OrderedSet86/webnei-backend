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
import src.graphql.models.recipe_models_autogen as recipe_models_autogen


# TODO:
# Actually follow graphql design philosophy lol
# (currently the whole resource is grabbed regardless of what the user asks)

# FIXME:
# "Row" is wrong, switch to model name


async def _getNEIItemInputs(session, rec_id) -> List[NEI_Item]:
    item_inputs = []
    input_group_rows = await getAll(session, recipe_models_autogen.RecipeItemGroup, filter=dict(recipe_id=rec_id))
    for row in input_group_rows:
        nei_item_info = {}

        group = row
        item_group_id = group.item_inputs_id
        nei_item_info['position'] = group.item_inputs_key

        group_info = await getOne(session, recipe_models_autogen.ItemGroupItemStacks, filter=dict(item_group_id=item_group_id))
        nei_item_info['item_id'] = group_info.item_stacks_item_id
        nei_item_info['stack_size'] = group_info.item_stacks_stack_size

        item_info = await getOne(session, recipe_models_autogen.Item, filter=dict(id=nei_item_info['item_id']))
        item_data = dict(item_info.__dict__)
        item_data.pop('_sa_instance_state')
        nei_item_info.update(item_data)
        nei_item_info['input'] = True

        item_inputs.append(NEI_Item(**nei_item_info))
    
    return item_inputs


async def _getNEIFluidInputs(session, rec_id) -> List[NEI_Fluid]:
    fluid_inputs = []
    input_group_rows = await getAll(session, recipe_models_autogen.RecipeFluidGroup, filter=dict(recipe_id=rec_id))
    for row in input_group_rows:
        nei_fluid_info = {}

        group = row
        fluid_group_id = group.fluid_inputs_id
        nei_fluid_info['position'] = group.fluid_inputs_key

        group_info = await getOne(session, recipe_models_autogen.FluidGroupFluidStacks, filter=dict(fluid_group_id=fluid_group_id))
        nei_fluid_info['fluid_id'] = group_info.fluid_stacks_fluid_id
        nei_fluid_info['liters'] = group_info.fluid_stacks_amount

        fluid_info = await getOne(session, recipe_models_autogen.Fluid, filter=dict(id=nei_fluid_info['fluid_id']))
        fluid_data = dict(fluid_info.__dict__)
        fluid_data.pop('_sa_instance_state')
        nei_fluid_info.update(fluid_data)
        nei_fluid_info['input'] = True

        fluid_inputs.append(NEI_Fluid(**nei_fluid_info)) 
    
    return fluid_inputs


async def _getNEIItemOutputs(session, rec_id) -> List[NEI_Item]:
    item_outputs = []
    output_rows = await getAll(session, recipe_models_autogen.RecipeItemOutputs, filter=dict(recipe_id=rec_id))
    for row in output_rows:
        nei_item_info = {}

        group = row
        nei_item_info['item_id'] = group.item_outputs_value_item_id
        nei_item_info['output_probability'] = group.item_outputs_value_probability
        nei_item_info['stack_size'] = group.item_outputs_value_stack_size
        nei_item_info['position'] = group.item_outputs_key

        item_info = await getOne(session, recipe_models_autogen.Item, filter=dict(id=nei_item_info['item_id']))
        item_data = dict(item_info.__dict__)
        item_data.pop('_sa_instance_state')
        nei_item_info.update(item_data)
        nei_item_info['input'] = False

        item_outputs.append(NEI_Item(**nei_item_info))
    
    return item_outputs


async def _getNEIFluidOutputs(session, rec_id) -> List[NEI_Fluid]:
    fluid_outputs = []
    output_rows = await getAll(session, recipe_models_autogen.RecipeFluidOutputs, filter=dict(recipe_id=rec_id))
    for row in output_rows:
        nei_fluid_info = {}

        group = row
        nei_fluid_info['fluid_id'] = group.fluid_outputs_value_fluid_id
        nei_fluid_info['output_probability'] = group.fluid_outputs_value_probability
        nei_fluid_info['liters'] = group.fluid_outputs_value_amount
        nei_fluid_info['position'] = group.fluid_outputs_key

        fluid_info = await getOne(session, recipe_models_autogen.Fluid, filter=dict(id=nei_fluid_info['fluid_id']))
        fluid_data = dict(fluid_info.__dict__)
        fluid_data.pop('_sa_instance_state')
        nei_fluid_info.update(fluid_data)
        nei_fluid_info['input'] = False

        fluid_outputs.append(NEI_Fluid(**nei_fluid_info))
    
    return fluid_outputs


async def _getNEIRecipe(session, rec_id) -> NEI_Base_Recipe:
    construction_dict = dict(recipe_id=rec_id)

    construction_dict['input_items'] = await _getNEIItemInputs(session, rec_id)
    construction_dict['input_fluids'] = await _getNEIFluidInputs(session, rec_id)
    construction_dict['output_items'] = await _getNEIItemOutputs(session, rec_id)
    construction_dict['output_fluids'] = await _getNEIFluidOutputs(session, rec_id)

    return NEI_Base_Recipe(**construction_dict)


async def _getNEIGTRecipe(session, rec_id) -> NEI_GT_Recipe:
    # Get basic machine info
    machine_type_id = (await getOne(session, recipe_models_autogen.Recipe, dict(id=rec_id))).recipe_type_id
    recipe_type_info = await getOne(session, recipe_models_autogen.RecipeType, dict(id=machine_type_id))
    recipe_type_info = dict(recipe_type_info.__dict__)

    # Get base recipe info
    recipe_type_info['base_recipe'] = await _getNEIRecipe(session, rec_id)
    recipe_type_info['recipe_id'] = rec_id

    # Get GT specific info
    gt_recipe_info = await getOne(session, recipe_models_autogen.GregTechRecipe, dict(recipe_id=rec_id))
    gt_recipe_info = dict(gt_recipe_info.__dict__)
    gt_recipe_info['duration_ticks'] = gt_recipe_info.pop('duration')
    recipe_type_info.update(gt_recipe_info)

    # Reformat data
    recipe_type_info.pop('_sa_instance_state')
    recipe_type_info.pop('id')
    recipe_type_info.pop('category') # They're all going to be "gregtech"
    recipe_type_info['localized_machine_name'] = recipe_type_info.pop('type')
    recipe_type_info['fluid_input_dims'] = NEI_Recipe_Dimensions(
        height = recipe_type_info.pop('fluid_input_dimension_height'),
        width = recipe_type_info.pop('fluid_input_dimension_width'),
    )
    recipe_type_info['fluid_output_dims'] = NEI_Recipe_Dimensions(
        height = recipe_type_info.pop('fluid_output_dimension_height'),
        width = recipe_type_info.pop('fluid_output_dimension_width'),
    )
    recipe_type_info['item_input_dims'] = NEI_Recipe_Dimensions(
        height = recipe_type_info.pop('item_input_dimension_height'),
        width = recipe_type_info.pop('item_input_dimension_width'),
    )
    recipe_type_info['item_output_dims'] = NEI_Recipe_Dimensions(
        height = recipe_type_info.pop('item_output_dimension_height'),
        width = recipe_type_info.pop('item_output_dimension_width'),
    )

    return NEI_GT_Recipe(**recipe_type_info)


async def getNEIGTRecipe(recipe_id, info: Info) -> NEI_GT_Recipe:
    async with get_session() as session:
        recipe = await _getNEIGTRecipe(session, recipe_id)
    
    return recipe


async def getNSidebarRecipes(limit: int, info: Info) -> List[SidebarItem]:
    async with get_session() as session:
        stmt = select(recipe_models_autogen.Item).limit(limit)
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

    async with get_session() as session:
        # 1. Filter recipes by GT or "Other"
        type_info = [
            (await getOne(session, recipe_models_autogen.Recipe, filter=dict(id=recipe_id))).recipe_type_id.split('~')[1]
            for recipe_id
            in recipe_ids
        ]

        recipe_ids_by_type = defaultdict(list)
        for recipe_id, type_id in zip(recipe_ids, type_info):
            if type_id == 'gregtech':
                recipe_ids_by_type['GT'].append(recipe_id)
            else:
                recipe_ids_by_type['Other'].append(recipe_id)

        # 2. Construct recipes
        for recipe_type, recipe_ids in recipe_ids_by_type.items():
            for recipe_id in recipe_ids:
                if recipe_type == 'GT':
                    output_recipes[recipe_type].append(await getNEIGTRecipe(recipe_id, {}))
                else:
                    output_recipes[recipe_type].append(await _getNEIRecipe(session, recipe_id))

    return output_recipes


async def _determineSingleIdType(session, single_id) -> str:
    if (await getAll(session, recipe_models_autogen.Item, dict(id=single_id))):
        return 'Item'
    elif (await getAll(session, recipe_models_autogen.Fluid, dict(id=single_id))):
        return 'Fluid'
    else:
        raise ValueError(f"Invalid single_id: {single_id}")


async def getNEIRecipesThatMakeSingleId(single_id: int, info: Info) -> AssociatedRecipes:
    async with get_session() as session:
        single_type = await _determineSingleIdType(session, single_id)

        relevant_table = {
            'Item': recipe_models_autogen.RecipeItemOutputs,
            'Fluid': recipe_models_autogen.RecipeFluidOutputs,
        }[single_type]
        relevant_filter_key = {
            'Item': 'item_outputs_value_item_id',
            'Fluid': 'fluid_outputs_value_fluid_id',
        }[single_type]

        results = await getAll(session, relevant_table, filter={relevant_filter_key: single_id})
        recipe_ids = [x.recipe_id for x in results]

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
        single_type = await _determineSingleIdType(session, single_id)

        relevant_table = {
            'Item': recipe_models_autogen.ItemGroupItemStacks,
            'Fluid': recipe_models_autogen.FluidGroupFluidStacks,
        }[single_type]
        relevant_filter_key = {
            'Item': 'item_stacks_item_id',
            'Fluid': 'fluid_stacks_fluid_id',
        }[single_type]

        results = await getAll(session, relevant_table, filter={relevant_filter_key: single_id})
        group_ids = [x.item_group_id for x in results]

        relevant_table = {
            'Item': recipe_models_autogen.RecipeItemGroup,
            'Fluid': recipe_models_autogen.RecipeFluidGroup,
        }[single_type]
        relevant_attr = {
            'Item': 'item_inputs_id',
            'Fluid': 'fluid_inputs_id',
        }[single_type]

        stmt = select(relevant_table).filter(getattr(relevant_table, relevant_attr).in_(group_ids))
        results = (await session.execute(stmt)).scalars().all()
        recipe_ids = [x.recipe_id for x in results]

    output_recipes = await _getAndSplitNEIRecipesByType(session, recipe_ids)
    output_recipes = AssociatedRecipes(
        single_id = single_id,
        makeOrUse = 'Make',
        GTRecipes = output_recipes['GT'],
        OtherRecipes = output_recipes['Other'],
    )

    return output_recipes
