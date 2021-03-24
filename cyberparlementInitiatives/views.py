import datetime

from django.contrib.auth import login, logout
from django.db.models import Q, Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, FormView, ListView, CreateView

from cyberparlementInitiatives.forms import InitiativePropositionForm, UserCreationForm, InitiativeStartPollForm
from cyberparlementInitiatives.models import Initiative, Cyberparlement, Choixinitiative, Personne, Voteinitiative
from cyberparlementInitiatives.utils.schedule import schedule_poll_start, schedule_poll_end
from cyberparlementInitiatives.utils.validation import validate_token, send_validation_email


# Vue d'index -- à des fins de debug
class IndexView(TemplateView):
    """
    Vue d'index.

    **Template**
    :template:'cyberparlementInitiatives/index.html'

    *Contexte*
    ``title``
        Titre de la page

    ``description``
        Description de la page
    """

    template_name = 'cyberparlementInitiatives/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cyberparlement Initiatives - Index'
        context['description'] = 'Index de Cyberparlement Initiatives'
        return context


# Vues des initiatives
class InitiativeListView(TemplateView):
    """
    Vue de la liste des initiatives par cyberparlement.

    **Contexte**

    ``title``
        Titre de la page

    ``description``
        Description de la page

    ``cyberparlement``
        Cyberparlement

    ``initiatives_en_cours``
        Initiatives en cours du cyberparlement

    ``initiatives_archive``
        Initiatives dont le scrutin est terminé du cyberparlement

    ``initiatives_a_valider``
        Initiatives à valider par un cyberchancelier du cyberparlement

    ``initiatives_a_venir``
        Initiatives validées dont le scrutin est à venir du cyberparlement

    ``need_vote_validation``
        Nombre de votes en attente de validation par l'utilisateur du cyberparlement


    **Template**
    :template:'cyberparlementInitiatives/initiatives/initiative_liste.html'
    """
    model = Initiative
    template_name = 'cyberparlementInitiatives/initiatives/initiative_liste.html'

    def get_cyberparlement(self):
        return Cyberparlement.objects.get(id=self.kwargs.get('id_cyberparlement'))

    def get_initiatives_par_cyberparlement(self):
        return Initiative.objects.filter(cyberparlement=self.get_cyberparlement())

    def get_initiatives_a_valider(self):
        return self.get_initiatives_par_cyberparlement().filter(Q(statut=Initiative.STATUT_A_VALIDER))

    def get_initiatives_a_venir(self):
        return self.get_initiatives_par_cyberparlement().filter(Q(statut=Initiative.STATUT_VALIDEE))

    def get_initiatives_archive(self):
        return self.get_initiatives_par_cyberparlement().filter(Q(statut=Initiative.STATUT_SCRUTIN_TERMINE))

    def get_initiatives_en_cours(self):
        initiatives_en_cours = self.get_initiatives_par_cyberparlement().filter(Q(statut=Initiative.STATUT_EN_SCRUTIN))
        need_validation = Count('voteinitiative', filter=~Q(mode_validation=Initiative.MODE_VALIDATION_AUCUN) & (Q(voteinitiative__statut_validation=Voteinitiative.STATUT_VALIDATION_NON_VALIDE) & Q(voteinitiative__personne=self.request.user)))  # Compte les votes de l'utilisateur actuel qui ne sont pas validés
        has_voted = Count('voteinitiative', filter=Q(voteinitiative__personne=self.request.user))  # Compte les votes de l'utilisateur actuel qui ne sont pas validés
        initiatives_en_cours = initiatives_en_cours.annotate(has_voted=has_voted)  # Applique l'agrégation de la requête précédente
        initiatives_en_cours = initiatives_en_cours.annotate(need_validation=need_validation)  # Applique l'agrégation de la requête précédente
        return initiatives_en_cours

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cyberparlement'] = self.get_cyberparlement()
        context['initiatives_en_cours'] = self.get_initiatives_en_cours()
        context['initiatives_archive'] = self.get_initiatives_archive()
        context['initiatives_a_valider'] = self.get_initiatives_a_valider()
        context['initiatives_a_venir'] = self.get_initiatives_a_venir()
        context['need_vote_validation'] = self.get_initiatives_en_cours().filter(Q(need_validation=1)).count()
        context['title'] = 'Liste des initiatives'
        context['description'] = f'Les des initiatives pour le cyberparlement {self.get_cyberparlement().nom}'
        return context


