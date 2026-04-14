from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

ROLES = (
        ("PROVISEUR", "Proviseur"),
        ("COMPTABLE", "Comptable"),
        ("CAISSIER", "Caissier"),
        ("SECRETAIRE", "Secrétaire"),
    )


class Utilisateur(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLES, default="SECRETAIRE")
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
