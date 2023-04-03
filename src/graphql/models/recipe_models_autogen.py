# Autogenerated by: sqlacodegen <db_name> > recipe_model_autogen.py
# Some tables generate as "Table" instead of inheriting from Base, those need manual editing

from sqlalchemy import BigInteger, Boolean, Column, Float, Index, Integer, PrimaryKeyConstraint, String, Table

from . import Base


class Aspect(Base):
    __tablename__ = 'aspect'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='aspect_pkey'),
    )

    id = Column(String(255))
    description = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    primal = Column(Boolean, nullable=False)
    icon_id = Column(String(255))


class AspectAspect(Base):
    __tablename__ = 'aspect_aspect'
    __table_args__ = (
        PrimaryKeyConstraint('component_of_id', 'components_id', name='aspect_aspect_pkey'),
    )

    component_of_id = Column(String(255), nullable=False)
    components_id = Column(String(255), nullable=False)


class AspectEntry(Base):
    __tablename__ = 'aspect_entry'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='aspect_entry_pkey'),
    )

    id = Column(String(255))
    amount = Column(Integer, nullable=False)
    aspect_id = Column(String(255))
    item_id = Column(String(255))


class Fluid(Base):
    __tablename__ = 'fluid'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='fluid_pkey'),
    )

    id = Column(String(255))
    density = Column(Integer, nullable=False)
    fluid_id = Column(Integer, nullable=False)
    gaseous = Column(Boolean, nullable=False)
    image_file_path = Column(String(255), nullable=False)
    internal_name = Column(String(255), nullable=False)
    localized_name = Column(String(255), nullable=False)
    luminosity = Column(Integer, nullable=False)
    mod_id = Column(String(255), nullable=False)
    nbt = Column(String(32767), nullable=False)
    temperature = Column(Integer, nullable=False)
    unlocalized_name = Column(String(255), nullable=False)
    viscosity = Column(Integer, nullable=False)


class FluidBlock(Base):
    __tablename__ = 'fluid_block'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='fluid_block_pkey'),
    )

    id = Column(String(255))
    block_id = Column(String(255))
    fluid_id = Column(String(255))


class FluidContainer(Base):
    __tablename__ = 'fluid_container'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='fluid_container_pkey'),
    )

    id = Column(String(255))
    fluid_stack_amount = Column(Integer, nullable=False)
    container_id = Column(String(255))
    empty_container_id = Column(String(255))
    fluid_stack_fluid_id = Column(String(255))


class FluidGroup(Base):
    __tablename__ = 'fluid_group'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='fluid_group_pkey'),
    )

    id = Column(String(255))


class FluidGroupFluidStacks(Base):
    __tablename__ = 'fluid_group_fluid_stacks'

    fluid_stacks_fluid_id = Column(String(255), primary_key=True)
    fluid_group_id = Column(String(255), nullable=False)
    fluid_stacks_amount = Column(Integer(), nullable=False)


class GregTechRecipe(Base):
    __tablename__ = 'greg_tech_recipe'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='greg_tech_recipe_pkey'),
    )

    id = Column(String(255))
    additional_info = Column(String(32767), nullable=False)
    amperage = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    requires_cleanroom = Column(Boolean, nullable=False)
    requires_low_gravity = Column(Boolean, nullable=False)
    voltage = Column(Integer, nullable=False)
    voltage_tier = Column(String(255), nullable=False)
    recipe_id = Column(String(255))


class GregTechRecipeItem(Base):
    __tablename__ = 'greg_tech_recipe_item'

    greg_tech_recipe_id = Column(String(255), primary_key=True, nullable=False)
    special_items_id = Column(String(255), nullable=False)


class GregTechRecipeModOwners(Base):
    __tablename__ = 'greg_tech_recipe_mod_owners'
    __table_args__ = (
        PrimaryKeyConstraint('greg_tech_recipe_id', 'mod_owners_order', name='greg_tech_recipe_mod_owners_pkey'),
    )

    greg_tech_recipe_id = Column(String(255), nullable=False)
    mod_owners_order = Column(Integer, nullable=False)
    mod_owners = Column(String(255))


class Item(Base):
    __tablename__ = 'item'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='item_pkey'),
    )

    id = Column(String(255))
    image_file_path = Column(String(255), nullable=False)
    internal_name = Column(String(255), nullable=False)
    item_damage = Column(Integer, nullable=False)
    item_id = Column(Integer, nullable=False)
    localized_name = Column(String(255), nullable=False)
    max_damage = Column(Integer, nullable=False)
    max_stack_size = Column(Integer, nullable=False)
    mod_id = Column(String(255), nullable=False)
    nbt = Column(String(32767), nullable=False)
    tooltip = Column(String(32767), nullable=False)
    unlocalized_name = Column(String(255), nullable=False)