class InitiativePropositionView(FormView):
    """
    Vue de proposition d'initiative.

    **Contexte**

    ``title``
        Titre de la page

    ``description``
        Description de la page

    **Template**
    :template:'cyberparlementInitiatives/initiatives/initiative_proposition.html'
    """

    form_class = InitiativePropositionForm
    template_name = 'cyberparlementInitiatives/initiatives/initiative_proposition.html'
    success_url = reverse_lazy('index')

    def post(self, *args, **kwargs):
        cyberparlement = Cyberparlement.objects.get(id=self.request.POST.get('cyberparlement'))

        initiative = Initiative(
            cyberparlement=cyberparlement,
            nom=self.request.POST.get('nom'),
            description=self.request.POST.get('description'),
            statut=Initiative.STATUT_A_VALIDER,
            initiateur=self.request.user
        )
        initiative.save()

        for key in self.request.POST:
            split_key = key.split('-')
            if len(split_key) > 1 and split_key[0] == 'reponse':
                try:
                    int(split_key[1])
                    Choixinitiative(
                        initiative=initiative,
                        ordre=split_key[1],
                        choix=self.request.POST[key],
                    ).save()
                except ValueError:
                    pass

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Proposer une initiative'
        context['description'] = 'Proposer une initiative'
        return context


