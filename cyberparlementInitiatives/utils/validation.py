import secrets

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django_q.tasks import async_task


def generate_validation_token(length):
    """
    Génère un jeton de validation cryptographiquement robuste.

    Arguments nommés :
    length -- nombre de chiffres du jeton de validation
    """

    choices = "1234567890"
    token = ""

    for i in range(0, length):
        token += choices[secrets.choice(range(0, len(choices)))]
    return token


def validate_token(validation_code, voteinitiative):
    """
    Retourne True si le jeton est valide, False s'il ne l'est pas.
    :param validation_code: code de validation
    :param voteinitiative: vote de l'initiative
    :return:
    """

    if voteinitiative.code_validation == validation_code:
        return True
    return False


def send_validation_email(voteinitiative, initiative, request):
    url = request.build_absolute_uri(reverse('initiative-validate-poll-vote', kwargs={'pk': initiative.id}))

    template = render_to_string(template_name='cyberparlementInitiatives/mail/poll_vote_validation.html',
                                context={
                                    'voteinitiative': voteinitiative,
                                    'initiative': initiative,
                                    'url': url,
                                },
                                request=request)

    async_task('django.core.mail.send_mail',
               subject='[Cyberparlement] Validation de votre vote',
               message="template",
               html_message=template,
               from_email='noa.devanthery@ceff.ch',
               recipient_list=[request.user.email],
               )
