from datetime import datetime
from decimal import Decimal
import random
from django.db import transaction
from caisse.exceptions import ErreurMetier
from caisse.models import FraisInscription, Payement
from django.db.models import Sum, Q

from caisse.services.audit_log import AuditService
from comptes.utils.security import *


class PayementService:

    def recu():
        dates = datetime.now().strftime("%Y-%m-%d")
        prefix = "Flamy"
        nombre = random.randint(1000, 9999)
        num = f"{prefix}{nombre}"
        return num

    @transaction.atomic
    def effectuer_paiement_inscription(
        inscription,
        montant,
        numero_recu,
        utilisateur
    ):
        verifier_role(utilisateur, ["CAISSIER"])
        if montant <= 0:
            raise ErreurMetier("Le montant du paiement doit être supérieur à zéro.")

        montant_restant = Decimal(montant)

        frais_a_payer = FraisInscription.objects.filter(
            inscription=inscription,
            montant_du__gt=0
        ).select_related("type_frais").order_by("type_frais__ordre")

        if not frais_a_payer.exists():
            raise ErreurMetier("Tous les frais sont déjà soldés pour cette inscription.")

        paiements_crees = []

        for frais in frais_a_payer:
            if montant_restant <= 0:
                break

            montant_a_affecter = min(frais.montant_du, montant_restant)

            paiement = Payement.objects.create(
                frais_inscription=frais,
                montant=montant_a_affecter,
                utilisateur=utilisateur,
                numero_recu=numero_recu
            )

            frais.montant_du -= montant_a_affecter
            frais.save(update_fields=["montant_du"])

            montant_restant -= montant_a_affecter
            paiements_crees.append(paiement)

        return {
            "paiements": paiements_crees,
            "reste_non_affecte": montant_restant
        }
    
    @staticmethod
    def annuler_paiement(*, paiement, motif, utilisateur):
        verifier_role(utilisateur, ["CAISSIER", "COMPTABLE"])
        if not motif:
            raise ErreurMetier("Un motif est obligatoire pour annuler un paiement.")

        if paiement.annule:
            raise ErreurMetier("Ce paiement est déjà annulé.")

        ancien = {
            "annule": paiement.annule,
            "montant": paiement.montant
        }

        paiement.annule = True
        paiement.save(update_fields=["annule"])
        montant_du = paiement.frais_inscription.montant_du + paiement.montant
        paiement.frais_inscription.montant_du = montant_du
        paiement.frais_inscription.save(update_fields=["montant_du"])
        
        AuditService.log(
            action="ANNULATION",
            modele="Payement",
            objet_id=paiement.id,
            utilisateur=utilisateur,
            motif=motif,
            donnees_avant=ancien,
            donnees_apres={"annule": True}
        )
