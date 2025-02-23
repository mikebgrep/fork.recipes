import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from fork_recipes.ws import api_request


@login_required
def schedule_list(request):
    date = str(datetime.datetime.now().date())

    if request.POST:
        date = request.POST.get('selected_date')
        if not date:
            date = str(datetime.datetime.now().date())

    response = api_request.request_get_schedule_of_a_day(date)

    breakfast = [x for x in response if x.timing == 'Breakfast']
    lunch = [x for x in response if x.timing == 'Lunch']
    dinner = [x for x in response if x.timing == 'Dinner']
    side = [x for x in response if x.timing == 'Side']

    breakfast = breakfast[0] if len(breakfast) > 0 else None
    lunch = lunch[0] if len(lunch) > 0 else None
    dinner = dinner[0] if len(dinner) > 0 else None
    side = side[0] if len(side) > 0 else None

    is_plan_empty = (breakfast, lunch, dinner, side) == (None, None, None, None)

    return render(request, 'schedule.html',
                  context={"breakfast": breakfast, "lunch": lunch, "dinner": dinner, "side": side, "current_selected_date": date, "is_plan_empty": is_plan_empty})


@login_required
def create_schedule_meal_type(request):
    if request.POST:
        meal_type = request.POST.get('meal_type')
        date = request.POST.get('date')
        recipe_id = request.POST.get('recipe_id')
        token = request.session.get("auth_token")

        response = api_request.request_post_schedule(date, recipe_id, meal_type, token)
        if response:
            messages.success(request, f'Recipe was added to schedule for date {date}')
        else:
            messages.error(request, f'There was an error processing the request.Please try again.')

        return redirect("recipes:recipe_detail", recipe_pk=recipe_id)
