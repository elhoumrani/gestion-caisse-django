from django.db.models import Sum
from decimal import Decimal
from caisse.models import FraisInscription, Payement

def situation_financiere_inscription(inscription):
    frais = FraisInscription.objects.filter(inscription=inscription)

    total_frais = frais.aggregate(
        total=Sum("montant_total")
    )["total"] or Decimal(0)

    total_restant = frais.aggregate(
        total=Sum("montant_du")
    )["total"] or Decimal(0)

    total_remise = frais.aggregate(
        total=Sum("remise")
    )["total"] or Decimal(0)

    details = []

    for f in frais.select_related("type_frais"):
        paye = Payement.objects.filter(
            frais_inscription=f,
            annule=False
        ).aggregate(total=Sum("montant"))["total"] or Decimal(0)

        details.append({
            "type_frais": f.type_frais.nom,
            "montant_total": f.montant_total,
            "montant_paye": paye,
            "montant_restant": f.montant_du,
            "statut": (
                "soldé" if f.montant_du == 0
                else "partiel" if paye > 0
                else "impayé"
            )
        })

    print(total_remise)
    total_frais -= total_remise
    total_paye = total_frais - total_restant

    return {
        "total_frais": total_frais,
        "total_paye": total_paye,
        "total_restant": total_restant,
        "total_remise": total_remise,
        "details": details
    }
