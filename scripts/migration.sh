#!/bin/bash

python manage.py makemigrations authentication
python manage.py makemigrations recipe
python manage.py makemigrations schedule
python manage.py makemigrations shopping
python manage.py makemigrations backupper
python manage.py migrate
python manage.py collectstatic --noinput


if [ "$1" == 'true' ]; then
    python manage.py seed_admin_user
    python manage.py seed_categories
fi