class ItemGroup(Base):
    __tablename__ = 'item_group'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='item_group_pkey'),
    )

    id = Column(String(255))
    base_item_group_id = Column(String(255))


class ItemGroupItemStacks(Base):
    __tablename__ = 'item_group_item_stacks'

    item_group_id = Column(String(255), nullable=False)
    item_stacks_item_id = Column(String(255), primary_key=True, nullable=False)
    item_stacks_stack_size = Column(Integer(), nullable=False)


class ItemToolClasses(Base):
    __tablename__ = 'item_tool_classes'
    __table_args__ = (
        PrimaryKeyConstraint('item_id', 'tool_classes_key', name='item_tool_classes_pkey'),
    )

    item_id = Column(String(255), nullable=False)
    tool_classes_key = Column(String(255), nullable=False)
    tool_classes = Column(Integer)


class Metadata(Base):
    __tablename__ = 'metadata'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='metadata_pkey'),
    )

    id = Column(Integer)
    creation_time_millis = Column(BigInteger, nullable=False)
    version = Column(String(255), nullable=False)


class MetadataActivePlugins(Base):
    __tablename__ = 'metadata_active_plugins'

    metadata_id = Column(Integer, primary_key=True, nullable=False)
    active_plugins = Column(String(255))


class OreDictionary(Base):
    __tablename__ = 'ore_dictionary'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='ore_dictionary_pkey'),
    )

    id = Column(String(255))
    name = Column(String(255), nullable=False)
    item_group_id = Column(String(255))


class Quest(Base):
    __tablename__ = 'quest'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='quest_pkey'),
    )

    id = Column(String(255))
    description = Column(String(32767), nullable=False)
    name = Column(String(255), nullable=False)
    quest_id = Column(Integer, nullable=False)
    quest_logic = Column(String(255), nullable=False)
    repeat_time = Column(Integer, nullable=False)
    task_logic = Column(String(255), nullable=False)
    visibility = Column(String(255), nullable=False)
    icon_id = Column(String(255))


class QuestLine(Base):
    __tablename__ = 'quest_line'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='quest_line_pkey'),
    )

    id = Column(String(255))
    description = Column(String(32767), nullable=False)
    name = Column(String(255), nullable=False)
    quest_line_id = Column(Integer, nullable=False)
    visibility = Column(String(255), nullable=False)
    icon_id = Column(String(255))


class QuestLineQuest(Base):
    __tablename__ = 'quest_line_quest'
    __table_args__ = (
        PrimaryKeyConstraint('quest_lines_id', 'quests_id', name='quest_line_quest_pkey'),
    )

    quest_lines_id = Column(String(255), nullable=False)
    quests_id = Column(String(255), nullable=False)


class QuestQuest(Base):
    __tablename__ = 'quest_quest'
    __table_args__ = (
        PrimaryKeyConstraint('required_by_quests_id', 'required_quests_id', name='quest_quest_pkey'),
    )

    required_by_quests_id = Column(String(255), nullable=False)
    required_quests_id = Column(String(255), nullable=False)


class QuestReward(Base):
    __tablename__ = 'quest_reward'
    __table_args__ = (
        PrimaryKeyConstraint('quest_id', 'rewards_order', name='quest_reward_pkey'),
    )

    quest_id = Column(String(255), nullable=False)
    rewards_id = Column(String(255), nullable=False)
    rewards_order = Column(Integer, nullable=False)


class QuestTask(Base):
    __tablename__ = 'quest_task'
    __table_args__ = (
        PrimaryKeyConstraint('quest_id', 'tasks_order', name='quest_task_pkey'),
    )

    quest_id = Column(String(255), nullable=False)
    tasks_id = Column(String(255), nullable=False)
    tasks_order = Column(Integer, nullable=False)


class Recipe(Base):
    __tablename__ = 'recipe'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='recipe_pkey'),
        Index('idxcpa5258x6vhsi07adbl3prq5m', 'recipe_type_id')
    )

    id = Column(String(255))
    recipe_type_id = Column(String(255))


class RecipeFluidGroup(Base):
    __tablename__ = 'recipe_fluid_group'
    __table_args__ = (
        PrimaryKeyConstraint('recipe_id', 'fluid_inputs_key', name='recipe_fluid_group_pkey'),
    )

    recipe_id = Column(String(255), nullable=False)
    fluid_inputs_id = Column(String(255), nullable=False)
    fluid_inputs_key = Column(Integer, nullable=False)


class RecipeFluidInputsFluids(Base):
    __tablename__ = 'recipe_fluid_inputs_fluids'
    __table_args__ = (
        PrimaryKeyConstraint('recipe_id', 'fluid_inputs_fluids_id', name='recipe_fluid_inputs_fluids_pkey'),
        Index('idxcufvh84l5i5affrolnox6raqu', 'fluid_inputs_fluids_id')
    )

    recipe_id = Column(String(255), nullable=False)
    fluid_inputs_fluids_id = Column(String(255), nullable=False)


