# WebNEI Backend

### Install \[Linux\]

1. Have PostgreSQL database version of nesql-exporter output
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
    makeOrUse
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
    makeOrUse
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