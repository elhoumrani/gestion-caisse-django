from django.contrib import admin
from django.urls import path
from comptes import views

urlpatterns = [
    path('', views.connexion, name="acceuil" ),
    path('deconnexion/', views.deconnexion, name="deconnexion"),
    path('forgot_password/', views.forgot_password, name="forgot_pwd"),
    path('update_password/<str:tk>/<str:uid>/', views.update_password, name="update"),
    path('list_users', views.list_user, name='list_users'),
    path('user/desactiver<int:id>', views.desactive_user, name='desactiver_user'),
    path('user/activer<int:id>', views.active_user, name='activer_user'),
    path('user/create', views.register, name="create_user"),
    path('comptes/', views.info_compte, name="account_information"),
    path('edit_profile/', views.edit_profile  , name="edit_profil"),
    path('update_pwd/', views.change_password, name="update_pwd"),
    path('page_error/', views.error_page, name='error_page'),
]