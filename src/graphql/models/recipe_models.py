from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

from . import Base


class SQLGregtechRecipe(Base):
    # recipe ID -> GT recipe info
    __tablename__ = 'greg_tech_recipe'

    id = Column(String(255), primary_key=True)
    additional_info = Column(String(32767))
    amperage = Column(Integer())
    duration = Column(Integer()) # in ticks
    requires_cleanroom = Column(Boolean())
    requires_low_gravity = Column(Boolean())
    voltage = Column(Integer())
    voltage_tier = Column(Integer())
    recipe_id = Column(String(255))


class SQLRecipe(Base):
    # recipe IDs by type (eg GT machine, crafting table)
    __tablename__ = 'recipe'

    id = Column('id', String(255), primary_key=True)
    recipe_type_id = Column(String(255))


class SQLItemGroup(Base):
    # recipe ID -> item "input group" IDs
    __tablename__ = 'recipe_item_group'

    recipe_id = Column(String(255), primary_key=True)
    item_inputs_id = Column(String(255))
    item_inputs_key = Column(Integer()) # "Position" of the item (meaning is recipe dependent)


class SQLItemIdAndStackSize(Base):
    # Item "input group" ID -> item and stack size
    __tablename__ = 'item_group_item_stacks'

    item_group_id = Column(String(255), primary_key=True)
    item_stacks_item_id = Column(String(255))
    item_stacks_stack_size = Column(Integer())


class SQLItemDetails(Base):
    # Item ID -> item details
    __tablename__ = 'item'

    id = Column(String(255), primary_key=True)
    image_file_path = Column(String(255))
    internal_name = Column(String(255))
    item_damage = Column(Integer())
    item_id = Column(Integer())
    localized_name = Column(String(255))
    max_damage = Column(Integer())
    max_stack_size = Column(Integer())
    mod_id = Column(String(255))
    nbt = Column(String(32767))
    tooltip = Column(String(32767))
    unlocalized_name = Column(String(255))


class SQLFluidGroup(Base):
    # recipe ID -> fluid "input group" IDs
    __tablename__ = 'recipe_fluid_group'

    recipe_id = Column(String(255), primary_key=True)
    fluid_inputs_id = Column(String(255))
    fluid_inputs_key = Column(Integer()) # "Position" of the fluid (meaning is recipe dependent)


class SQLFluidIdAndLiters(Base):
    # Item "input group" ID -> item and stack size
    __tablename__ = 'fluid_group_fluid_stacks'

    fluid_group_id = Column(String(255), primary_key=True)
    fluid_stacks_amount = Column(Integer())
    fluid_stacks_fluid_id = Column(String(255))


class SQLFluidDetails(Base):
    # fluid ID -> fluid details
    __tablename__ = 'fluid'

    id = Column(String(255), primary_key=True)
    density = Column(Integer())
    fluid_id = Column(Integer())
    gaseous = Column(Boolean())
    image_file_path = Column(String(255))
    internal_name = Column(String(255))
    localized_name = Column(String(255))
    luminosity = Column(Integer())
    mod_id = Column(String(255))
    nbt = Column(String(32767))
    temperature = Column(Integer())
    unlocalized_name = Column(String(255))
    viscosity = Column(Integer())


class SQLRecipeItemOutputs(Base):
    # recipe id -> output item IDs
    __tablename__ = 'recipe_item_outputs'

    recipe_id = Column(String(255), primary_key=True)
    item_outputs_value_item_id = Column(String(255))
    item_outputs_value_probability = Column(DOUBLE_PRECISION())
    item_outputs_value_stack_size = Column(Integer())
    item_outputs_key = Column(Integer()) # "Position" of the item (meaning is recipe dependent)


class SQLRecipeFluidOutputs(Base):
    # recipe id -> output fluid IDs
    __tablename__ = 'recipe_fluid_outputs'

    recipe_id = Column(String(255), primary_key=True)
    fluid_outputs_value_amount = Column(Integer())
    fluid_outputs_value_fluid_id = Column(String(255))
    fluid_outputs_value_probability = Column(DOUBLE_PRECISION())
    fluid_outputs_key = Column(Integer()) # "Position" of the fluid (meaning is recipe dependent)


class SQLRecipeTypeInfo(Base):
    # recipe id -> dims and localized name
    __tablename__ = 'recipe_type'

    id = Column(String(255), primary_key=True)
    category = Column(String(255))
    fluid_input_dimension_height = Column(Integer())
    fluid_input_dimension_width = Column(Integer())
    fluid_output_dimension_height = Column(Integer())
    fluid_output_dimension_width = Column(Integer())
    icon_info = Column(String(255))
    item_input_dimension_height = Column(Integer()) 
    item_input_dimension_width = Column(Integer())
    item_output_dimension_height = Column(Integer())
    item_output_dimension_width = Column(Integer())
    shapeless = Column(Boolean())
    type = Column(String(255))
    icon_id = Column(String(255))
