import os
import random
import uuid
from http import HTTPMethod

import responses
from . import models
from recipes.ws import api_request
from recipes.models import DIFFICULTY_CHOICES


DIFFICULTY_CHOICES_CHOICE = [choice[0] for choice in DIFFICULTY_CHOICES]
BOUNDARY = "BoUnDaRyStRiNg"
MULTIPART_CONTENT = "multipart/form-data; boundary=%s" % BOUNDARY



def responses_register_mock(method: responses, path: str, status_code: int, json_data=None):
    responses.add(
        method,
        f"{os.getenv('SERVICE_BASE_URL')}/{path}",
        json=json_data,
        status=status_code,
    )


def mock_get_recipe_by_pk(client):
    json_response, categories_response = mock_categories_and_get_json_response(models.RecipeResponseType.RECIPE_DETAILS)

    recipe_pk = json_response['pk']
    responses_register_mock(method=responses.GET, path=f"api/recipe/{recipe_pk}/", json_data=json_response,
                            status_code=200)
    api_request.get_recipe_by_pk(recipe_pk)

    return json_response, recipe_pk, categories_response


def mock_post_recipe_ingredients(recipe_pk: int):
    response_data = [{"name": "Kasher salt", "quantity": "1/5", "metric": "tbsp"},
                     {"name": "Pudding mix", "quantity": "1", "metric": "pcs"}]

    responses_register_mock(method=responses.POST, path=f"api/recipe/{recipe_pk}/ingredients", status_code=201,
                            json_data=response_data)

    return response_data


def mock_post_recipe_instructions(recipe_pk: int):
    response_data = [{"text": "Heat the oven"}, {"text": "Take a break"}, {"text": "Prepare the mix"},
                     {"text": "Enjoy"}]
    responses_register_mock(method=responses.POST, path=f"api/recipe/{recipe_pk}/steps", status_code=201,
                            json_data=response_data)

    return response_data


def mock_create_update_recipe_full_info(method: HTTPMethod, status_code: int):
    response_recipe = {"pk": 1,
                     "image": "http://localhost:8000/media/images/d729b3c0-104a-46b4-8947-b212ca8a4c95_annie-spratt-vI-uFNolpLA-unsplash.jpg",
                     "name": "New name", "servings": 4, "chef": "Thomas Keller",
                     "video": "http://localhost:8000/media/videos/6022c9d3-ad36-4130-a947-53d93cee0163_upload-video.mp4",
                     "description": "asd", "category": 1, "tag": None, "prep_time": 21, "cook_time": 25,
                     "total_time": 0.77,
                     "difficulty": "Intermediate", "is_favorite": False,
                     "ingredients": [{"name": "chicken breast", "quantity": "2", "metric": "lbs"},
                                     {"name": "all-purpose flour", "quantity": "1.5", "metric": "cups"}],
                     "steps": [{"text": "Preheat the oven to 375°F."}, {"text": "Chop the carrots into small cubes."},
                               {"text": "Whisk the eggs until fluffy."},
                               {"text": "Add 2 cups of flour to the mixture."}]}

    response_data = response_recipe if status_code != 400 else {"category":["Incorrect type. Expected pk value, received str."]}

    match method:
        case HTTPMethod.POST:
            responses_register_mock(method=responses.POST, path=f"api/recipe/", status_code=status_code, json_data=response_data)
        case HTTPMethod.PUT:
            responses_register_mock(method=responses.PUT, path=f"api/recipe/{response_recipe['pk']}", status_code=status_code,
                                    json_data=response_data)

    ingredients_response_data = mock_post_recipe_ingredients(response_recipe['pk'])
    instructions_response_data = mock_post_recipe_instructions(response_recipe['pk'])

    return response_data, ingredients_response_data, instructions_response_data


