# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libpcre3-dev \
    && rm -rf /var/lib/apt/lists/*

# Raspberry Pi packages 📦
# RUN apt update && apt install -y \
#    libjpeg-dev \
#    zlib1g-dev \
#    libpng-dev \
#    libfreetype6-dev \
#    liblcms2-dev \
#    libopenjp2-7-dev \
#    libtiff5-dev \
#    libwebp-dev \
#    tcl8.6-dev \
#    tk8.6-dev \
#    python3-tk \
#    libharfbuzz-dev \
#    libfribidi-dev

# Set the working directory
WORKDIR /fork_recipes

# Copy the project
COPY /fork_recipes /fork_recipes

COPY ./requirements.txt /fork_recipes/requirements.txt

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# Collect static files
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations recipes
RUN python manage.py migrate

# Give permissions around and add www-data to staff
RUN chmod 660 /fork_recipes/backend/sql/db.sqlite3
RUN usermod -g staff www-data