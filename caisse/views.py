from decimal import Decimal
from pyexpat.errors import messages
import random
from urllib import request
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from datetime import datetime
from django.contrib.auth.decorators import login_required
import uuid
from caisse import services
from caisse.form import *
from django.template.loader import render_to_string
from caisse.services.annee_service import annee_en_cours
from caisse.services.audit_log import AuditService
from caisse.services.dashboard_service import DashboardService
from caisse.services.details_inscription_service import situation_financiere_inscription
from caisse.services.frais_inscriptions_service import FraisInscriptionService
from caisse.services.impayes_service import impayes_par_filtre
from caisse.services.inscriptions_service import InscriptionsService
from caisse.services.payement_service import PayementService
from caisse.services.retard_service import RetardService
import pdfkit
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.db.models import Sum, Q
import logging
import datetime
from dateutil.relativedelta import relativedelta 
from django.db.models  import Max 
from openpyxl import Workbook
from django.core.paginator import Paginator

from comptes.utils.decorators import role_autorise

def generer_matricule(): #methode pour generer un idetifiant unique pour chaque eleve
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d%H%M%S")
    prefix = "FLamy"
    atteinte = 0
    while atteinte < 100 :
        id = str(uuid.uuid4().int)[:4]
        matricule_id = f"{date_str}{id}"

        if not Student.objects.filter(matricule=matricule_id).exists():
            return matricule_id
        atteinte = atteinte + 1
        raise Exception("imposible de generer un matricule, il semble que la limite est atteinte")

def get_new_matricule():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d%H%M%S")  # Format : YYYYMMDDHHMMSS
    nbre_student = Eleve.objects.count()
    
    if nbre_student != 0:
        new_number = nbre_student + 1
    else:
        new_number = 1

    return f"{date_str}{new_number:05d}"  # Format : YYYYMMDDHHMMSS0001

# fonction pour generr un num de reçu
def numero_recu():
    dates = datetime.datetime.now().strftime("%Y-%m-%d")
    prefix = "Flamy"
    nombre = random.randint(1000, 9999)
    num = f"{prefix}{nombre}"
    return num

#list year_school  
@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def index_year(request):  
    annee_sc = Annee_Scolaire.objects.all()
    for elt in annee_sc:
        if elt.date_fin < timezone.now().date():
           elt.statut = STATUT_YEAR[1][1]
           elt.save()
    context = {'annee_sc': annee_sc}
    return render(request, 'annee_sc/index.html', context)

