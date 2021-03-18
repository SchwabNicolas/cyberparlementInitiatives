import operator

from django.db.models import Q

from cyberparlementInitiatives.models import Choixinitiative, Voteinitiative, Initiative


def get_detailed_vote_count(initiative_id):
    choixinitiatives = Choixinitiative.objects.filter(initiative_id=initiative_id)

    votes = {}

    for choixinitiative in choixinitiatives:
        votes_choixinitiative = Voteinitiative.objects.filter(Q(choixinitiative_id=choixinitiative.id) & Q(statut_validation=Voteinitiative.STATUT_VALIDATION_VALIDE)).count()
        votes[choixinitiative.id] = votes_choixinitiative


def get_winning_choices(votes):
    winning_choices = {}

    maximum = max(votes, key=votes.get)
    for vote in votes:
        if votes[vote] == maximum:
            winning_choices[vote] = votes[vote]

    return winning_choices