class RecipeFluidOutputs(Base):
    __tablename__ = 'recipe_fluid_outputs'
    __table_args__ = (
        PrimaryKeyConstraint('recipe_id', 'fluid_outputs_key', name='recipe_fluid_outputs_pkey'),
    )

    recipe_id = Column(String(255), nullable=False)
    fluid_outputs_value_amount = Column(Integer, nullable=False)
    fluid_outputs_value_probability = Column(Float(53), nullable=False)
    fluid_outputs_key = Column(Integer, nullable=False)
    fluid_outputs_value_fluid_id = Column(String(255))


class RecipeItemGroup(Base):
    __tablename__ = 'recipe_item_group'
    __table_args__ = (
        PrimaryKeyConstraint('recipe_id', 'item_inputs_key', name='recipe_item_group_pkey'),
    )

    recipe_id = Column(String(255), nullable=False)
    item_inputs_id = Column(String(255), nullable=False)
    item_inputs_key = Column(Integer, nullable=False)


class RecipeItemInputsItems(Base):
    __tablename__ = 'recipe_item_inputs_items'
    __table_args__ = (
        PrimaryKeyConstraint('recipe_id', 'item_inputs_items_id', name='recipe_item_inputs_items_pkey'),
        Index('idx7c3suiaky8746skwfqg71no9x', 'item_inputs_items_id')
    )

    recipe_id = Column(String(255), nullable=False)
    item_inputs_items_id = Column(String(255), nullable=False)


class RecipeItemOutputs(Base):
    __tablename__ = 'recipe_item_outputs'
    __table_args__ = (
        PrimaryKeyConstraint('recipe_id', 'item_outputs_key', name='recipe_item_outputs_pkey'),
    )

    recipe_id = Column(String(255), nullable=False)
    item_outputs_value_probability = Column(Float(53), nullable=False)
    item_outputs_value_stack_size = Column(Integer, nullable=False)
    item_outputs_key = Column(Integer, nullable=False)
    item_outputs_value_item_id = Column(String(255))


class RecipeType(Base):
    __tablename__ = 'recipe_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='recipe_type_pkey'),
    )

    id = Column(String(255))
    category = Column(String(255), nullable=False)
    fluid_input_dimension_height = Column(Integer, nullable=False)
    fluid_input_dimension_width = Column(Integer, nullable=False)
    fluid_output_dimension_height = Column(Integer, nullable=False)
    fluid_output_dimension_width = Column(Integer, nullable=False)
    icon_info = Column(String(255), nullable=False)
    item_input_dimension_height = Column(Integer, nullable=False)
    item_input_dimension_width = Column(Integer, nullable=False)
    item_output_dimension_height = Column(Integer, nullable=False)
    item_output_dimension_width = Column(Integer, nullable=False)
    shapeless = Column(Boolean, nullable=False)
    type = Column(String(255), nullable=False)
    icon_id = Column(String(255))


class Reward(Base):
    __tablename__ = 'reward'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='reward_pkey'),
    )

    id = Column(String(255))
    command = Column(String(255), nullable=False)
    complete_quest_id = Column(Integer, nullable=False)
    levels = Column(Boolean, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    xp = Column(Integer, nullable=False)


class RewardItemGroup(Base):
    __tablename__ = 'reward_item_group'
    __table_args__ = (
        PrimaryKeyConstraint('reward_id', 'items_order', name='reward_item_group_pkey'),
    )

    reward_id = Column(String(255), nullable=False)
    items_id = Column(String(255), nullable=False)
    items_order = Column(Integer, nullable=False)


class Task(Base):
    __tablename__ = 'task'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='task_pkey'),
    )

    id = Column(String(255))
    consume = Column(Boolean, nullable=False)
    dimension_name = Column(String(255), nullable=False)
    entity_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    number_required = Column(Integer, nullable=False)
    type = Column(String(255), nullable=False)


class TaskFluids(Base):
    __tablename__ = 'task_fluids'
    __table_args__ = (
        PrimaryKeyConstraint('task_id', 'fluids_order', name='task_fluids_pkey'),
    )

    task_id = Column(String(255), nullable=False)
    fluids_amount = Column(Integer, nullable=False)
    fluids_order = Column(Integer, nullable=False)
    fluids_fluid_id = Column(String(255))


class TaskItemGroup(Base):
    __tablename__ = 'task_item_group'
    __table_args__ = (
        PrimaryKeyConstraint('task_id', 'items_order', name='task_item_group_pkey'),
    )

    task_id = Column(String(255), nullable=False)
    items_id = Column(String(255), nullable=False)
    items_order = Column(Integer, nullable=False)
