from datetime import date
from decimal import Decimal, ROUND_FLOOR
from django.db.models import Sum
from caisse.exceptions import ErreurMetier
from caisse.models import FraisInscription, Payement


class RetardService:

    @staticmethod
    def calculer_mois_exigibles(date_debut, date_reference, jour_limite):
        if date_reference < date_debut:
            return 0

        mois = (date_reference.year - date_debut.year) * 12 + \
            (date_reference.month - date_debut.month)

        if date_reference.day >= jour_limite:
            mois += 1

        return max(mois, 0)

    @staticmethod
    def calculer_retard_inscription(
        inscription,
        jour_limite=20,
        date_reference=None
    ):
        if date_reference is None:
            date_reference = date.today()

        # récupérer les frais de scolarité
        try:
            frais_scolarite = FraisInscription.objects.select_related("type_frais").get(
                inscription=inscription,
                type_frais__nom__iexact="scolarité"
            )
        except FraisInscription.DoesNotExist:
            raise ErreurMetier("Aucun frais de scolarité trouvé pour cette inscription.")

        # base de calcul : montant dû (après remise)
        montant_reference = frais_scolarite.montant_du + (
            Payement.objects.filter(
                frais_inscription=frais_scolarite,
                annule=False
            ).aggregate(total=Sum("montant"))["total"] or Decimal("0")
        )

        # nombre de mois prévus (à rendre paramétrable plus tard)
        nombre_mois_paiement = 8

        mensualite = (montant_reference / Decimal(nombre_mois_paiement)).quantize(
            Decimal("1."), rounding=ROUND_FLOOR
        )

        # mois exigibles
        date_debut = inscription.annee_scolaire.date_debut
        mois_exigibles = RetardService.calculer_mois_exigibles(
            date_debut=date_debut,
            date_reference=date_reference,
            jour_limite=jour_limite
        )

        # montant attendu
        montant_attendu = mensualite * mois_exigibles

        # total payé
        total_paye = Payement.objects.filter(
            frais_inscription=frais_scolarite,
            annule=False,
            date_paiement__lte=date_reference
        ).aggregate(total=Sum("montant"))["total"] or Decimal("0")

        # calcul du retard
        retard_montant = montant_attendu - total_paye
        retard_montant = max(retard_montant, Decimal("0"))

        # calcul du retard en mois
        mois_couverts = (total_paye / mensualite).quantize(
            Decimal("1."), rounding=ROUND_FLOOR
        )

        mois_retard = max(mois_exigibles - int(mois_couverts), 0)

        # determiner le statut selon le nombr de mosi de retard
        if mois_retard == 0:
            statut = "A JOUR"
        else:
            statut = f"RETARD {mois_retard} MOIS"

        return {
            "inscription": inscription,
            "mensualite": mensualite,
            "mois_exigibles": mois_exigibles,
            "mois_couverts": int(mois_couverts),
            "mois_retard": mois_retard,
            "montant_attendu": montant_attendu,
            "montant_paye": total_paye,
            "montant_retard": retard_montant,
            "statut": statut
        }

