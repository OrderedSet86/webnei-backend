from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / "envs/.env"
load_dotenv(dotenv_path=env_path)

from sqlalchemy import create_engine, text

from src.graphql.core.config import settings


database_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(database_url)


get_drop_index_commands = text("""
    SELECT 
        'DROP INDEX ' || quote_ident(n.nspname) || '.' || quote_ident(i.relname) AS drop_command
    FROM pg_index idx 
    JOIN pg_class i ON i.oid = idx.indexrelid
    JOIN pg_class t ON t.oid = idx.indrelid
    JOIN pg_namespace n ON n.oid = i.relnamespace
    WHERE NOT idx.indisprimary
    AND n.nspname = 'public'
""")

get_foreign_key_constraints = text("""
    SELECT 
        conname AS constraint_name,
        quote_ident(n.nspname) || '.' || quote_ident(c.relname) AS table_name
    FROM pg_constraint con
    JOIN pg_class c ON c.oid = con.conrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE confrelid > 0
    AND n.nspname = 'public'
""")

def generateHashCommand(table_name: str, column_name: str) -> str:
    index_name = f"hash_index_{table_name}_{column_name}"
    command = f"CREATE INDEX {index_name} ON {table_name} USING hash({column_name});"
    print(f'Generated index: {command}')
    return text(command)


with engine.connect() as connection:
    # Drop existing indexes
    result = connection.execute(get_drop_index_commands)
    for row in result:
        drop_index_command = row['drop_command']
        connection.execute(drop_index_command)
        print(f"Successfully executed: {drop_index_command}")

    # Drop existing foreign key constraints
    result = connection.execute(get_foreign_key_constraints)
    for row in result:
        constraint_name = row['constraint_name']
        table_name = row['table_name']
        drop_constraint_command = f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}"
        connection.execute(drop_constraint_command)
        print(f"Successfully executed: {drop_constraint_command}")

    # Add indexes for all commonly used joins
    # _getNEIItemInputs
    connection.execute(generateHashCommand('item_group_item_stacks', 'item_stacks_item_id'))
    connection.execute(generateHashCommand('item_group_item_stacks', 'item_group_id'))
    connection.execute(generateHashCommand('item', 'id'))
    connection.execute(generateHashCommand('recipe_item_group', 'item_inputs_id'))
    connection.execute(generateHashCommand('recipe_item_group', 'recipe_id'))
    # _getNEIFluidInputs
    connection.execute(generateHashCommand('fluid_group_fluid_stacks', 'fluid_stacks_fluid_id'))
    connection.execute(generateHashCommand('fluid_group_fluid_stacks', 'fluid_group_id'))
    connection.execute(generateHashCommand('fluid', 'id'))
    connection.execute(generateHashCommand('recipe_fluid_group', 'fluid_inputs_id'))
    connection.execute(generateHashCommand('recipe_fluid_group', 'recipe_id'))
    # _getNEIItemOutputs
    connection.execute(generateHashCommand('recipe_item_outputs', 'item_outputs_value_item_id'))
    connection.execute(generateHashCommand('recipe_item_outputs', 'recipe_id'))
    # _getNEIFluidOutputs
    connection.execute(generateHashCommand('recipe_fluid_outputs', 'fluid_outputs_value_fluid_id'))
    connection.execute(generateHashCommand('recipe_fluid_outputs', 'recipe_id'))
    # _getNEIGTRecipe
    connection.execute(generateHashCommand('recipe', 'id'))
    connection.execute(generateHashCommand('recipe', 'recipe_type_id'))
    connection.execute(generateHashCommand('greg_tech_recipe', 'recipe_id'))
    connection.execute(generateHashCommand('recipe_type', 'id'))
    # _getAndSplitNEIRecipesByType
    connection.execute(generateHashCommand('recipe_type', 'category'))

    # TODO: Add foreign key relationships where appropriate
