# audit/services/audit_service.py

from caisse.models import AuditLog


class AuditService:
    @staticmethod
    def log(
        *,
        action,
        modele,
        objet_id,
        utilisateur=None,
        motif="",
        donnees_avant=None,
        donnees_apres=None
    ):
        """
        Enregistre une action dans le journal d’audit.

        Paramètres obligatoires :
        - action (CREATION, MODIFICATION, PAIEMENT, ANNULATION, REMISE)
        - modele (Inscription, Payement, FraisInscription, etc.)
        - objet_id (id de l'objet concerné)

        Paramètres optionnels :
        - utilisateur
        - motif
        - donnees_avant
        - donnees_apres
        """

        # règle métier : motif obligatoire pour ANNULATION et REMISE
        if action in ["ANNULATION", "REMISE"] and not motif:
            raise ValueError(
                "Un motif est obligatoire pour une annulation ou une remise."
            )

        AuditLog.objects.create(
            action=action,
            modele=modele,
            objet_id=objet_id,
            utilisateur=utilisateur,
            motif=motif,
            donnees_avant=donnees_avant,
            donnees_apres=donnees_apres,
        )
    
    
    @staticmethod
    def lister_audits(
        action=None,
        modele=None,
        utilisateur=None
    ):
        qs = AuditLog.objects.select_related("utilisateur").order_by("-date_action")

        if action:
            qs = qs.filter(action=action)

        if modele:
            qs = qs.filter(modele=modele)

        if utilisateur:
            qs = qs.filter(utilisateur_id=utilisateur)

        return qs