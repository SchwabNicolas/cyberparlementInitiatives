"""
Configuration relative à l'administration de Django.
"""

from django.contrib import admin

from cyberparlementInitiatives.models import Personne, Voteinitiative, Initiative


@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    pass


@admin.register(Voteinitiative)
class VoteinitiativeAdmin(admin.ModelAdmin):
    pass


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    pass
