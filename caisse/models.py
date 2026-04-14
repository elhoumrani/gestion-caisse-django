from datetime import date
from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from GestionCaisse import settings
from phonenumber_field.modelfields import PhoneNumberField

from comptes.models import Utilisateur


STATUTS_INSCRIPTION =  [
    ('non_inscrit', 'Non Inscrit'),
    ('inscrit', 'Inscrit'),
    ('termine', 'Terminé'),
    ]

STATUS_REGIME = [
    ('normal', 'Normal' ),
    ('exonoré', 'Exoneré'),
    ]

CYCLE = [
        ('Premier','1er Cycle'),
        ('Second', '2end Cycle')]

STATUT_YEAR = [
        ('active', 'Active'),
        ('cloturee', 'Cloturée'),
    ]
SEXE_CHOICES = [
        ('masculin', 'M'),
        ('feminin', 'F'),
    ]

class Annee_Scolaire(models.Model):
    date_debut = models.DateField()
    date_fin = models.DateField()
    libelle = models.CharField(max_length=12)  # ex: 2023-2024
    statut = models.CharField(max_length=8, choices=STATUT_YEAR, default=STATUT_YEAR[0][1])

    def __str__(self):
        return self.libelle

class Eleve(models.Model):
    matricule = models.CharField(max_length=20)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=12, choices=SEXE_CHOICES)
    parent_contact = PhoneNumberField()
    email = models.EmailField()
    localisation = models.CharField(max_length=20)


    def __str__(self):
        return f" {self.nom} {self.prenom} , {self.matricule}  "

class Classe(models.Model):
    niveau = models.CharField(max_length=100)  # ex: "Second", "Terminale"
    libele = models.CharField(max_length=20) # ex: "Second A, Second B"
    cycle = models.CharField(max_length=30, choices=CYCLE)

    def __str__(self):
        return self.libele


class Inscription(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(Annee_Scolaire, on_delete=models.CASCADE)
    
    regime = models.CharField(
        max_length=50,  
        choices=STATUS_REGIME, 
        default=STATUS_REGIME[1][1])
    
    
    statut = models.CharField(
        max_length=125, 
        choices=STATUTS_INSCRIPTION, 
        default=STATUTS_INSCRIPTION[0][1])
    
    date_inscription = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('eleve', 'classe', 'annee_scolaire')

    def __str__(self):
        return f"{self.eleve} - {self.classe} - {self.annee_scolaire} "


class TypeFrais(models.Model):
    nom = models.CharField(max_length=50)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    actif = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField()

    def __str__(self):
        return self.nom

class FraisInscription(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE)
    type_frais = models.ForeignKey(TypeFrais, on_delete=models.CASCADE)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_du = models.DecimalField(max_digits=10, decimal_places=2)
    motif_remise = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('inscription', 'type_frais')
    
    def recalculer_montant_du(self):
        montant_du = self.montant_total - self.remise
        if montant_du < 0:
            raise ValueError("La remise ne peut pas dépasser le montant total.")
        self.montant_du = montant_du

    def __str__(self):
        return f"{self.inscription}"


class Payement(models.Model):
    frais_inscription = models.ForeignKey(FraisInscription, on_delete=models.CASCADE)
    montant = models.IntegerField()
    date_paiement = models.DateField(auto_now_add=True)
    numero_recu = models.CharField(max_length=12)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    annule = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.montant} - {self.date_paiement} ({self.frais_inscription})"

class Depense(models.Model):
    montant = models.IntegerField()
    motif = models.CharField(max_length=30)
    date_depense = models.DateField(auto_now_add=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.motif} - {self.montant} - {self.date_depense}"

class AuditLog(models.Model): 
    ACTIONS = ( ("CREATION", "Création"), ("MODIFICATION", "Modification"), ("ANNULATION", "Annulation"), ("REMlSE", "Remise"), ("PAIEMENT", "Paiement"), ) 
    action = models.CharField(max_length=30, choices=ACTIONS) 
    modele = models.CharField(max_length=100) 
    objet_id = models.PositiveIntegerField()

    utilisateur = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True
)
    date_action = models.DateTimeField(auto_now_add=True) 
    motif = models.TextField(blank=True) 
    donnees_avant = models.JSONField(null=True, blank=True) 
    donnees_apres = models.JSONField(null=True, blank=True) 
    def __str__(self): 
        return f"{self.action} - {self.modele} - {self.objet_id}" 