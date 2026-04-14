from caisse.models import FraisInscription

def impayes_par_filtre(annee_scolaire=None, classe=None, type_frais=None):
    qs = FraisInscription.objects.filter(montant_du__gt=0)

    if annee_scolaire:
        qs = qs.filter(inscription__annee_scolaire=annee_scolaire)

    if classe:
        qs = qs.filter(inscription__classe=classe)

    if type_frais:
        qs = qs.filter(type_frais=type_frais)

    return qs.select_related(
        "inscription__eleve",
        "inscription__classe",
        "inscription__annee_scolaire",
        "type_frais"
    )
