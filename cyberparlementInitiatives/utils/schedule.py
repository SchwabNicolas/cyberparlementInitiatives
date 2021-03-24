from django.db.models import Q
from django_q.models import Schedule
from django_q.tasks import schedule

from cyberparlementInitiatives.models import Initiative, Choixinitiative


def open_poll(initiative_id):
    initiative = Initiative.objects.get(id=initiative_id)
    initiative.statut = Initiative.STATUT_EN_SCRUTIN
    initiative.save()

    blank_order = Choixinitiative.objects.filter(Q(initiative_id=initiative_id) & ~Q(choix=Choixinitiative.BLANK_CHOICE)).count() + 1

    choixinitiative = Choixinitiative(
        initiative=initiative,
        ordre=blank_order,
        choix=Choixinitiative.BLANK_CHOICE,
    )

    choixinitiative.save()


def schedule_poll_start(initiative_id):
    initiative = Initiative.objects.get(id=initiative_id)
    debut_scrutin = initiative.debut_scrutin
    name = f'start-poll-{initiative_id}'

    if initiative.debut_scrutin is not None:
        Schedule.objects.filter(name=name).delete()

    if initiative.parent:
        initiative.parent.statut = Initiative.STATUT_SECOND_TOUR

    schedule(
        'cyberparlementInitiatives.utils.schedule.open_poll',
        initiative_id,
        next_run=debut_scrutin,
        name=name,
    )


def close_poll(initiative_id):
    initiative = Initiative.objects.get(id=initiative_id)
    initiative.statut = Initiative.STATUT_SCRUTIN_TERMINE
    if initiative.parent:
        initiative.parent.statut = Initiative.STATUT_SCRUTIN_TERMINE
    initiative.save()


def schedule_poll_end(initiative_id):
    initiative = Initiative.objects.get(id=initiative_id)
    fin_scrutin = initiative.fin_scrutin
    name = f'end-poll-{initiative_id}'

    if initiative.debut_scrutin is not None:
        Schedule.objects.filter(name=name).delete()

    schedule(
        'cyberparlementInitiatives.utils.schedule.close_poll',
        initiative_id,
        next_run=fin_scrutin,
        name=name,
    )
