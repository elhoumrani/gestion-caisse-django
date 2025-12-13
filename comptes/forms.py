from django import forms
from django.contrib.auth.forms import UserCreationForm

from comptes.models import Utilisateur

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Un email valide est requis.")

    class Meta:
        model = Utilisateur
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
# forms.py


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'email']