# afficher les details d'une année scolaire
@role_autorise("PROVISEUR", "COMPTABLE")
def details_year(reqest, id):
    annee_scolaire = get_object_or_404(Annee_Scolaire, pk=id)
    revenu_total = 0
    
   
    # Nombre total d'inscrits
    total_inscrits = Inscription.objects.filter(annee_scolaire=annee_scolaire).count()
    total_inscrits_exo = Inscription.objects.filter(annee_scolaire=annee_scolaire, regime=STATUS_REGIME[1][0]).count()
    total_inscrits_normal = Inscription.objects.filter(annee_scolaire=annee_scolaire, regime=STATUS_REGIME[0][0]).count()
    
    # Revenu total de l'année (somme des frais de scolarité de tous les inscrits)
    inscriptions = Inscription.objects.filter(annee_scolaire=annee_scolaire).select_related('classe')

    # eleve irreguliers 
    paie =0
    reste_paie=0
    eleves_irreguliers = []
    frais = 0
    for inscrit in inscriptions:
        frais_ins = inscrit.classe.frais_inscription
        paie = Payement.objects.filter(inscription = inscrit).aggregate(total=Sum('montant'))['total'] or 0
        
        if inscrit.regime == STATUS_REGIME[0][0]  and paie > 0:
                inscrit.statut = STATUTS_INSCRIPTION[1][1]  # inscrit
                frais = inscrit.classe.frais_total
                reste_paie = frais - paie
                revenu_total += inscrit.classe.frais_total
                

        elif inscrit.regime == STATUS_REGIME[0][0]  and paie < 0:
            inscrit.statut = STATUTS_INSCRIPTION[0][0] # non inscrit
            frais = inscrit.classe.frais_total
            reste_paie = frais - paie
            revenu_total += inscrit.classe.frais_total
               
        elif inscrit.regime == STATUS_REGIME[0][0]  and paie == frais:
            inscrit.statut = STATUTS_INSCRIPTION[2][1]
            frais = inscrit.classe.frais_total
            reste_paie = frais - paie
            revenu_total += inscrit.classe.frais_total
                

        elif inscrit.regime == STATUS_REGIME[1][0] and inscrit.pourcentage=="100%": # boursier 100%
            frais = frais_ins
            revenu_total += frais
            reste_paie  = frais - paie
                
            if reste_paie > 0 :   
                inscrit.statut = STATUTS_INSCRIPTION[0][0]
            else : 
                inscrit.statut = "Boursier 100%"
        elif inscrit.regime == STATUS_REGIME[1][0] and inscrit.pourcentage=="50%":
            frais = frais_ins + (inscrit.classe.frais_scolarite)/2
            reste_paie = frais - paie
            revenu_total += frais
            retard = 0 
            if paie < 0 :   
                inscrit.statut = STATUTS_INSCRIPTION[0][0]
            else : 
                inscrit.statut = "Boursier 50%"
        
        if reste_paie > 0 :
            eleves_irreguliers.append({
                'inscrit': inscrit,
                'reste_paie': reste_paie,
                'paie': paie,
                
            })

    # Revenu total des paiements effectués
    recu = Payement.objects.filter(inscription__annee_scolaire = annee_scolaire).aggregate(total = Sum('montant'))['total'] or 0
    reste = revenu_total - recu

    context = {
        'annee_scolaire': annee_scolaire,
        'total_inscrits_exo': total_inscrits_exo,
        'total_inscrits_normal': total_inscrits_normal,
        'total_inscrits': total_inscrits,
        'revenu_total': revenu_total,
        'recu': recu,
        'reste': reste,
        'eleve_irregulier': eleves_irreguliers,
        'inscriptions' : inscriptions
    }

    return render(reqest, 'annee_sc/details.html', context)

#create year_school
@login_required()
@role_autorise("PROVISEUR")
def create_year(request):
    # Vérifier s'il existe une année scolaire active
    annee_active = Annee_Scolaire.objects.filter(statut=STATUT_YEAR[0][1]).exists()

    msg = ""
    reste = 0
    form = AnneeScolaireForm()
    if request.method == 'POST':
        form = AnneeScolaireForm(request.POST)
        if form.is_valid():
            if annee_active:
                msg = "Impossible d'effectuer cette opération, car une année est déjà en cours."
            else:
                event = form.save(commit=False)
                reste = (event.date_fin - event.date_debut).days
                print(reste)
                if reste < 243:
                    msg = "La durée normale de l'année scolaire est definie à 365 jours."
                else:
                    event.save()
                    return redirect('index_year')
        else:
            msg = f"Une erreur s'est produite : {form.errors}"
            print(msg)

    return render(request, 'annee_sc/create.html', {"form": form, 'msg': msg})


#edit year_school
@login_required()
@role_autorise("PROVISEUR")
def edit_year(request, id):
    anneesc = get_object_or_404(Annee_Scolaire, pk=id)
    print(anneesc.date_debut)
   
    form = AnneeScolaireForm(request.POST or None, instance=anneesc)
    if form.is_valid():
        #event = form.save(commit=False)
        #reste = (event.date_fin - event.date_debut).days
        #print(reste)
        #if reste < 363:
         #   msg = "La durée normale de l'année scolaire est definie à 365 jours."
        #else:
         #   event.save()
          #  return redirect('index_year')
        form.save()
        return redirect('index_year')
    
  
    return render(request, 'annee_sc/edit.html', {'form': form})

