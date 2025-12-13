from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth import decorators
from django.contrib.auth.models import User 
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator # generer un token par defaut
from django.utils.encoding import force_bytes, force_str  # forcer la conversion en bit
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode# encoder en base 64
import codecs

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from caisse.models import Payment
from comptes.models import Utilisateur
from .forms import CustomUserCreationForm, UserUpdateForm


def connexion(request):
    message = ""
    if request.method == 'POST':
        nom = request.POST.get('username')
        pwd = request.POST.get('password')

        utilisateur = authenticate(username=nom, password=pwd)
        if utilisateur is not None:
            login(request, utilisateur)
            return redirect('payment_index')
        else:
            message="identifications invalides" 
            return render(request, 'login.html', {"msg": message})
  
    return render(request, "login.html")

def deconnexion(request):
    logout(request)
    return redirect('acceuil')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        utilisateur = Utilisateur.objects.filter(email=email).first() 
        if utilisateur is not None : 
            print("user found")
            tk = default_token_generator.make_token(utilisateur)
            uid = urlsafe_base64_encode(force_bytes(utilisateur.id))
            domain_site =  request.META['HTTP_HOST']
            context = {
                "uidd": uid, 
                "tok": tk,
                "domain_site": f"http://{domain_site}"
            }
            html_text = render_to_string('email.html', context)   
            msg = EmailMessage(
                "Récupération de mot de passe",
                 html_text,
                "NISCG <abdoulayeattamouyoussouf@gmail.com>",
                [utilisateur.email])
            msg.content_subtype = "html"
            msg.send()
        else:  
            print("user not found")
            #abdallahbenyous515@gmail.com
    return render(request, "forgot_pwd.html")

def update_password(request, tk, uid):
    msg = ""
    try:
        user_id = urlsafe_base64_decode(uid)
        decode_uid = codecs.decode(user_id, 'utf-8')
        user = Utilisateur.objects.get(id=decode_uid)
    except:
        return HttpResponse("Invalid token")
    check_tk = default_token_generator.check_token(user, tk)
    print(check_tk)
    if not check_tk:
        return HttpResponse("Invalid token")
    if request.method == 'POST':
        pwd = request.POST.get('new_pwd')
        confirm = request.POST.get('confirm_pwd')
        if pwd == confirm:
            user.set_password(pwd)
            user.save()
            return redirect('acceuil')
        else:
            msg = "Les mots de passe ne correspondent pas"
            return render(request, "update_pwd.html", {"msg": msg})
    return render(request, "update_pwd.html")


@decorators.login_required
def info_compte(request):
    users = request.user
    nom = users.username
    email = users.email
    operation = Payment.objects.filter(utilisateur_id=users.id).count()

    context = {
        "users": users,
        "nom": nom,
        "email": email,
        "operation": operation
        }
    return render(request, 'compte.html', context)

@decorators.login_required
def list_user(request):
    users = Utilisateur.objects.filter(is_superuser = False)
    return render(request, 'list_user.html', {'users':users})

@decorators.login_required
def desactive_user(request, id):
    user = Utilisateur.objects.get(id=id)
    user.is_active = False
    user.save()
    return redirect('list_users')

@decorators.login_required
def active_user(request, id):
    user = Utilisateur.objects.get(id=id)
    user.is_active = True
    user.save()
    return redirect('list_users')

@decorators.login_required
def register(request):
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                if request.user.is_censeur:
                    user = form.save()
                    user.is_informaticien = True
                    user.save()
                    return redirect('acceuil')  # Redirige vers la page d'accuei
                elif request.user.is_admin:
                    user = form.save()
                    return redirect('acceuil')
                else : 
                    return redirect('error_page')
        else:
            form = CustomUserCreationForm()
        return render(request, 'create_user.html', {'form': form})

def error_page(request):
    return render(request, 'page_erreur.html')


@decorators.login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account_information')  # Redirigez vers la page de profil
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'editProfil.html', {'form': form})

@decorators.login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Maintient la session ouverte
            # Vous pouvez envoyer un email ici si nécessaire
            return redirect('account_information')  # Redirection après succès
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'change_pwd.html', {'form': form})