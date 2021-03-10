import datetime

from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, FormView, ListView, CreateView

from cyberparlementInitiatives.forms import InitiativePropositionForm, UserCreationForm
from cyberparlementInitiatives.models import Initiative, Cyberparlement, Choixinitiative, Personne


class IndexView(TemplateView):
    template_name = 'cyberparlementInitiatives/index.html'


class InitiativeDetailView(DetailView):
    model = Initiative
    context_object_name = 'initiative'
    template_name = 'cyberparlementInitiatives/initiatives/initiative_detail.html'


class InitiativeListView(TemplateView):
    model = Initiative
    context_object_name = 'initiatives'
    template_name = 'cyberparlementInitiatives/initiatives/initiative_liste.html'

    def get_cyberparlement(self):
        return Cyberparlement.objects.get(id=self.kwargs.get('id_cyberparlement'))

    def get_initiatives_par_cyberparlement(self):
        return Initiative.objects.filter(cyberparlement=self.get_cyberparlement())

    def get_initiatives_a_valider(self):
        return self.get_initiatives_par_cyberparlement().filter(statut=Initiative.STATUT_A_VALIDER)

    def get_initiatives_archive(self):
        return self.get_initiatives_par_cyberparlement().filter(echeance__lt=datetime.datetime.now())

    def get_initiatives_en_cours(self):
        return self.get_initiatives_par_cyberparlement().filter(echeance__gt=datetime.datetime.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cyberparlement'] = self.get_cyberparlement()
        context['initiatives_en_cours'] = self.get_initiatives_en_cours()
        context['initiatives_archive'] = self.get_initiatives_archive()
        context['initiatives_a_valider'] = self.get_initiatives_a_valider()
        return context


class InitiativePropositionView(FormView):
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


class InitiativeValidationView(FormView):
    form_class = InitiativePropositionForm
    template_name = 'cyberparlementInitiatives/initiatives/initiative_proposition.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
