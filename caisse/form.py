from caisse.models import *
from django import forms

class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = Annee_Scolaire
        fields = ['libelle', 'date_debut', 'date_fin']
        
        labels = {
            'libelle': 'Libellé',
        }

        widgets = {
            
            'date_debut': forms.DateInput(attrs={'type': 'date', 'format': 'yyyy-mm-dd'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'format': 'yyyy-mm-dd'}),

        }


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe

        fields = ['niveau', 'libele', 'cycle',]

        labels = {
            'niveau': 'Niveau',
            'libele': 'Libelé',
            'cycle': 'Cycle',
            }
        
        widgets = {
            "niveau": forms.TextInput(
                attrs={
                    'placeholder': 'Entrez le niveau ',
                    'class': 'form-control'}),
            
            "libele": forms.TextInput(
                attrs={
                    'placeholder': 'Entrez le libelé ',
                    'class': 'form-control'}),

            "cycle": forms.Select(
                attrs={
                    'placeholder': 'choisir le cycle ',
                    'class': 'form-control'}),

                    }



class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve

        fields = ['nom', 'prenom', 'date_naissance', 'sexe', 'localisation', 'parent_contact', 'email']

        labels ={
            'nom' : 'Nom',
            'prenom' : 'Prenom',
            'date_naissance' : 'Date de naissance',
            'sexe' : 'Sexe',
            'localisation' : 'Localisation',
            'parent_contact' : 'Contact Parent',
            'email' : 'Email',
            }
        
        widgets = {
            
             "date_naissance": forms.DateInput(
                attrs={
                    'placeholder': 'Entrez le matricule',
                    'class': 'form-control',
                    'type': 'date'}),
            "parent_contact": forms.TextInput(
                attrs={
                   
                    'class': 'form-control',  # Classe CSS pour le style
                    'pattern': '[+][0-9]*',  # Exemple de pattern pour valider le format
            }),      
                    }


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription

        fields = ['eleve', 'classe', 'regime', 'annee_scolaire', ]

        labels ={
            'eleve': 'Eleve',
            'classe' : 'Classe',
            'annee_scolaire' : 'Anne Scolaire',
            'regime': 'Regime',
            }
        
        widgets = {
            "matricule": forms.TextInput(
                attrs={
                    'placeholder': 'Entrez le matricule',
                    'class': 'form-control'}),   
            
            }
        
class TypeFraisForm(forms.ModelForm):
    class Meta:
        model = TypeFrais

        fields = ['nom', 'montant', 'ordre']

        labels = {
            'nom': 'Nom du frais',
            'montant': 'Montant (FCFA)',
            'ordre': 'Ordre d\'affichage',
            
        }

        widgets = {
            'montant': forms.NumberInput(attrs={'min': 0}),
        }

class FraisInscriptionForm(forms.ModelForm):
    class Meta:
        model = FraisInscription

        fields = ['inscription', 'type_frais', 'remise', 'motif_remise',]

        labels = {
            'inscription': 'Inscription',
            'type_frais': 'Type de frais',
            'remise': 'Remise (FCFA)',
            'motif_remise': 'Motif de remise',
            
        }

        widgets = {
            'montant_total': forms.NumberInput(attrs={'min': 0}),
            'remise': forms.NumberInput(attrs={'min': 0}),
            'montant_du': forms.NumberInput(attrs={'min': 0}),
        }

class FraisInscription_UpdateForm(forms.ModelForm):
    class Meta:
        model = FraisInscription
        fields = [
            "type_frais",
            "montant_total",
            "remise",
            "montant_du",
            "motif_remise"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs non modifiables côté UX
        self.fields["type_frais"].disabled = True
        self.fields["montant_total"].disabled = True
        self.fields["montant_du"].disabled = True

    def clean(self):
        cleaned = super().clean()

        remise = cleaned.get("remise") or Decimal("0")
        motif = cleaned.get("motif_remise")

        montant_total = self.instance.montant_total
        ancien_montant_du = self.instance.montant_du
        ancienne_remise = self.instance.remise or Decimal("0")

        # Si remise modifiée → motif obligatoire
        if self.instance.pk:
            nouvelle_remise = remise or Decimal("0")

            if nouvelle_remise != ancienne_remise and not motif:
                self.add_error(
                    "motif_remise",
                    "Le motif est obligatoire lorsqu'une remise est modifiée."
                )

        # Calcul du nouveau montant dû
        nouveau_montant_du = montant_total - remise

        if nouveau_montant_du < 0:
            raise forms.ValidationError(
                "La remise ne peut pas être supérieure au montant total."
            )

        # Mise à jour du montant dû dans les données nettoyées
        cleaned["montant_du"] = nouveau_montant_du

        # verification que le montant du ne peut pas être augmenté après encaissement
        if nouveau_montant_du > ancien_montant_du:
            raise forms.ValidationError(
                "Impossible d’augmenter le montant dû après encaissement."
            )

        return cleaned

class PaiementGlobalForm(forms.Form):
    inscription = forms.ModelChoiceField(
        queryset=Inscription.objects.all(),
        label="Inscription"
    )
    montant = forms.DecimalField(
        min_value=1,
        label="Montant payement (FCFA)" 
    )
 

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Payement
        fields = ['frais_inscription', 'montant']
        

        labels = {
            'frais_inscription': 'Frais inscription',
            'montant': 'Montant (FCFA)',
        }
        
        widgets = {
            'montant': forms.NumberInput(attrs={'min': 0}),
        }

    

class AnnulationPaiementForm(forms.Form):
    motif = forms.CharField(
        label="Motif de l’annulation",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Expliquez la raison de l'annulation"
        }),
        required=True
    )



        
        