@login_required()
@role_autorise("PROVISEUR")
def delete_year(request, id):
    annee = get_object_or_404(Annee_Scolaire, pk=id)
    
    annee.delete()
    return redirect('index_year')

   

@login_required()
@role_autorise("PROVISEUR", "COMPTABLE", "CAISSIER")
def index_payement(request): # acceuil payement
    if request.user.role == "PROVISEUR" or request.user.role == "COMPTABLE":
        liste_payement = Payement.objects.filter(annule=False).order_by('-id')
    else :
        liste_payement = Payement.objects.filter(utilisateur = request.user, annule=False).order_by('-id')

    return render(request, 'payment/index.html', {'liste': liste_payement})

@login_required()
def index_formations(request): # acceuil formation
    liste_formation = Classe.objects.all()
    return render(request, 'formation/index.html', {'liste': liste_formation})

@login_required()
@role_autorise("PROVISEUR", "SECRETAIRE", "COMPTABLE")
def index_eleves(request):  # acceuil eleve
    liste_eleve = Eleve.objects.all()
    return render(request, 'students/index.html', {'liste': liste_eleve})


@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def index_type_frais(request):  # acceuil type de frais
    liste_type_frais = TypeFrais.objects.all()
    return render(request, 'type_frais/index.html', {'liste': liste_type_frais})

@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def index_frais_inscription(request):  # acceuil frais d'inscription
    liste_frais_inscription = FraisInscription.objects.all()
    return render(request, 'frais_inscription/index.html', {'liste': liste_frais_inscription})

logger = logging.getLogger(__name__)
@login_required()
@role_autorise("SECRETAIRE")
def index_inscription(request):

    try:
        annee_scolaire_active = Annee_Scolaire.objects.get(statut="Active")
    except Annee_Scolaire.DoesNotExist:
        annee_scolaire_active = None

    if annee_scolaire_active:
        # Récupérer les inscriptions de l'année scolaire active
        inscrits = Inscription.objects.filter(annee_scolaire=annee_scolaire_active)

    context = {
            'inscrit': inscrits }
    
    return render(request, 'inscription/index.html', context)

# ajouter un apprenant
@login_required()
@role_autorise("PROVISEUR", "SECRETAIRE")
def create_eleve(request):
    msg = ""
    formulaire = EleveForm()
    if request.method == "POST":
        formulaire = EleveForm(request.POST)
        if formulaire.is_valid():
            event = formulaire.save(commit=False)
            event.matricule = get_new_matricule()
            # calcul de l'age de l'eleve
            today = timezone.now().date()
            age = today.year - event.date_naissance.year # obtenir l'age exact de l'eleve
            # verifier si l'anniversaire de l'eleve n'est pas atteint et faire moins 1 sur son age.
            if ((today.month, today.year) < (event.date_naissance.month, event.date_naissance.year)):
                age = age - 1
            if age < 10 : 
                msg = "L'apprenant doit avoir au moins 10 ans."
            else:
                event.save()
                return redirect('eleve_index')

    return render(request, 'students/create.html', {'form': formulaire, "msg":msg} )

#editer un apprenant
@login_required()
@role_autorise("PROVISEUR", "SECRETAIRE")
def edit_students(request, id):
    apprenant = get_object_or_404(Eleve, pk=id)
    formualire = EleveForm(request.POST or None, instance=apprenant)
    if formualire.is_valid():
        formualire.save()
        return redirect('eleve_index')
    return render(request, 'students/edit.html', {'form': formualire})

# effacer un apprenant de la base de données
@login_required()
@role_autorise("PROVISEUR", "SECRETAIRE")
def delete_students(request, id):
    apprenant = get_object_or_404(Eleve, pk=id)
    apprenant.delete()
    return redirect('eleve_index')

