from django.contrib import admin
from django.urls import path
from caisse import views

urlpatterns = [
    
    #annee_scolaire
    path('Annee/index', views.index_year, name='index_year'),
    path('Annee/create', views.create_year, name='create_year'),
    path('Annee/datails/<int:id>', views.details_year, name='details_year'),
    path('Annee/edit/<int:id>', views.edit_year, name='edit_year'),
    path('Annee/delete/<int:id>', views.delete_year, name='delete_year'),

    #inscription
    path('inscription/create', views.create_inscription, name='inscription_create'),
    path('inscription/index', views.index_inscription, name='inscription_index'),
    path('inscription/edit/<int:id>', views.edit_inscription, name='inscription_edit'),
    path('inscription/cdelete/<int:id>', views.delete_inscription, name='inscription_delete'),

    #details de situation d'un eleve (details inscription)
    path('inscription/details/<int:inscription_id>', views.details_inscription_eleve, name='details_inscription_eleve'),

    #apprenant
    path('eleve/index', views.index_eleves, name='eleve_index'),
    path('eleve/create', views.create_eleve, name="eleve_create"),
    path('eleve/edit/<int:id>', views.edit_students, name='eleve_edit'),
    path('eleve/delete/<int:id>', views.delete_students, name='eleve_delete'),
    
    #formation
    path('formation/index', views.index_formations, name='formation_index'),
    path('formation/create', views.create_classe, name="formation_create"),
    path('formation/edit/<int:id>', views.edit_classe, name='formation_adit'),
    path('formation/delete/<int:id>', views.delete_classe, name='formation_delete'),

    #Type de frais
    path('type_frais/index', views.index_type_frais, name='type_frais_index'),
    path('type_frais/create', views.create_type_frais, name='type_frais_create'),
    path('type_frais/edit/<int:id>', views.edit_type_frais, name='type_frais_edit'),
    
    #Frais inscription
    path('frais_inscription/index', views.index_frais_inscription, name='frais_inscription_index'),
    path('frais_inscription/create', views.create_frais_inscription, name='frais_inscription_create'),
    path('frais_inscription/edit/<int:id>', views.edit_frais_inscription, name='frais_inscription_edit'),
    path('frais/impayes', views.liste_impayes, name='impayes_list'),

    #payement
    path('Payement/index', views.index_payement, name="payment_index" ),
    path('Payement/create', views.create_payement, name='payment_create'),
    path('Payement/retard', views.eleves_en_retard, name='retard_payement'),
    path('Payement/annuler/<int:paiement_id>', views.annuler_payement, name='payment_cancel'),
    
    # generer le recu de payement
    path(
        "paiements/<int:paiement_id>/recu/",
        views.recu_paiement,
        name="recu_paiement")
,

    # journal de traçablité
    path('journal-tracablite/', views.liste_audit, name="journal_tracablite"),
    #dashboard
    path('dashboard/', views.dashboard_direction, name='dash_board'),
    
       
]