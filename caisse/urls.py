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


    #payement
    path('Payement/index', views.index_payement, name="payment_index" ),
    path('Payement/create', views.create_payement, name='payment_create'),
    path('regler_payment/<int:id>', views.regler_payment, name='regler_paye'),

    path('Payement/generate_pdf/<int:id>', views.generate_pdf, name="pdf_generate"),
    path('Payement/edit/<int:id>', views.edit_paye, name='payment_edit'),
    path('Payement/delete/<int:id>', views.delete_payement, name='payment_delete'),
    path('Payement/confirm', views.confim_payement, name='payment_confirm'),
    path('Payement/recalcitrant/<int:id>', views.index_recalcitrants, name='recalcitrant'),
    path('payement/imprimer/<int:id>', views.imprimer_liste, name ='imprimer'),
    path('export-apprenants/<int:id>/', views.export_excel, name='export_apprenants'),
    #apprenant
    path('eleve/index', views.index_eleves, name='eleve_index'),
    path('eleve/create', views.create_students, name="eleve_create"),
    path('eleve/edit/<int:id>', views.edit_students, name='eleve_edit'),
    path('eleve/delete/<int:id>', views.delete_students, name='eleve_delete'),
    
    #formation
    path('formation/index', views.index_formations, name='formation_index'),
    path('formation/create', views.create_formation, name="formation_create"),
    path('formation/edit/<int:id>', views.edit_formation, name='formation_adit'),
    path('formation/delete/<int:id>', views.delete_formation, name='formation_delete'),
  

    #inscription
    path('inscription/create', views.create_inscription, name='inscription_create'),
    path('inscription/index', views.index_inscription, name='inscription_index'),
    path('inscription/edit/<int:id>', views.edit_inscription, name='inscription_edit'),
    path('inscription/cdelete/<int:id>', views.delete_inscription, name='inscription_delete'),

    #dashboard
    path('dashboard/', views.index_dashboard, name='dash_board'),
    
       
]