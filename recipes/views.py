from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from requests import session

from backend import settings
from ws import api_request
from .models import Recipe, User
from .utils import email_util


def login_view(request):
    if request.user.is_authenticated:
        return render(request, "recipes/recipe_list.html")

    context = {}
    if request.POST:
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Set the session cookie to 30 days
        if request.POST.get("remember-me"):
            settings.SESSION_COOKIE_AGE = 60 * 60 * 24 * 30

        user = api_request.get_user_token(email, password)

        if user:
            request.session['auth_token'] = user.token
            request.session['email'] = user.email
            login(request, user)
            return redirect("/")
        else:
            context = {
                "message": "Wrong email or password!"
            }

    return render(request, 'recipes/login.html', context=context)


def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.POST:
        email = request.POST.get("email")
        host = request.get_host()
        data = {
            "email": email
        }
        result = api_request.request_forgot_password_token(data=data)
        if result:
            email_util.send_reset_password_link(host, email, result.token)
            return render(request, 'recipes/forgot_password_send.html')

        messages.error(request, "Somethings when wrong. Please try again later or contact administrator!")
    return render(request, 'recipes/forgot_password.html')


def change_password_after_reset(request):
    if request.GET:
        request_token = request.GET.get("token")
        request.session['request_token'] = request_token

    if request.POST:
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            data = {
                "password": new_password,
                "confirm_password": confirm_password
            }
            result = api_request.request_change_user_password_on_reset(request.session.get('request_token'), data=data)
            if result:
                messages.success(request, "Password was successfully reset.")
                return redirect('recipes:login')
        else:
            messages.error(request, "Both password does not match!")

        messages.error(request, "Something when wrong.Contact administrator.")
    return render(request, 'recipes/reset_password.html')


def log_out_view(request):
    logout(request)
    return redirect('recipes:login')


@login_required
def recipe_list(request):
    current_page_number = request.GET.get('page', 1)
    categories = api_request.get_categories()

    category_pk = request.GET.get('category', '')
    search = request.GET.get('search', '')

    # TODO:// Refactoring must be done
    total_recipes = None
    if category_pk and len(category_pk) > 0:
        total_recipes = api_request.get_recipes_by_category(category_pk)
    else:
        if search:
            count, next_page, prev_page, recipes = api_request.get_recipe_home_preview(search_query=search,
                                                                                       page_number=current_page_number)
        else:
            count, next_page, prev_page, recipes = api_request.get_recipe_home_preview(page_number=current_page_number)

        total_recipes = [None] * count

        # Get start and end index
        start_index = (int(current_page_number) - 1) * 15
        end_index = start_index + 15

        total_recipes[start_index:end_index] = recipes

    paginator = Paginator(total_recipes, 15)
    page_obj = paginator.get_page(current_page_number)

    return render(request, 'recipes/recipe_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_pk,
        'search_query': search,
    })


@login_required
def recipe_detail(request, recipe_pk):
    recipe = api_request.get_recipe_by_pk(recipe_pk)
    categories = api_request.get_categories()
    category = [x for x in categories if recipe.category == x.pk][0]
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'category': category
    })


