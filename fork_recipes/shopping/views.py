from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from fork_recipes.ws import api_request


@login_required
def shopping_list(request):
    token = request.session.get("auth_token")
    shopping_lists = api_request.request_get_list_shopping_lists(token)

    return render(request, "shopping.html", context={"shopping_lists": shopping_lists})


@login_required
def get_shopping_list(request, list_pk):
    token = request.session.get("auth_token")
    single_shopping_list = api_request.request_get_shopping_list(list_pk, token)
    recipes = None
    try:
        recipes = [api_request.get_recipe_by_pk(x) for x in single_shopping_list.recipes]
    except AttributeError as ex:
        print(ex)

    return render(request, "shopping_list.html", context={"shopping_list": single_shopping_list, "recipes": recipes})


@login_required
def delete_list(request, list_pk):
    token = request.session.get("auth_token")
    response = api_request.request_delete_shopping_list(list_pk, token)
    if response:
        return redirect("shopping:shopping_list")

    messages.error(request, "There an error.Please try again later or contact support")
    return redirect("shopping:shopping_list")


@login_required
def create_list(request):
    if request.method == "POST":
        name = request.POST.get('name')
        token = request.session.get("auth_token")
        created_shopping_list = api_request.request_create_shopping_list(name, token)

        if created_shopping_list:
            return redirect("shopping:shopping_list")

        messages.error(request, "There an error.Please try again later or contact support")

    return redirect("shopping:shopping_list")


@login_required
def update_shopping_item(request, item_pk):
    if request.method == "POST":
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        metric = request.POST.get('metric')
        times = request.POST.get('times')
        list_pk = request.POST.get('list_pk')
        token = request.session.get("auth_token")

        data = {
            "name": name,
            "quantity": quantity,
            "metric": metric,
            "times": times if times else 1
        }

        item = api_request.request_update_shopping_list_item(item_pk, data, token)
        if item:
            return redirect("shopping:single_shopping_list", list_pk=list_pk)

        messages.error(request, "There an error.Please try again later or contact support")
        return redirect("shopping:single_shopping_list", list_pk=list_pk)


@login_required
def add_shopping_list_item(request, list_pk):
    if request.method == "POST":
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        metric = request.POST.get('metric')
        token = request.session.get("auth_token")

        data = {
            "name": name,
            "quantity": quantity,
            "metric": metric,
        }
        ingredient = api_request.request_add_ingredient_to_shopping_list(list_pk, data, token)

        if ingredient:
            return redirect("shopping:single_shopping_list", list_pk=list_pk)

        messages.error(request, "There an error.Please try again later or contact support")
        return redirect("shopping:single_shopping_list", list_pk=list_pk)


@login_required
def delete_shopping_list_item(request, list_pk, item_pk):
    token = request.session.get("auth_token")
    response = api_request.request_delete_ingredient_from_shopping_list(item_pk, token)
    if response:
        return redirect("shopping:single_shopping_list", list_pk=list_pk)

    messages.error(request, "There an error.Please try again later or contact support")
    return redirect("shopping:single_shopping_list", list_pk=list_pk)

@login_required
def complete_shopping_list(request, list_pk):
    token = request.session.get("auth_token")
    is_completed = api_request.request_complete_shopping_list(list_pk, token)

    if is_completed:
        return redirect("shopping:single_shopping_list", list_pk=list_pk)

    messages.error(request, "There an error.Please try again later or contact support")
    return redirect("shopping:single_shopping_list", list_pk=list_pk)


@login_required
def complete_single_shopping_list_item(request, list_pk, item_pk):
    token = request.session.get("auth_token")
    is_completed = api_request.request_complete_single_ingredient(item_pk, token)
    if is_completed:
        return JsonResponse({
            "status": "success",
            "message": "Item marked as complete!"
        })

    return JsonResponse({
                "status": "Bad request",
                "message": "Item is not marked as complete!"
            })
