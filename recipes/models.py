from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator




class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    token = models.CharField(max_length=40)

    def __str__(self):
        return self.username




class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]
    
    CATEGORY_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Desserts', 'Desserts'),
        ('Vegetarian', 'Vegetarian'),
    ]

    title = models.CharField(max_length=200)
    image = models.URLField()
    video = models.URLField(blank=True, null=True)
    time = models.CharField(max_length=50)
    servings = models.IntegerField(validators=[MinValueValidator(1)])
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    chef = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    ingredients = models.JSONField()
    instructions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_upload = models.ImageField(
        upload_to='recipe_images/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        blank=True,
        null=True,
        default=None

    )
    video_upload = models.FileField(
        upload_to='recipe_videos/',
        validators=[FileExtensionValidator(['mp4', 'webm', 'mov'])],
        blank=True,
        null=True,
        default=None
    )
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