@login_required
def edit_recipe(request, recipe_pk):
    recipe = api_request.get_recipe_by_pk(recipe_pk)
    categories = api_request.get_categories()
    difficulties = [choice[0] for choice in Recipe.DIFFICULTY_CHOICES]
    context = {
        'recipe': recipe,
        'categories': categories,
        'difficulties': difficulties,
    }

    if request.method == 'POST':
        name = request.POST.get('name')
        category_pk = request.POST.get('category')
        new_category = request.POST.get('new_category')
        difficulty = request.POST.get('difficulty')
        prep_time = request.POST.get('prep_time')
        cook_time = request.POST.get('cook_time')
        servings = request.POST.get('servings')
        description = request.POST.get('description')
        chef = request.POST.get('chef')

        ingredient_names = request.POST.getlist('ingredient_name[]')
        ingredient_quantities = request.POST.getlist('ingredient_quantity[]')
        ingredient_metrics = request.POST.getlist('ingredient_metric[]')
        instructions = request.POST.getlist('instructions[]')

        image = request.FILES.get('image')
        video = request.FILES.get('video')

        token = request.session.get("auth_token")

        category = None
        if new_category:
            new_category_data = {
                "name": new_category
            }
            category = api_request.post_category(token, new_category_data)

        recipe_main_info_data = {
            "name": name,
            "category": category.pk if category else int(category_pk),
            "difficulty": difficulty,
            "prep_time": int(prep_time),
            "cook_time": int(cook_time),
            "servings": int(servings),
            "description": description,
            "chef": chef
        }

        ingredients_data = list()
        instructions_data = list()
        recipe_files = []

        for name, quantity, metric in zip(ingredient_names, ingredient_quantities, ingredient_metrics):
            ingredients_data.append({"name": name, "quantity": quantity, "metric": metric})

        for instruction in instructions:
            instructions_data.append({"text": instruction})

        # Handle image
        if 'image' in request.FILES:
            recipe_files = [
                ("image", image)
            ]

        # Handle video
        if request.POST.get('clear_video') == 'true':
            recipe_main_info_data['clear_video'] = True
        elif 'video' in request.FILES:
            recipe_files.append(("video", video))
        token = request.session.get("auth_token")

        response_recipe = api_request.update_recipe_main_info(recipe.pk, multipart_form_data=recipe_main_info_data,
                                                              files=recipe_files, token=token)

        if response_recipe is not None:
            api_request.post_ingredients_for_recipe(response_recipe.pk, token=token, data=ingredients_data)
            api_request.post_instructions_for_recipe(response_recipe.pk, token=token, data=instructions_data)

            return redirect('recipes:recipe_detail', recipe_pk=response_recipe.pk)

        context['message'] = "Something went wrong.Try again later"

    return render(request, 'recipes/edit_recipe.html', context)


@login_required
def saved_recipes(request):
    current_page_number = request.GET.get('page', 1)
    count, next_page, prev_page, recipes = api_request.get_favorite_recipes(current_page_number)
    total_recipes = [None] * count

    start_index = (int(current_page_number) - 1) * 15
    end_index = start_index + 15
    total_recipes[start_index:end_index] = recipes

    paginator = Paginator(total_recipes, 15)
    page_obj = paginator.get_page(current_page_number)

    return render(request, 'recipes/saved_recipes.html', {
        'page_obj': page_obj
    })