def mock_data_recipe_on_update_or_create(method: HTTPMethod, recipe_pk, categories_response, status_code: int):
    post_data = {
        "name": f"name-{uuid.uuid4()}",
        "category": categories_response[0]['pk'],
        "difficulty": random.choice(DIFFICULTY_CHOICES_CHOICE),
        "prep_time": int(random.uniform(20, 60)),
        "cook_time": int(random.uniform(10, 60)),
        "servings": int(random.uniform(1, 10)),
        "description": f"Description-{uuid.uuid4()}",
        "chef": f"Chef-{uuid.uuid4()}",
        "ingredient_name[]": ['ingredient-1', 'ingredient-4', 'ingredient-3'],
        "ingredient_quantity[]": ['10', '20', '30'],
        "ingredient_metric[]": ["pcs", "tbs", "tps"],
        "instructions[]": [f"Instruction-{uuid.uuid4()}", f"Instruction-{uuid.uuid4()}"],
        "clear_video": False
    }

    recipe_main_info_data = {
        "name": post_data['name'],
        "category": post_data['category'],
        "difficulty": post_data['difficulty'],
        "prep_time": post_data['prep_time'],
        "cook_time": post_data['cook_time'],
        "servings": post_data['servings'],
        "description": post_data['description'],
        "chef": post_data['chef'],
        "is_favorite": True
    }

    recipe_files = [
        ("image", open("tests/uploads/upload-image.png", 'rb')),
        ("video", open("tests/uploads/upload-video.mp4", 'rb'))
    ]

    ingredients_data = []
    for name, quantity, metric in zip(post_data["ingredient_name[]"], post_data['ingredient_quantity[]'],
                                      post_data['ingredient_metric[]']):
        ingredients_data.append({"name": name, "quantity": quantity, "metric": metric})

    instructions_data = []
    for instruction in post_data['instructions[]']:
        instructions_data.append({"text": instruction})

    mock_create_update_recipe_full_info(method, status_code)
    generate_token = uuid.uuid4()

    match method:
        case HTTPMethod.PUT:
            api_request.update_recipe_main_info(recipe_pk, multipart_form_data=recipe_main_info_data, files=recipe_files, token=generate_token)
        case HTTPMethod.POST:
            api_request.post_new_recipe_main_info(multipart_form_data=recipe_main_info_data, files=recipe_files, token=generate_token)

    api_request.post_ingredients_for_recipe(recipe_pk, token=generate_token, data=ingredients_data)
    api_request.post_instructions_for_recipe(recipe_pk, token=generate_token, data=instructions_data)

    return  post_data


def mock_categories_and_get_json_response(recipe_response_type: models.RecipeResponseType):
    categories_response = [{"pk": 1, "name": "Breakfast"}, {"pk": 2, "name": "Lunch"}, {"pk": 3, "name": "Sunday"},
                           {"pk": 4, "name": "Pizza"}, {"pk": 5, "name": "Brunch"}]

    responses_register_mock(method=responses.GET, path=f"api/recipe/category",
                            json_data=categories_response,
                            status_code=200)

    api_request.get_categories()
    recipe_response = {}

    match recipe_response_type:
        case models.RecipeResponseType.HOME_PREVIEW_PAGINATE:

            recipe_response = {"count": 1, "next": None,
                               "previous": None,
                               "results": [{"pk": 46,
                                            "image": "http://localhost:8000/media/images/8ddef70f-dd9d-44b1-847f-834cdf97e7bd_d5122d74-1c5e-40d3-a505-f9d09383d1ba_delicio_X3L8djK.jpg",
                                            "name": "Creamy Mushroom Risotto", "chef": "Julia Child", "servings": 1,
                                            "total_time": 1.62,
                                            "difficulty": "Intermediate", "is_favorite": False}]}
        case models.RecipeResponseType.HOME_PREVIEW_BY_CATEGORY:

            recipe_response = [{"pk": 46,
                                "image": "http://localhost:8000/media/images/8ddef70f-dd9d-44b1-847f-834cdf97e7bd_d5122d74-1c5e-40d3-a505-f9d09383d1ba_delicio_X3L8djK.jpg",
                                "name": "Creamy Mushroom Risotto", "chef": "Julia Child", "servings": 1,
                                "total_time": 1.62,
                                "difficulty": "Intermediate", "is_favorite": False}]
        case models.RecipeResponseType.RECIPE_DETAILS:

            recipe_response = {
                "pk": 1,
                "image": "http://localhost:8000/media/images/6b732e73-73b9-40e4-b8c9-1d5c65361d0e_1667446a-2636-41d1-9e03-bd43f1873f79_top-vie_eSzouHS.jpg",
                "name": "Tuscan White Bean Soup",
                "servings": 5,
                "chef": "Thomas Keller",
                "video": "http://localhost:8000/media/videos/58457d14-3f2f-413a-82d4-4a67fbb6a6b8_7451c646-5600-4ab3-801d-c861a2585d00_4935156_Jj5bDqV.mp4",
                "description": "A savory and hearty chicken stew packed with tender vegetables, slow-cooked in a rich tomato-based broth, perfect for a cozy dinner.",
                "category": 4,
                "tag": None,
                "prep_time": 38,
                "cook_time": 13,
                "total_time": 0.85,
                "difficulty": "Intermediate",
                "is_favorite": False,
                "ingredients": [
                    {
                        "name": "chicken breast",
                        "quantity": "2",
                        "metric": "lbs"
                    },
                    {
                        "name": "all-purpose flour",
                        "quantity": "1.5",
                        "metric": "cups"
                    }
                ],
                "steps": [
                    {
                        "text": "Preheat the oven to 375°F."
                    },
                    {
                        "text": "Chop the carrots into small cubes."
                    }
                ]
            }

    return recipe_response, categories_response