def verifier_role(utilisateur, roles_autorises):
    if not utilisateur:
        raise Exception("Utilisateur non authentifié")

    if utilisateur.role not in roles_autorises:
        raise Exception("Accès refusé")