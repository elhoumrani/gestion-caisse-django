from django.contrib import admin

# Register your models here.
from comptes.models import Utilisateur

admin.site.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)
    list_per_page = 20