# enregistrer une classe
@login_required()
@role_autorise("PROVISEUR")
def create_classe(request):
    formulaire = ClasseForm()

    if request.method == 'POST':
        formulaire = ClasseForm(request.POST)

        if formulaire.is_valid():
            event = formulaire.save(commit=False)
            event.save()
            return redirect('formation_index')
        
    return render(request, 'formation/create.html', {'form': formulaire})

# editer une classe
@login_required()
@role_autorise("PROVISEUR")
def edit_classe(request, id):
    formation = get_object_or_404(Classe, pk=id)
    formulaire = ClasseForm(request.POST or None, instance=formation)
    if formulaire.is_valid():
        formulaire.save()
        return redirect('formation_index')
    return render(request, 'formation/edit.html', {'form': formulaire})

#supprimer classe
@login_required()
@role_autorise("PROVISEUR")
def delete_classe(request, id):
    formation = get_object_or_404(Classe, pk=id)
    formation.delete()
    return redirect('formation_index')


# enregistrer un type de frais
@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def create_type_frais(request):
    formulaire = TypeFraisForm()

    if request.method == 'POST':
        formulaire = TypeFraisForm(request.POST)

        if formulaire.is_valid():
            event = formulaire.save(commit=False)
            event.save()
            return redirect('type_frais_index')
        
    return render(request, 'type_frais/create.html', {'form': formulaire})

#editer type de frais 
@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def edit_type_frais(request, id):
    type_frais = get_object_or_404(TypeFrais, pk=id)
    formulaire = TypeFraisForm(request.POST or None, instance=type_frais)
    if formulaire.is_valid():
        formulaire.save()
        return redirect('type_frais_index')
    return render(request, 'type_frais/edit.html', {'form': formulaire})

# enregistrer frais d'incription
@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def create_frais_inscription(request):
    formulaire = FraisInscriptionForm()
    msg=""

    if request.method == 'POST':
        formulaire = FraisInscriptionForm(request.POST)
        if formulaire.is_valid():
            event = formulaire.save(commit=False)
            FraisInscriptionService.creer_frais(
                inscription=event.inscription,
                type_frais=event.type_frais,
                remise=event.remise,
                motif_remise=event.motif_remise
            )
            event.save()
            return redirect('frais_inscription_index')
        else : 
            msg = "le formulaire contient des erreurs"

    return render(request, 'frais_inscription/create.html', {'form':formulaire, 'message': msg})

#editer frais inscription
@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def edit_frais_inscription(request, id):
    frais_inscription = get_object_or_404(FraisInscription, pk=id)
    if request.method == "POST":
        form = FraisInscription_UpdateForm(request.POST, instance=frais_inscription)
        remise_avant = frais_inscription.remise
        motif_avant = frais_inscription.motif_remise
        if form.is_valid():
            AuditService.log(
                action="MODIFICATION",
                modele= frais_inscription.__class__.__name__,
                objet_id=frais_inscription.id,
                utilisateur=request.user,
                motif=form.cleaned_data.get("motif_remise", ""),
                donnees_avant={
                    "type_frais": frais_inscription.type_frais.nom,
                    "remise": str(remise_avant),
                    "motif_remise": motif_avant,
                },
                donnees_apres={
                    "type_frais": form.cleaned_data["type_frais"].nom,
                    "remise": str(form.cleaned_data["remise"]),
                    "motif_remise": form.cleaned_data.get("motif_remise", ""),
                }
                
            )
            form.save()
            return redirect("frais_inscription_index")
    else:
        form = FraisInscription_UpdateForm(instance=frais_inscription)

    return render(request, "frais_inscription/edit.html", {
        "form": form,
        "frais": frais_inscription
    })

