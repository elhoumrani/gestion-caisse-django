from django.db.models import Sum, Count, Q
from decimal import Decimal


from caisse.models import (
    Inscription,
    FraisInscription,
    Payement,
    Classe,
    Annee_Scolaire
)

class DashboardService:

    @staticmethod
    def get_dashboard_stats(annee_scolaire):
        """
        Retourne toutes les statistiques nécessaires
        pour le tableau de bord direction.
        """

        
        inscriptions = Inscription.objects.filter(
            annee_scolaire=annee_scolaire
        )

        total_eleves = inscriptions.count()
        total_classes = Classe.objects.filter(
            inscription__annee_scolaire=annee_scolaire
        ).distinct().count()

        frais = FraisInscription.objects.filter(
            inscription__annee_scolaire=annee_scolaire
        )

        total_attendu = frais.aggregate(
            total=Sum("montant_total")
        )["total"] or Decimal("0")

        total_impaye = frais.aggregate(
            total=Sum("montant_du")
        )["total"] or Decimal("0")

        total_encaisse = total_attendu - total_impaye

        taux_recouvrement = (
            (total_encaisse / total_attendu) * 100
            if total_attendu > 0 else 0
        )
        paiements = Payement.objects.filter(
            frais_inscription__inscription__annee_scolaire=annee_scolaire
        )

        stats_caissiers = (
            paiements
            .values("utilisateur__username")
            .annotate(
                total_encaisse=Sum("montant"),
                nb_paiements=Count("id"),
                nb_annules=Count("id", filter=Q(annule=True))
            )
            .order_by("-total_encaisse")
        )

        impayes_par_classe = (
            frais
            .values("inscription__classe__libele")
            .annotate(total_impaye=Sum("montant_du"))
            .order_by("-total_impaye")
        )

        impayes_par_type = (
            frais
            .values("type_frais__nom")
            .annotate(total_impaye=Sum("montant_du"))
            .order_by("-total_impaye")
        )

        return {
            "total_eleves": total_eleves,
            "total_attendu": total_attendu,
            "total_encaisse": total_encaisse,
            "total_impaye": total_impaye,
            "taux_recouvrement": round(taux_recouvrement, 2),

            "stats_caissiers": stats_caissiers,
            "impayes_par_classe": impayes_par_classe,
            "impayes_par_type": impayes_par_type,
        }





