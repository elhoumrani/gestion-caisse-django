

from caisse.models import Inscription
from caisse.exceptions import ErreurMetier
from caisse.services.frais_inscriptions_service import FraisInscriptionService

class InscriptionsService:

    @staticmethod
    def inscrire_eleve(eleve, classe, annee_scolaire, regime):

        # Verifier si l'année scolaire est active
        if  not annee_scolaire.statut == 'Active':
            raise ErreurMetier("L'année scolaire n'est pas active. Impossible d'inscrire l'élève.")

        # Verifier si l'élève est déjà inscrit dans la même classe pour la même année scolaire
        inscriptions = Inscription.objects.filter(
            eleve=eleve, 
            annee_scolaire=annee_scolaire)
        
        if inscriptions.exists():
            raise ErreurMetier("L'eleve est déjà inscrit dans cette classe pour l'année scolaire donnée.")
        
        # Créer une nouvelle inscription
        inscription = Inscription.objects.create(
            eleve=eleve,
            classe=classe,
            annee_scolaire=annee_scolaire,
            regime=regime
        )
        FraisInscriptionService.creer_frais(inscription)

        return inscription