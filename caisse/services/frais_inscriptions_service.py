
from django.db import transaction
from caisse.exceptions import ErreurMetier
from caisse.models import FraisInscription, TypeFrais


class FraisInscriptionService:



    @transaction.atomic
    def creer_frais(inscription):
               
        # verifier si des frais d'inscription pour ce type de frais existent déjà pour cette inscription
        type_frais = TypeFrais.objects.filter(actif=True)

        if not type_frais.exists():
            raise ErreurMetier("Aucun type de frais actif n'est disponible. Veuillez en créer un avant de continuer.")
        creer_frais = []

        for t in type_frais:

            frais = FraisInscription.objects.filter(inscription=inscription, type_frais=t)
            if frais.exists():
                raise ErreurMetier("Des frais d'inscription pour ce type de frais existent déjà pour cette inscription.")
        
            # determiner le montant total, le montant dû et la remise
            montant_t = t.montant
            montant_du = montant_t - 0

        # verifier que le montant dû n'est pas négatif
            if montant_du < 0:
                raise ErreurMetier("Le montant dû ne peut pas être négatif.")
            
            # creer les frais d'inscription
            frais_inscription = FraisInscription.objects.create(
                inscription=inscription,
                type_frais=t,
                montant_total = montant_t,
                remise=0,
                montant_du=montant_du,
                motif_remise="")
            frais_inscription.recalculer_montant_du()
            creer_frais.append(frais_inscription)

        return creer_frais

        
      

        

   