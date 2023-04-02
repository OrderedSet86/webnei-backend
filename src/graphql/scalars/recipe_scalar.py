import strawberry
from pydantic import List


@strawberry.type
class NEI_Item:
    item_id: int

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
    fluid_id: int

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
class NEI_Base_Recipe:
    recipe_id: int

    input_items: List[NEI_Item]
    input_fluids: List[NEI_Fluid]
    output_items: List[NEI_Item]
    output_fluids: List[NEI_Item]


@strawberry.type
class NEI_GT_Recipe:
    recipe_id: int

    base_recipe: NEI_Base_Recipe

    # Type info for recipe
    localized_machine_name: str
    fluid_input_dims: List[int]
    fluid_output_dims: List[int]
    item_input_dims: List[int]
    item_output_dims: List[int]
    icon_info: str
    icon_id: str
    shapeless: bool
