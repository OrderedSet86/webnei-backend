from pydantic.typing import List

from src.graphql.db.session import get_session
from src.graphql.db.utils import getOne, getAll
from src.graphql.scalars.recipe_scalar import (
    NEI_Base_Recipe,
    NEI_Fluid,
    NEI_GT_Recipe,
    NEI_Item,
    NEI_Recipe_Dimensions,
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
        item_data.pop('id')
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
        fluid_data.pop('id')
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
        item_data.pop('id')
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

        fluid_info = await getOne(session, recipe_models_autogen.SQLFluidDetails, filter=dict(id=nei_fluid_info['fluid_id']))
        fluid_data = dict(fluid_info.__dict__)
        fluid_data.pop('_sa_instance_state')
        fluid_data.pop('id')
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


async def get_recipe(recipe_id, info) -> NEI_GT_Recipe:
    async with get_session() as session:
        recipe = await _getNEIGTRecipe(session, recipe_id)
    
    return recipe