@login_required
def profile_view(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        # Handle avatar upload
        # In a real app, you would save the file and update the user's avatar
        pass

    # In a real app, this would get the current user's data
    user_data = {
        'username': 'johndoe',
        'email': 'john@example.com',
        'avatar': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256 <boltAction type="file" filePath="recipes/views.py">&q=80'
    }
    return render(request, 'recipes/profile.html', {'user': user_data})


def toggle_favorite(request, recipe_pk):
    status_code = api_request.patch_favorite_recipe(recipe_pk, request.session.get("auth_token"))
    return JsonResponse({'status': 'success' if status_code == 201 else "failure"})


@login_required
def new_recipe(request):
    categories = api_request.get_categories()
    difficulties = [choice[0] for choice in Recipe.DIFFICULTY_CHOICES]

    context = {
        'categories': categories,
        'difficulties': difficulties,
    }

    if request.method == 'POST':
        name = request.POST.get('name')
        category_pk = request.POST.get('category')
        new_category = request.POST.get('new_category')
        difficulty = request.POST.get('difficulty')
        prep_time = request.POST.get('prep_time')
        cook_time = request.POST.get('cook_time')
        servings = request.POST.get('servings')
        description = request.POST.get('description')
        chef = request.POST.get('chef')
        ingredient_names = request.POST.getlist('ingredient_name[]')
        ingredient_quantities = request.POST.getlist('ingredient_quantity[]')
        ingredient_metrics = request.POST.getlist('ingredient_metric[]')
        instructions = request.POST.getlist('instructions[]')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        token = request.session.get("auth_token")

        category = None
        if new_category:
            new_category_data = {
                "name": new_category
            }
            category = api_request.post_category(token, new_category_data)

        recipe_main_info_data = {
            "name": name,
            "category": category.pk if category else int(category_pk),
            "difficulty": difficulty,
            "prep_time": int(prep_time),
            "cook_time": int(cook_time),
            "servings": int(servings),
            "description": description,
            "chef": chef
        }

        recipe_files = [
            ("image", image)
        ]

        if video:
            recipe_files.append(("video", video))

        ingredients_data = list()
        instructions_data = list()

        for name, quantity, metric in zip(ingredient_names, ingredient_quantities, ingredient_metrics):
            ingredients_data.append({"name": name, "quantity": quantity, "metric": metric})

        for instruction in instructions:
            instructions_data.append({"text": instruction})

        recipe = api_request.post_new_recipe_main_info(multipart_form_data=recipe_main_info_data, token=token,
                                                       files=recipe_files)

        if recipe is not None:
            api_request.post_ingredients_for_recipe(recipe.pk, token=token, data=ingredients_data)
            api_request.post_instructions_for_recipe(recipe.pk, token=token, data=instructions_data)

            return redirect('recipes:recipe_detail', recipe_pk=recipe.pk)
        context['message'] = "Something went wrong.Try again later"

    return render(request, 'recipes/new_recipe.html', context)


@login_required
def settings_view(request):
    context = {
        'service_url': settings.SERVICE_BASE_URL,
        "smtp_host": settings.EMAIL_HOST_TEMP,
        "smtp_port": settings.EMAIL_PORT_TEMP,
        "smtp_username": settings.EMAIL_HOST_USER_TEMP,
        "smtp_password": settings.EMAIL_HOST_PASSWORD_TEMP
    }
    return render(request, 'recipes/settings.html', context)


@login_required
def change_password(request):
    context = {}
    if request.method == 'POST':
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if new_password == confirm_password:
            data = {
                "old_password": current_password,
                "new_password": new_password
            }
            token = request.session.get("auth_token")

            result = api_request.change_logged_user_password(data=data, token=token)
            if result is True:
                messages.success(request, 'Your password was successfully updated!')
                return redirect('recipes:settings')
            else:
                context = {
                    "error": "There problem with your new password.Please choice minimum 8 char long password and not to common."}
        else:
            context = {
                "error": "Your new password does not match confirm password!"}

        messages.error(request, 'Please correct the error below.')
    return render(request, 'recipes/settings.html', context=context)


@login_required
def update_service_url(request):
    if request.method == 'POST':
        url = request.POST.get('service_url')
        if url:
            settings.SERVICE_BASE_URL = url
            messages.success(request, 'Service URL updated successfully!')
        else:
            messages.error(request, 'Please provide a valid URL.')
    return redirect('recipes:settings')


@login_required
def update_smtp_settings(request):
    if request.method == 'POST':
        smtp_host = request.POST.get('smtp_host')
        smtp_port = request.POST.get('smtp_port')
        smtp_username = request.POST.get('smtp_username')
        smtp_password = request.POST.get('smtp_password')

        settings.EMAIL_HOST_TEMP = smtp_host
        settings.EMAIL_HOST_USER_TEMP = smtp_username
        settings.EMAIL_HOST_PASSWORD_TEMP = smtp_password
        settings.EMAIL_PORT_TEMP = smtp_port

        messages.success(request, 'Your smtp settings was successfully updated!')

        user_email = request.session.get('email')
        email_util.send_test_email_to_user_after_change_smtp(user_email)

    return redirect('recipes:settings')


@login_required
def delete_account(request):
    if request.method == 'POST':
        token = request.session.get('auth_token')
        email = request.session.get('email')

        result = api_request.delete_user_account(token)
        if result:
            messages.success(request, 'Your account has been successfully deleted.')
            User.objects.get(email=email).delete()
            return redirect('recipes:login')

        messages.error(request, "Something went wrong.Please try again later!")

    return redirect('recipes:settings')
