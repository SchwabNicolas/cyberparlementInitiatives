from bootstrap_datepicker_plus import DateTimePickerInput
from django.forms import CharField, Textarea, ModelForm, DateTimeField

from cyberparlementInitiatives.models import Initiative, Personne


class InitiativePropositionForm(ModelForm):
    """
    Formulaire de proposition d'initiative.
    """

    nom = CharField(
        label='Nom de l\'initiative',
        label_suffix='',
        max_length=45
    )
    description = CharField(
        label='Description',
        label_suffix='',
        max_length=1000,
        widget=Textarea
    )

    class Meta:
        model = Initiative
        fields = [
            'cyberparlement',
            'nom',
            'description'
        ]


class InitiativeStartPollForm(ModelForm):
    """
    Formulaire d'organisation de scrutin.
    """

    debut_scrutin = DateTimeField(label='Début du scrutin',
                                  label_suffix='',
                                  widget=DateTimePickerInput(format='%Y-%m-%d %H:%M'))

    fin_scrutin = DateTimeField(label='Fin du scrutin',
                                label_suffix='',
                                widget=DateTimePickerInput(format='%Y-%m-%d %H:%M'))

    class Meta:
        model = Initiative
        fields = [
            'debut_scrutin',
            'fin_scrutin',
            'mode_validation',
        ]


# Formulaire d'authentification -- à des fins de test
class UserCreationForm(ModelForm):
    class Meta:
        model = Personne
        fields = '__all__'
