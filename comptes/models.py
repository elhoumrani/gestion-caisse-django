from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Utilisateur(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_caissier = models.BooleanField(default=True)
    is_informaticien = models.BooleanField(default=False)
    is_censeur = models.BooleanField(default=False)
    is_comptable = models.BooleanField(default=False)
