from enum import Enum


class RecipeResponseType(Enum):
    HOME_PREVIEW_PAGINATE = 0,
    HOME_PREVIEW_BY_CATEGORY = 1,
    RECIPE_DETAILS = 2
