from caisse.models import Annee_Scolaire

def annee_en_cours():
    return Annee_Scolaire.objects.filter(statut="Active").last()