# faire une inscription
@login_required() 
@role_autorise("SECRETAIRE")
def create_inscription(request):
    formulaire = InscriptionForm()
    msg = ""

    if request.method == 'POST':
        formulaire = InscriptionForm(request.POST)
        if formulaire.is_valid():
            InscriptionsService.inscrire_eleve(
                eleve=formulaire.cleaned_data["eleve"],
                classe=formulaire.cleaned_data["classe"],
                regime=formulaire.cleaned_data["regime"],
                annee_scolaire=formulaire.cleaned_data["annee_scolaire"],  
            )

            return redirect('inscription_index')
            
        else:
            msg = f"Le formulaire contient des erreurs. Veuillez les corriger et réessayer. Détails : {formulaire.errors}"

    return render(request, 'inscription/create.html', {'form': formulaire, 'msg': msg})

# afficher les details financier d'un eleve
@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def details_inscription_eleve(request, inscription_id):
    inscription = get_object_or_404(Inscription, id=inscription_id)

    situation = situation_financiere_inscription(inscription)

    context = {
        "inscription": inscription,
        "situation": situation
    }

    return render(request, "inscription/details_inscription.html", context)

# afficher les impayés selon les filtres
@login_required()
@role_autorise("PROVISEUR", "COMPTABLE")
def liste_impayes(request):
    
    # reccuperer les parametres de filtrage
    classe_id = request.GET.get("classe") or None
    annee_id = request.GET.get("annee") or None
    type_frais_id = request.GET.get("type_frais") or None
    page_number = request.GET.get("page")

    # reccuperons les objets filtres
    classe = Classe.objects.filter(id=classe_id).first() if classe_id else None
    type_frais = TypeFrais.objects.filter(id=type_frais_id).first() if type_frais_id else None

    # par defaut annee == annee en cours
    if annee_id:
        annee = Annee_Scolaire.objects.filter(id=annee_id).first()
    else:
        annee = annee_en_cours()

    # filtrer les impayes selon les criteres (Anne scolaire, classe, type de frais)
    impayes_qs = impayes_par_filtre(
        annee_scolaire=annee,
        classe=classe,
        type_frais=type_frais
    )

    # pagination (50 par page)
    paginator = Paginator(impayes_qs, 50)
    impayes = paginator.get_page(page_number)

    context = {
        "impayes": impayes,
        "classes": Classe.objects.all(),
        "annees": Annee_Scolaire.objects.all(),
        "types_frais": TypeFrais.objects.all(),
        "classe_selected": classe_id,
        "annee_selected": annee.id if annee else None,
        "type_frais_selected": type_frais_id,
    }
    
    return render(request, "frais_inscription/impayes_list.html", context)

# edit inscription
@login_required()
@role_autorise("SECRETAIRE")
def edit_inscription(request, id):
    inscription = get_object_or_404(Inscription, pk=id)
    formulaire = InscriptionForm(request.POST or None, instance=inscription)
    if formulaire.is_valid():
        formulaire.save()
        return redirect('inscription_index')
    
    return render(request, 'inscription/edit.html', {'form': formulaire})

@login_required()
@role_autorise("SECRETAIRE")
def delete_inscription(request, id):
    inscription =  get_object_or_404(Inscription, pk=id)
    inscription.delete()
    return redirect('inscription_index')



# effectuer un payement
@login_required()
@role_autorise("CAISSIER")
def create_payement(request):
    msg = ""
    utilisateur = request.user
    formulaire = PaiementGlobalForm()
    if request.method == "POST":
        formulaire = PaiementGlobalForm(request.POST)
        if formulaire.is_valid():
            try:
                PayementService.effectuer_paiement_inscription(
                    inscription=formulaire.cleaned_data["inscription"],
                    montant=formulaire.cleaned_data["montant"],
                    utilisateur=utilisateur,
                    numero_recu=PayementService.recu()
                    )       
                return redirect('payment_index')
            except Exception as e:
                msg = str(e)
   
    return render(request, 'payment/create.html', {
        'form': formulaire,
        'msg': msg,
        
    })

