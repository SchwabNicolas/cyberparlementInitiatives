from django.contrib.auth.models import User
from django.forms import CharField, forms, Textarea, ModelChoiceField, ModelForm

from cyberparlementInitiatives.models import Initiative, Personne


class InitiativePropositionForm(ModelForm):
    nom = CharField(label='Nom de l\'initiative', label_suffix='', max_length=45)
    description = CharField(label='Description', label_suffix='', max_length=1000, widget=Textarea)

    class Meta:
        model = Initiative
        fields = [
            'cyberparlement',
            'nom',
            'description'
        ]


# Formulaires d'authentification (pour tester)
class UserCreationForm(ModelForm):
    class Meta:
        model = Personne
        fields = '__all__'
