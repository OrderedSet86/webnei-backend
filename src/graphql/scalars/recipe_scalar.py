import strawberry
from typing import List


@strawberry.type
class NEI_Item:
    id: str
    item_id: str

    position: int
    stack_size: int

    image_file_path: str
    internal_name: str
    item_damage: int
    localized_name: str
    max_damage: int
    max_stack_size: int
    mod_id: str
    nbt: str
    tooltip: str
    unlocalized_name: str

    input: bool
    output_probability: float = -1.0


@strawberry.type
class NEI_Fluid:
    id: str
    fluid_id: str

    position: int
    liters: int

    density: int
    fluid_id: int
    gaseous: bool
    image_file_path: str
    internal_name: str
    localized_name: str
    luminosity: int
    mod_id: str
    nbt: str
    temperature: int
    unlocalized_name: str
    viscosity: int

    input: bool
    output_probability: float = -1.0


@strawberry.type
class NEI_Recipe_Dimensions:
    height: int
    width: int


@strawberry.type
class NEI_All_Dimensions:
    fluid_input_dims: NEI_Recipe_Dimensions
    fluid_output_dims: NEI_Recipe_Dimensions
    item_input_dims: NEI_Recipe_Dimensions
    item_output_dims: NEI_Recipe_Dimensions


@strawberry.type
class NEI_Base_Recipe:
    recipe_id: str

    recipe_type: str
    icon_id: str
    dimensions: NEI_All_Dimensions
    input_items: List[NEI_Item]
    output_items: List[NEI_Item]
    input_fluids: List[NEI_Fluid]
    output_fluids: List[NEI_Fluid]


@strawberry.type
class NEI_GT_Recipe:
    recipe_id: str

    base_recipe: NEI_Base_Recipe

    # Type info for recipe
    localized_machine_name: str
    icon_info: str
    icon_id: str
    shapeless: bool

    # GT Info for recipe
    additional_info: str
    amperage: int
    duration_ticks: int
    requires_cleanroom: bool
    requires_low_gravity: bool
    voltage: int
    voltage_tier: str


@strawberry.type
class SidebarItem:
    item_id: str
    image_file_path: str
    localized_name: str
    tooltip: str


@strawberry.type
class AssociatedRecipes:
    single_id: str
    GTRecipes: List[NEI_GT_Recipe]
    OtherRecipes: List[NEI_Base_Recipe]