# generer reçu de payement
@login_required
@role_autorise("CAISSIER", "COMPTABLE", "PROVISEUR")
def recu_paiement(request, paiement_id):
    paiement = get_object_or_404(
        Payement.objects.select_related(
            "frais_inscription",
            "frais_inscription__type_frais",
            "frais_inscription__inscription__eleve",
            "frais_inscription__inscription__classe",
            "utilisateur"
        ),
        id=paiement_id
    )

    context = {
        "paiement": paiement,
        "numero_recu": f"RC-{paiement.id:06d}"
    }

    return render(request, "payment/reçu_payement.html", context)


#Annuler payement
@login_required()
@role_autorise("CAISSIER", "COMPTABLE")
def annuler_payement(request, paiement_id):
    paiement = get_object_or_404(Payement, id=paiement_id)

    if request.method == "POST":
        form = AnnulationPaiementForm(request.POST)
        if form.is_valid():
            PayementService.annuler_paiement(
                paiement=paiement,
                motif=form.cleaned_data["motif"],
                utilisateur=request.user
            )
            return redirect("payment_index")

    else:
        form = AnnulationPaiementForm()

    return render(request, "payment/delete.html", {
        "form": form,
        "paiement": paiement
    })


# retard de payement
@login_required
@role_autorise("COMPTABLE", "PROVISEUR")
def eleves_en_retard(request):
    annee = annee_en_cours()
    classe_id = request.GET.get("classe")
    mois_id = request.GET.get("mois")

    inscriptions = Inscription.objects.filter(
        annee_scolaire=annee
    ).select_related("eleve", "classe")

    if classe_id:
        inscriptions = inscriptions.filter(classe_id=classe_id)

    resultats = []

    for inscription in inscriptions:
        situation = RetardService.calculer_retard_inscription(inscription)

        if situation["mois_retard"] > 0:
            if mois_id:
                mois_id = int(mois_id)
                if situation["mois_retard"] < mois_id:
                    continue
            resultats.append(situation)

    # pagination
    paginator = Paginator(resultats, 25)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    context = {
        "page_obj": page_obj,
        "classes": Classe.objects.all(),
        "classe_selectionnee": classe_id,
        "mois_selectionne": mois_id,
        "annee": annee
    }

    return render(request, "payment/retard.html", context)


# liste des audits 
@login_required
@role_autorise("PROVISEUR", "COMPTABLE")
def liste_audit(request):
    action = request.GET.get("action")
    modele = request.GET.get("modele")
    utilisateur_id = request.GET.get("utilisateur")

    audits = AuditService.lister_audits(
        action=action,
        modele=modele,
        utilisateur=utilisateur_id
    )

    paginator = Paginator(audits, 20)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    context = {
        # audits
        "page_obj": page_obj,

        # filtres
        "actions": AuditLog.ACTIONS,
        "modeles": AuditLog.objects.values_list("modele", flat=True).distinct(),
        "utilisateurs": Utilisateur.objects.all(),

        "action_selectionnee": action,
        "modele_selectionne": modele,
        "utilisateur_selectionne": utilisateur_id,
    }

    return render(request, "dashboard/liste_audit.html", context)

# dashboard
@login_required
@role_autorise("PROVISEUR", "COMPTABLE")
def dashboard_direction(request):
    # --- année scolaire ---
    annee_id = request.GET.get("annee")

    if annee_id:
        annee = Annee_Scolaire.objects.get(id=annee_id)
    else:
        annee = Annee_Scolaire.objects.filter(statut="Active").first()

    # sécurité
    if not annee:
        return render(request, "dashboard/erreur.html", {
            "message": "Aucune année scolaire active."
        })

    # --- appel du service ---
    stats = DashboardService.get_dashboard_stats(annee)

    return render(request, "base/index.html", {
        "annee": annee,
        "annees": Annee_Scolaire.objects.all(),
        **stats
    })
