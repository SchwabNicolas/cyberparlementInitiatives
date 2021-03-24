"""
Configuration relative à l'administration de Django.
"""

from django.contrib import admin

from cyberparlementInitiatives.models import Personne, Voteinitiative, Initiative, Choixinitiative


@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    """
    Modèle d'administration de :cyberparlement.Personne:.
    """
    pass


@admin.register(Voteinitiative)
class VoteinitiativeAdmin(admin.ModelAdmin):
    """
    Modèle d'administration de :cyberparlement.Voteinitiative:.
    """
    pass


@admin.register(Choixinitiative)
class ChoixinitiativeAdmin(admin.ModelAdmin):
    """
    Modèle d'administration de :cyberparlement.Choixinitiative:.
    """
    pass


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    """
    Modèle d'administration de :cyberparlement.Initiative:.
    """
    pass
