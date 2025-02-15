from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=150, unique=True)
    token = models.CharField(max_length=40)

    def __str__(self):
        return self.username

DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]

LANGUAGES_CHOICES = [
    ('English', 'English'),
    ('Spanish', 'Español'),
    ('French', 'Français'),
    ('German', 'Deutsch'),
    ('Chinese', '中文'),
    ('Russian', 'Русский'),
    ('Italian', 'Italiano'),
    ('Japanese', '日本語'),
    ('Dutch', 'Nederlands'),
    ('Polish', 'Polski'),
    ('Greek', 'Ελληνικά'),
    ('Swedish', 'Svenska'),
    ('Czech', 'Čeština'),
    ('Bulgarian', 'Български'),
]


