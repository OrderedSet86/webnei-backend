# WebNEI Backend

### Install \[Linux\]

1. Have PostgreSQL database version of nesql-exporter output (2.2.8 zip here https://github.com/harrynull/NEIGraphQL/releases/tag/gtnh_dump, you can load the dump with `psql -d nesql228 -f Downloads/dump.sql`)
2. Install pipenv https://pypi.org/project/pipenv/
3. (in root directory) `pipenv install`
4. Adjust PostgreSQL connection info in `envs/.env`
4. `pipenv shell` (do this before running anything in the directory)
5. Run database migration script `python -m src.scripts.prepare_postgres_db`. This sets up indices for faster search
6. `python main.py`
7. Check running properly at `http://localhost:5000/graphql`
8. Try sending these example queries:

```graphql
query RecipeByRecipeID {
  getGTRecipeByRecipeId(recipeId: "r~--eEYPHsN5GqWygrEHan4A==") {
    localizedMachineName
    durationTicks
    voltage
    amperage
    baseRecipe {
      dimensions {
        itemInputDims {
          height
          width
        }
      }
      inputItems {
        id
        localizedName
        stackSize
      }
      outputItems {
        id
        localizedName
        itemId
        stackSize
      }
    }
  }
}
```

```graphql
query SidebarItems(
  $limit: Int! = 1000,
  $search: String! = "Zombie|Skeleton",
  $mode: String! = "regex"
) {
  getNSidebarItems(limit: $limit, search: $search, mode: $mode) {
    itemId
    localizedName
    tooltip
    imageFilePath
  }
}
```

```graphql
query UseItems($single_id: String! = "i~gregtech~gt.metaitem.01~23019") {
  getRecipesThatUseSingleId(itemId: $single_id) {
    singleId
    GTRecipes {
      localizedMachineName
      amperage
      voltage
      durationTicks
      baseRecipe {
        inputItems {
          id
          localizedName
          stackSize
        }
        outputItems {
          localizedName
          stackSize
        }
      }
    }
  }
}
```

```graphql
query MakeItems($single_id: String! = "i~gregtech~gt.metaitem.01~23019") {
  getRecipesThatMakeSingleId(itemId: $single_id) {
    singleId
    GTRecipes {
      localizedMachineName
      amperage
      voltage
      durationTicks
      baseRecipe {
        ...NEIBaseRecipeFragment
      }
      additionalInfo
      recipeId
      requiresCleanroom
      requiresLowGravity
      shapeless
      voltageTier
    }
    OtherRecipes {
      ...NEIBaseRecipeFragment
    }
  }
}

fragment NEIFluidFragment on NEIFluid {
  density
  fluidId
  gaseous
  id
  imageFilePath
  input
  internalName
  localizedName
  liters
  luminosity
  modId
  nbt
  outputProbability
  position
  temperature
  unlocalizedName
  viscosity
}

fragment NEIItemFragment on NEIItem {
  id
  localizedName
  stackSize
  imageFilePath
  input
  internalName
  itemDamage
  itemId
  maxDamage
  maxStackSize
  modId
  nbt
  outputProbability
  position
  tooltip
  unlocalizedName
}

fragment RecipeDimensionFragment on NEIRecipeDimensions {
  height
  width
}

fragment NEIDimensionFragment on NEIAllDimensions {
  itemInputDims {
    ...RecipeDimensionFragment
  }
  itemOutputDims {
    ...RecipeDimensionFragment
  }
  fluidInputDims {
    ...RecipeDimensionFragment
  }
  fluidOutputDims {
    ...RecipeDimensionFragment
  }
}

fragment NEIBaseRecipeFragment on NEIBaseRecipe {
  recipeId
  
  iconId
  dimensions {
    ...NEIDimensionFragment
  }
  inputItems {
    ...NEIItemFragment
  }
  outputItems {
    ...NEIItemFragment
  }
  inputFluids {
    ...NEIFluidFragment
  }
  outputFluids {
    ...NEIFluidFragment
  }
}
```