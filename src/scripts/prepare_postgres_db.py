from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / "envs/.env"
load_dotenv(dotenv_path=env_path)

from typing import List

from sqlalchemy import create_engine, text

from src.graphql.core.config import settings


script_config = dict(
    override_existing_indexes=True,
    override_existing_primary_keys=True,
    override_existing_foreign_keys=True,
)

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

def getPrimaryKeyColumns(engine, table_name: str) -> List[str]:
    check_primary_key_query = text(f"""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_schema = 'public'
        AND tc.table_name = '{table_name}'
        AND tc.constraint_type = 'PRIMARY KEY';
    """)
    with engine.connect() as connection:
        result = connection.execute(check_primary_key_query, schema_name="public", table_name=table_name)
    column_names = [row.column_name for row in result]
    return column_names

def generateHashCommand(table_name: str, column_name: str) -> str:
    index_name = f"hash_index_{table_name}_{column_name}"
    command = f"CREATE INDEX {index_name} ON {table_name} USING hash({column_name});"
    print(f'Generated index: {command}')
    return text(command)

def generatePrimaryKeyCommand(table_name: str, column_name: str) -> str:
    constraint_name = f"pk_{table_name}"
    command = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} PRIMARY KEY ({column_name});"
    print(f'Generated primary key: {command}')
    return text(command)

def generateForeignKeyCommand(table_name: str, column_name: str, referenced_table_name: str, referenced_column_name: str) -> str:
    constraint_name = f"fk_{table_name}_{column_name}_{referenced_table_name}_{referenced_column_name}"
    command = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({column_name}) REFERENCES {referenced_table_name} ({referenced_column_name});"
    print(f'Generated foreign key: {command}')
    return text(command)

with engine.connect() as connection:
    if script_config['override_existing_indexes']:
        # Drop existing indexes
        result = connection.execute(get_drop_index_commands)
        for row in result:
            drop_index_command = row['drop_command']
            connection.execute(drop_index_command)
            print(f"Successfully executed: {drop_index_command}")

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
        # getNEIRecipesThatUseSingleId
        connection.execute(generateHashCommand('recipe_item_inputs_items', 'item_inputs_items_id'))
        connection.execute(generateHashCommand('recipe_fluid_inputs_fluids', 'fluid_inputs_fluids_id'))

    if script_config['override_existing_primary_keys']:
        # Add primary key constraints to tables without any (so sqlacodegen doesn't produce non-classes)
        if not getPrimaryKeyColumns(engine, 'item_group_item_stacks'):
            connection.execute(generatePrimaryKeyCommand(
                'item_group_item_stacks',
                'item_group_id, item_stacks_item_id, item_stacks_stack_size',
            ))
        if not getPrimaryKeyColumns(engine, 'fluid_group_fluid_stacks'):
            connection.execute(generatePrimaryKeyCommand(
                'fluid_group_fluid_stacks',
                'fluid_group_id, fluid_stacks_fluid_id, fluid_stacks_amount',
            ))
        if not getPrimaryKeyColumns(engine, 'greg_tech_recipe_item'):
            connection.execute(generatePrimaryKeyCommand(
                'greg_tech_recipe_item',
                'greg_tech_recipe_id, special_items_id',
            ))
        if not getPrimaryKeyColumns(engine, 'metadata_active_plugins'):
            connection.execute(generatePrimaryKeyCommand(
                'metadata_active_plugins',
                'metadata_id, active_plugins',
            ))

    if script_config['override_existing_foreign_keys']:
        # Drop existing foreign key constraints
        result = connection.execute(get_foreign_key_constraints)
        for row in result:
            constraint_name = row['constraint_name']
            table_name = row['table_name']
            drop_constraint_command = f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}"
            connection.execute(drop_constraint_command)
            print(f"Successfully executed: {drop_constraint_command}")

        # Add foreign key relationships
        connection.execute(generateForeignKeyCommand('item_group_item_stacks', 'item_stacks_item_id', 'item', 'id'))
        # connection.execute(generateForeignKeyCommand('item_group_item_stacks', 'item_group_id', 'recipe_item_group', 'item_inputs_id'))
