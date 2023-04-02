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
import src.graphql.models.recipe_models as recipe_models


# TODO:
# Actually follow graphql design philosophy lol
# (currently the whole resource is grabbed regardless of what the user asks)


async def _getNEIRecipeInputs(rec_id) -> List[NEI_Item]:
    item_inputs = []
    input_group_rows = await getAll(recipe_models.SQLItemGroup, filter=dict(recipe_id=rec_id))
    for row in input_group_rows:
        nei_item_info = {}

        group = row[0]
        item_group_id = group.item_inputs_id
        nei_item_info['position'] = group.item_inputs_key

        group_info = await getOne(recipe_models.SQLItemIdAndStackSize, filter=dict(item_group_id=item_group_id))
        nei_item_info['item_id'] = group_info.item_stacks_item_id
        nei_item_info['stack_size'] = group_info.item_stacks_stack_size

        item_info = await getOne(recipe_models.SQLItemDetails, filter=dict(id=nei_item_info['item_id']))
        item_data = dict(item_info.__dict__)
        item_data.pop('_sa_instance_state')
        item_data.pop('id')
        nei_item_info.update(item_data)
        nei_item_info['input'] = True

        item_inputs.append(NEI_Item(**nei_item_info))
    
    return item_inputs


async def _getNEIFluidInputs(rec_id) -> List[NEI_Fluid]:
    fluid_inputs = []
    input_group_rows = await getAll(recipe_models.SQLFluidGroup, filter=dict(recipe_id=rec_id))
    for row in input_group_rows:
        nei_fluid_info = {}

        group = row[0]
        fluid_group_id = group.fluid_inputs_id
        nei_fluid_info['position'] = group.fluid_inputs_key

        group_info = await getOne(recipe_models.SQLFluidIdAndLiters, filter=dict(fluid_group_id=fluid_group_id))
        nei_fluid_info['fluid_id'] = group_info.fluid_stacks_fluid_id
        nei_fluid_info['liters'] = group_info.fluid_stacks_amount

        fluid_info = await getOne(recipe_models.SQLFluidDetails, filter=dict(id=nei_fluid_info['fluid_id']))
        fluid_data = dict(fluid_info.__dict__)
        fluid_data.pop('_sa_instance_state')
        fluid_data.pop('id')
        nei_fluid_info.update(fluid_data)
        nei_fluid_info['input'] = True

        fluid_inputs.append(NEI_Fluid(**nei_fluid_info)) 
    
    return fluid_inputs


async def _getNEIItemOutputs(rec_id) -> List[NEI_Item]:
    item_outputs = []
    output_rows = await getAll(recipe_models.SQLRecipeItemOutputs, filter=dict(recipe_id=rec_id))
    for row in output_rows:
        nei_item_info = {}

        group = row[0]
        nei_item_info['item_id'] = group.item_outputs_value_item_id
        nei_item_info['output_probability'] = group.item_outputs_value_probability
        nei_item_info['stack_size'] = group.item_outputs_value_stack_size
        nei_item_info['position'] = group.item_outputs_key

        item_info = await getOne(recipe_models.SQLItemDetails, filter=dict(id=nei_item_info['item_id']))
        item_data = dict(item_info.__dict__)
        item_data.pop('_sa_instance_state')
        item_data.pop('id')
        nei_item_info.update(item_data)
        nei_item_info['input'] = False

        item_outputs.append(NEI_Item(**nei_item_info))
    
    return item_outputs


async def _getNEIFluidOutputs(rec_id) -> List[NEI_Fluid]:
    fluid_outputs = []
    output_rows = await getAll(recipe_models.SQLRecipeFluidOutputs, filter=dict(recipe_id=rec_id))
    for row in output_rows:
        nei_fluid_info = {}

        group = row[0]
        nei_fluid_info['fluid_id'] = group.fluid_outputs_value_fluid_id
        nei_fluid_info['output_probability'] = group.fluid_outputs_value_probability
        nei_fluid_info['liters'] = group.fluid_outputs_value_amount
        nei_fluid_info['position'] = group.fluid_outputs_key

        fluid_info = await getOne(recipe_models.SQLFluidDetails, filter=dict(id=nei_fluid_info['fluid_id']))
        fluid_data = dict(fluid_info.__dict__)
        fluid_data.pop('_sa_instance_state')
        fluid_data.pop('id')
        nei_fluid_info.update(fluid_data)
        nei_fluid_info['input'] = False

        fluid_outputs.append(NEI_Fluid(**nei_fluid_info))
    
    return fluid_outputs


async def _getNEIRecipe(rec_id) -> NEI_Base_Recipe:
    item_inputs = await _getNEIRecipeInputs(rec_id)
    item_outputs = await _getNEIItemOutputs(rec_id)
    fluid_inputs = await _getNEIFluidInputs(rec_id)
    fluid_outputs = await _getNEIFluidOutputs(rec_id)

    return NEI_Base_Recipe(rec_id, item_inputs, item_outputs, fluid_inputs, fluid_outputs)


async def _getNEIGTRecipe(rec_id) -> NEI_GT_Recipe:
    machine_type_id = (await getOne(recipe_models.SQLRecipe, dict(id=rec_id))).recipe_type_id
    recipe_type_info = await getOne(recipe_models.SQLRecipeType, dict(id=machine_type_id))
    recipe_type_info = dict(recipe_type_info.__dict__)
    recipe_type_info.pop('_sa_instance_state')
    recipe_type_info.pop('id')
    recipe_type_info.pop('category') # They're all going to be "gregtech"
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
        recipe = await _getNEIGTRecipe(recipe_id)
    
    return recipe
