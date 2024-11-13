from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from backend import settings
from .models import Recipe


def login_view(request):
    return render(request, 'recipes/login.html')

def forgot_password(request):
    return render(request, 'recipes/forgot_password.html')

def recipe_list(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')

    recipes = Recipe.objects.all()

    if category and category != 'all':
        recipes = recipes.filter(category=category)

    if search:
        recipes = recipes.filter(title__icontains=search)

    paginator = Paginator(recipes, 6)  # Show 6 recipes per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    categories = [choice[0] for choice in Recipe.CATEGORY_CHOICES]

    return render(request, 'recipes/recipe_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'search_query': search,
    })

def recipe_detail(request, recipe_id):
    recipe = Recipe.objects.get(pk=recipe_id)
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe
    })


def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        # Update recipe with form data
        recipe.title = request.POST.get('title')
        recipe.category = request.POST.get('category')
        recipe.difficulty = request.POST.get('difficulty')
        recipe.time = request.POST.get('time')
        recipe.servings = int(request.POST.get('servings'))
        recipe.description = request.POST.get('description')
        recipe.ingredients = request.POST.getlist('ingredients[]')
        recipe.instructions = request.POST.getlist('instructions[]')

        # Handle image
        if request.POST.get('clear_image') == 'true':
            recipe.image = None
        elif 'image' in request.FILES:
            recipe.image_upload = request.FILES['image']

        # Handle video
        if request.POST.get('clear_video') == 'true':
            recipe.video = None
        elif 'video' in request.FILES:
            recipe.video_upload = request.FILES['video']

        # TODO:// after save to API get the recipe object

        recipe.save()
        return redirect('recipes:recipe_detail', recipe_id=recipe.id)

    categories = [choice[0] for choice in Recipe.CATEGORY_CHOICES]
    difficulties = [choice[0] for choice in Recipe.DIFFICULTY_CHOICES]

    return render(request, 'recipes/edit_recipe.html', {
        'recipe': recipe,
        'categories': categories,
        'difficulties': difficulties,
    })
def saved_recipes(request):
    recipes = Recipe.objects.all()  # Fetch all saved recipes
    paginator = Paginator(recipes, 6)  # Show 4 recipes per page

    # Get the current page number from the request (default to 1)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'recipes/saved_recipes.html', {
        'page_obj': page_obj
    })
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

def toggle_favorite(request, recipe_id):
    # In a real app, this would toggle the favorite status for the current user
    return JsonResponse({'status': 'success'})

def new_recipe(request):
    if request.method == 'POST':
        # Handle form submission
        # In a real app, you would save the recipe to the database
        title = request.POST.get('title')
        category = request.POST.get('category')
        difficulty = request.POST.get('difficulty')
        time = request.POST.get('time')
        servings = request.POST.get('servings')
        description = request.POST.get('description')
        ingredients = request.POST.getlist('ingredients[]')
        instructions = request.POST.getlist('instructions[]')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        # Create new recipe
        recipe = Recipe.objects.create(
            title=title,
            category=category,
            difficulty=difficulty,
            time=time,
            servings=servings,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            chef='Current User',  # In a real app, this would be the logged-in user
            image=image.url if image else ''
        )

        return redirect('recipes:recipe_detail', recipe_id=recipe.id)

    categories = [choice[0] for choice in Recipe.CATEGORY_CHOICES]
    difficulties = [choice[0] for choice in Recipe.DIFFICULTY_CHOICES]
    
    return render(request, 'recipes/new_recipe.html', {
        'categories': categories,
        'difficulties': difficulties,
    })
    
# @login_required
def settings_view(request):
    context = {
        'service_url': settings.SERVICE_BASE_URL
    }
    return render(request, 'recipes/settings.html', context)

# @login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the error below.')
    return redirect('settings')

# @login_required
def update_service_url(request):
    if request.method == 'POST':
        url = request.POST.get('service_url')
        if url:
            # Update the service URL in your settings or database
            settings.SERVICE_BASE_URL = url
            messages.success(request, 'Service URL updated successfully!')
        else:
            messages.error(request, 'Please provide a valid URL.')
    return redirect('settings')

# @login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('login')
    return redirect('settings')