class InitiativeValidationView(FormView):
    """
    Vue de validation d'une initiative par un cyberchancelier.

    **Contexte**

    ``title``
       Titre de la page

    ``description``
       Description de la page

    ``form``
       Formulaire de validation

    ``choix``
       Choix de réponse de l'initiative à valider

    **Template**
    ``cyberparlementInitiatives/initiatives/initiative_validation.html``
    """

    form_class = InitiativePropositionForm
    template_name = 'cyberparlementInitiatives/initiatives/initiative_validation.html'
    success_url = reverse_lazy('index')

    def get_initiative(self):
        return Initiative.objects.get(id=self.kwargs.get('id_initiative'))

    def get_choix_initiative(self):
        blank_choice = Choixinitiative.objects.filter(initiative=self.get_initiative(), choix=Choixinitiative.BLANK_CHOICE)
        if blank_choice:
            Choixinitiative.objects.filter(initiative=self.get_initiative(), choix=Choixinitiative.BLANK_CHOICE).delete()

        return Choixinitiative.objects.filter(initiative=self.get_initiative()).order_by('ordre')

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('delete'):
            cyberparlement_id = self.get_initiative().cyberparlement.id
            self.get_initiative().delete()
            return redirect(reverse_lazy('initiative-list', kwargs={'id_cyberparlement': cyberparlement_id}))
        else:
            cyberparlement = Cyberparlement.objects.get(id=self.request.POST.get('cyberparlement'))

            initiative = Initiative(
                id=self.get_initiative().id,
                cyberparlement=cyberparlement,
                nom=self.request.POST.get('nom'),
                description=self.request.POST.get('description'),
            )
            initiative.save()

            self.get_choix_initiative().delete()

            index = 0
            for key in self.request.POST:
                split_key = key.split('-')
                if len(split_key) > 1 and split_key[0] == 'reponse':
                    try:
                        index += 1
                        Choixinitiative(
                            initiative=initiative,
                            ordre=index,
                            choix=self.request.POST[key],
                        ).save()
                    except ValueError:
                        pass

            return redirect(reverse_lazy('initiative-start-poll', kwargs={"id_initiative": self.get_initiative().id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Valider une initiative'
        context['description'] = 'Valider une initiative'
        context['form'] = self.form_class(instance=self.get_initiative())
        context['choix'] = self.get_choix_initiative()
        return context


class InitiativeCreateSecondRoundView(FormView):
    """
    Vue de permettant de créer un nouveau tour.

    **Contexte**

    ``title``
        Titre de la page

    ``description``
        Description de la page

    ``initiative``
        Initiative pour laquelle il faut créer un nouveau tour

    **Template**
    :template:'cyberparlementInitiatives/initiatives/initiative_create_second_round.html'
    """

    form_class = InitiativeStartPollForm
    template_name = 'cyberparlementInitiatives/initiatives/initiative_create_second_round.html'

    def get_parent_initiative(self):
        return Initiative.objects.get(id=self.kwargs.get('id_initiative'))

    def get_placeholder_initiative(self):
        initiative = self.get_parent_initiative()
        initiative.id = None
        return initiative

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Organiser un nouveau tour'
        context['description'] = 'Organiser un nouveau tour'
        context['initiative'] = self.get_placeholder_initiative()
        return context

    def post(self, request, *args, **kwargs):
        initiative = self.get_placeholder_initiative()
        initiative.debut_scrutin = self.request.POST.get('debut_scrutin')
        initiative.fin_scrutin = self.request.POST.get('fin_scrutin')
        initiative.mode_validation = self.request.POST.get('mode_validation')
        if self.get_parent_initiative().parent is not None:
            initiative.parent = self.get_parent_initiative().parent
        else:
            initiative.parent = self.get_parent_initiative()
        initiative.statut = Initiative.STATUT_VALIDEE
        initiative.save()

        parent_choixinitiatives = Choixinitiative.objects.filter(initiative=self.get_parent_initiative())
        for choixinitiative in parent_choixinitiatives:
            if choixinitiative.choix != Choixinitiative.BLANK_CHOICE and not choixinitiative.is_last:
                choixinitiative_placeholder = choixinitiative
                choixinitiative_placeholder.initiative = initiative
                choixinitiative_placeholder.id = None
                choixinitiative.save()

        schedule_poll_start(initiative.id)
        schedule_poll_end(initiative.id)

        cyberparlement_id = initiative.cyberparlement.id
        return redirect(reverse_lazy('initiative-list', kwargs={'id_cyberparlement': cyberparlement_id}))


class InitiativeStartPollView(FormView):
    """
    Vue de permettant d'organiser un scrutin.

    **Contexte**

    ``title``
        Titre de la page

    ``description``
        Description de la page

    ``initiative``
        Initiative pour laquelle on organise un scrutin

    **Template**
    :template:'cyberparlementInitiatives/initiatives/initiative_start_poll.html'
    """

    form_class = InitiativeStartPollForm
    template_name = 'cyberparlementInitiatives/initiatives/initiative_start_poll.html'

    def get_initiative(self):
        return Initiative.objects.get(id=self.kwargs.get('id_initiative'))

    def post(self, request, *args, **kwargs):
        initiative = self.get_initiative()
        initiative.debut_scrutin = self.request.POST.get('debut_scrutin')
        initiative.fin_scrutin = self.request.POST.get('fin_scrutin')
        initiative.mode_validation = self.request.POST.get('mode_validation')
        initiative.statut = Initiative.STATUT_VALIDEE
        initiative.save()

        schedule_poll_start(self.get_initiative().id)
        schedule_poll_end(self.get_initiative().id)

        cyberparlement_id = self.get_initiative().cyberparlement.id
        return redirect(reverse_lazy('initiative-list', kwargs={'id_cyberparlement': cyberparlement_id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Organiser un scrutin'
        context['description'] = 'Organiser un scrutin'
        context['initiative'] = self.get_initiative()
        return context


class InitiativePollVoteView(DetailView):
    """
    Vue de permettant de voter durant un scrutin.

    **Contexte**
    ``title``
        Titre de la page

    ``description``
        Description de la page

    ``choix``
        Choix de l'initiative pour laquelle on organise un scrutin

    **Template**
    :template:'cyberparlementInitiatives/initiatives/initiative_start_poll.html'
    """

    template_name = 'cyberparlementInitiatives/initiatives/initiative_vote_poll.html'
    model = Initiative
    context_object_name = 'initiative'

    def get_choix_initiative(self):
        return Choixinitiative.objects.filter(initiative=self.get_object()).order_by('ordre')

    def post(self, *args, **kwargs):
        if self.request.POST.get('reponse'):
            choix_initiative = Choixinitiative.objects.get(id=self.request.POST.get('reponse'))
            vote_initiative = Voteinitiative(
                timestamp=datetime.datetime.now(),
                initiative_id=self.get_object().id,
                personne_id=self.request.user.id,
                choixinitiative=choix_initiative
            )
            vote_initiative.save()

            if self.get_object().mode_validation == Initiative.MODE_VALIDATION_AUCUN:
                vote_initiative.statut_validation = Voteinitiative.STATUT_VALIDATION_VALIDE
            elif self.get_object().mode_validation == Initiative.MODE_VALIDATION_EMAIL:
                send_validation_email(voteinitiative=vote_initiative, request=self.request, initiative=self.get_object())

        if self.get_object().mode_validation == Initiative.MODE_VALIDATION_AUCUN:
            return redirect(reverse_lazy('initiative-list', kwargs={'id_cyberparlement': self.get_object().cyberparlement.id}))
        else:
            return redirect(reverse_lazy('initiative-validate-poll-vote', kwargs={'pk': self.get_object().id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Voter'
        context['description'] = f'Voter sur {self.get_object().nom}'
        context['choix'] = self.get_choix_initiative()
        return context


class InitiativePollDetailView(DetailView):
    """
    Vue des résultats d'un scrutin.

    **Contexte**

    ``title``
        Titre de la page

    ``description``
        Description de la page

    **Template**
    :template:'cyberparlementInitiatives/initiatives/initiative_poll_detail.html'
    """

    template_name = 'cyberparlementInitiatives/initiatives/initiative_poll_detail.html'
    model = Initiative
    context_object_name = 'initiative'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Résultats'
        context['description'] = f'Résultats du scrutin pour {self.get_object().nom}'
        return context


class InitiativeValidatePollVoteView(DetailView):
    """
    Vue de validation d'un vote.

    **Contexte**

    ``title``
        Titre de la page

    ``description``
        Description de la page

    ``validation_text``
        Texte d'information concernant la validation

    **Template**
    :template:'cyberparlementInitiatives/initiatives/initiative_validate_poll_vote.html'
    """

    model = Initiative
    template_name = 'cyberparlementInitiatives/initiatives/initiative_validate_poll_vote.html'
    context_object_name = 'initiative'

    def get_validation_text(self):
        if self.get_object().mode_validation == Initiative.MODE_VALIDATION_AUCUN:
            return ""
        elif self.get_object().mode_validation == Initiative.MODE_VALIDATION_EMAIL:
            return "Un email vous a été envoyé."
        elif self.get_object().mode_validation == Initiative.MODE_VALIDATION_SMS:
            return "Un SMS vous a été envoyé."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Valider un vote'
        context['description'] = 'Valider un vote'
        context['validation_text'] = self.get_validation_text()
        return context

    def get_voteinitiative(self):
        return Voteinitiative.objects.get(initiative=self.get_object(), personne=self.request.user)

    def post(self, *args, **kwargs):
        print(self.request.POST)
        if self.request.POST.get('sendMail'):
            vote_initiative = Voteinitiative.objects.get(personne=self.request.user, initiative=self.get_object())
            send_validation_email(voteinitiative=vote_initiative, initiative=self.get_object(), request=self.request)
        if self.request.POST.get('validationCode'):
            validation_code = self.request.POST.get('validationCode')
            is_valid = validate_token(validation_code=validation_code, voteinitiative=self.get_voteinitiative())
            print(is_valid)
            if is_valid:
                choix_initiative = self.get_voteinitiative()
                choix_initiative.statut_validation = Voteinitiative.STATUT_VALIDATION_VALIDE
                choix_initiative.save()
                cyberparlement_id = self.get_object().cyberparlement.id
                return redirect(reverse_lazy('initiative-list', kwargs={'id_cyberparlement': cyberparlement_id}))
        return redirect(reverse_lazy('initiative-validate-poll-vote', kwargs={'pk': self.get_object().id}))


# Vues relatives aux cyberparlements -- à des fins de test
class CyberparlementListView(ListView):
    template_name = 'cyberparlementInitiatives/cyberparlements/cyberparlement_liste.html'
    model = Cyberparlement
    context_object_name = 'cyberparlements'

    def post(self, *args, **kwargs):
        if self.request.POST.get('idcyberparlement'):
            idcyberparlement = self.request.POST.get('idcyberparlement')
            cyberparlement = Cyberparlement.objects.get(id=idcyberparlement)
            if self.request.POST.get('becUser'):
                cyberparlement.cyberchanceliers.remove(self.request.user)
            elif self.request.POST.get('becCyberchancelier'):
                cyberparlement.cyberchanceliers.add(self.request.user)
        return redirect('cyberparlement-list')


# Vues relatives à l'authentification
class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = 'cyberparlementInitiatives/auth/create_user.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Koolapic'
        context['description'] = 'Créer une activité sur Koolapic'
        return context


class UserLoginView(TemplateView):
    template_name = 'cyberparlementInitiatives/auth/change_user.html'

    def post(self, *args, **kwargs):
        if self.request.POST.get('logout'):
            logout(self.request)
            return redirect('user-login')
        if self.request.POST.get('user'):
            user = Personne.objects.get(username=self.request.POST.get('user'))
            login(request=self.request, user=user)
            return redirect('user-login')

    def get_users(self):
        return Personne.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.get_users()
        return context
